# utils/loader.py
import pandas as pd
import streamlit as st
from utils.regions import assign_region   
from utils.merged_datasets import load_merged_dataset

def load_master_data():
    return load_merged_dataset()

@st.cache_data(ttl=600, show_spinner=True)
def load_base_data() -> pd.DataFrame:
    """Global AQI dataset (merged Kaggle/global pollution data)."""
    df = pd.read_csv("data/raw/global_air_pollution.csv")

    # Normalise column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace(".", "", regex=False)  # pm2.5 -> pm25
    )

    # Standardise key column names if present
    rename_map = {}
    for c in df.columns:
        if c in ["entity", "country_name"]:
            rename_map[c] = "country"
        if c in ["overall_aqi_value", "overall_aqi", "aqi"]:
            rename_map[c] = "aqi_value"
        if c in ["overall_aqi_category"]:
            rename_map[c] = "aqi_category"
        if "pm25" in c and "aqi_value" in c:
            rename_map[c] = "pm25_aqi_value"
        if "pm10" in c and "aqi_value" in c:
            rename_map[c] = "pm10_aqi_value"
        if "no2" in c and "aqi_value" in c:
            rename_map[c] = "no2_aqi_value"
        if ("ozone" in c or "o3" in c) and "aqi_value" in c:
            rename_map[c] = "ozone_aqi_value"
        if "co" in c and "aqi_value" in c and c != "aqi_value":
            rename_map[c] = "co_aqi_value"

    if rename_map:
        df = df.rename(columns=rename_map)

    # 🔹 Add region column using country name
    if "country" in df.columns:
        df["region"] = df["country"].apply(assign_region)
    else:
        df["region"] = "Other"

    return df


@st.cache_data(ttl=600)
def load_pm25_data():
    try:
        path = "data/raw/pm25-air-pollution.csv"
        df = pd.read_csv(path)

        # Standardize column names
        df.columns = [c.strip() for c in df.columns]

        # Fix Year column
        if "Year" in df.columns and "year" not in df.columns:
            df = df.rename(columns={"Year": "year"})

        # Fix entity/country
        if "Entity" in df.columns:
            df = df.rename(columns={"Entity": "country"})
        if "entity" in df.columns:
            df = df.rename(columns={"entity": "country"})

        # Clean numeric Year
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"])
        df["year"] = df["year"].astype(int)

        return df

    except Exception as e:
        print("Error loading pm25 data:", e)
        return None

