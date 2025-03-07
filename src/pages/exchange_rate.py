import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import streamlit as st
from bs4 import BeautifulSoup


# 卖汇
@st.cache_data(ttl=1800)
def parse_exchange_rates(html):
    """javascripe 转换后用soup的我查"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    driver.get(html)
    time.sleep(5)  


    html = driver.page_source
    driver.quit()
    try:
 
        soup = BeautifulSoup(html, "html.parser")
        p_element = soup.find('p', string=lambda text: text and "现汇卖出价" in text)
        next_p = p_element.find_next_sibling('p') if p_element else None
        st.write(next_p)
        if not p_element:
            return "Error: Could not find the <b> element."
        
        usd_to_cny = next_p.text.split('=')[1].split('元')[0]
        return usd_to_cny
    except Exception as e:
        return f"Error parsing data: {e}"


#美元兑雷埃厄，美元指数
@st.cache_data(ttl=1800)  # 30 min
def fetch_dxy(url):
    
    try:

        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        

        driver = webdriver.Chrome(service=Service(), options=chrome_options)
    
        driver.get(url)

        time.sleep(5)
        

        dxy_element = driver.find_element(By.CSS_SELECTOR, "span.last-JWoJqCpY.js-symbol-last")
        dxy_value = dxy_element.text

        driver.quit()
        
    except Exception as e:
        dxy_value = f"Error fetching data: {e}"

    return dxy_value


def show():
    st.title("汇率")  
    url1 = "https://www.tradingview.com/symbols/TVC-DXY/"#tradingview
    url2 = 'https://www.tradingview.com/symbols/USDBRL/'#tradingview
    url3 = "https://chl.cn/huilv/?usd"#我查
    dxy = fetch_dxy(url1)
    usd_br = fetch_dxy(url2)
    st.metric(label="美元指数", value=dxy)
    st.metric(label="美元对巴西雷亚尔", value=usd_br)
    exchange_rates = parse_exchange_rates(url3)
    st.metric(label="美元对人名币（现汇卖出价）", value=exchange_rates)

    if st.button("Refresh Now"):
        st.cache_data.clear()  # Clear the cache data
        st.rerun()  # Trigger a rerun

