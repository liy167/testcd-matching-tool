"""
网页版检查项目匹配器
使用Streamlit创建Web界面
"""

import streamlit as st
from lab_test_matcher import LabTestMatcher
import json
import re
import os

# 尝试从.env文件加载环境变量（如果安装了python-dotenv）
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载.env文件
except ImportError:
    # 如果没有安装python-dotenv，跳过
    pass

# 翻译功能（使用deep-translator，如果不可用则使用简单回退）
try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

# 翻译缓存（避免重复翻译相同文本）
_translation_cache = {}

def translate_text(text: str) -> str:
    """
    翻译文本为中文
    
    Args:
        text: 要翻译的文本
        
    Returns:
        翻译后的中文文本，如果翻译失败则返回原文本
    """
    if not text or not text.strip():
        return text
    
    # 如果文本已经是中文（包含中文字符），直接返回
    if re.search(r'[\u4e00-\u9fff]', text):
        return text
    
    # 检查缓存
    if text in _translation_cache:
        return _translation_cache[text]
    
    # 如果文本主要是英文，尝试翻译
    if HAS_TRANSLATOR:
        try:
            # 只翻译英文部分，保留分号分隔的结构
            if ';' in text:
                parts = text.split(';')
                translated_parts = []
                for part in parts:
                    part = part.strip()
                    if part and not re.search(r'[\u4e00-\u9fff]', part):
                        try:
                            translator = GoogleTranslator(source='en', target='zh')
                            translated = translator.translate(part)
                            translated_parts.append(f"{part} ({translated})")
                        except:
                            translated_parts.append(part)
                    else:
                        translated_parts.append(part)
                result = '; '.join(translated_parts)
            else:
                try:
                    translator = GoogleTranslator(source='en', target='zh')
                    translated = translator.translate(text)
                    result = f"{text} ({translated})"
                except:
                    result = text
            
            # 缓存结果
            _translation_cache[text] = result
            return result
        except Exception:
            return text
    else:
        # 如果没有翻译器，返回原文本
        return text

# 页面配置
st.set_page_config(
    page_title="检查项目匹配器",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化匹配器（使用缓存避免重复加载）
@st.cache_resource
def get_matcher():
    """获取匹配器实例（带缓存）"""
    return LabTestMatcher()

# 标题
st.title("🔬 检查项目TEST - > TESTCD 查询工具")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    top_k = st.slider("返回结果数量", min_value=1, max_value=20, value=10, step=1)
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    1. 在输入框中输入检查项目名称（支持中英文）
    2. 点击"搜索"按钮或按Enter键
    3. 查看匹配结果，按相似度排序
    """)

# 初始化匹配器
try:
    with st.spinner("正在初始化匹配器..."):
        matcher = get_matcher()
    st.success("匹配器初始化成功！")
except Exception as e:
    st.error(f"初始化失败: {e}")
    st.stop()

# 搜索输入
st.subheader("🔍 搜索")
query = st.text_input(
    "输入检查项目名称（支持中英文）",
    placeholder="例如：血红蛋白 或 Hemoglobin",
    label_visibility="collapsed"
)

# 搜索按钮
col1, col2 = st.columns([1, 10])
with col1:
    search_button = st.button("搜索", type="primary", use_container_width=True)

# 执行搜索
if search_button or query:
    if query.strip():
        try:
            with st.spinner(f"正在搜索 '{query}'..."):
                results = matcher.search_top_matches(query, top_k=top_k)
            
            if results:
                st.markdown("---")
                # 检查是否为精确匹配
                is_exact_match = results[0].get('is_exact_match', False)
                
                if is_exact_match:
                    st.subheader(f"✅ 精确匹配结果（共 {len(results)} 条）")
                    st.info("🎯 在TEST_TESTCD_mapping.xlsx中找到精确匹配！")
                else:
                    st.subheader(f"📊 语义匹配结果（共 {len(results)} 条）")
                
                # 显示表格
                import pandas as pd
                df_data = []
                
                if is_exact_match:
                    # 精确匹配：显示TESTDS、TESTS_CN、TESTS_EN列（来自TEST_TESTCD_mapping.xlsx）
                    for i, result in enumerate(results, 1):
                        df_data.append({
                            "排名": i,
                            "相似度": f"{result['similarity']:.4f}",
                            "TESTDS": result.get('testds_value', ''),
                            "TESTS_CN": result.get('tests_cn_value', ''),
                            "TESTS_EN": result.get('tests_en_value', '')
                        })
                else:
                    # 语义匹配：显示E、F、H列
                    for i, result in enumerate(results, 1):
                        # F列：优先使用映射文件中的中文，如果没有则使用翻译API
                        f_value = result.get('f_value', '')
                        f_cn_value = result.get('f_cn_value', '')
                        
                        if f_cn_value:
                            # 如果映射文件中有中文，显示：英文 (中文)
                            f_value_display = f"{f_value} ({f_cn_value})" if f_value else f_cn_value
                        else:
                            # 如果没有映射文件的中文，使用翻译API
                            f_value_display = translate_text(f_value)
                        
                        # H列：使用翻译API
                        h_value = result.get('h_value', '')
                        h_value_with_translation = translate_text(h_value)
                        
                        df_data.append({
                            "排名": i,
                            "相似度": f"{result['similarity']:.4f}",
                            "CDISC Submission Value (E)": result.get('e_value', ''),
                            "CDISC Synonym(s) (F)": f_value_display,
                            "NCI Preferred Term (H)": h_value_with_translation
                        })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # 显示详细信息（可展开）
                with st.expander("📋 查看JSON格式结果"):
                    json_result = matcher.format_results_json(results)
                    st.json(json_result)
                
                # 下载结果
                json_str = json.dumps(json_result, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 下载JSON结果",
                    data=json_str,
                    file_name=f"search_results_{query}.json",
                    mime="application/json"
                )
            else:
                st.warning("未找到匹配结果。")
                
        except Exception as e:
            st.error(f"搜索失败: {e}")
            st.exception(e)
    else:
        st.warning("请输入查询文本")

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>检查项目TEST - > TESTCD 查询工具 | 使用语义相似度匹配</div>",
    unsafe_allow_html=True
)

