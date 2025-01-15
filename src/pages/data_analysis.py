import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.utils.db import DatabaseConnection
from src.config import load_config
from datetime import datetime
import re

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
        for column in [col for col in df.columns if col not in ['year', 'month', 'date']]:
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
    #标题选择
    tit1,tit2 =st.columns([1,1])
    with tit1:#国家选择
        select_country =st.selectbox("请选择国家",["巴西","测试"])
    
    with tit2:#查看对象
        select_object=st.selectbox("请选择要查看的对象",["活牛指数","小牛指数","小牛均重"])
        

    st.title(select_country+select_object+"分析")
    
    # 定义一个国家映射字典
    country_mapping = {
    "巴西": "BR",
    "中国": "CN",
    "美国": "US",
    "日本": "JP",
    "德国": "DE"
    }
    select_cou = country_mapping.get(select_country)

    # 定义一个对象映射字典
    country_mapping = {

    "活牛指数":"live_cattle",
    "小牛指数":"calf_head",
    "小牛均重":"calf_avg_weight_kg"
    }
    select_obj = country_mapping.get(select_object)   


    # 创建数据库连接
    config = load_config()
    db = DatabaseConnection(config)
    
    # 从数据库读取对应国家数据
    sql = """
    SELECT*
    FROM dataease_data."""+select_cou+"""_cattle_index 
    ORDER BY date DESC
    """
    df = db.query_to_df(sql)
    
    if df is not None:
        # 找到对象的在数据库里的名称

        # 创建正则表达式模式，匹配包含所有关键词的列（不关心顺序）
        regex_pattern = r"(?=.*" + re.escape(select_obj.split('_')[0]) + r")(?=.*" + re.escape(select_obj.split('_')[1]) + r")"
        # 查找列名中包含 "select_obj" 的列
        #st.write([col for col in df.columns])
        matching_columns = [col for col in df.columns if re.search(regex_pattern, col)]

        # 输出匹配的列名
        #st.write("匹配的列名:", matching_columns)
        newmatch = matching_columns 
        newmatch.append('date')
        # 创建包含 'date' 和匹配列的新 DataFrame
        df = df[newmatch]

        # 转换日期列并重命名列


        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df = df.rename(columns={
            col: (
                f"雷亚尔{select_country}{select_object}" if "R" in col else
                f"美元{select_country}{select_object}" if "USD" in col else
                f"{select_country}{select_object}"
            
            )for col in df.columns if col not in ['year', 'month', 'date']
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
        if df.shape[1] == 5:
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['雷亚尔'+select_country+select_object],
                name='雷亚尔价格',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=filtered_df['美元'+select_country+select_object],
                name='美元价格',
                line=dict(color='red'),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title=select_country+select_object+'走势',
                yaxis=dict(title='雷亚尔 (R$)', side='left'),
                yaxis2=dict(title='美元 (USD)', side='right', overlaying='y'),
                hovermode='x unified'
            )
        
        #非货币类时间序列图
        else:
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=filtered_df[select_country+select_object],
                name=select_country+select_object,
                line=dict(color='red'),
            ))
            
            fig.update_layout(
                title=select_country+select_object+'走势',
                yaxis=dict(title="公斤(kg)", side='left'),
                hovermode='x unified')

        st.plotly_chart(fig)
        
        # Seasonal Plot
        st.write("### 季节性分析")
        
        # 创建雷亚尔的季节性图表
        if df.shape[1]==5:
            fig_seasonal_r = px.line(
                filtered_df,
                x='month',
                y='雷亚尔'+select_country+select_object,
                color='year',
                title=select_country+select_object+'雷亚尔季节性走势'
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
                y='美元'+select_country+select_object,
                color='year',
                title=select_country+select_object+'美元季节性走势'
            )
            fig_seasonal_usd.update_xaxes(
                title='月份',
                ticktext=['一月', '二月', '三月', '四月', '五月', '六月', 
                        '七月', '八月', '九月', '十月', '十一月', '十二月'],
                tickvals=list(range(1, 13))
            )
            fig_seasonal_usd.update_yaxes(title='价格 (USD)')
            st.plotly_chart(fig_seasonal_usd)
        #非货币类季节性图
        else:
                fig_seasonal_kg = px.line(
                filtered_df,
                x='month',
                y=select_country+select_object,
                color='year',
                title=select_country+select_object+'季节性走势'
            )
                fig_seasonal_kg.update_xaxes(
                title='月份',
                ticktext=['一月', '二月', '三月', '四月', '五月', '六月', 
                        '七月', '八月', '九月', '十月', '十一月', '十二月'],
                tickvals=list(range(1, 13))
            )
                fig_seasonal_kg.update_yaxes(title='重量(kg)')
                st.plotly_chart(fig_seasonal_kg)

        #全部二期图（未解决）
        # 创建雷亚尔的季节性图表二期(未解决)
        if df.shape[1]==5:
            filtered_df['month_day'] = filtered_df['date'].dt.strftime('%m-%d')

            # 确保 month_day 按自然顺序排序
            filtered_df['sort_key'] = (
                filtered_df['date'].dt.month * 100 + filtered_df['date'].dt.day
            )
            filtered_df = filtered_df.sort_values('sort_key')

            fig_seasonal_r = px.line(
                filtered_df,
                x='month_day',
                y='雷亚尔'+select_country+select_object,
                color='year',
                title=select_country+select_object+'雷亚尔季节性走势'
            )
            fig_seasonal_r.update_xaxes(
                title='时间',
                tickangle=45,
                type='category'
            )
            fig_seasonal_r.update_yaxes(title='价格 (R$)')
            st.plotly_chart(fig_seasonal_r)
            
            # 创建美元的季节性图表二期
            fig_seasonal_usd = px.line(
                filtered_df,
                x='month',
                y='美元'+select_country+select_object,
                color='year',
                title=select_country+select_object+'美元季节性走势'
            )
            fig_seasonal_usd.update_xaxes(
                title='月份',
                ticktext=filtered_df['date'],
                tickvals=list(range(1, 13))
            )
            fig_seasonal_usd.update_yaxes(title='价格 (USD)')
            st.plotly_chart(fig_seasonal_usd)
        #非货币类季节性图二期
        else:
                fig_seasonal_kg = px.line(
                filtered_df,
                x='month',
                y=select_country+select_object,
                color='year',
                title=select_country+select_object+'季节性走势'
            )
                fig_seasonal_kg.update_xaxes(
                title='月份',
                ticktext=filtered_df['date'],
                tickvals=list(range(1, 13))
            )
                fig_seasonal_kg.update_yaxes(title='重量(kg)')
                st.plotly_chart(fig_seasonal_kg)
    


        # 添加基本统计信息

    else:
        st.error("无法获取数据，请检查数据库连接")

    # 关闭数据库连接
    db.close() 