import streamlit as st
from utils.loader import load_base_data, load_pm25_data
from utils.ui import header
from styles.custom_css_loader import load_css   # optional

st.set_page_config(
    page_title="Global Air Pollution Dashboard",
    page_icon="🌍",
    layout="wide",
)

load_css()

header(
    "🌍 Global Air Pollution Analytics Suite",
    "Use the sidebar to navigate between visualisation modules."
)

st.write("### Welcome!")
st.write("""
This dashboard provides:
- Global AQI mapping  
- Pollutant profiles  
- Multi-country comparison  
- PM2.5 historical trends  
- Dynamic data processing & analysis  
""")
