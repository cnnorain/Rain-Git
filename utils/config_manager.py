import json
import os
from pathlib import Path
import hashlib
import base64

class ConfigManager:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent  # 项目根目录
        self.config_file = self.config_dir / 'config.json'
        self.salt = os.environ.get('PASSWORD_SALT', 'default_salt')
        self._ensure_config()
        self._load_config()

    def _ensure_config(self):
        """确保配置文件存在"""
        if not self.config_file.exists():
            # 生成默认加密密码
            default_password = self._hash_password('admin')
            default_config = {
                "admin": {
                    "username": "admin",
                    "password": default_password
                },
                "tokens": {
                    "github_token": "",
                    "gitee_token": ""
                }
            }
            self._save_config(default_config)

    def _load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            # 生成默认加密密码
            default_password = self._hash_password('admin')
            self.config = {
                "admin": {
                    "username": "admin",
                    "password": default_password
                },
                "tokens": {
                    "github_token": "",
                    "gitee_token": ""
                }
            }

    def _save_config(self, config):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            return True
        except Exception as e:
            return False

    def get_tokens(self):
        """获取所有token"""
        return self.config.get('tokens', {
            'github_token': '',
            'gitee_token': ''
        })

    def update_tokens(self, github_token=None, gitee_token=None):
        """更新token"""
        if 'tokens' not in self.config:
            self.config['tokens'] = {}
            
        if github_token is not None:
            self.config['tokens']['github_token'] = github_token
        if gitee_token is not None:
            self.config['tokens']['gitee_token'] = gitee_token
        return self._save_config(self.config)

    def _hash_password(self, password):
        """对密码进行加密"""
        # 使用 PBKDF2 进行密码加密
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            self.salt.encode(),
            100000  # 迭代次数
        )
        return base64.b64encode(dk).decode()

    def _verify_password(self, password, hashed):
        """验证密码"""
        return self._hash_password(password) == hashed

    def check_login(self, username, password):
        """检查登录凭据"""
        admin = self.config.get('admin', {
            'username': 'admin',
            'password': self._hash_password('admin')  # 默认密码加密
        })
        return username == admin['username'] and self._verify_password(password, admin['password'])

    def update_admin(self, username, password):
        """更新管理员账号"""
        # 验证用户名和密码格式
        import re
        pattern = r'^[a-zA-Z0-9.][a-zA-Z0-9._-]{4,17}$'
        if not re.match(pattern, username) or not re.match(pattern, password):
            return False

        if 'admin' not in self.config:
            self.config['admin'] = {}
        
        self.config['admin']['username'] = username
        self.config['admin']['password'] = self._hash_password(password)
        return self._save_config(self.config)

# 创建全局配置管理器实例
config_manager = ConfigManager() 