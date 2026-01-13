"""
配置文件
从环境变量读取文件路径
支持从.env文件加载（如果使用python-dotenv）
注意：Streamlit Secrets会在streamlit_app.py中读取并设置为环境变量
"""
import os

# 尝试从.env文件加载环境变量（如果安装了python-dotenv）
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载.env文件
except ImportError:
    # 如果没有安装python-dotenv，跳过
    pass

# Excel文件路径（从环境变量读取，如果没有则使用默认值）
EXCEL_PATH = os.getenv('EXCEL_PATH', r"C:\Users\liy167\YuLI\testcd_map\SDTM Terminology.xls")

# 映射文件路径（从环境变量读取，如果没有则使用默认值）
MAPPING_FILE = os.getenv('MAPPING_FILE', r"C:\Users\liy167\YuLI\testcd_map\TEST_TESTCD_mapping.xlsx")

# 缓存目录路径（从环境变量读取，如果没有则使用默认值）
CACHE_DIR = os.getenv('CACHE_DIR', r"C:\Users\liy167\YuLI\testcd_map\testcd_embedding")

# 检查必需的环境变量
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

