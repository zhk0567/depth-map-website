document.getElementById('uploadButton').addEventListener('click', function() {
    document.getElementById('imageInput').click();
});

document.getElementById('imageInput').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('image', file);

        fetch('/', {  // 发送到根路径
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // 设置彩色深度图的 src 为 Base64 数据
                document.getElementById('colorImage').src = 'data:image/jpeg;base64,' + data.color_image;
                // 设置灰度深度图的 src 为 Base64 数据
                document.getElementById('grayImage').src = 'data:image/jpeg;base64,' + data.gray_image;
                document.getElementById('resultSection').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('发生错误，请稍后再试。');
        });
    }
});

document.getElementById('downloadColor').addEventListener('click', function() {
    const base64Data = dataURLtoBlob(document.getElementById('colorImage').src);
    const blob = new Blob([base64Data], { type: 'image/jpeg' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'depth_map_color.jpg';
    link.click();
    window.URL.revokeObjectURL(url);
});

document.getElementById('downloadGray').addEventListener('click', function() {
    const base64Data = dataURLtoBlob(document.getElementById('grayImage').src);
    const blob = new Blob([base64Data], { type: 'image/jpeg' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'depth_map_gray.jpg';
    link.click();
    window.URL.revokeObjectURL(url);
});

// 辅助函数：将 Data URL 转换为 Blob
function dataURLtoBlob(dataurl) {
    const parts = dataurl.split(',');
    const mime = parts[0].split(':')[1].split(';')[0];
    const byteCharacters = atob(parts[1]);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mime });
}