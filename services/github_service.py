import requests
from config import Config

class GitHubService:
    def __init__(self):
        self.token = ""
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        self.update_token(Config().GITHUB_TOKEN)
    
    def update_token(self, token):
        """更新token"""
        self.token = token
        self.headers["Authorization"] = f"token {token}" if token else ""
    
    def get_repositories(self):
        """获取用户的所有仓库"""
        try:
            if not self.token:
                return []
                
            response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                params={"sort": "updated", "per_page": 100}
            )
            response.raise_for_status()
            repos = response.json()
            
            return [{
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "html_url": repo["html_url"],
                "default_branch": repo.get("default_branch", "master"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "private": repo.get("private", False),
                "updated_at": repo.get("updated_at", ""),
                "clone_url": repo.get("clone_url", ""),
                "ssh_url": repo.get("ssh_url", "")
            } for repo in repos]
            
        except requests.exceptions.RequestException as e:
            return []
    
    def create_repository(self, name, description="", private=False, init_readme=False):
        """创建新仓库"""
        try:
            data = {
                "name": name,
                "description": description,
                "private": private,
                "auto_init": init_readme
            }
            
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return True, "仓库创建成功"
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '创建失败')
            return False, str(e)
    
    def delete_repository(self, repo_name):
        """删除仓库"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            response = requests.delete(
                f"{self.base_url}/repos/{username}/{repo_name}",
                headers=self.headers
            )
            response.raise_for_status()
            return True, "仓库删除成功"
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                error_msg = e.response.json().get('message', '删除失败')
                print(f"GitHub API error response: {error_msg}")
                return False, error_msg
            return False, str(e)
    
    def update_repository(self, repo_name, description=None, private=None, new_name=None, has_issues=None, has_wiki=None, has_projects=None):
        """更新仓库设置"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            data = {}
            if new_name is not None and new_name != repo_name:
                data['name'] = new_name
            if description is not None:
                data['description'] = description
            if private is not None:
                data['private'] = private
            if has_issues is not None:
                data['has_issues'] = has_issues
            if has_wiki is not None:
                data['has_wiki'] = has_wiki
            if has_projects is not None:
                data['has_projects'] = has_projects
            
            response = requests.patch(
                f"{self.base_url}/repos/{username}/{repo_name}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return True, "仓库设置更新成功"
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                error_msg = e.response.json().get('message', '更新失败')
                print(f"GitHub API error response: {error_msg}")
                return False, error_msg
            return False, str(e)
    
    def get_repository_files(self, repo_name, path=''):
        """获取仓库文件列表"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                headers=self.headers
            )
            response.raise_for_status()
            contents = response.json()
            
            # 格式化文件列表
            files = [{
                'name': item['name'],
                'path': item['path'],
                'type': 'dir' if item['type'] == 'dir' else 'file',
                'size': item.get('size', 0),
                'url': item['html_url']
            } for item in contents]
            
            return True, files
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '获取文件列表失败')
            return False, str(e)
    
    def get_file_content(self, repo_name, path):
        """获取文件内容"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                headers=self.headers
            )
            response.raise_for_status()
            content = response.json()
            
            if content['type'] != 'file':
                return False, '不是文件'
            
            import base64
            decoded_content = base64.b64decode(content['content']).decode('utf-8')
            return True, decoded_content
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '获取文件内容失败')
            return False, str(e)
    
    def delete_file(self, repo_name, path):
        """删除文件"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            # 先获取文件的SHA值
            response = requests.get(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                headers=self.headers
            )
            response.raise_for_status()
            content = response.json()
            
            # 删除文件
            response = requests.delete(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                headers=self.headers,
                json={
                    'message': f'Delete {path}',
                    'sha': content['sha']
                }
            )
            response.raise_for_status()
            return True, "文件删除成功"
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '删除文件失败')
            return False, str(e)
    
    def upload_file(self, repo_name, path, content, message):
        """上传文件"""
        try:
            # 获取用户名
            user_response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            user_response.raise_for_status()
            username = user_response.json()['login']
            
            # 检查文件是否已存在
            try:
                response = requests.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                    headers=self.headers
                )
                response.raise_for_status()
                existing_file = response.json()
                # 文件存在，需要提供sha
                data = {
                    'message': message,
                    'content': content,
                    'sha': existing_file['sha']
                }
            except requests.exceptions.RequestException:
                # 文件不存在，直接创建
                data = {
                    'message': message,
                    'content': content
                }
            
            # 上传文件
            response = requests.put(
                f"{self.base_url}/repos/{username}/{repo_name}/contents/{path}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return True, "文件上传成功"
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API error: {str(e)}")
            if hasattr(e.response, 'text'):
                return False, e.response.json().get('message', '上传文件失败')
            return False, str(e) 