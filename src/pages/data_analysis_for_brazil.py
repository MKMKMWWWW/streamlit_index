import streamlit as st
from src.utils.db import DatabaseConnection
from src.config import load_config
import pandas as pd
import numpy as np
def show():
    st.title("巴西数据出口分析")
    
    #国家翻译
    country_dict = {
        "Bangladesh": "孟加拉",
        "Caimán, Islas": "开曼群岛",
        "China": "中国",
        "Chipre": "塞浦路斯",
        "Corea (Sur)": "韩国",
        "Grecia": "希腊",
        "Guinea": "几内亚",
        "Hong Kong": "香港",
        "Islas Marshall": "马绍尔群岛",
        "Italia": "意大利",
        "Japón": "日本",
        "Liberia": "利比里亚",
        "Malta": "马耳他",
        "Panamá": "巴拿马",
        "Países Bajos": "荷兰",
        "Portugal": "葡萄牙",
        "Singapur": "新加坡",
        "Alemania": "德国",
        "Antigua y Barbuda": "安提瓜和巴布达",
        "Arabia Saudita": "沙特阿拉伯",
        "Argelia": "阿尔及利亚",
        "Aruba": "阿鲁巴",
        "Bahamas": "巴哈马",
        "Bahrein": "巴林",
        "Bélgica": "比利时",
        "Chile": "智利",
        "Curazao": "库拉索",
        "Dinamarca": "丹麦",
        "Emiratos Árabes Unidos": "阿联酋",
        "España": "西班牙",
        "Estados Unidos": "美国",
        "Filipinas": "菲律宾",
        "Francia": "法国",
        "Guinea-Bissau": "几内亚比绍",
        "Isla de Man": "马恩岛",
        "Israel": "以色列",
        "Jordania": "约旦",
        "Kuwait": "科威特",
        "Líbano": "黎巴嫩",
        "Malasia": "马来西亚",
        "Montenegro": "黑山",
        "México": "墨西哥",
        "Noruega": "挪威",
        "Omán": "阿曼",
        "Palau": "帕劳",
        "Paraguay": "巴拉圭",
        "Perú": "秘鲁",
        "Puerto Rico": "波多黎各",
        "Qatar": "卡塔尔",
        "Reino Unido": "英国",
        "Suecia": "瑞典",
        "Suiza": "瑞士",
        "Tailandia": "泰国",
        "Turquía": "土耳其",
        "Uruguay": "乌拉圭",
        "Angola": "安哥拉",
        "Argentina": "阿根廷",
        "Brasil": "巴西",
        "Guyana": "圭亚那",
        "Marianas Septentrionales, Islas": "北马里亚纳群岛",
        "Marruecos": "摩洛哥",
        "Martinica": "马提尼克",
        "Tanzanía": "坦桑尼亚",
        "Viet Nam": "越南",
        "Acerbaiyan": "阿塞拜疆",
        "Albania": "阿尔巴尼亚",
        "Barbados": "巴巴多斯",
        "Bermuda": "百慕大",
        "Bolivia": "玻利维亚",
        "Cabo Verde": "佛得角",
        "Canadá": "加拿大",
        "Comoras": "科摩罗",
        "Congo": "刚果",
        "Costa de Marfil": "科特迪瓦",
        "Cuba": "古巴",
        "Egipto": "埃及",
        "Gabón": "加蓬",
        "Georgia": "格鲁吉亚",
        "Ghana": "加纳",
        "Indonesia": "印度尼西亚",
        "Irak": "伊拉克",
        "Libia": "利比亚",
        "Maldivas": "马尔代夫",
        "Mayotte": "马约特",
        "Palestina": "巴勒斯坦",
        "Polonia": "波兰",
        "Rusia": "俄罗斯",
        "Senegal": "塞内加尔",
        "Serbia": "塞尔维亚",
        "Sierra Leona": "塞拉利昂",
        "Sint Maarten": "圣马丁",
        "Suriname": "苏里南",
        "Tokelau": "托克劳",
        "Turkmenistán": "土库曼斯坦",
        "Túnez": "突尼斯",
        "Ucrania": "乌克兰",
        "Bhután": "不丹",
        "Guinea Ecuatorial": "赤道几内亚",
        "Laos": "老挝",
        "Myanmar": "缅甸",
        "Papua Nueva Guinea": "巴布亚新几内亚",
        "República Democrática del Congo": "刚果民主共和国",
        "India": "印度",
        "Bonaire, Saint Eustatius y Saba": "博奈尔、圣尤斯特歇斯和萨巴",
        "Gibraltar": "直布罗陀",
        "Seychelles": "塞舌尔",
        "Camerún": "喀麦隆",
        "Cook, Islas": "库克群岛",
        "Irán": "伊朗",
        "Macao": "澳门",
        "Mozambique": "莫桑比克",
        "Taiwán": "台湾",
        "Camboya": "柬埔寨",
        "Granada": "格林纳达",
        "Saint Kitts y Nevis": "圣基茨和尼维斯",
        "Belice": "伯利兹",
        "Lituania": "立陶宛",
        "Swazilandia": "斯威士兰",
        "San Vicente y las Granadinas": "圣文森特和格林纳丁斯",
        "Venezuela": "委内瑞拉",
        "Armenia": "亚美尼亚",
        "Gambia": "冈比亚",
        "Mauricio": "毛里求斯",
        "Timor Leste": "东帝汶",
        "Malvinas (Falkland), Islas": "马尔维纳斯群岛",
        "Nigeria": "尼日利亚",
        "Kenya": "肯尼亚",
        "Macedonia": "北马其顿",
        "Tayikistán": "塔吉克斯坦",
        "Luxemburgo": "卢森堡",
        "Mauritania": "毛里塔尼亚",
        "Djibouti": "吉布提",
        "Croacia": "克罗地亚",
        "Vanuatu": "瓦努阿图",
        "Irlanda": "爱尔兰",
        "Mónaco": "摩纳哥",
        "República Dominicana": "多米尼加共和国",
        "Finlandia": "芬兰",
        "Pitcairn": "皮特凯恩",
        "Honduras": "洪都拉斯",
        "Kazakhstán": "哈萨克斯坦",
        "Santo Tomé y Príncipe": "圣多美和普林西比",
        "Austria": "奥地利",
        "Letonia": "拉脱维亚",
        "Kirguistán": "吉尔吉斯斯坦",
        "Guam": "关岛",
        "Australia": "澳大利亚",
        "Rumania": "罗马尼亚",
        "Sudáfrica": "南非"
    }

    #编号翻译
    code_dict = {
    "020120": "鲜或冷的带骨牛肉",
    "020130": "鲜或冷的去骨牛肉",
    "020210": "冻整头及半头牛肉",
    "020220": "冻带骨牛肉",
    "020230": "冻去骨牛肉",
    "020629": "其他冻牛杂碎"
    }

    # 创建数据库连接
    config = load_config()
    db = DatabaseConnection(config)

    # 从数据库读取对应国家数据
    sql = """
    SELECT*
    FROM brazil_beef_export_meta_data
    """
    
    df = db.query_to_df(sql)
    
    
    if df  is not None:
        
        
        #其实没啥区别就是方便记忆    
        
        #重新命名方便观看
        df.columns = [
            "Año", 
            "Mes", 
            "Código SA6", 
            "Descripción SA6", 
            "País", 
            "Valor US$ FOB", 
            "Peso (kg)", 
        ]

        #添加列
        df["对应翻译"] = df['Código SA6'].map(code_dict).fillna(df['Código SA6'])
        df["国家"]= df['País'].map(country_dict).fillna(df['País'])
        df["平均KG价格(美元）"] = df['Valor US$ FOB']/df['Peso (kg)']
        df['t'] = df['Peso (kg)']/1000
        df.insert(df.columns.get_loc("Código SA6") + 1,"对应翻译", df.pop("对应翻译"))
        df.insert(df.columns.get_loc("País") + 1,"国家" ,df.pop("国家"))
        
        #重新更改对应列名称

        st.write(df)
        st.write("")
        years = df["Año"].unique()
        tit1,tit2,tit3 =st.columns([1,1,1])
        with tit1:#国家选择
            select_country =st.selectbox("请选择国家",df["国家"].unique())
        
        with tit2:#查看时间
            select_year=st.selectbox("请选择开始年",years,index=0,
                key='start_year')
        with tit3:#查看时间
            select_year1=st.selectbox("请选择结束年",years,index=0,
                key='end_year')
        
        #创建n个新的表 n = numberoftable
        
        numberoftable = int(select_year1)-int(select_year)+1

        #出口量的表    
        st.write("巴西总出口价 "+select_country+" "+select_year+" ~ "+select_year1+" ")
        year = select_year1
        new_df = df[(df["Año"] == year)]
    
        new_df1 = new_df.groupby(["Mes","国家"])["平均KG价格(美元）"].mean().reset_index()
        #先显示对应国家的表
        new_df1 = new_df1[new_df1["国家"]== select_country]

        new_df1 = new_df1.rename(columns={"平均KG价格(美元）": year+select_country})
        #再删除国家这一列
        new_df2 = new_df1.drop(columns=["国家"])

        while (numberoftable> 1) and (select_year != select_year1):
            year = str(int(year)-1)
            new_df = df[(df["Año"] == year)]
        
            new_df1 = new_df.groupby(["Mes","国家"])["平均KG价格(美元）"].mean().reset_index()
            #先显示对应国家的表
            new_df1 = new_df1[new_df1["国家"]== select_country]

            new_df1 = new_df1.rename(columns={"平均KG价格(美元）": year+select_country})
            #再删除国家这一列
            new_df3 = new_df1.drop(columns=["国家"])
            new_df2 = pd.merge(new_df2,new_df3,on="Mes", how='right')

            numberoftable-=1

        st.write(new_df2)


        #价格表
        year = select_year1
        numberoftable = int(select_year1)-int(select_year)+1
        st.write("巴西总出口量占比 "+select_country+" "+select_year+" ~ "+select_year1+" ")
        new_df = df[(df["Año"] == year)]
        
        new_df1 = new_df.groupby(["Mes"])['t'].sum().reset_index()
        
        new_df1 = new_df1.rename(columns={'t': year+'总计'})
        new_df2 = new_df.groupby(["Mes","国家"])['t'].sum().reset_index()
        #先显示对应国家的表
        new_df2 = new_df2[new_df2["国家"]== select_country]

        new_df2 = new_df2.rename(columns={'t': year+select_country})

        new_df3 =  pd.merge(new_df1,new_df2,on="Mes")
        #再删除国家这一列
        new_df3 = new_df3.drop(columns=["国家"])
        new_df3[year+"百分比%"]=new_df3[year+select_country]/new_df3[year+"总计"]*100

        while (numberoftable> 1) and (select_year != select_year1):
            year = str(int(year)-1)
            new_df = df[(df["Año"] == year)]
        
            new_df1 = new_df.groupby(["Mes"])['t'].sum().reset_index()
            
            new_df1 = new_df1.rename(columns={'t': year+'总计'})
            new_df2 = new_df.groupby(["Mes","国家"])['t'].sum().reset_index()
            #先显示对应国家的表
            new_df2 = new_df2[new_df2["国家"]== select_country]

            new_df2 = new_df2.rename(columns={'t': year+select_country})

            new_df4 =  pd.merge(new_df1,new_df2,on="Mes")
            #再删除国家这一列
            new_df4 = new_df4.drop(columns=["国家"])
            new_df4[year+"百分比%"]=new_df4[year+select_country]/new_df4[year+"总计"]*100
            new_df3 = pd.merge(new_df3,new_df4,on="Mes", how='right')
            numberoftable-=1
        st.write(new_df3)
        


    # 示例交互组件
    if st.button("点击我"):
        st.balloons() 