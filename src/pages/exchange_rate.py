import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Function to fetch DXY value using Selenium
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_dxy():
    url = "https://www.tradingview.com/symbols/TVC-DXY/"
    
    try:
        # Set up Selenium options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        
        # Set up the WebDriver (make sure chromedriver is installed and in your PATH)
        driver = webdriver.Chrome(service=Service(), options=chrome_options)
        
        # Open the TradingView page
        driver.get(url)
        
        # Wait for the page to load (adjust the sleep time as needed)
        time.sleep(5)
        
        # Locate the DXY value element
        dxy_element = driver.find_element(By.CSS_SELECTOR, "span.last-JWoJqCpY.js-symbol-last")
        dxy_value = dxy_element.text
        # Close the browser
        driver.quit()
        
    except Exception as e:
        dxy_value = f"Error fetching data: {e}"
    
    return dxy_value

# Fetch data and display
def show():
    st.title("汇率")  # Title inside show function
    
    dxy = fetch_dxy()
    st.metric(label="美元指数", value=dxy)

    # Refresh button
    if st.button("Refresh Now"):
        st.cache_data.clear()  # Clear the cache data
        st.rerun()  # Trigger a rerun

