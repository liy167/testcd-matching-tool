# Git安装指南（Windows）

## 问题：git命令无法识别

如果看到以下错误：
```
git : 无法将"git"项识别为 cmdlet、函数、脚本文件或可运行程序的名称
```

说明Git未安装或未添加到系统PATH中。

## 解决方案

### 方法1：安装Git for Windows（推荐）

#### 步骤1：下载Git

1. 访问Git官网：https://git-scm.com/download/win
2. 页面会自动检测您的系统，显示下载链接
3. 点击下载按钮（文件名类似：`Git-2.42.0-64-bit.exe`）

#### 步骤2：安装Git

1. **双击下载的安装程序**

2. **安装向导步骤**：
   - **许可协议**：点击"Next"
   - **选择安装位置**：保持默认，点击"Next"
   - **选择组件**：保持默认（已勾选的选项），点击"Next"
   - **选择开始菜单文件夹**：保持默认，点击"Next"
   - **选择默认编辑器**：推荐选择"Use Visual Studio Code as Git's default editor"（如果安装了VS Code），或保持默认，点击"Next"
   - **调整PATH环境变量**：**重要！** 选择 **"Git from the command line and also from 3rd-party software"**，点击"Next"
   - **选择HTTPS传输后端**：保持默认（OpenSSL），点击"Next"
   - **配置行尾转换**：保持默认（Checkout Windows-style, commit Unix-style），点击"Next"
   - **配置终端模拟器**：保持默认（Use MinTTY），点击"Next"
   - **选择默认的"git pull"行为**：保持默认，点击"Next"
   - **选择凭据助手**：保持默认，点击"Next"
   - **配置额外选项**：保持默认，点击"Next"
   - **配置实验性选项**：不勾选任何选项，点击"Install"
   - 等待安装完成，点击"Finish"

#### 步骤3：验证安装

1. **关闭所有PowerShell和命令提示符窗口**（重要！）

2. **重新打开PowerShell**：
   - 按 `Win + X`，选择"Windows PowerShell"
   - 或在开始菜单搜索"PowerShell"

3. **验证Git是否安装成功**：
   ```powershell
   git --version
   ```
   
   如果显示版本号（如 `git version 2.42.0.windows.1`），说明安装成功！

#### 步骤4：配置Git（首次使用）

在PowerShell中执行以下命令：

```powershell
# 设置用户名（替换为您的姓名）
git config --global user.name "您的姓名"

# 设置邮箱（替换为您的邮箱，建议使用GitHub邮箱）
git config --global user.email "您的邮箱"
```

例如：
```powershell
git config --global user.name "Zhang San"
git config --global user.email "zhangsan@example.com"
```

**验证配置**：
```powershell
git config --global --list
```

应该能看到您刚才设置的用户名和邮箱。

### 方法2：使用Winget安装（如果已安装Windows包管理器）

```powershell
winget install --id Git.Git -e --source winget
```

安装后需要重新打开PowerShell。

### 方法3：使用Chocolatey安装（如果已安装Chocolatey）

```powershell
choco install git
```

安装后需要重新打开PowerShell。

## 常见问题

### Q1: 安装后仍然提示"无法识别git命令"

**解决方法**：
1. **完全关闭所有PowerShell/CMD窗口**
2. **重新打开PowerShell**（必须重新打开才能加载新的PATH）
3. 如果还是不行，检查PATH环境变量：
   - 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 确认包含：`C:\Program Files\Git\cmd` 或 `C:\Program Files (x86)\Git\cmd`
   - 如果没有，点击"新建"添加上述路径
   - 点击"确定"保存
   - **重新打开PowerShell**

### Q2: 如何检查Git是否已安装？

在PowerShell中运行：
```powershell
git --version
```

如果显示版本号，说明已安装。

### Q3: 安装时选择哪个PATH选项？

**推荐选择**：`Git from the command line and also from 3rd-party software`

这个选项会将Git添加到系统PATH，可以在任何地方使用git命令。

### Q4: 安装后需要重启电脑吗？

通常不需要重启电脑，但**必须重新打开PowerShell/CMD窗口**才能使用git命令。

## 下一步

安装完成后，回到 `QUICK_DEPLOY.md` 继续部署流程。

## 参考链接

- Git官网：https://git-scm.com/
- Git下载：https://git-scm.com/download/win
- Git文档：https://git-scm.com/doc

