import streamlit as st
import pandas as pd

@st.cache_data(ttl=600, show_spinner=True)
def load_base_data():
    df = pd.read_csv("data/raw/global_air_pollution.csv")

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    rename_map = {
        "overall_aqi_value": "aqi_value",
        "overall_aqi_category": "aqi_category",
    }
    df = df.rename(columns=rename_map)

    return df


@st.cache_data(ttl=600)
def load_pm25_data():
    try:
        df = pd.read_csv("data/raw/pm25-air-pollution.csv")
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(".", "", regex=False)
        )
        return df
    except FileNotFoundError:
        return None
