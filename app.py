import streamlit as st
from utils.loader import load_base_data, load_pm25_data
from utils.ui import header
from utils.loader import load_master_data

st.set_page_config(
    page_title="Global Air Pollution Dashboard",
    page_icon="🌍",
    layout="wide",
)

def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
# ---------------------------------------------------------
# Hero Section
# ---------------------------------------------------------
st.markdown("""
<div style="padding: 10px 0 30px 0;">
    <h1 style="font-size: 2.7rem; font-weight: 700; color: #1f2937;">
        🌍 Global Air Pollution Analytics Suite
    </h1>
    <p style="font-size:1.15rem; color:#4b5563; max-width: 820px;">
        Analyse global AQI levels, pollutant distributions, regional trends, WHO PM₂.₅ 
        time-series, and multi-country comparisons using scientific visualisation and 
        data-processing techniques.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ---------------------------------------------------------
# Dashboard Overview
# ---------------------------------------------------------
st.markdown("## 🚀 Welcome to the Global Air Pollution Dashboard!")

st.markdown("""
This dashboard allows you to explore worldwide air quality using processed AQI data, 
regional analysis, pollutant-level comparisons, and WHO long-term PM₂.₅ records.

Below are the main modules:
""")

# ---------------------------------------------------------
# Feature Cards Section
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🗺 Global Map</div>
            <div class="feature-desc">
                Visualise AQI values across countries using an interactive geographic map.
            </div>
        </div>
        <br>
        <div class="feature-card">
            <div class="feature-title">📊 Health & Risk Index</div>
            <div class="feature-desc">
                Explore pollution-induced health risks using processed and normalised AQI indicators.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🌎 Regional Explorer</div>
            <div class="feature-desc">
                Analyse raw vs processed pollutant levels by region, including radar, heatmap, and comparison views.
            </div>
        </div>
        <br>
        <div class="feature-card">
            <div class="feature-title">⏳ Time Series (WHO PM₂.₅)</div>
            <div class="feature-desc">
                Observe long-term pollution trends using WHO datasets with health-risk transformations.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 20px 0; color: #6b7280;">
    Built with Streamlit · Global Air Pollution Analytics Suite by Priscilla, Ehang, Qi Yun, Kavieraj, and Juhitashyia
</div>
""", unsafe_allow_html=True)
