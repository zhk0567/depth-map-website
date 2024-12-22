from flask import Flask, request, jsonify, send_file, redirect, url_for, send_from_directory
from io import BytesIO
import base64
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 模型文件的下载链接（从 GitHub Releases 获取）
MODEL_URL = "https://github.com/your-username/depth-map-website/releases/download/v1.0/dpt_large_384.pt"

@app.route('/')
def index():
    return '''
        <!doctype html>
        <title>深度图生成器</title>
        <h1>上传图片以生成深度图</h1>
        <form method=post enctype=multipart/form-data action="/">
          <input type=file name=image>
          <input type=submit value=上传>
        </form>
        <div class="download-model">
            <h3>下载模型文件</h3>
            <a href="/download_model" download>点击这里下载模型文件</a>
        </div>
    '''

@app.route('/upload', methods=['POST'])
def upload_image():
    # ... [之前的上传处理代码保持不变]
    pass

@app.route('/download_color', methods=['GET'])
def download_color():
    # ... [之前的下载彩色深度图代码保持不变]
    pass

@app.route('/download_gray', methods=['GET'])
def download_gray():
    # ... [之前的下载灰度深度图代码保持不变]
    pass

@app.route('/download_model', methods=['GET'])
def download_model():
    try:
        # 发送 GET 请求到 GitHub Releases 下载链接
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
