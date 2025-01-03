import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.utils.db import DatabaseConnection
from src.config import load_config
from datetime import datetime

def process_data(df, start_year, end_year, remove_outliers=False, ma_window=5, std_multiplier=2):
    """
    处理数据函数，包括年份筛选和离群点处理
    ma_window: 移动平均窗口大小
    std_multiplier: 标准差倍数，用于判定离群点阈值
    """
    # 先进行年份筛选
    mask = (df['year'] >= start_year) & (df['year'] <= end_year)
    filtered_df = df.loc[mask].copy()
    
    # 如果需要处理离群点，在筛选后的数据上进行处理
    if remove_outliers:
        original_count = len(filtered_df)
        outlier_mask = pd.Series(True, index=filtered_df.index)
        
        # 为每个价格列计算移动平均和标准差
        for column in ['雷亚尔巴西活牛价格', '美元巴西活牛价格']:
            # 计算移动平均
            ma = filtered_df[column].rolling(window=ma_window, center=True).mean()
            # 计算移动标准差
            rolling_std = filtered_df[column].rolling(window=ma_window, center=True).std()
            
            # 计算与移动平均线的偏差
            deviation = abs(filtered_df[column] - ma)
            
            # 判断离群点：偏离移动平均线超过n个标准差的点
            column_mask = deviation <= (std_multiplier * rolling_std)
            outlier_mask &= column_mask
            
            # 显示判定标准
            st.write(f"{column}的离群点判定标准：")
            st.write(f"- 移动平均窗口：{ma_window}天")
            st.write(f"- 允许偏离范围：{std_multiplier}倍标准差")
        
        # 应用掩码过滤数据
        filtered_df = filtered_df[outlier_mask]
        
        removed_count = original_count - len(filtered_df)
        if removed_count > 0:
            st.info(f"当前年份范围（{start_year}-{end_year}）中已移除 {removed_count} 个离群点数据（占比 {(removed_count/original_count*100):.1f}%）")
    
    return filtered_df

def show():
    st.title("巴西活牛价格分析")
    
    # 创建数据库连接
    config = load_config()
    db = DatabaseConnection(config)
    
    # 从数据库读取数据
    sql = """
    SELECT date, live_cattle_R, live_cattle_USD 
    FROM dataease_data.BR_cattle_index 
    ORDER BY date DESC
    """
    df = db.query_to_df(sql)
    
    if df is not None:
        # 转换日期列并重命名列
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df = df.rename(columns={
            'live_cattle_R': '雷亚尔巴西活牛价格',
            'live_cattle_USD': '美元巴西活牛价格'
        })
        df['month'] = df['date'].dt.month
        
        # 获取可用的年份范围
        years = sorted(df['year'].unique())
        
        # 添加年份筛选和离群点处理选项
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            start_year = st.selectbox(
                "开始年份",
                years,
                index=0,
                key='start_year'
            )
        with col2:
            end_year = st.selectbox(
                "结束年份",
                years,
                index=len(years)-1,
                key='end_year'
            )
        with col3:
            remove_outliers_option = st.checkbox(
                "排除离群点",
                help="基于移动平均线移除异常值",
                key='remove_outliers'
            )
            if remove_outliers_option:
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    ma_window = st.slider(
                        "移动平均窗口(天)",
                        min_value=3,
                        max_value=30,
                        value=5,
                        key='ma_window'
                    )
                with col3_2:
                    std_multiplier = st.slider(
                        "标准差倍数",
                        min_value=1.0,
                        max_value=5.0,
                        value=2.0,
                        step=0.5,
                        key='std_multiplier'
                    )
        
        # 处理数据
        filtered_df = process_data(
            df, 
            start_year, 
            end_year, 
            remove_outliers_option,
            ma_window if remove_outliers_option else 5,
            std_multiplier if remove_outliers_option else 2
        )
        
        # 显示过滤后的数据，调整表格高度
        st.write("### 数据表格")
        # 使用container来控制表格大小
        with st.container():
            st.dataframe(
                filtered_df.sort_values('date', ascending=False),
                height=300  # 设置固定高度
            )
        
        # 添加一个小间距
        st.write("")
        
        # 创建时间序列图
        st.write("### 时间序列分析")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df['雷亚尔巴西活牛价格'],
            name='雷亚尔价格',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df['美元巴西活牛价格'],
            name='美元价格',
            line=dict(color='red'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='巴西活牛价格走势',
            yaxis=dict(title='雷亚尔 (R$)', side='left'),
            yaxis2=dict(title='美元 (USD)', side='right', overlaying='y'),
            hovermode='x unified'
        )
        st.plotly_chart(fig)
        
        # Seasonal Plot
        st.write("### 季节性分析")
        
        # 创建雷亚尔的季节性图表
        fig_seasonal_r = px.line(
            filtered_df,
            x='month',
            y='雷亚尔巴西活牛价格',
            color='year',
            title='巴西活牛雷亚尔价格季节性走势'
        )
        fig_seasonal_r.update_xaxes(
            title='月份',
            ticktext=['一月', '二月', '三月', '四月', '五月', '六月', 
                     '七月', '八月', '九月', '十月', '十一月', '十二月'],
            tickvals=list(range(1, 13))
        )
        fig_seasonal_r.update_yaxes(title='价格 (R$)')
        st.plotly_chart(fig_seasonal_r)
        
        # 创建美元的季节性图表
        fig_seasonal_usd = px.line(
            filtered_df,
            x='month',
            y='美元巴西活牛价格',
            color='year',
            title='巴西活牛美元价格季节性走势'
        )
        fig_seasonal_usd.update_xaxes(
            title='月份',
            ticktext=['一月', '二月', '三月', '四月', '五月', '六月', 
                     '七月', '八月', '九月', '十月', '十一月', '十二月'],
            tickvals=list(range(1, 13))
        )
        fig_seasonal_usd.update_yaxes(title='价格 (USD)')
        st.plotly_chart(fig_seasonal_usd)
        
        # 添加基本统计信息
        st.write("### 统计摘要")
        col1, col2 = st.columns(2)
        with col1:
            st.write("雷亚尔价格统计")
            st.write(filtered_df['雷亚尔巴西活牛价格'].describe())
        with col2:
            st.write("美元价格统计")
            st.write(filtered_df['美元巴西活牛价格'].describe())
    
    else:
        st.error("无法获取数据，请检查数据库连接")
    
    # 关闭数据库连接
    db.close() 