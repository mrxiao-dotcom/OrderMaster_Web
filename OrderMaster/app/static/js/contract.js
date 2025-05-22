function submitContract(event) {
    event.preventDefault();
    
    // 获取表单数据
    const formData = new FormData(event.target);
    console.log('提交的表单数据:', Object.fromEntries(formData));
    
    // 发送请求
    fetch('/orders/contract/new', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('服务器响应:', data);
        if (data.success) {
            window.location.href = '/orders/';
        } else {
            alert(data.message || '保存失败');
        }
    })
    .catch(error => {
        console.error('保存出错:', error);
        alert('保存失败');
    });
}