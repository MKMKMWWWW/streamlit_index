import streamlit as st

def show():
    st.title("数据streamlit")
    
    st.write("""
    示例首页。
    - 项目介绍
    - 主要功能
    - 使用说明
    """)
    
    # 示例交互组件
    if st.button("点击我"):
        st.balloons() 