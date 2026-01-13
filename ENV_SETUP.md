# 环境变量配置指南

本应用的所有文件路径都通过环境变量配置，不再使用硬编码路径。

**✅ 推荐方式**：项目根目录已创建 `.env` 文件，代码已自动支持从 `.env` 文件加载环境变量。您只需编辑 `.env` 文件中的路径即可。

## 必需的环境变量

- **EXCEL_PATH**: SDTM Terminology.xls 文件的完整路径
- **MAPPING_FILE**: TEST_TESTCD_mapping.xlsx 文件的完整路径
- **CACHE_DIR**: embedding缓存目录的完整路径

## Windows 设置方法

### 方法1：PowerShell（临时设置，当前会话有效）

```powershell
$env:EXCEL_PATH = "C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls"
$env:MAPPING_FILE = "C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx"
$env:CACHE_DIR = "C:\Users\liy167\YuLI\testcd_map\testcd_embedding"
```

### 方法2：命令提示符（临时设置，当前会话有效）

```cmd
set EXCEL_PATH=C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls
set MAPPING_FILE=C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx
set CACHE_DIR=C:\Users\liy167\YuLI\testcd_map\testcd_embedding
```

### 方法3：系统环境变量（永久设置）

1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"用户变量"或"系统变量"中点击"新建"
5. 添加以下变量：
   - 变量名：`EXCEL_PATH`，变量值：`C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls`
   - 变量名：`MAPPING_FILE`，变量值：`C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx`
   - 变量名：`CACHE_DIR`，变量值：`C:\Users\liy167\YuLI\testcd_map\testcd_embedding`
6. 点击"确定"保存
7. **重要**：需要重新打开命令行窗口或重启IDE才能生效

### 方法4：使用 .env 文件（推荐用于开发）✅

**注意**：`.env` 文件已经创建在项目根目录，代码已自动支持从 `.env` 文件加载环境变量。

1. **安装 python-dotenv**（如果还没有安装）：
   ```bash
   pip install python-dotenv
   ```
   或者安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. **编辑 `.env` 文件**（已创建，位于项目根目录）：
   ```
   EXCEL_PATH=C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls
   MAPPING_FILE=C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx
   CACHE_DIR=C:\Users\liy167\YuLI\testcd_map\testcd_embedding
   ```
   
   根据您的实际路径修改 `.env` 文件中的值。

3. **代码已自动支持**：
   - `config.py` 已自动加载 `.env` 文件
   - `streamlit_app.py` 已自动加载 `.env` 文件
   - 无需额外配置，直接运行即可

4. **验证**：
   运行程序时，会自动从 `.env` 文件读取环境变量。如果 `.env` 文件不存在或变量未设置，会使用默认值。

## Linux/Mac 设置方法

### 方法1：临时设置（当前会话有效）

```bash
export EXCEL_PATH="/path/to/SDTM Terminology.xls"
export MAPPING_FILE="/path/to/TEST_TESTCD_mapping.xlsx"
export CACHE_DIR="/path/to/testcd_embedding"
```

### 方法2：永久设置

编辑 `~/.bashrc` 或 `~/.zshrc`，添加：

```bash
export EXCEL_PATH="/path/to/SDTM Terminology.xls"
export MAPPING_FILE="/path/to/TEST_TESTCD_mapping.xlsx"
export CACHE_DIR="/path/to/testcd_embedding"
```

然后执行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

### 方法3：使用 .env 文件（推荐用于开发）✅

**注意**：`.env` 文件已经创建在项目根目录，代码已自动支持从 `.env` 文件加载环境变量。

1. **安装 python-dotenv**（如果还没有安装）：
   ```bash
   pip install python-dotenv
   ```
   或者安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. **编辑 `.env` 文件**（已创建，位于项目根目录）：
   ```
   EXCEL_PATH=/path/to/SDTM Terminology.xls
   MAPPING_FILE=/path/to/TEST_TESTCD_mapping.xlsx
   CACHE_DIR=/path/to/testcd_embedding
   ```
   
   根据您的实际路径修改 `.env` 文件中的值（使用Linux/Mac路径格式）。

3. **代码已自动支持**：
   - `config.py` 已自动加载 `.env` 文件
   - `streamlit_app.py` 已自动加载 `.env` 文件
   - 无需额外配置，直接运行即可

## Streamlit Cloud 设置

在 Streamlit Cloud 中设置环境变量：

1. 访问您的应用页面
2. 点击 "Manage app" → "Settings" → "Secrets"
3. 添加以下内容：

```toml
[paths]
EXCEL_PATH = "C:/Users/liy167/YuLI/testcd_map/SDTM Terminology.xls"
MAPPING_FILE = "C:/Users/liy167/YuLI/testcd_map/TEST_TESTCD_mapping.xlsx"
CACHE_DIR = "C:/Users/liy167/YuLI/testcd_map/testcd_embedding"
```

**注意**：Streamlit Cloud 使用 TOML 格式，路径使用正斜杠 `/`。

## Docker 设置

在 `docker-compose.yml` 或 `docker run` 命令中设置：

```yaml
environment:
  - EXCEL_PATH=/data/SDTM Terminology.xls
  - MAPPING_FILE=/mapping/TEST_TESTCD_mapping.xlsx
  - CACHE_DIR=/cache/testcd_embedding
```

## 验证环境变量

运行以下Python代码验证环境变量是否设置正确：

```python
import os

print("EXCEL_PATH:", os.getenv('EXCEL_PATH'))
print("MAPPING_FILE:", os.getenv('MAPPING_FILE'))
print("CACHE_DIR:", os.getenv('CACHE_DIR'))
```

如果输出为 `None`，说明环境变量未设置。

## 常见问题

**Q: 为什么程序报错说环境变量未设置？**

A: 请确保在运行程序之前已经设置了环境变量。如果使用系统环境变量，需要重新打开命令行窗口。

**Q: 路径中包含空格怎么办？**

A: 路径中的空格不需要特殊处理，直接使用完整路径即可。

**Q: 可以使用相对路径吗？**

A: 可以，但建议使用绝对路径以避免路径问题。

**Q: 在Streamlit Cloud中如何设置？**

A: 使用Secrets功能，格式为TOML，路径使用正斜杠。

