# Streamlit应用部署指南

本指南将帮助您将检查项目TEST -> TESTCD查询工具部署到网络上，供团队成员通过网址访问。

## 部署方案选择

### 方案一：Streamlit Cloud（推荐 - 最简单）

**优点**：
- 免费（公开仓库）或付费（私有仓库）
- 自动部署和更新
- 无需服务器维护
- 支持GitHub/GitLab集成

**缺点**：
- 需要将代码推送到Git仓库
- 免费版仅支持公开仓库

### 方案二：自建服务器部署

**优点**：
- 完全控制
- 可以部署在内网
- 数据更安全

**缺点**：
- 需要服务器资源
- 需要维护和配置

### 方案三：云平台部署（AWS/Azure/GCP等）

**优点**：
- 可扩展性强
- 专业级服务

**缺点**：
- 需要云平台账号
- 配置相对复杂
- 可能有费用

---

## 方案一：Streamlit Cloud 部署（推荐）

### 前置要求

1. GitHub账号（如果没有，请先注册：https://github.com）
2. Git已安装
3. 代码已准备好

### 步骤1：准备代码仓库

#### 1.1 初始化Git仓库（如果还没有）

```bash
# 在项目目录下
git init
```

#### 1.2 创建.gitignore文件（如果还没有）

```bash
# 创建.gitignore文件，内容如下：
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
embeddings_cache/
*.npy
*.npz
*.pkl
.env
.venv
env/
venv/
.DS_Store
*.log
```

#### 1.3 提交代码到本地仓库

```bash
git add .
git commit -m "Initial commit: Streamlit app for test item matching"
```

### 步骤2：创建GitHub仓库并推送代码

#### 2.1 在GitHub上创建新仓库

1. 登录GitHub
2. 点击右上角"+" → "New repository"
3. 填写仓库信息：
   - Repository name: `testcd-matching-tool`（或您喜欢的名称）
   - Description: "检查项目TEST -> TESTCD查询工具"
   - 选择 Public（免费版）或 Private（需要付费）
   - **不要**勾选"Initialize this repository with a README"
4. 点击"Create repository"

#### 2.2 推送代码到GitHub

GitHub会显示推送命令，类似：

```bash
git remote add origin https://github.com/your-username/testcd-matching-tool.git
git branch -M main
git push -u origin main
```

**注意**：如果您的代码包含敏感信息（如文件路径），请先处理：

1. **创建配置文件**：将硬编码的路径移到配置文件
2. **使用环境变量**：在Streamlit Cloud中设置环境变量

### 步骤3：配置Streamlit Cloud

#### 3.1 访问Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 使用GitHub账号登录
3. 点击"New app"

#### 3.2 配置应用

1. **Repository**: 选择您刚创建的GitHub仓库
2. **Branch**: 选择 `main`（或您的主分支）
3. **Main file path**: 输入 `streamlit_app.py`
4. **App URL**: 可以自定义（如：`testcd-matching-tool`）

#### 3.3 配置环境变量（如果需要）

如果代码中使用了环境变量或需要配置路径，点击"Advanced settings"：

- 添加环境变量（如果需要）

#### 3.4 部署

点击"Deploy!"，等待部署完成（通常需要1-2分钟）

### 步骤4：访问应用

部署完成后，您会获得一个URL，例如：
```
https://your-app-name.streamlit.app
```

将这个URL分享给团队成员即可。

### 步骤5：更新应用

每次您推送代码到GitHub的main分支，Streamlit Cloud会自动重新部署应用。

---

## 方案二：自建服务器部署

### 前置要求

1. 一台服务器（Windows/Linux）
2. Python 3.8+ 已安装
3. 服务器有公网IP或域名

### 步骤1：在服务器上安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Streamlit
pip install streamlit
```

### 步骤2：配置防火墙

确保服务器防火墙允许访问Streamlit的默认端口（8501）：

**Windows**：
```powershell
# 以管理员身份运行PowerShell
New-NetFirewallRule -DisplayName "Streamlit" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

**Linux**：
```bash
sudo ufw allow 8501/tcp
```

### 步骤3：运行Streamlit应用

#### 方式A：直接运行（测试用）

```bash
streamlit run streamlit_app.py
```

#### 方式B：后台运行（生产环境）

**Windows（使用PowerShell）**：
```powershell
# 创建启动脚本 start_app.ps1
$script = @"
cd C:\path\to\testcd_map
python -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
"@
$script | Out-File -FilePath start_app.ps1 -Encoding UTF8

# 使用任务计划程序或nssm创建Windows服务
```

**Linux（使用systemd）**：

创建服务文件 `/etc/systemd/system/streamlit-app.service`：

```ini
[Unit]
Description=Streamlit TestCD Matching App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/testcd_map
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit-app
sudo systemctl start streamlit-app
```

### 步骤4：配置反向代理（可选，推荐）

使用Nginx作为反向代理，提供HTTPS支持：

#### 安装Nginx

**Ubuntu/Debian**：
```bash
sudo apt update
sudo apt install nginx
```

**CentOS/RHEL**：
```bash
sudo yum install nginx
```

#### 配置Nginx

编辑 `/etc/nginx/sites-available/streamlit-app`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/streamlit-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 配置HTTPS（使用Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 步骤5：访问应用

- **直接访问**：`http://your-server-ip:8501`
- **通过域名**：`http://your-domain.com`（如果配置了Nginx）
- **HTTPS**：`https://your-domain.com`（如果配置了SSL）

---

## 方案三：Docker部署（推荐用于生产环境）

### 步骤1：创建Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 启动命令
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 步骤2：创建.dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
embeddings_cache/
*.npy
*.npz
*.pkl
.env
.venv
.git
.gitignore
README.md
DEPLOYMENT_GUIDE.md
archive/
```

### 步骤3：构建和运行Docker容器

```bash
# 构建镜像
docker build -t testcd-matching-app .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -v C:/Users/liy167/YuLI/testcd_map:/data \
  -v C:/Users/liy167/YuLI/testcd_map:/mapping \
  -v C:/Users/liy167/YuLI/testcd_map/testcd_embedding:/cache \
  --name testcd-app \
  testcd-matching-app
```

### 步骤4：使用Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - C:/Users/liy167/YuLI/testcd_map:/data
      - C:/Users/liy167/YuLI/testcd_map:/mapping
      - C:/Users/liy167/YuLI/testcd_map/testcd_embedding:/cache
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
```

运行：
```bash
docker-compose up -d
```

---

## 重要配置说明

### 1. 文件路径配置

由于应用使用了硬编码的Windows路径，部署时需要：

**选项A：修改代码使用相对路径或环境变量**

创建 `config.py`：
```python
import os

# 从环境变量读取路径，如果没有则使用默认值
EXCEL_PATH = os.getenv('EXCEL_PATH', r"C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls")
MAPPING_FILE = os.getenv('MAPPING_FILE', r"C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx")
CACHE_DIR = os.getenv('CACHE_DIR', r"C:\Users\liy167\YuLI\testcd_map\testcd_embedding")
```

修改 `lab_test_matcher.py`：
```python
from config import EXCEL_PATH, MAPPING_FILE, CACHE_DIR

def __init__(self, excel_path: str = EXCEL_PATH, mapping_file: str = MAPPING_FILE, cache_dir: str = CACHE_DIR):
```

**选项B：在部署平台设置环境变量**

在Streamlit Cloud或服务器上设置环境变量。

### 2. 数据文件部署

确保数据文件在服务器上可访问：

- **Streamlit Cloud**：需要将数据文件上传到代码仓库（如果文件不大），或使用外部存储（S3等）
- **自建服务器**：确保文件在指定路径存在
- **Docker**：使用volume挂载数据文件

### 3. 性能优化

- **首次运行**：embedding模型下载和计算需要时间，建议预先运行一次
- **缓存**：确保缓存目录有写入权限
- **并发**：Streamlit默认支持多用户并发访问

---

## 安全建议

1. **不要将敏感信息提交到Git仓库**
   - 使用环境变量存储路径和配置
   - 使用`.gitignore`排除敏感文件

2. **使用HTTPS**
   - 配置SSL证书（Let's Encrypt免费）

3. **访问控制**（如果需要）
   - Streamlit Cloud支持密码保护
   - 自建服务器可以使用Nginx的HTTP Basic Auth

4. **定期更新**
   - 保持依赖包最新
   - 定期检查安全更新

---

## 故障排除

### 问题1：应用无法启动

- 检查Python版本（需要3.8+）
- 检查依赖是否安装完整
- 查看错误日志

### 问题2：文件路径错误

- 检查文件是否存在于指定路径
- 检查文件权限
- 使用绝对路径或环境变量

### 问题3：端口被占用

- 更改端口：`streamlit run streamlit_app.py --server.port 8502`
- 或停止占用端口的进程

### 问题4：embedding加载失败

- 检查缓存目录权限
- 检查磁盘空间
- 查看详细错误信息

---

## 推荐部署流程总结

### 最简单方案（适合快速部署）

1. **使用Streamlit Cloud**：
   - 将代码推送到GitHub
   - 在Streamlit Cloud连接仓库
   - 自动部署完成

### 企业内网方案（适合内部使用）

1. **自建服务器 + Nginx**：
   - 在内部服务器上部署
   - 使用Nginx反向代理
   - 配置内网域名访问

### 生产环境方案（适合正式使用）

1. **Docker + Docker Compose**：
   - 使用Docker容器化部署
   - 易于管理和扩展
   - 支持多环境部署

---

## 下一步

1. 选择适合您的部署方案
2. 按照对应方案的步骤执行
3. 测试应用功能
4. 分享URL给团队成员
5. 监控应用运行状态

如有问题，请查看Streamlit官方文档：https://docs.streamlit.io/

