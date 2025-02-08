from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
import os
from config import Config, config_manager
from services.github_service import GitHubService
from services.gitee_service import GiteeService

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

# 初始化服务
github_service = GitHubService()
gitee_service = GiteeService()

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if config_manager.check_login(username, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """退出登录"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# 主页路由
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', config_manager=config_manager)

@socketio.on('connect')
def handle_connect(auth):
    if not session.get('logged_in'):
        return False
    
    # 连接成功后立即发送仓库数据
    emit_repositories()

@socketio.on('refresh_repos')
def handle_refresh():
    """处理刷新仓库列表的请求"""
    if not session.get('logged_in'):
        return
    
    emit_repositories()

def emit_repositories():
    """获取并发送仓库数据"""
    # 获取GitHub仓库
    github_repos = github_service.get_repositories()
    socketio.emit('github_repos', {'repos': github_repos})
    
    # 获取Gitee仓库
    gitee_repos = gitee_service.get_repositories()
    socketio.emit('gitee_repos', {'repos': gitee_repos})

@app.route('/settings')
def settings():
    """设置页面"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('settings.html', tokens=config_manager.get_tokens())

@app.route('/api/settings/tokens', methods=['POST'])
def update_tokens():
    """更新 token 设置"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    github_token = data.get('github_token')
    gitee_token = data.get('gitee_token')
    
    if config_manager.update_tokens(github_token, gitee_token):
        # 更新服务实例的token
        github_service.update_token(github_token)
        gitee_service.update_token(gitee_token)
        
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '保存设置失败'})

@app.route('/api/settings/admin', methods=['POST'])
def update_admin_settings():
    """更新管理员设置"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    if config_manager.update_admin(username, password):
        return jsonify({'success': True, 'message': '管理员设置已更新'})
    else:
        return jsonify({'success': False, 'message': '更新失败，请检查输入格式'})

@app.route('/api/repos/create', methods=['POST'])
def create_repository():
    """创建新仓库"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    platform = data.get('platform')
    name = data.get('name')
    description = data.get('description', '')
    is_private = data.get('private', False)
    init_readme = data.get('init_readme', False)
    sync_create = data.get('sync_create', False)
    
    if not name:
        return jsonify({'success': False, 'message': '仓库名称不能为空'})
    
    results = []
    
    if platform == 'github':
        success, message = github_service.create_repository(
            name, description, is_private, init_readme
        )
        results.append({"platform": "GitHub", "success": success, "message": message})
        
        if sync_create:
            success, message = gitee_service.create_repository(
                name, description, is_private, init_readme
            )
            results.append({"platform": "Gitee", "success": success, "message": message})
            
    elif platform == 'gitee':
        success, message = gitee_service.create_repository(
            name, description, is_private, init_readme
        )
        results.append({"platform": "Gitee", "success": success, "message": message})
        
        if sync_create:
            success, message = github_service.create_repository(
                name, description, is_private, init_readme
            )
            results.append({"platform": "GitHub", "success": success, "message": message})
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    # 判断是否全部成功
    all_success = all(result["success"] for result in results)
    
    # 生成消息
    messages = [f"{result['platform']}: {result['message']}" for result in results]
    
    return jsonify({
        'success': all_success,
        'message': '\n'.join(messages)
    })

@app.route('/api/repos/delete', methods=['POST'])
def delete_repository():
    """删除仓库"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    platform = data.get('platform')
    repo_name = data.get('repo_name')
    sync_delete = data.get('sync_delete', False)
    
    if not repo_name:
        return jsonify({'success': False, 'message': '仓库名称不能为空'})
    
    results = []
    
    if platform == 'github':
        success, message = github_service.delete_repository(repo_name)
        print(f"GitHub delete result: success={success}, message={message}")
        results.append({"platform": "GitHub", "success": success, "message": message})
        
        if sync_delete:
            success, message = gitee_service.delete_repository(repo_name)
            print(f"Gitee sync delete result: success={success}, message={message}")
            results.append({"platform": "Gitee", "success": success, "message": message})
            
    elif platform == 'gitee':
        success, message = gitee_service.delete_repository(repo_name)
        print(f"Gitee delete result: success={success}, message={message}")
        results.append({"platform": "Gitee", "success": success, "message": message})
        
        if sync_delete:
            success, message = github_service.delete_repository(repo_name)
            print(f"GitHub sync delete result: success={success}, message={message}")
            results.append({"platform": "GitHub", "success": success, "message": message})
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    # 判断是否全部成功
    all_success = all(result["success"] for result in results)
    
    # 生成消息
    messages = [f"{result['platform']}: {result['message']}" for result in results]
    
    return jsonify({
        'success': all_success,
        'message': '\n'.join(messages)
    })

@app.route('/api/repos/update', methods=['POST'])
def update_repository():
    """更新仓库设置"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    platform = data.get('platform')
    old_repo_name = data.get('old_repo_name')
    repo_name = data.get('repo_name')
    description = data.get('description')
    is_private = data.get('private')
    has_issues = data.get('has_issues')
    has_wiki = data.get('has_wiki')
    has_projects = data.get('has_projects')
    sync_edit = data.get('sync_edit', False)
    
    if not repo_name:
        return jsonify({'success': False, 'message': '仓库名称不能为空'})
    
    results = []
    
    if platform == 'github':
        success, message = github_service.update_repository(
            old_repo_name,
            description=description,
            private=is_private,
            new_name=repo_name if repo_name != old_repo_name else None,
            has_issues=has_issues,
            has_wiki=has_wiki,
            has_projects=has_projects
        )
        results.append({"platform": "GitHub", "success": success, "message": message})
        
        if sync_edit:
            success, message = gitee_service.update_repository(
                old_repo_name,
                description=description,
                private=is_private,
                new_name=repo_name if repo_name != old_repo_name else None,
                has_issues=has_issues,
                has_wiki=has_wiki
            )
            results.append({"platform": "Gitee", "success": success, "message": message})
            
    elif platform == 'gitee':
        success, message = gitee_service.update_repository(
            old_repo_name,
            description=description,
            private=is_private,
            new_name=repo_name if repo_name != old_repo_name else None,
            has_issues=has_issues,
            has_wiki=has_wiki,
            path=repo_name if repo_name != old_repo_name else None
        )
        results.append({"platform": "Gitee", "success": success, "message": message})
        
        if sync_edit:
            success, message = github_service.update_repository(
                old_repo_name,
                description=description,
                private=is_private,
                new_name=repo_name if repo_name != old_repo_name else None,
                has_issues=has_issues,
                has_wiki=has_wiki,
                has_projects=has_projects
            )
            results.append({"platform": "GitHub", "success": success, "message": message})
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    # 判断是否全部成功
    all_success = all(result["success"] for result in results)
    
    # 生成消息
    messages = [f"{result['platform']}: {result['message']}" for result in results]
    
    return jsonify({
        'success': all_success,
        'message': '\n'.join(messages)
    })

@app.route('/api/repos/files')
def get_repository_files():
    """获取仓库文件列表"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    platform = request.args.get('platform')
    repo = request.args.get('repo')
    path = request.args.get('path', '')
    
    if platform == 'github':
        success, files = github_service.get_repository_files(repo, path)
    elif platform == 'gitee':
        success, files = gitee_service.get_repository_files(repo, path)
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    if success:
        return jsonify({'success': True, 'files': files})
    else:
        return jsonify({'success': False, 'message': files})

@app.route('/api/repos/file-content')
def get_file_content():
    """获取文件内容"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    platform = request.args.get('platform')
    repo = request.args.get('repo')
    path = request.args.get('path')
    
    if platform == 'github':
        success, content = github_service.get_file_content(repo, path)
    elif platform == 'gitee':
        success, content = gitee_service.get_file_content(repo, path)
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    if success:
        return jsonify({'success': True, 'content': content})
    else:
        return jsonify({'success': False, 'message': content})

@app.route('/api/repos/delete-file', methods=['POST'])
def delete_repository_file():
    """删除仓库文件"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    platform = data.get('platform')
    repo = data.get('repo')
    path = data.get('path')
    
    if platform == 'github':
        success, message = github_service.delete_file(repo, path)
    elif platform == 'gitee':
        success, message = gitee_service.delete_file(repo, path)
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/repos/upload-file', methods=['POST'])
def upload_repository_file():
    """上传仓库文件"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    data = request.get_json()
    platform = data.get('platform')
    repo = data.get('repo')
    path = data.get('path')
    content = data.get('content')
    message = data.get('message')
    sync_upload = data.get('sync_upload', False)
    
    results = []
    
    if platform == 'github':
        success, msg = github_service.upload_file(repo, path, content, message)
        results.append({"platform": "GitHub", "success": success, "message": msg})
        
        if sync_upload:
            success, msg = gitee_service.upload_file(repo, path, content, message)
            results.append({"platform": "Gitee", "success": success, "message": msg})
            
    elif platform == 'gitee':
        success, msg = gitee_service.upload_file(repo, path, content, message)
        results.append({"platform": "Gitee", "success": success, "message": msg})
        
        if sync_upload:
            success, msg = github_service.upload_file(repo, path, content, message)
            results.append({"platform": "GitHub", "success": success, "message": msg})
    else:
        return jsonify({'success': False, 'message': '不支持的平台'})
    
    # 判断是否全部成功
    all_success = all(result["success"] for result in results)
    
    # 生成消息
    messages = [f"{result['platform']}: {result['message']}" for result in results]
    
    return jsonify({
        'success': all_success,
        'message': '\n'.join(messages)
    })

@app.context_processor
def inject_config_manager():
    return dict(config_manager=config_manager)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 默认端口5000，可通过环境变量设置
    socketio.run(app, host='0.0.0.0', port=port, debug=True) 