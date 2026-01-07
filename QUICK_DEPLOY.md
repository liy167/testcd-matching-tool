# 快速部署步骤 - Streamlit应用

## 最简单方案：使用Streamlit Cloud（推荐）

### 前置步骤：安装Git

**如果遇到 "git : 无法将'git'项识别为..." 错误，说明Git未安装。**

1. **下载Git**
   - 访问：https://git-scm.com/download/win
   - 点击下载按钮（会自动下载适合Windows的版本）

2. **安装Git**
   - 双击下载的安装程序（通常是 `Git-x.x.x-64-bit.exe`）
   - 安装过程中：
     - 保持默认选项即可
     - **重要**：在"Adjusting your PATH environment"步骤，选择 **"Git from the command line and also from 3rd-party software"**（推荐）
     - 其他选项保持默认，点击"Next"直到完成

3. **验证安装**
   - **关闭当前的PowerShell窗口**（重要！）
   - 重新打开PowerShell
   - 输入以下命令验证：
     ```powershell
     git --version
     ```
   - 如果显示版本号（如 `git version 2.42.0`），说明安装成功

4. **配置Git（首次使用）**
   ```powershell
   git config --global user.name "您的姓名"
   git config --global user.email "您的邮箱"
   ```
   例如：
   ```powershell
   git config --global user.name "Zhang San"
   git config --global user.email "zhangsan@example.com"
   ```

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

**在哪里输入命令？**
- 打开 **PowerShell** 或 **命令提示符（CMD）**
- 使用 `cd` 命令切换到项目目录：
  ```powershell
  cd C:\Users\liy167\YuLI\testcd_map
  ```
- 然后依次执行以下命令：

```bash
# 命令1：初始化Git（如果还没有）
# 作用：在当前目录创建一个Git仓库
git init

# 命令2：添加所有文件到Git暂存区
# 作用：告诉Git要跟踪哪些文件
git add .

# 命令3：提交文件到本地Git仓库
# 作用：保存当前的文件状态，创建一个"快照"
git commit -m "Initial commit: Streamlit app"

# 命令4：连接到GitHub仓库
# 作用：将本地仓库与GitHub上的远程仓库关联
# ⚠️ 重要：将 your-username 替换为您的GitHub用户名
git remote add origin https://github.com/your-username/testcd-matching-tool.git

# 命令5：将分支重命名为main（GitHub默认使用main分支）
git branch -M main

# 命令6：推送代码到GitHub
# 作用：将本地代码上传到GitHub
git push -u origin main
```

**详细说明**：
- **`git init`**：在当前文件夹初始化Git仓库（只需要执行一次）
- **`git add .`**：添加当前目录下的所有文件（`.` 表示当前目录）
- **`git commit`**：提交更改，`-m` 后面是提交说明
- **`git remote add origin`**：添加远程仓库地址（只需要执行一次）
- **`git branch -M main`**：将当前分支重命名为 `main`
- **`git push`**：将代码推送到GitHub

**注意**：
- 如果提示输入用户名和密码，请使用GitHub Personal Access Token作为密码
- 如果还没有安装Git，请先下载安装：https://git-scm.com/download/win
- 如果提示"fatal: not a git repository"，说明需要先执行 `git init`

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

