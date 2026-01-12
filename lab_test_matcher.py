"""
检查项目匹配器
使用embedding模型计算语义相似度，在SDTM Terminology.xls中查找最相似的检查项目
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import os
import sys
import hashlib

# 导入配置
try:
    from config import EXCEL_PATH, MAPPING_FILE, CACHE_DIR, check_required_env_vars
except ImportError:
    # 如果config.py不存在，直接从环境变量读取
    import os
    EXCEL_PATH = os.getenv('EXCEL_PATH')
    MAPPING_FILE = os.getenv('MAPPING_FILE')
    CACHE_DIR = os.getenv('CACHE_DIR')
    
    def check_required_env_vars():
        """检查必需的环境变量是否已设置"""
        missing_vars = []
        if not EXCEL_PATH:
            missing_vars.append('EXCEL_PATH')
        if not MAPPING_FILE:
            missing_vars.append('MAPPING_FILE')
        if not CACHE_DIR:
            missing_vars.append('CACHE_DIR')
        
        if missing_vars:
            error_msg = (
                f"错误：以下环境变量未设置：{', '.join(missing_vars)}\n"
                f"请设置以下环境变量：\n"
                f"  - EXCEL_PATH: SDTM Terminology.xls 文件路径\n"
                f"  - MAPPING_FILE: TEST_TESTCD_mapping.xlsx 文件路径\n"
                f"  - CACHE_DIR: embedding缓存目录路径\n"
                f"\n"
                f"设置方法（Windows PowerShell）：\n"
                f"  $env:EXCEL_PATH = 'C:\\Users\\liy167\\YuLI\\testcd_map\\SDTM Terminology.xls'\n"
                f"  $env:MAPPING_FILE = 'C:\\Users\\liy167\\YuLI\\testcd_map\\TEST_TESTCD_mapping.xlsx'\n"
                f"  $env:CACHE_DIR = 'C:\\Users\\liy167\\YuLI\\testcd_map\\testcd_embedding'\n"
                f"\n"
                f"设置方法（Linux/Mac）：\n"
                f"  export EXCEL_PATH='/path/to/SDTM Terminology.xls'\n"
                f"  export MAPPING_FILE='/path/to/TEST_TESTCD_mapping.xlsx'\n"
                f"  export CACHE_DIR='/path/to/testcd_embedding'"
            )
            raise ValueError(error_msg)
        
        return True


class LabTestMatcher:
    """检查项目匹配器"""
    
    def __init__(self, excel_path: str = None, mapping_file: str = None, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2", cache_dir: str = None):
        """
        初始化匹配器
        
        Args:
            excel_path: Excel文件路径（优先使用参数，否则从环境变量EXCEL_PATH读取）
            mapping_file: 映射文件路径（优先使用参数，否则从环境变量MAPPING_FILE读取）
            model_name: embedding模型名称
            cache_dir: embedding缓存目录（优先使用参数，否则从环境变量CACHE_DIR读取）
        """
        # 如果参数未提供，从环境变量读取
        if excel_path is None:
            if EXCEL_PATH is None:
                check_required_env_vars()  # 会抛出异常
            excel_path = EXCEL_PATH
        
        if mapping_file is None:
            if MAPPING_FILE is None:
                check_required_env_vars()  # 会抛出异常
            mapping_file = MAPPING_FILE
        
        if cache_dir is None:
            if CACHE_DIR is None:
                check_required_env_vars()  # 会抛出异常
            cache_dir = CACHE_DIR
        
        self.excel_path = excel_path
        self.mapping_file = mapping_file
        self.model = None
        self.model_name = model_name
        self.data = None
        self.cache_dir = cache_dir
        self.embeddings_e = None  # E列的embedding
        self.embeddings_f = None  # F列的embedding
        self.embeddings_h = None  # H列的embedding
        self.f_synonyms_map = {}  # F列分号分隔的同义词映射 {row_idx: {'synonyms': [...], 'embeddings': np.array}}
        self.h_synonyms_map = {}  # H列分号分隔的同义词映射
        self.mapping_data = None  # 映射文件数据
        self._load_data()
        self._load_mapping_file()
        self._load_or_compute_embeddings()
    
    def _load_data(self):
        """加载Excel数据"""
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel文件不存在: {self.excel_path}")
        
        # 读取第二个sheet（索引为1）
        try:
            xls = pd.ExcelFile(self.excel_path)
            sheet_names = xls.sheet_names
            if len(sheet_names) < 2:
                raise ValueError(f"Excel文件至少需要2个sheet，当前只有{len(sheet_names)}个")
            
            # 读取第二个sheet
            self.data = pd.read_excel(self.excel_path, sheet_name=1)
            
            # 筛选D列值="Laboratory Test Code"的行
            # D列是第4列（索引3），列名是 'Codelist Name'
            if 'Codelist Name' not in self.data.columns:
                raise ValueError("Excel文件缺少 'Codelist Name' 列")
            
            #self.data = self.data[self.data['Codelist Name'] == 'Laboratory Test Code'].copy() #先暂时不筛选，可以搜索所有CT
            
            if len(self.data) == 0:
                raise ValueError("未找到 'Laboratory Test Code' 的数据行")
            
            # 注意：在MCP server环境中，print输出到stdout会干扰MCP协议通信
            # 如果需要调试信息，应该输出到stderr
            # print(f"成功加载 {len(self.data)} 条检查项目数据", file=sys.stderr)
            
        except Exception as e:
            raise Exception(f"加载Excel文件失败: {str(e)}")
    
    def _load_mapping_file(self):
        """加载映射文件TEST_TESTCD_mapping.xlsx"""
        if not os.path.exists(self.mapping_file):
            print(f"警告: 映射文件不存在: {self.mapping_file}，将跳过精确匹配", file=sys.stderr, flush=True)
            self.mapping_data = None
            return
        
        try:
            # 读取映射文件（读取Sheet1，索引为0）
            self.mapping_data = pd.read_excel(self.mapping_file, sheet_name=0)
            
            # 自动识别列名
            # 用于匹配的列：TEST列、TESTS_CN列、TESTS_EN列
            # 用于显示的列：TESTDS、TESTS_CN、TESTS_EN
            test_col = None  # 用于匹配的TEST列
            tests_cn_col = None  # TESTS_CN列（用于匹配和显示）
            tests_en_col = None  # TESTS_EN列（用于匹配和显示）
            testds_col = None  # TESTDS列（用于显示）
            
            # 可能的列名（用于匹配）
            possible_test_cols = ['TEST', 'Test', '测试']
            possible_tests_cn_cols = ['TESTS_CN', 'Tests CN', '中文', 'Chinese']
            possible_tests_en_cols = ['TESTS_EN', 'Tests EN', '英文', 'English']
            
            # 用于显示的列名
            possible_testds_cols = ['TESTDS', 'Test Description', '测试描述']
            
            for col in self.mapping_data.columns:
                col_str = str(col).strip()
                # 识别用于匹配的列
                if test_col is None:
                    for possible in possible_test_cols:
                        if possible.lower() == col_str.lower() or col_str == possible:
                            test_col = col
                            break
                if tests_cn_col is None:
                    for possible in possible_tests_cn_cols:
                        if possible.lower() == col_str.lower() or col_str == possible:
                            tests_cn_col = col
                            break
                if tests_en_col is None:
                    for possible in possible_tests_en_cols:
                        if possible.lower() == col_str.lower() or col_str == possible:
                            tests_en_col = col
                            break
                # 识别用于显示的列
                if testds_col is None:
                    for possible in possible_testds_cols:
                        if possible.lower() == col_str.lower() or col_str == possible:
                            testds_col = col
                            break
            
            # 检查必要的列（用于匹配的TEST、TESTS_CN和TESTS_EN列至少需要存在一个）
            if test_col is None and tests_cn_col is None and tests_en_col is None:
                print(f"警告: 无法识别映射文件的TEST、TESTS_CN或TESTS_EN列（用于匹配），将跳过精确匹配", file=sys.stderr, flush=True)
                self.mapping_data = None
                return
            
            # 保存列名
            self.mapping_test_col = test_col  # 用于匹配的TEST列
            self.mapping_tests_cn_col = tests_cn_col  # TESTS_CN列（用于匹配和显示）
            self.mapping_tests_en_col = tests_en_col  # TESTS_EN列（用于匹配和显示）
            self.mapping_testds_col = testds_col  # 用于显示的TESTDS列
            
            print(f"成功加载映射文件: {len(self.mapping_data)} 条数据", file=sys.stderr, flush=True)
            print(f"映射文件列识别: TEST列（匹配）={test_col}, TESTS_CN列（匹配）={tests_cn_col}, TESTS_EN列（匹配）={tests_en_col}", file=sys.stderr, flush=True)
            print(f"映射文件列识别: TESTDS（显示）={testds_col}", file=sys.stderr, flush=True)
            print(f"映射文件所有列名: {list(self.mapping_data.columns)}", file=sys.stderr, flush=True)
            
        except Exception as e:
            print(f"警告: 加载映射文件失败: {e}，将跳过精确匹配", file=sys.stderr, flush=True)
            self.mapping_data = None
    
    def _exact_match_in_mapping(self, query: str) -> Optional[List[Dict]]:
        """
        在映射文件中进行精确匹配（忽略大小写）
        支持TEST列、TESTS_CN列和TESTS_EN列中包含分号分隔的值（分号前后视为同义词）
        匹配时忽略"计数"和"绝对值"一词（如"红细胞计数"等价于"红细胞"，"淋巴细胞绝对值"等价于"淋巴细胞"）
        匹配顺序：TEST列、TESTS_CN列、TESTS_EN列
        
        Args:
            query: 查询字符串
            
        Returns:
            如果匹配成功，返回结果列表（包含TESTDS、TESTS_CN、TESTS_EN列），否则返回None
        """
        if self.mapping_data is None:
            return None
        
        # 检测查询语言：检查是否包含中文字符
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
        
        # 清理查询字符串：去除首尾空格，转换为小写，移除"计数"和"绝对值"
        query_clean = query.strip().lower()
        # 移除"计数"和"绝对值"（忽略大小写）
        query_clean = query_clean.replace('计数', '').replace('绝对值', '').strip()
        # 同时移除英文的"Absolute Value"等变体
        query_clean = query_clean.replace('absolute value', '').replace('absolutevalue', '').strip()
        if not query_clean:
            return None
        
        matched_rows = []
        
        def remove_ignored_words(text: str) -> str:
            """移除文本中的'计数'和'绝对值'等需要忽略的词"""
            if not text:
                return text
            result = text
            # 移除中文的"计数"和"绝对值"
            result = result.replace('计数', '').replace('绝对值', '')
            # 移除英文的"Absolute Value"等变体
            result = result.replace('absolute value', '').replace('absolutevalue', '')
            return result.strip()
        
        def check_match(text: str, query: str) -> bool:
            """检查文本是否与查询匹配（支持分号分隔的同义词，忽略'计数'和'绝对值'）"""
            if not text:
                return False
            # 转换为字符串并清理
            text_str = str(text).strip()
            if not text_str or text_str.lower() == 'nan':
                return False
            
            text_lower = text_str.lower()
            # 移除"计数"和"绝对值"后进行比较
            text_cleaned = remove_ignored_words(text_lower)
            query_cleaned = remove_ignored_words(query)
            
            # 完全匹配（移除忽略词后）
            if text_cleaned == query_cleaned:
                return True
            
            # 如果包含分号，检查每个分号分隔的部分
            if ';' in text_str:
                parts = [s.strip() for s in text_str.split(';') if s.strip()]
                for part in parts:
                    part_cleaned = remove_ignored_words(part.lower())
                    if part_cleaned == query_cleaned:
                        return True
            return False
        
        # 匹配顺序：TEST列、TESTS_CN列、TESTS_EN列
        for idx, row in self.mapping_data.iterrows():
            # 获取各列的值
            test_value = str(row[self.mapping_test_col]) if self.mapping_test_col and pd.notna(row[self.mapping_test_col]) else ""
            tests_cn_value = str(row[self.mapping_tests_cn_col]) if self.mapping_tests_cn_col and pd.notna(row[self.mapping_tests_cn_col]) else ""
            tests_en_value = str(row[self.mapping_tests_en_col]) if self.mapping_tests_en_col and pd.notna(row[self.mapping_tests_en_col]) else ""
            
            # 按顺序检查：TEST列 -> TESTS_CN列 -> TESTS_EN列
            if test_value and check_match(test_value, query_clean):
                matched_rows.append({
                    'testds_value': str(row[self.mapping_testds_col]) if self.mapping_testds_col and pd.notna(row[self.mapping_testds_col]) else "",
                    'tests_cn_value': tests_cn_value,
                    'tests_en_value': tests_en_value
                })
            elif tests_cn_value and check_match(tests_cn_value, query_clean):
                matched_rows.append({
                    'testds_value': str(row[self.mapping_testds_col]) if self.mapping_testds_col and pd.notna(row[self.mapping_testds_col]) else "",
                    'tests_cn_value': tests_cn_value,
                    'tests_en_value': tests_en_value
                })
            elif tests_en_value and check_match(tests_en_value, query_clean):
                matched_rows.append({
                    'testds_value': str(row[self.mapping_testds_col]) if self.mapping_testds_col and pd.notna(row[self.mapping_testds_col]) else "",
                    'tests_cn_value': tests_cn_value,
                    'tests_en_value': tests_en_value
                })
        
        if matched_rows:
            # 返回匹配结果，格式化为与语义匹配相同的结果格式
            results = []
            for match in matched_rows:
                results.append({
                    'similarity': 1.0,  # 精确匹配，相似度为1.0
                    'testds_value': match.get('testds_value', ''),
                    'tests_cn_value': match.get('tests_cn_value', ''),
                    'tests_en_value': match.get('tests_en_value', ''),
                    'is_exact_match': True,  # 标记为精确匹配
                    'row_index': -1  # 映射文件没有对应的行索引
                })
            return results
        
        return None
    
    def _get_model(self):
        """懒加载embedding模型"""
        if self.model is None:
            # 注意：在MCP server环境中，print输出到stdout会干扰MCP协议通信
            # 如果需要调试信息，应该输出到stderr
            print(f"正在加载embedding模型: {self.model_name}...", file=sys.stderr, flush=True)
            self.model = SentenceTransformer(self.model_name)
            print("模型加载完成", file=sys.stderr, flush=True)
        return self.model
    
    def _get_cache_path(self):
        """获取缓存文件路径"""
        # 基于Excel文件路径和模型名称生成唯一的缓存文件名
        cache_key = f"{os.path.abspath(self.excel_path)}_{self.model_name}"
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        return {
            'e': os.path.join(self.cache_dir, f"embeddings_e_{cache_hash}.npy"),
            'f': os.path.join(self.cache_dir, f"embeddings_f_{cache_hash}.npy"),
            'h': os.path.join(self.cache_dir, f"embeddings_h_{cache_hash}.npy"),
            'meta': os.path.join(self.cache_dir, f"meta_{cache_hash}.npz")
        }
    
    def _compute_and_save_embeddings(self):
        """计算并保存所有数据的embedding"""
        model = self._get_model()
        
        # 获取列名
        e_col = 'CDISC Submission Value'
        f_col = 'CDISC Synonym(s)'
        h_col = 'NCI Preferred Term'
        
        # 准备文本数据
        e_texts = [str(row[e_col]) if pd.notna(row[e_col]) else "" for _, row in self.data.iterrows()]
        f_texts = [str(row[f_col]) if pd.notna(row[f_col]) else "" for _, row in self.data.iterrows()]
        h_texts = [str(row[h_col]) if pd.notna(row[h_col]) else "" for _, row in self.data.iterrows()]
        
        print(f"正在计算 {len(e_texts)} 条数据的embedding...", file=sys.stderr, flush=True)
        
        # 批量计算embedding（更高效）
        print("计算E列embedding...", file=sys.stderr, flush=True)
        self.embeddings_e = model.encode(e_texts, convert_to_numpy=True, show_progress_bar=True, batch_size=32)
        
        print("计算F列embedding...", file=sys.stderr, flush=True)
        # 处理F列：如果包含分号，分别计算每个同义词的embedding
        self.embeddings_f, self.f_synonyms_map = self._compute_embeddings_with_synonyms(
            model, f_texts, self.data.index.tolist()
        )
        
        print("计算H列embedding...", file=sys.stderr, flush=True)
        # 处理H列：如果包含分号，分别计算每个同义词的embedding
        self.embeddings_h, self.h_synonyms_map = self._compute_embeddings_with_synonyms(
            model, h_texts, self.data.index.tolist()
        )
        
        # 保存embedding
        cache_paths = self._get_cache_path()
        np.save(cache_paths['e'], self.embeddings_e)
        np.save(cache_paths['f'], self.embeddings_f)
        np.save(cache_paths['h'], self.embeddings_h)
        
        # 保存同义词映射（如果有）
        import pickle
        if self.f_synonyms_map:
            with open(cache_paths['f'].replace('.npy', '_synonyms.pkl'), 'wb') as f:
                pickle.dump(self.f_synonyms_map, f)
        if self.h_synonyms_map:
            with open(cache_paths['h'].replace('.npy', '_synonyms.pkl'), 'wb') as f:
                pickle.dump(self.h_synonyms_map, f)
        
        # 保存元数据（数据行数，用于验证）
        np.savez(cache_paths['meta'], 
                data_count=len(self.data),
                model_name=self.model_name)
        
        print(f"Embedding已保存到缓存目录: {self.cache_dir}", file=sys.stderr, flush=True)
    
    def _compute_embeddings_with_synonyms(self, model, texts: List[str], row_indices: List) -> Tuple[np.ndarray, Dict]:
        """
        计算embedding，处理包含分号的同义词
        
        注意：只使用分号";"作为分隔符，"/"表示Ratio（比值），不作为分隔符
        
        Args:
            model: embedding模型
            texts: 文本列表
            row_indices: 行索引列表
            
        Returns:
            (基础embedding数组, 同义词映射字典)
        """
        synonyms_map = {}
        
        # 首先计算所有文本的基础embedding（完整文本）
        base_embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, batch_size=32)
        
        # 处理包含分号的文本（只使用分号";"作为分隔符，"/"表示Ratio，不作为分隔符）
        for idx, text in enumerate(texts):
            if ';' in text and text.strip():
                # 按分号分割，去除空白（注意："/"不是分隔符，表示Ratio比值）
                synonyms = [s.strip() for s in text.split(';') if s.strip()]
                if len(synonyms) > 1:
                    # 为每个同义词计算embedding
                    synonym_embeddings = model.encode(synonyms, convert_to_numpy=True, show_progress_bar=False, batch_size=32)
                    synonyms_map[row_indices[idx]] = {
                        'synonyms': synonyms,
                        'embeddings': synonym_embeddings
                    }
        
        return base_embeddings, synonyms_map
    
    def _load_embeddings(self):
        """从缓存加载embedding"""
        cache_paths = self._get_cache_path()
        
        # 检查缓存文件是否存在
        if not all(os.path.exists(path) for path in [cache_paths['e'], cache_paths['f'], cache_paths['h'], cache_paths['meta']]):
            return False
        
        try:
            # 验证元数据
            meta = np.load(cache_paths['meta'], allow_pickle=True)
            if meta['data_count'] != len(self.data) or meta['model_name'] != self.model_name:
                print("缓存文件与当前数据不匹配，将重新计算", file=sys.stderr, flush=True)
                return False
            
            # 加载embedding
            print("从缓存加载embedding...", file=sys.stderr, flush=True)
            self.embeddings_e = np.load(cache_paths['e'])
            self.embeddings_f = np.load(cache_paths['f'])
            self.embeddings_h = np.load(cache_paths['h'])
            
            # 加载同义词映射（如果存在）
            import pickle
            f_synonyms_path = cache_paths['f'].replace('.npy', '_synonyms.pkl')
            h_synonyms_path = cache_paths['h'].replace('.npy', '_synonyms.pkl')
            
            if os.path.exists(f_synonyms_path):
                with open(f_synonyms_path, 'rb') as f:
                    self.f_synonyms_map = pickle.load(f)
            else:
                self.f_synonyms_map = {}
            
            if os.path.exists(h_synonyms_path):
                with open(h_synonyms_path, 'rb') as f:
                    self.h_synonyms_map = pickle.load(f)
            else:
                self.h_synonyms_map = {}
            
            print("Embedding加载完成", file=sys.stderr, flush=True)
            return True
        except Exception as e:
            print(f"加载缓存失败: {e}，将重新计算", file=sys.stderr, flush=True)
            return False
    
    def _load_or_compute_embeddings(self):
        """加载或计算embedding"""
        if not self._load_embeddings():
            self._compute_and_save_embeddings()
    
    def _calculate_similarity_batch(self, query_embedding: np.ndarray, data_embeddings: np.ndarray) -> np.ndarray:
        """
        批量计算查询embedding与数据embedding的余弦相似度（向量化操作，更高效）
        
        Args:
            query_embedding: 查询的embedding向量 (1, dim)
            data_embeddings: 数据的embedding矩阵 (n, dim)
            
        Returns:
            相似度分数数组 (n,)
        """
        # 归一化embedding向量
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        data_norms = data_embeddings / (np.linalg.norm(data_embeddings, axis=1, keepdims=True) + 1e-8)
        
        # 批量计算余弦相似度（向量化操作）
        similarities = np.dot(data_norms, query_norm.T).flatten()
        
        return similarities
    
    def _calculate_similarity_with_synonyms(self, query: str, query_embedding: np.ndarray, base_embeddings: np.ndarray, 
                                           synonyms_map: Dict, row_indices: List, original_texts: List[str]) -> np.ndarray:
        """
        计算相似度，处理包含分号分隔的同义词
        
        注意：只使用分号";"作为分隔符，"/"表示Ratio（比值），不作为分隔符
        
        Args:
            query: 查询字符串（用于精确匹配检查）
            query_embedding: 查询的embedding向量 (1, dim)
            base_embeddings: 基础embedding矩阵 (n, dim)
            synonyms_map: 同义词映射字典 {row_idx: {'synonyms': [...], 'embeddings': np.array}}
            row_indices: 行索引列表
            original_texts: 原始文本列表（用于精确匹配检查）
            
        Returns:
            相似度分数数组 (n,)，对于有同义词的行，取所有同义词中的最大相似度
        """
        # 先计算基础相似度
        base_similarities = self._calculate_similarity_batch(query_embedding, base_embeddings)
        
        # 对于有同义词的行，计算每个同义词的相似度，取最大值
        similarities = base_similarities.copy()
        
        query_lower = query.strip().lower()
        
        # 首先检查所有行的精确匹配（包括不在synonyms_map中的行）
        for i, row_idx in enumerate(row_indices):
            if i < len(original_texts):
                original_text = original_texts[i]
                if ';' in original_text and original_text.strip():
                    # 获取分号前的第一个词（去除前后空白）
                    # 注意：只按分号";"分割，"/"表示Ratio，不作为分隔符
                    first_word = original_text.split(';')[0].strip()
                    # 如果第一个词与查询完全相同（忽略大小写），给予最高相似度
                    if first_word.lower() == query_lower:
                        similarities[i] = 1.0  # 精确匹配，给予最高相似度
                        continue  # 跳过后续的同义词处理
        
        # 对于在synonyms_map中的行，进一步处理同义词
        if synonyms_map:
            for i, row_idx in enumerate(row_indices):
                # 如果已经是精确匹配，跳过
                if similarities[i] >= 1.0:
                    continue
                    
                if row_idx in synonyms_map:
                    synonym_data = synonyms_map[row_idx]
                    synonyms = synonym_data['synonyms']
                    synonym_embeddings = synonym_data['embeddings']
                    
                    # 检查同义词列表中是否有完全匹配
                    exact_match = False
                    for synonym in synonyms:
                        if synonym.strip().lower() == query_lower:
                            exact_match = True
                            similarities[i] = 1.0  # 精确匹配，给予最高相似度
                            break
                    
                    # 如果没有精确匹配，计算查询与每个同义词的相似度
                    if not exact_match:
                        synonym_similarities = self._calculate_similarity_batch(query_embedding, synonym_embeddings)
                        
                        # 取所有同义词中的最大相似度
                        max_synonym_sim = np.max(synonym_similarities)
                        
                        # 与基础相似度比较，取最大值
                        similarities[i] = max(base_similarities[i], max_synonym_sim)
        
        return similarities
    
    def search_top_matches(self, query: str, top_k: int =10) -> List[Dict]:
        """
        搜索与查询最相似的前k个检查项目
        
        第一步：先在映射文件中进行精确匹配（忽略大小写）
        - 中文输入优先匹配F列，英文输入优先匹配G列
        - 如果匹配成功，直接返回映射文件的结果（A、E、F、G列）
        
        第二步：如果精确匹配失败，进行语义匹配
        - 与SDTM Terminology.xls的E、F、H列进行语义匹配
        - 返回前top_k个结果（默认10）
        
        Args:
            query: 用户输入的检查项目名称（支持中英文）
            top_k: 返回前k个结果，默认10（仅用于语义匹配）
            
        Returns:
            结果列表，每个结果包含：
            - similarity: 相似度分数
            - a_value: A列值（仅精确匹配时返回）
            - e_value: E列值
            - f_value: F列值
            - g_value: G列值（仅精确匹配时返回）
            - h_value: H列值（仅语义匹配时返回）
            - is_exact_match: 是否为精确匹配
            - row_index: 原始行索引
        """
        # 第一步：尝试精确匹配
        exact_match_results = self._exact_match_in_mapping(query)
        if exact_match_results:
            print(f"在映射文件中找到精确匹配: {len(exact_match_results)} 条结果", file=sys.stderr, flush=True)
            return exact_match_results
        else:
            print(f"映射文件中未找到精确匹配，将进行语义匹配", file=sys.stderr, flush=True)
        
        # 第二步：精确匹配失败，进行语义匹配
        if self.data is None or len(self.data) == 0:
            return []
        
        if self.embeddings_e is None or self.embeddings_f is None or self.embeddings_h is None:
            raise ValueError("Embedding未加载，请先初始化匹配器")
        
        # 获取列名
        e_col = 'CDISC Submission Value'  # E列
        f_col = 'CDISC Synonym(s)'  # F列
        h_col = 'NCI Preferred Term'  # H列
        
        # 确保列存在
        if e_col not in self.data.columns or f_col not in self.data.columns or h_col not in self.data.columns:
            raise ValueError("Excel文件缺少必要的列：CDISC Submission Value, CDISC Synonym(s), 或 NCI Preferred Term")
        
        # 处理查询：忽略"绝对值"（Absolute Value）
        # 移除查询中的"绝对值"或"Absolute Value"（不区分大小写）
        processed_query = query
        processed_query = processed_query.replace('绝对值', '').replace(' ', '')
        processed_query = processed_query.replace('Absolute Value', '').replace('absolute value', '').replace('Absolute value', '')
        processed_query = processed_query.replace('AbsoluteValue', '').replace('absolutevalue', '')
        # 去除多余空格
        processed_query = ' '.join(processed_query.split())
        if not processed_query.strip():
            # 如果移除后查询为空，使用原查询
            processed_query = query
        
        # 计算查询的embedding（忽略大小写，统一转换为小写以提高匹配效果）
        model = self._get_model()
        # 为了更好的匹配效果，在计算embedding时也考虑大小写不敏感的情况
        # 但保留原始查询用于精确匹配检查
        query_embedding = model.encode([processed_query], convert_to_numpy=True)
        
        # 批量计算与E、F、H列的相似度
        similarities_e = self._calculate_similarity_batch(query_embedding, self.embeddings_e)
        
        # 获取F列和H列的原始文本（用于精确匹配检查）
        f_texts = [str(row[f_col]) if pd.notna(row[f_col]) else "" for _, row in self.data.iterrows()]
        h_texts = [str(row[h_col]) if pd.notna(row[h_col]) else "" for _, row in self.data.iterrows()]
        
        # 计算F列相似度（处理分号分隔的同义词）
        # 使用处理后的查询进行相似度计算，但保留原查询用于精确匹配检查
        similarities_f = self._calculate_similarity_with_synonyms(
            processed_query, query_embedding, self.embeddings_f, self.f_synonyms_map, 
            self.data.index.tolist(), f_texts
        )
        
        # 计算H列相似度（处理分号分隔的同义词）
        similarities_h = self._calculate_similarity_with_synonyms(
            processed_query, query_embedding, self.embeddings_h, self.h_synonyms_map, 
            self.data.index.tolist(), h_texts
        )
        
        # 检查查询中是否包含"比值"或"Ratio"（中英文都要检查）
        # 使用处理后的查询进行检查
        query_lower = processed_query.lower()
        has_ratio_keyword = '比值' in processed_query or 'ratio' in query_lower
        
        # 如果查询中不含"比值"或"Ratio"，对F列和H列中包含'/'的值进行降权
        # 使不含'/'的值的相似度高于含'/'的值
        if not has_ratio_keyword:
            # 对F列中包含'/'的值进行降权
            for i, f_text in enumerate(f_texts):
                if '/' in f_text and similarities_f[i] < 1.0:  # 精确匹配（1.0）不受影响
                    similarities_f[i] *= 0.8  # 降权20%
            
            # 对H列中包含'/'的值进行降权
            for i, h_text in enumerate(h_texts):
                if '/' in h_text and similarities_h[i] < 1.0:  # 精确匹配（1.0）不受影响
                    similarities_h[i] *= 0.8  # 降权20%
        
        # 优先匹配F列和H列：优先使用F和H列的最大值
        # 计算F和H列的最大值（优先列）
        fh_max = np.maximum(similarities_f, similarities_h)
        
        # 检查是否有精确匹配（相似度为1.0的情况）
        # 精确匹配应该具有最高优先级，不受E列影响
        exact_match_mask = fh_max >= 1.0
        
        # 对于精确匹配的情况，直接使用F/H列的最大值（已经是1.0）
        # 对于非精确匹配的情况，使用优先策略
        fh_advantage = fh_max - similarities_e
        use_fh_priority = fh_advantage >= -0.1
        
        # 构建最终相似度：
        # 1. 精确匹配（1.0）：直接使用F/H列的最大值，确保排在前面
        # 2. 非精确匹配但F/H列优先：使用F/H列的最大值
        # 3. 其他情况：使用加权组合
        max_similarities = np.where(
            exact_match_mask,
            fh_max,  # 精确匹配：直接使用F/H列的最大值（1.0）
            np.where(
                use_fh_priority,
                fh_max,  # F/H列优先：使用F/H列的最大值
                np.maximum(fh_max * 1.05, similarities_e)  # 其他情况：加权组合
            )
        )
        
        # 对结果进行排序，确保精确匹配排在前面
        # 使用稳定的排序，对于相同相似度的结果，保持原有顺序
        # 为了确保精确匹配排在前面，我们可以给精确匹配添加一个小的偏移量
        sort_key = max_similarities.copy()
        # 对于精确匹配，添加一个小的偏移量确保排在前面（但不超过1.0）
        # 实际上，由于精确匹配已经是1.0，它们会自动排在前面
        # 但为了确保稳定性，我们使用稳定的排序
        top_indices = np.argsort(-sort_key, kind='stable')[:top_k]  # 降序排序，取前top_k个
        
        # 构建结果列表
        results = []
        for idx in top_indices:
            row = self.data.iloc[idx]
            e_value = row[e_col] if pd.notna(row[e_col]) else ""
            f_value = row[f_col] if pd.notna(row[f_col]) else ""
            h_value = row[h_col] if pd.notna(row[h_col]) else ""
            
            results.append({
                'similarity': float(max_similarities[idx]),
                'e_value': str(e_value) if e_value else "",
                'f_value': str(f_value) if f_value else "",
                'h_value': str(h_value) if h_value else "",
                'is_exact_match': False,  # 标记为语义匹配
                'row_index': int(self.data.index[idx])
            })
        
        return results
    
    def format_results_json(self, results: List[Dict]) -> Dict:
        """
        将结果格式化为JSON格式
        
        Args:
            results: search_top_matches返回的结果列表
            
        Returns:
            JSON格式的字典
        """
        return {
            'total_matches': len(results),
            'results': results
        }
    
    def format_results_table(self, results: List[Dict], query: str = "") -> str:
        """
        将结果格式化为Markdown表格格式
        
        Args:
            results: search_top_matches返回的结果列表
            query: 查询文本（用于显示）
            
        Returns:
            Markdown表格字符串
        """
        if not results:
            return "未找到匹配结果。"
        
        # 检查第一个结果是否为精确匹配，以决定表格列
        is_exact_match = results[0].get('is_exact_match', False)
        
        table = f"## 查询: {query}\n\n"
        
        if is_exact_match:
            # 精确匹配结果：显示A、E、F、G列
            table += "| 排名 | 相似度 | A列 (TESTCD) | E列 (CDISC Submission Value) | F列 (中文) | G列 (英文) |\n"
            table += "|------|--------|--------------|----------------------------|------------|------------|\n"
            
            for i, result in enumerate(results, 1):
                similarity = f"{result['similarity']:.4f}"
                a_val = result.get('a_value', '')[:50] + "..." if len(result.get('a_value', '')) > 50 else result.get('a_value', '')
                e_val = result.get('e_value', '')[:50] + "..." if len(result.get('e_value', '')) > 50 else result.get('e_value', '')
                f_val = result.get('f_value', '')[:50] + "..." if len(result.get('f_value', '')) > 50 else result.get('f_value', '')
                g_val = result.get('g_value', '')[:50] + "..." if len(result.get('g_value', '')) > 50 else result.get('g_value', '')
                
                # 转义表格中的管道符
                a_val = str(a_val).replace('|', '\\|')
                e_val = str(e_val).replace('|', '\\|')
                f_val = str(f_val).replace('|', '\\|')
                g_val = str(g_val).replace('|', '\\|')
                
                table += f"| {i} | {similarity} | {a_val} | {e_val} | {f_val} | {g_val} |\n"
        else:
            # 语义匹配结果：显示E、F、H列
            table += "| 排名 | 相似度 | CDISC Submission Value (E) | CDISC Synonym(s) (F) | NCI Preferred Term (H) |\n"
            table += "|------|--------|---------------------------|---------------------|------------------------|\n"
            
            for i, result in enumerate(results, 1):
                similarity = f"{result['similarity']:.4f}"
                e_val = result.get('e_value', '')[:50] + "..." if len(result.get('e_value', '')) > 50 else result.get('e_value', '')
                f_val = result.get('f_value', '')[:50] + "..." if len(result.get('f_value', '')) > 50 else result.get('f_value', '')
                h_val = result.get('h_value', '')[:50] + "..." if len(result.get('h_value', '')) > 50 else result.get('h_value', '')
                
                # 转义表格中的管道符
                e_val = str(e_val).replace('|', '\\|')
                f_val = str(f_val).replace('|', '\\|')
                h_val = str(h_val).replace('|', '\\|')
                
                table += f"| {i} | {similarity} | {e_val} | {f_val} | {h_val} |\n"
        
        return table

