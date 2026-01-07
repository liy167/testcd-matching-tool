# 检查项目 TEST -> TESTCD 查询工具

这是一个基于Streamlit的Web应用，用于根据用户输入的检查项目名称（支持中英文），通过两步匹配机制查找最相似的匹配项。

## 功能特性

- **两步匹配机制**：
  1. **精确匹配**：首先在`TEST_TESTCD_mapping.xlsx`中进行精确匹配（TEST、TESTS_CN、TESTS_EN列）
  2. **语义匹配**：精确匹配失败时，在`SDTM Terminology.xls`中进行语义相似度匹配（E、F、H列）

- **智能匹配特性**：
  - 支持中英文输入
  - 忽略大小写
  - 支持分号分隔的同义词（`;`前后视为同义词）
  - 自动忽略"计数"和"绝对值"关键词
  - 处理Ratio关键词（不含"比值"时降权含'/'的值）
  - 优先匹配F列和H列

- **结果展示**：
  - 精确匹配：显示TESTDS、TESTS_CN、TESTS_EN列
  - 语义匹配：显示E、F、H列（F和H列自动显示中文翻译）
  - 支持JSON格式结果下载

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 确保数据文件存在

确保以下文件在指定路径存在：

- **SDTM Terminology.xls**: `Z:\projects\utility\metadata\SDTM Terminology.xls`
- **TEST_TESTCD_mapping.xlsx**: `Z:\projects\utility\macros\09_metadata\TEST_TESTCD_mapping.xlsx`

> 注意：如果文件在其他位置，可以在代码中修改路径或通过参数传入。

## 使用方法

### 运行Streamlit应用

```bash
python -m streamlit run streamlit_app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

### 使用界面

1. **输入查询**：在搜索框中输入检查项目名称（支持中英文）
2. **配置参数**：在侧边栏调整返回结果数量（1-20，默认10）
3. **查看结果**：
   - 精确匹配：显示绿色提示，展示TESTDS、TESTS_CN、TESTS_EN列
   - 语义匹配：显示相似度排序的结果，展示E、F、H列（带中文翻译）
4. **下载结果**：点击"下载JSON结果"按钮保存结果

## 匹配逻辑

### 精确匹配（第一步）

- **匹配列**：TEST列、TESTS_CN列、TESTS_EN列
- **匹配顺序**：TEST → TESTS_CN → TESTS_EN
- **特性**：
  - 忽略大小写
  - 支持分号分隔的同义词（`;`前后视为同义词）
  - 自动移除"计数"和"绝对值"后进行比较
  - 例如："红细胞计数"可以匹配到"红细胞"

### 语义匹配（第二步）

- **匹配列**：SDTM Terminology.xls的E、F、H列
- **特性**：
  - 使用多语言embedding模型计算语义相似度
  - 优先匹配F列和H列
  - 支持分号分隔的同义词
  - 自动忽略"绝对值"关键词
  - 处理Ratio关键词：如果查询不含"比值"或"Ratio"，则对F列和H列中包含'/'的值进行降权（乘以0.8）
- **返回结果**：默认返回前10个最相似的结果

## 技术实现

### 核心组件

- **lab_test_matcher.py**: 核心匹配逻辑
  - `LabTestMatcher`: 主匹配器类
  - `_load_mapping_file()`: 加载映射文件
  - `_exact_match_in_mapping()`: 精确匹配逻辑
  - `search_top_matches()`: 两步匹配主方法
  - `_calculate_similarity_with_synonyms()`: 语义相似度计算（支持同义词）

- **streamlit_app.py**: Streamlit Web界面
  - 提供友好的用户界面
  - 自动翻译英文术语为中文
  - 根据匹配类型显示不同列

### 使用的技术

- **Streamlit**: Web应用框架
- **pandas**: Excel文件读取和处理
- **openpyxl**: Excel文件支持
- **sentence-transformers**: 多语言embedding模型
- **paraphrase-multilingual-MiniLM-L12-v2**: 支持中英文的多语言模型
- **deep-translator**: 文本翻译
- **numpy**: 数值计算和向量相似度

### 数据流程

#### 精确匹配流程

1. 读取`TEST_TESTCD_mapping.xlsx`的Sheet1
2. 识别TEST、TESTS_CN、TESTS_EN列（用于匹配）
3. 识别TESTDS、TESTS_CN、TESTS_EN列（用于显示）
4. 对查询进行清理（移除"计数"、"绝对值"）
5. 依次与TEST、TESTS_CN、TESTS_EN列进行精确匹配（忽略大小写，支持分号分隔的同义词）
6. 匹配成功：返回TESTDS、TESTS_CN、TESTS_EN列

#### 语义匹配流程

1. 读取`SDTM Terminology.xls`的第二个sheet
2. 筛选D列（Codelist Name）值为"Laboratory Test Code"的行
3. 加载或计算E、F、H列的embeddings（支持缓存）
4. 对查询进行清理（移除"绝对值"）
5. 计算查询与E、F、H列的语义相似度
6. 处理同义词（分号分隔）
7. 处理Ratio关键词（不含"比值"时降权）
8. 优先使用F和H列的最大相似度
9. 按相似度降序排序，返回前k个结果

## 文件结构

```
testcd_map/
├── streamlit_app.py              # Streamlit Web应用（主入口）
├── lab_test_matcher.py           # 核心匹配逻辑
├── requirements.txt              # Python依赖包列表
├── README.md                     # 本文件
├── SESSION_RECORD.md             # 开发会话记录
├── testcd_embedding/             # Embedding缓存目录（位于Z:\projects\utility\metadata\，自动生成）
│   ├── embeddings_e_*.npy        # E列embeddings
│   ├── embeddings_f_*.npy       # F列embeddings
│   ├── embeddings_h_*.npy         # H列embeddings
│   └── meta_*.npz                # 元数据
└── archive/                      # 归档文件（旧版本和测试脚本）
    ├── lab_test_matcher_cn_v0.1.py
    ├── lab_test_matcher_only_CT_v1.0.py
    ├── lab_test_matcher_v1.py
    ├── test_matcher.py
    ├── mcp_client.py
    ├── mcp_server.py
    ├── quick_test.py
    ├── test_connection.py
    └── example_usage.py
```

## 配置说明

### 默认文件路径

- **SDTM Terminology.xls**: `Z:\projects\utility\metadata\SDTM Terminology.xls`
- **TEST_TESTCD_mapping.xlsx**: `Z:\projects\utility\macros\09_metadata\TEST_TESTCD_mapping.xlsx`

### 默认参数

- **模型名称**: `paraphrase-multilingual-MiniLM-L12-v2`
- **缓存目录**: `Z:\projects\utility\metadata\testcd_embedding`
- **默认top_k**: 10（语义匹配时返回的结果数量）

### 自定义路径

如果需要使用不同的文件路径，可以在代码中修改`LabTestMatcher`的初始化参数：

```python
from lab_test_matcher import LabTestMatcher

matcher = LabTestMatcher(
    excel_path="your/path/to/SDTM Terminology.xls",
    mapping_file="your/path/to/TEST_TESTCD_mapping.xlsx"
)
```

## 输出格式

### 精确匹配结果

| 排名 | 相似度 | TESTDS | TESTS_CN | TESTS_EN |
|------|--------|--------|----------|----------|
| 1 | 1.0000 | ... | ... | ... |

### 语义匹配结果

| 排名 | 相似度 | CDISC Submission Value (E) | CDISC Synonym(s) (F) | NCI Preferred Term (H) |
|------|--------|---------------------------|---------------------|------------------------|
| 1 | 0.8523 | Hemoglobin | HGB, Hb (血红蛋白) | Hemoglobin Measurement (血红蛋白测量) |
| ... | ... | ... | ... | ... |

### JSON格式

```json
{
  "total_matches": 10,
  "results": [
    {
      "similarity": 1.0,
      "testds_value": "...",
      "tests_cn_value": "...",
      "tests_en_value": "...",
      "is_exact_match": true,
      "row_index": -1
    },
    ...
  ]
}
```

## 注意事项

1. **首次运行**: embedding模型会在首次运行时自动下载（约420MB），需要网络连接
2. **缓存机制**: embeddings会缓存到本地`embeddings_cache`目录，提高后续搜索速度
3. **文件路径**: 确保映射文件和SDTM文件在指定路径存在，或修改代码中的默认路径
4. **列识别**: 程序会自动识别列名，支持多种列名变体（如TEST、Tests、测试等）
5. **Unicode转义**: Windows路径使用原始字符串（`r"..."`）避免转义问题

## 故障排除

### 文件未找到错误

- 检查文件是否在默认路径存在
- 或修改代码中的文件路径

### 模型下载失败

首次运行需要下载embedding模型，确保网络连接正常。如果下载失败，可以手动下载模型到本地。

### 列名不匹配

程序会自动识别列名，支持多种变体。如果识别失败，请检查Excel文件的列名，或查看控制台输出的列识别信息。

### Streamlit命令未找到

如果`streamlit`命令不可用，使用：
```bash
python -m streamlit run streamlit_app.py
```

## 开发

### 在Python代码中直接使用

```python
from lab_test_matcher import LabTestMatcher

# 初始化匹配器
matcher = LabTestMatcher()

# 执行搜索
results = matcher.search_top_matches("血红蛋白", top_k=10)

# 查看结果
for result in results:
    print(f"相似度: {result['similarity']:.4f}")
    if result.get('is_exact_match'):
        print(f"TESTDS: {result.get('testds_value')}")
        print(f"TESTS_CN: {result.get('tests_cn_value')}")
        print(f"TESTS_EN: {result.get('tests_en_value')}")
    else:
        print(f"E列: {result.get('e_value')}")
        print(f"F列: {result.get('f_value')}")
        print(f"H列: {result.get('h_value')}")
```

## 许可证

本项目仅供内部使用。
# testcd-matching-tool
