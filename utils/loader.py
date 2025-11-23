import pandas as pd
import streamlit as st

@st.cache_data
def load_raw_global():
    return pd.read_csv("data/raw/global_air_pollution.csv")

@st.cache_data
def load_raw_pm25():
    return pd.read_csv("data/raw/pm25_air_pollution.csv")
