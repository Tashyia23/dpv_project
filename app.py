import streamlit as st
from utils.loader import load_base_data, load_pm25_data
from utils.ui import header
from utils.merged_dataset import load_master_dataset


st.set_page_config(
    page_title="Global Air Pollution Dashboard",
    page_icon="🌍",
    layout="wide",
)

def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
# header
header(
    "🌍 Global Air Pollution Analytics Suite",
    "Analyse global AQI levels, pollutant distributions, and long-term PM2.5 trends using scientific visualisation techniques."
)

# welcome display
st.write("### Welcome to the Global Air Pollution Dashboard!")
st.write("""
This dashboard provides:
- Global AQI mapping  
- Pollutant profiles  
- Multi-country comparison  
- PM2.5 historical trends  
- Dynamic data processing & analysis  
""")
