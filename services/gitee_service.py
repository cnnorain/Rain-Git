import requests
from config import Config
import hashlib

class GiteeService:
    def __init__(self):
        self.token = ""
        self.base_url = "https://gitee.com/api/v5"
        self.headers = {}
        self.update_token(Config().GITEE_TOKEN)
    
    def update_token(self, token):
        """更新token"""
        self.token = token
    
    def get_repositories(self):
        """获取用户的所有仓库"""
        try:
            if not self.token:
                return []
                
            response = requests.get(
                f"{self.base_url}/user/repos",
                params={
                    "access_token": self.token,
                    "sort": "updated",
                    "per_page": 100,
                    "type": "all"
                }
            )
            response.raise_for_status()
            repos = response.json()
            
            # 格式化仓库数据
            return [{
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "html_url": repo.get("html_url", ""),
                "default_branch": repo.get("default_branch", "master"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "private": repo.get("private", False),
                "updated_at": repo.get("updated_at", ""),
                "clone_url": repo.get("html_url"),
                "ssh_url": f"git@gitee.com:{repo.get('full_name')}.git"
            } for repo in repos]
            
        except requests.exceptions.RequestException as e:
            return [] 

    def create_repository(self, name, description="", private=False, init_readme=False):
        """创建新仓库"""
        try:
            data = {
                "access_token": self.token,
                "name": name,
                "description": description,
                "private": private,
                "auto_init": init_readme,
                "has_issues": True,
                "has_wiki": True
            }
            
            response = requests.post(
                f"{self.base_url}/user/repos",
                params=data
            )
            response.raise_for_status()
            return True, "仓库创建成功"
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '创建失败')
            return False, str(e) 

    def delete_repository(self, repo_name):
        """删除仓库"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                params={"access_token": self.token}
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            response = requests.delete(
                f"{self.base_url}/repos/{username}/{repo_name}",
                params={"access_token": self.token}
            )
            response.raise_for_status()
            return True, "仓库删除成功"
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                error_msg = e.response.json().get('message', '删除失败')
                return False, error_msg
            return False, str(e) 

    def update_repository(self, repo_name, description=None, private=None, new_name=None, has_issues=None, has_wiki=None, path=None):
        """更新仓库设置"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                params={"access_token": self.token}
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            # 构建请求数据
            data = {}
            data['access_token'] = self.token
            data['name'] = new_name if new_name is not None else repo_name
            
            if new_name is not None and new_name != repo_name:
                data['path'] = new_name  # Gitee要求path和name保持一致
            if description is not None:
                data['description'] = description
            if private is not None:
                data['private'] = 1 if private else 0
            if has_issues is not None:
                data['has_issues'] = 1 if has_issues else 0
            if has_wiki is not None:
                data['has_wiki'] = 1 if has_wiki else 0
            
            url = f"{self.base_url}/repos/{username}/{repo_name}"
            
            response = requests.patch(
                url,
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 404:
                return False, f"仓库 {username}/{repo_name} 不存在，请检查仓库名称是否正确"
            
            response.raise_for_status()
            return True, "仓库设置更新成功"
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                try:
                    error_msg = e.response.json().get('message', '更新失败')
                except ValueError:
                    error_msg = e.response.text
                return False, error_msg
            return False, str(e) 

    def get_repository_files(self, repo_name, path=''):
        """获取仓库文件列表"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                params={"access_token": self.token}
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            # 构建请求参数
            params = {
                "access_token": self.token,
                "ref": "master"  # 默认使用master分支
            }
            
            response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                params=params
            )
            response.raise_for_status()
            contents = response.json()
            
            # 格式化文件列表
            if isinstance(contents, dict):  # 单个文件的情况
                contents = [contents]
            
            files = [{
                'name': item['name'],
                'path': item['path'],
                'type': 'dir' if item['type'] == 'tree' else 'file',
                'size': item.get('size', 0),
                'url': item['html_url']
            } for item in contents]
            
            return True, files
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '获取文件列表失败')
            return False, str(e)

    def get_file_content(self, repo_name, path):
        """获取文件内容"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                params={"access_token": self.token}
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            # 构建请求参数
            params = {
                "access_token": self.token,
                "ref": "master"  # 默认使用master分支
            }
            
            response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                params=params
            )
            response.raise_for_status()
            content = response.json()
            
            if content.get('type') != 'file':
                return False, '不是文件'
            
            import base64
            try:
                decoded_content = base64.b64decode(content['content']).decode('utf-8')
                return True, decoded_content
            except UnicodeDecodeError:
                return False, '不支持的文件格式（可能是二进制文件）'
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '获取文件内容失败')
            return False, str(e) 

    def delete_file(self, repo_name, path):
        """删除文件"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                params={"access_token": self.token}
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            # 先获取文件的SHA值
            response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                params={"access_token": self.token}
            )
            response.raise_for_status()
            content = response.json()
            
            # 删除文件
            response = requests.delete(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                params={"access_token": self.token},
                json={
                    'message': f'Delete {path}',
                    'sha': content['sha']
                }
            )
            response.raise_for_status()
            return True, "文件删除成功"
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '删除文件失败')
            return False, str(e) 

    def upload_file(self, repo_name, path, content, message):
        """上传文件"""
        try:
            print("\n=== Gitee 文件上传开始 ===")
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                params={"access_token": self.token}
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            print(f"当前用户: {username}")
            
            # 先检查仓库是否存在
            repo_response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}",
                params={"access_token": self.token}
            )
            if repo_response.status_code == 404:
                return False, "仓库不存在"
            repo_response.raise_for_status()
            
            # 使用当前用户作为所有者
            url = f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}"
            print(f"请求URL: {url}")
            
            # 检查文件是否已存在
            try:
                check_response = requests.get(
                    url,
                    params={"access_token": self.token}
                )
                check_response.raise_for_status()
                if check_response.status_code == 200:
                    existing_file = check_response.json()
                    if not isinstance(existing_file, list):
                        # 文件已存在，需要提供 sha
                        data = {
                            'message': message or f'Update file {path}',
                            'content': content,
                            'sha': existing_file['sha'],
                            'branch': 'master'
                        }
                    else:
                        # 是目录
                        return False, "不能上传到目录位置"
                else:
                    # 文件不存在，创建新文件
                    data = {
                        'message': message or f'Add file {path}',
                        'content': content,
                        'branch': 'master'
                    }
            except requests.exceptions.RequestException:
                # 文件不存在，创建新文件
                data = {
                    'message': message or f'Add file {path}',
                    'content': content,
                    'branch': 'master'
                }
            
            print(f"Uploading file to Gitee: {username}/{repo_name}/{path}")
            print(f"请求数据: {data}")
            
            # 上传文件
            response = requests.post(
                url,
                params={"access_token": self.token},
                json=data,
                headers={
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Accept': 'application/json'
                }
            )
            print(f"上传响应状态码: {response.status_code}")
            print(f"上传响应内容: {response.text[:500]}")
            print(f"请求URL: {response.request.url}")
            print(f"请求方法: {response.request.method}")
            print(f"请求体: {response.request.body}")
            
            # 处理非 JSON 响应
            if response.status_code == 404:
                return False, "仓库或路径不存在"
            
            try:
                response.raise_for_status()
                response_json = response.json()
                print(f"响应JSON: {response_json}")
                return True, "文件上传成功"
            except ValueError:
                print(f"非JSON响应: {response.text}")
                return False, "服务器返回了非预期的响应"
            
        except requests.exceptions.RequestException as e:
            print("\n=== Gitee 文件上传错误 ===")
            print(f"错误信息: {str(e)}")
            if hasattr(e.response, 'text'):
                try:
                    error_msg = e.response.json().get('message', '上传文件失败')
                except ValueError:
                    error_msg = '上传文件失败'
                print(f"错误响应: {error_msg}")
                print(f"完整响应: {e.response.text}")
            print("=== 错误信息结束 ===\n")
            return False, error_msg 