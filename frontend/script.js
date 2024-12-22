document.getElementById('uploadButton').addEventListener('click', function() {
    document.getElementById('imageInput').click();
});

document.getElementById('imageInput').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('image', file);

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('colorImage').src = data.color_image;
                document.getElementById('grayImage').src = data.gray_image;
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
    const uniqueId = document.getElementById('colorImage').src.split('/').pop().split('.')[0].split('_')[1];
    window.location.href = `/download_color?id=${uniqueId}`;
});

document.getElementById('downloadGray').addEventListener('click', function() {
    const uniqueId = document.getElementById('grayImage').src.split('/').pop().split('.')[0].split('_')[1];
    window.location.href = `/download_gray?id=${uniqueId}`;
});

document.getElementById('downloadModel').addEventListener('click', function() {
    window.location.href = '/download_model';
});
