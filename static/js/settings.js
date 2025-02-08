// 处理管理员设置表单提交
document.getElementById('adminForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;
    
    // 验证格式
    const pattern = /^[a-zA-Z0-9.][a-zA-Z0-9._-]{4,17}$/;
    if (!pattern.test(username)) {
        alert('用户名格式不正确！');
        return;
    }
    if (!pattern.test(password)) {
        alert('密码格式不正确！');
        return;
    }
    
    try {
        const response = await fetch('/api/settings/admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const result = await response.json();
        if (result.success) {
            alert('管理员设置已保存');
            // 清空密码输入框
            document.getElementById('adminPassword').value = '';
        } else {
            alert('保存管理员设置失败: ' + result.message);
        }
    } catch (error) {
        alert('保存管理员设置时出错: ' + error);
    }
}); 