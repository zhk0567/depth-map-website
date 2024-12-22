from flask import Flask, request, jsonify, send_file, redirect, url_for, send_from_directory
from io import BytesIO
import base64
from flask_cors import CORS
import uuid
import os
import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests

app = Flask(__name__)
CORS(app)

# 加载预训练的 MiDaS 模型
midas_model_type = "DPT_Large"  # 选择模型类型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型
midas = torch.hub.load("intel-isl/MiDaS", midas_model_type, pretrained=True, trust_repo=True)
midas.to(device)
midas.eval()

# 设置图像保存路径
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 设置模型文件的下载链接
MODEL_URL = "https://github.com/zhk0567/depth-map-website/releases/download/v1.0/dpt_large_384.pt"

MODEL_PATH = "models/dpt_large_384.pt"

@app.before_first_request
def download_model():
    if not os.path.exists(MODEL_PATH):
        response = requests.get(MODEL_URL, stream=True)
        with open(MODEL_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return upload_image()
    else:
        return '''
            <!doctype html>
            <title>深度图生成器</title>
            <h1>上传图片以生成深度图</h1>
            <form method=post enctype=multipart/form-data action="/">
              <input type=file name=image>
              <input type=submit value=上传>
            </form>
        '''

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        return jsonify({'error': 'Invalid file type'}), 400

    if file.content_length > 5 * 1024 * 1024:
        return jsonify({'error': 'File too large'}), 400

    try:
        # 读取图像
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # 将图像转换为 RGB 格式
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_image = cv2.resize(image_rgb, (384, 384))  # 根据模型输入调整大小
        input_image = input_image.astype(np.float32) / 255.0  # 归一化
        input_image = input_image.transpose(2, 0, 1)  # 变换维度为 C, H, W
        input_tensor = torch.from_numpy(input_image).unsqueeze(0).to(device)

        # 使用模型预测深度图
        with torch.no_grad():
            depth_map = midas(input_tensor)

        # 处理输出
        depth_map = depth_map.squeeze().cpu().numpy()
        depth_map = cv2.resize(depth_map, (image.shape[1], image.shape[0]))  # 调整至原图大小
        depth_map_normalized = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())  # 归一化
        depth_map_uint8 = (depth_map_normalized * 255).astype(np.uint8)  # 转换为 8 位

        # 生成彩色深度图
        depth_map_color = plt.cm.plasma(depth_map_normalized)[:, :, :3] * 255
        depth_map_color_uint8 = depth_map_color.astype(np.uint8)

        # 保存图像到服务器
        unique_id = uuid.uuid4()
        color_filename = f'static/images/color_{unique_id}.jpg'
        gray_filename = f'static/images/gray_{unique_id}.jpg'

        cv2.imwrite(color_filename, depth_map_color_uint8)
        cv2.imwrite(gray_filename, depth_map_uint8)

        # 返回结果
        return jsonify({
            'color_image': url_for('static', filename=color_filename),
            'gray_image': url_for('static', filename=gray_filename)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_color', methods=['GET'])
def download_color():
    try:
        unique_id = request.args.get('id')
        color_filename = f'static/images/color_{unique_id}.jpg'
        return send_from_directory(app.config['UPLOAD_FOLDER'], f'color_{unique_id}.jpg', as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_gray', methods=['GET'])
def download_gray():
    try:
        unique_id = request.args.get('id')
        gray_filename = f'static/images/gray_{unique_id}.jpg'
        return send_from_directory(app.config['UPLOAD_FOLDER'], f'gray_{unique_id}.jpg', as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_model', methods=['GET'])
def download_model():
    try:
        response = requests.get(MODEL_URL, stream=True)
        return send_file(
            BytesIO(response.content),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name='dpt_large_384.pt'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
