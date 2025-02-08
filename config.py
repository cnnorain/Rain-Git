import os
from utils.config_manager import config_manager

class Config:
    # Flask配置
    SECRET_KEY = os.urandom(24)
    
    # 从配置管理器获取token
    @property
    def GITHUB_TOKEN(self):
        return config_manager.get_tokens()['github_token']
    
    @property
    def GITEE_TOKEN(self):
        return config_manager.get_tokens()['gitee_token'] 