# 会话记录 - 实验室检查项目匹配器开发

## 项目概述

将本地Python脚本转换为基于Streamlit的网页应用，实现实验室检查项目的语义相似度匹配功能。

## 开发时间线

### 1. 初始需求
- **需求**：将本地Python脚本（`test_matcher.py`）转换为网页版，支持直接输入文字查询结果
- **技术选型**：使用Streamlit框架

### 2. 性能优化
- **需求**：预计算并保存embeddings，避免每次搜索都重新计算
- **实现**：
  - 创建缓存目录 `embeddings_cache`
  - 基于文件路径和模型名称生成唯一缓存键
  - 使用NumPy保存embedding数组
  - 使用pickle保存同义词映射
  - 首次运行计算并保存，后续运行直接加载

### 3. 匹配优先级优化
- **需求**：计算相似性时，优先匹配F列和H列
- **实现**：在相似度计算中，优先使用F和H列的最大值，如果F/H列相似度接近E列，则优先使用F/H列

### 4. 同义词处理
- **需求**：F列和H列中，分号（`;`）前后的词语视为同义词
- **实现**：
  - 检测包含分号的文本
  - 为每个同义词单独计算embedding
  - 匹配时取所有同义词中的最大相似度
  - 精确匹配时，如果分号前的第一个词与查询完全相同，给予最高相似度（1.0）

### 5. 精确匹配逻辑修复
- **问题**：输入'Hemoglobin'时，'Hemoglobin A'排在'Hemoglobin; Hemoglobin Monomer'之前
- **修复**：确保精确匹配（相似度为1.0）的结果具有最高优先级，不受E列影响

### 6. 大小写不敏感匹配
- **需求**：匹配时忽略大小写
- **实现**：在比较时统一转换为小写

### 7. Ratio符号处理
- **需求**：F列和H列中的"/"不是分隔符，表示Ratio（比值）
- **实现**：
  - 明确注释：只使用分号（`;`）作为分隔符
  - "/"不作为分隔符处理

### 8. Ratio关键词处理
- **需求**：如果输入值中不含"比值"或"Ratio"，则F和H列中不含'/'的相似度高于含'/'的值
- **实现**：
  - 检测查询中是否包含"比值"或"ratio"
  - 如果不包含，对F列和H列中包含'/'的值进行降权（乘以0.8）
  - 精确匹配（1.0）不受降权影响

### 9. 默认top_k调整
- **需求**：将默认top_k值从5改为10
- **修改文件**：
  - `lab_test_matcher.py`: `search_top_matches`方法默认参数
  - `streamlit_app.py`: slider默认值
  - `mcp_server.py`: 默认值
  - `mcp_client.py`: 默认值和帮助文本

### 10. 绝对值关键词处理
- **需求**：忽略输入值中的"绝对值"
- **实现**：
  - 在查询处理时移除"绝对值"或"Absolute Value"（不区分大小写）
  - 移除后如果查询为空，则使用原查询

### 11. 中文翻译显示
- **需求**：Streamlit页面输出的F列和H列，展示英文的同时展示汉语翻译
- **实现**：
  - 使用`deep-translator`库进行翻译
  - 实现翻译缓存机制（TTL=3600秒）
  - 检查文本是否已包含中文，避免重复翻译
  - 处理分号分隔的多个同义词

### 12. 映射文件集成
- **需求**：读取`TEST_TESTCD_mapping.xlsx`（Sheet1），E列与`SDTM Terminology.xls`的E列关联，获取映射文件的F列作为SDTM文件的F列中文翻译，并对映射文件的F列也做embedding
- **实现**：
  - 添加`_load_mapping_file`方法
  - 自动识别E列和F列（支持多种列名）
  - 建立E列到F列中文的映射
  - 计算F列中文的embedding
  - 在相似度计算中考虑F列中文的相似度
  - 在结果中包含`f_cn_value`

### 13. 根据输入语言优化匹配
- **需求**：若用户输入是中文，则优选F_CN和H列；若用户输入是英文，则优选F和H列
- **实现**：
  - 检测查询是否包含中文字符
  - 中文输入：优先使用F列中文和H列的最大值
  - 英文输入：优先使用F列英文和H列的最大值

### 14. 两步匹配机制
- **需求**：
  - 第一步：输入值首先与`TEST_TESTCD_mapping.xlsx`的F列或G列进行精确匹配（忽略大小写）
    - 中文输入值优选F列，英文输入值优选G列
    - 若能匹配上，直接输出映射文件的A、E、F、G列
  - 第二步：若不能匹配上，则与`SDTM Terminology.xls`的E、F、H列进行语义匹配
- **实现**：
  - 添加`_exact_match_in_mapping`方法进行精确匹配
  - 修改`search_top_matches`方法，先尝试精确匹配，失败后再进行语义匹配
  - 精确匹配结果包含`is_exact_match=True`标记
  - Streamlit页面根据匹配类型显示不同列

### 15. 精确匹配优化
- **需求**：
  - 精确匹配时显示映射文件的E、F、G列（后改为TESTDS、TESTS_CN、TESTS_EN列）
  - 增加C列匹配（后改为TEST列匹配）
  - 匹配时忽略"计数"和"绝对值"
- **实现**：
  - 修改列识别逻辑，识别TEST、TESTS_CN、TESTS_EN列（用于匹配）
  - 识别TESTDS、TESTS_CN、TESTS_EN列（用于显示）
  - 匹配顺序：TEST列 → TESTS_CN列 → TESTS_EN列
  - 实现`remove_ignored_words`函数，移除"计数"和"绝对值"
  - 在查询清理和匹配比较时都应用忽略词处理

### 16. 文件路径配置
- **需求**：修改文件路径
  - `TEST_TESTCD_mapping.xlsx`: `C:\Users\liy167\YuLI\testcd_map\`
  - `SDTM Terminology.xls`: `C:\Users\liy167\YuLI\testcd_map\`
- **实现**：
  - 修改`__init__`方法的默认路径参数
  - 使用原始字符串（`r"..."`）避免转义问题
  - 修复文档字符串中的路径（使用正斜杠）

## 核心功能

### 精确匹配（第一步）
- **匹配列**：TEST列、TESTS_CN列、TESTS_EN列
- **匹配顺序**：TEST → TESTS_CN → TESTS_EN
- **特性**：
  - 忽略大小写
  - 支持分号分隔的同义词
  - 忽略"计数"和"绝对值"
- **返回列**：TESTDS、TESTS_CN、TESTS_EN

### 语义匹配（第二步）
- **匹配列**：SDTM Terminology.xls的E、F、H列
- **特性**：
  - 使用多语言embedding模型计算语义相似度
  - 优先匹配F列和H列
  - 支持分号分隔的同义词
  - 忽略"绝对值"
  - 处理Ratio关键词（不含"比值"时降权含'/'的值）
- **返回列**：E、F、H列（F列和H列显示中文翻译）

## 技术栈

- **Python 3.x**
- **Streamlit**: Web应用框架
- **pandas**: Excel文件处理
- **sentence-transformers**: 多语言embedding模型
- **numpy**: 数值计算和向量相似度
- **deep-translator**: 文本翻译

## 文件结构

```
testcd_map/
├── lab_test_matcher.py          # 核心匹配逻辑
├── streamlit_app.py              # Streamlit Web界面
├── test_matcher.py              # 本地测试脚本
├── mcp_server.py                # MCP服务器
├── mcp_client.py                # MCP客户端
├── requirements.txt             # 依赖包列表
├── embeddings_cache/            # Embedding缓存目录
└── SESSION_RECORD.md            # 本会话记录文档
```

## 主要代码修改

### lab_test_matcher.py

#### 关键方法

1. **`__init__`**: 初始化匹配器，加载数据和映射文件
2. **`_load_mapping_file`**: 加载映射文件，识别TEST、TESTS_CN、TESTS_EN列
3. **`_exact_match_in_mapping`**: 在映射文件中进行精确匹配
4. **`_compute_and_save_embeddings`**: 计算并保存embeddings
5. **`_load_embeddings`**: 从缓存加载embeddings
6. **`search_top_matches`**: 两步匹配：先精确匹配，再语义匹配
7. **`_calculate_similarity_with_synonyms`**: 计算相似度，处理同义词

#### 关键特性

- **缓存机制**: 基于文件路径和模型名称的MD5哈希生成唯一缓存键
- **同义词处理**: 分号分隔的同义词分别计算embedding，取最大相似度
- **精确匹配优先**: 精确匹配结果直接返回，跳过语义匹配
- **忽略词处理**: 自动移除"计数"和"绝对值"进行匹配

### streamlit_app.py

#### 关键功能

1. **翻译功能**: 使用`deep-translator`翻译英文术语
2. **结果展示**: 根据匹配类型（精确匹配/语义匹配）显示不同列
3. **精确匹配显示**: TESTDS、TESTS_CN、TESTS_EN列
4. **语义匹配显示**: E、F、H列（F和H列带中文翻译）

## 配置说明

### 默认文件路径

- **SDTM Terminology.xls**: `C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls`
- **TEST_TESTCD_mapping.xlsx**: `C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx`

### 默认参数

- **模型名称**: `paraphrase-multilingual-MiniLM-L12-v2`
- **缓存目录**: `embeddings_cache`
- **默认top_k**: 10

## 使用说明

### 运行Streamlit应用

```bash
python -m streamlit run streamlit_app.py
```

### 匹配流程

1. **精确匹配**：
   - 输入值与TEST、TESTS_CN、TESTS_EN列进行精确匹配
   - 忽略大小写、"计数"、"绝对值"
   - 支持分号分隔的同义词
   - 匹配成功：返回TESTDS、TESTS_CN、TESTS_EN列

2. **语义匹配**（精确匹配失败时）：
   - 与SDTM Terminology.xls的E、F、H列进行语义相似度匹配
   - 返回前10个最相似的结果
   - F列和H列显示中文翻译

## 注意事项

1. **首次运行**: embedding模型会自动下载（约420MB），需要网络连接
2. **缓存机制**: embeddings会缓存到本地，提高后续搜索速度
3. **文件路径**: 确保映射文件和SDTM文件在指定路径存在
4. **列识别**: 程序会自动识别列名，支持多种列名变体
5. **Unicode转义**: Windows路径使用原始字符串（`r"..."`）避免转义问题

## 未来改进建议

1. 支持更多文件格式（CSV、JSON等）
2. 添加批量查询功能
3. 优化大文件处理性能
4. 添加更多匹配策略配置选项
5. 支持自定义忽略词列表

