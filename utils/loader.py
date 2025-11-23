import streamlit as st
from utils.merged_dataset import load_master_dataset

@st.cache_data(show_spinner=False)
def load_master():
    """Returns the master dataset dict."""
    return load_master_dataset()


def load_time_series():
    """Loads PM2.5 time series data."""
    master = load_master()
    return master.get("time_series")


def load_pollutant_index():
    """Loads pollutant breakdown dataset."""
    master = load_master()
    return master.get("pollutant_index")


def load_risk_index():
    """Loads health & risk index dataset."""
    master = load_master()
    return master.get("risk_index")

