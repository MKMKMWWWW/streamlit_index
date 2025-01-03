import os
from dotenv import load_dotenv

def load_config():
    """
    加载配置文件
    """
    load_dotenv()
    
    return {
        "app_name": "我的Streamlit应用",
        "version": "1.0.0",
        # 数据库配置
        "database": {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 3309)),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
        }
    } 