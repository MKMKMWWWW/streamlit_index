import streamlit as st
from src.config import load_config
from src.pages import home, about, data_analysis
from src.utils.helpers import setup_page

def main():
    # 加载配置
    config = load_config()
    
    # 设置页面基本配置
    setup_page()
    
    # 创建侧边栏导航
    st.sidebar.title("导航")
    page = st.sidebar.selectbox(
        "选择页面",
        ["首页", "牛肉数据分析", "关于"]
    )
    
    # 页面路由
    if page == "首页":
        home.show()
    elif page == "牛肉数据分析":
        data_analysis.show()
    elif page == "关于":
        about.show()

if __name__ == "__main__":
    main()
