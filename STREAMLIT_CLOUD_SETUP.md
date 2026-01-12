# Streamlit Cloud 配置指南

## 当前状态

您的应用已成功部署到 Streamlit Cloud：
- **应用URL**: `https://testcd-matching-tool-mkr7ouueecddpvbwra6bvd.streamlit.app`
- **问题**: 环境变量未配置，导致初始化失败

## 解决步骤

### 步骤1：进入应用管理页面

1. 访问您的应用：https://testcd-matching-tool-mkr7ouueecddpvbwra6bvd.streamlit.app
2. 点击页面右上角的 **"☰"（菜单）** 或 **"Manage app"** 按钮
   - 如果看不到菜单，也可以直接访问：https://share.streamlit.io/
   - 登录后，在应用列表中点击您的应用

### 步骤2：打开Settings（设置）

1. 在应用管理页面，点击 **"Settings"** 标签
2. 向下滚动找到 **"Secrets"** 部分

### 步骤3：配置Secrets

在 **"Secrets"** 文本框中，输入以下内容（使用TOML格式）：

```toml
[paths]
EXCEL_PATH = "Z:/projects/utility/metadata/SDTM Terminology.xls"
MAPPING_FILE = "Z:/projects/utility/macros/09_metadata/TEST_TESTCD_mapping.xlsx"
CACHE_DIR = "Z:/projects/utility/metadata/testcd_embedding"
```

**重要提示**：
- ✅ 路径使用 **正斜杠** `/`（不是反斜杠 `\`）
- ✅ 格式必须是TOML格式（使用 `[paths]` 作为节名）
- ✅ 每个路径用引号括起来

### 步骤4：保存并等待部署

1. 点击 **"Save"** 按钮保存配置
2. 应用会自动重新部署（通常需要30秒到1分钟）
3. 页面会显示部署进度

### 步骤5：验证配置

1. 等待部署完成后，刷新应用页面
2. 如果看到 **"匹配器初始化成功！"**，说明配置正确 ✅
3. 如果仍然报错，检查：
   - Secrets中的路径是否正确
   - 路径格式是否正确（使用正斜杠）
   - 文件是否存在于指定路径

## 如果文件在GitHub仓库中

如果您的数据文件已经上传到GitHub仓库，可以使用相对路径：

```toml
[paths]
EXCEL_PATH = "data/SDTM Terminology.xls"
MAPPING_FILE = "data/TEST_TESTCD_mapping.xlsx"
CACHE_DIR = "cache/testcd_embedding"
```

**前提条件**：
- 数据文件必须在GitHub仓库中
- 路径相对于项目根目录
- 确保文件已提交到仓库

## 常见问题

### Q1: 找不到"Manage app"按钮？

**解决方法**：
- 直接访问 https://share.streamlit.io/
- 登录后，在应用列表中点击您的应用名称
- 然后点击"Settings"

### Q2: 保存后仍然报错？

**检查清单**：
- [ ] Secrets格式是否正确（TOML格式）
- [ ] 路径使用正斜杠 `/`
- [ ] 路径用引号括起来
- [ ] 文件是否存在于指定路径
- [ ] 等待部署完成（可能需要1-2分钟）

### Q3: 如何确认Secrets已保存？

- 保存后，Secrets文本框中的内容应该保持不变
- 应用会自动触发重新部署
- 可以在"Activity"标签中查看部署日志

### Q4: 路径中的空格如何处理？

路径中的空格不需要特殊处理，直接使用引号括起来即可：
```toml
EXCEL_PATH = "Z:/projects/utility/metadata/SDTM Terminology.xls"
```

## 快速参考

**Secrets配置模板**（复制粘贴使用）：

```toml
[paths]
EXCEL_PATH = "Z:/projects/utility/metadata/SDTM Terminology.xls"
MAPPING_FILE = "Z:/projects/utility/macros/09_metadata/TEST_TESTCD_mapping.xlsx"
CACHE_DIR = "Z:/projects/utility/metadata/testcd_embedding"
```

**修改路径后，记得点击"Save"保存！**

