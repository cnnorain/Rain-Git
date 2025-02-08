# Rain-Git - 代码仓库管理工具

Rain-Git 是一个基于 Flask 的 Web 应用，用于同时管理 GitHub 和 Gitee 代码仓库。它提供了一个统一的界面来管理两个平台的仓库，支持仓库的创建、删除、修改等基本操作，以及文件的上传、删除和查看功能。

## 功能特点

- 统一管理 GitHub 和 Gitee 仓库
- 支持仓库的基本操作：
  - 创建新仓库
  - 删除仓库
  - 修改仓库设置
  - 查看仓库文件
- 文件管理功能：
  - 浏览仓库文件
  - 上传文件
  - 删除文件
  - 查看文件内容
- 支持跨平台同步操作：
  - 同步创建仓库
  - 同步删除仓库
  - 同步修改仓库设置
  - 同步上传文件
- 实时更新：使用 WebSocket 实时刷新仓库列表
- 安全特性：
  - 登录认证
  - 密码加密存储
  - Token 安全管理

## 技术栈

- 后端：
  - Flask
  - Flask-SocketIO
  - Python Requests
- 前端：
  - Bootstrap 5
  - Socket.IO
  - highlight.js

## 安装使用

1. 克隆项目：

```bash
git clone https://github.com/yourusername/rain-git.git
cd rain-git
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行应用：

```bash
python app.py
```

4. 访问 `http://localhost:5000` 并使用默认账号登录：
- 用户名：admin
- 密码：admin

5. 在设置页面配置 GitHub 和 Gitee 的访问令牌

## 配置说明

### Token 配置
- GitHub Token: 在 GitHub Settings -> Developer settings -> Personal access tokens 中获取
- Gitee Token: 在 Gitee 设置 -> 私人令牌 中获取

### 管理员账号
- 支持修改管理员用户名和密码
- 用户名和密码要求：
  - 以字母、数字或点(.)开头
  - 只能包含字母、数字、下划线(_)、中划线(-)、英文句号(.)
  - 长度为5-18个字符

## 开发说明

### 项目结构
```
Rain-Git/
├── app.py              # 主应用入口
├── config.py           # 配置文件
├── requirements.txt    # 依赖列表
├── services/          # 服务层
│   ├── github_service.py
│   └── gitee_service.py
├── static/           # 静态文件
│   ├── css/
│   └── js/
├── templates/        # 模板文件
└── utils/           # 工具类
```

### 本地开发
1. 启用调试模式：
```bash
export FLASK_ENV=development
python app.py
```

2. 访问 `http://localhost:5000`

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

[cnnorain](https://github.com/cnnorain)
    