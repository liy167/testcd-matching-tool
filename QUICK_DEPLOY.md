# 快速部署步骤 - Streamlit应用

## 最简单方案：使用Streamlit Cloud（推荐）

### 第一步：准备GitHub仓库

1. **注册/登录GitHub账号**
   - 访问 https://github.com
   - 如果没有账号，点击"Sign up"注册

2. **创建新仓库**
   - 登录后，点击右上角"+" → "New repository"
   - Repository name: `testcd-matching-tool`
   - Description: "检查项目TEST -> TESTCD查询工具"
   - 选择 **Public**（免费）或 **Private**（需要付费）
   - **不要**勾选"Initialize this repository with a README"
   - 点击"Create repository"

3. **在本地项目目录执行以下命令**

```bash
# 初始化Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Streamlit app"

# 连接到GitHub仓库（替换your-username为您的GitHub用户名）
git remote add origin https://github.com/your-username/testcd-matching-tool.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

**注意**：如果提示输入用户名和密码，请使用GitHub Personal Access Token作为密码。

### 第二步：部署到Streamlit Cloud

1. **访问Streamlit Cloud**
   - 打开 https://share.streamlit.io
   - 点击"Sign in with GitHub"使用GitHub账号登录

2. **创建新应用**
   - 点击"New app"按钮
   - 填写信息：
     - **Repository**: 选择您刚创建的仓库 `testcd-matching-tool`
     - **Branch**: `main`
     - **Main file path**: `streamlit_app.py`
     - **App URL**: 可以自定义（如：`testcd-matching`）

3. **配置环境变量（重要）**

   由于应用使用了Windows路径，需要在Streamlit Cloud中设置环境变量：

   点击"Advanced settings" → "Secrets"，添加以下内容：

   ```toml
   [paths]
   EXCEL_PATH = "Z:/projects/utility/metadata/SDTM Terminology.xls"
   MAPPING_FILE = "Z:/projects/utility/macros/09_metadata/TEST_TESTCD_mapping.xlsx"
   CACHE_DIR = "Z:/projects/utility/metadata/testcd_embedding"
   ```

   **或者**，如果数据文件需要上传到仓库：
   - 将数据文件添加到GitHub仓库
   - 修改`config.py`使用相对路径

4. **部署**
   - 点击"Deploy!"按钮
   - 等待1-2分钟，应用会自动部署

### 第三步：访问应用

部署完成后，您会看到：
- **应用URL**: `https://testcd-matching.streamlit.app`（或您自定义的URL）
- 将这个URL分享给团队成员即可访问

### 第四步：更新应用

以后每次修改代码后：

```bash
git add .
git commit -m "Update: 描述您的修改"
git push
```

Streamlit Cloud会自动检测到更新并重新部署（通常需要1-2分钟）。

---

## 如果使用自建服务器（内网部署）

### 第一步：准备服务器

1. **确保服务器已安装Python 3.8+**
   ```bash
   python --version
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install streamlit
   ```

3. **确保数据文件在服务器上**
   - 将`SDTM Terminology.xls`和`TEST_TESTCD_mapping.xlsx`复制到服务器
   - 确保路径正确，或修改`config.py`中的路径

### 第二步：运行应用

**测试运行**：
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

**后台运行（Linux）**：
```bash
nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

**后台运行（Windows）**：
```powershell
Start-Process python -ArgumentList "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0" -WindowStyle Hidden
```

### 第三步：配置防火墙

**Windows**：
```powershell
# 以管理员身份运行
New-NetFirewallRule -DisplayName "Streamlit" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

**Linux**：
```bash
sudo ufw allow 8501/tcp
```

### 第四步：访问应用

- 内网访问：`http://服务器IP:8501`
- 如果有域名：配置Nginx反向代理（参考DEPLOYMENT_GUIDE.md）

---

## 重要提示

### 关于数据文件

**Streamlit Cloud部署时**：
- 如果数据文件很大（>100MB），建议使用外部存储（如AWS S3）
- 如果数据文件较小，可以上传到GitHub仓库，但需要修改代码使用相对路径

**自建服务器部署时**：
- 确保数据文件在服务器上可访问
- 检查文件路径和权限

### 关于路径配置

代码已支持通过环境变量配置路径：
- 在Streamlit Cloud的Secrets中设置
- 或在服务器上设置环境变量
- 或直接修改`config.py`文件

### 关于性能

- 首次运行需要下载embedding模型（约420MB）
- 首次计算embeddings需要较长时间
- 后续运行会使用缓存，速度较快

---

## 常见问题

**Q: Streamlit Cloud部署失败？**
A: 检查GitHub仓库是否正确，Main file path是否为`streamlit_app.py`

**Q: 应用无法找到数据文件？**
A: 检查环境变量配置，或修改`config.py`中的路径

**Q: 如何查看部署日志？**
A: 在Streamlit Cloud的应用页面点击"Manage app" → "Logs"

**Q: 如何停止应用？**
A: 在Streamlit Cloud中点击"Manage app" → "Settings" → "Delete app"

---

## 需要帮助？

详细部署说明请参考：`DEPLOYMENT_GUIDE.md`

