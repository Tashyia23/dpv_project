import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.ui import header

st.set_page_config(layout="wide")

# -----------------------------------------------------
# Helper Functions
# -----------------------------------------------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standard auto-cleaning for any uploaded dataset."""
    df = df.copy()

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Convert obvious date columns
    for col in df.columns:
        if any(keyword in col for keyword in ["date", "time", "year"]):
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except:
                pass

    # Convert numeric-like columns
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except:
                pass

    # Handle missing values
    numeric_cols = df.select_dtypes(include=np.number).columns
    categorical_cols = df.select_dtypes(exclude=np.number).columns

    if len(numeric_cols) > 0:
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    if len(categorical_cols) > 0:
        df[categorical_cols] = df[categorical_cols].fillna("Unknown")

    return df


def detect_pollution_dataset(df: pd.DataFrame) -> bool:
    """Check if uploaded dataset is an air pollution dataset."""
    pollution_keywords = [
        "pm25", "pm10", "aqi", "co", "no2", "o3", "ozone",
        "carbon_monoxide", "nitrogen_dioxide", "fine_particulate"
    ]

    cols = " ".join(df.columns)
    return any(keyword in cols.lower() for keyword in pollution_keywords)


# -----------------------------------------------------
# Page Layout Header
# -----------------------------------------------------

header(
    "📤 Upload & Analyse Your Dataset",
    "Upload any CSV file for automatic cleaning, profiling, and visualisation."
)

st.markdown("### Upload a dataset to begin:")

uploaded_file = st.file_uploader("Choose a CSV file:", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a dataset to start analysis.")
    st.stop()

# -----------------------------------------------------
# Load & Clean Data
# -----------------------------------------------------

try:
    raw_df = pd.read_csv(uploaded_file)
except Exception:
    st.error("❌ Could not read the file. Make sure it's a valid CSV.")
    st.stop()

df = clean_dataframe(raw_df)

st.success("✅ Dataset successfully loaded and cleaned!")

st.markdown("### 📄 Preview of cleaned dataset:")
st.dataframe(df.head(), use_container_width=True)

# -----------------------------------------------------
# Auto-Detect Dataset Type
# -----------------------------------------------------

is_pollution = detect_pollution_dataset(df)

if is_pollution:
    st.markdown("### 🔍 Detected: Air Pollution Dataset")
else:
    st.markdown("### 🔍 Detected: General Dataset")

# -----------------------------------------------------
# Tabs
# -----------------------------------------------------

tab_overview, tab_visuals, tab_advanced = st.tabs(
    ["🔎 Overview", "📊 Visualisations", "🧪 Advanced Analysis"]
)

# -----------------------------------------------------
# TAB 1 — Overview
# -----------------------------------------------------
with tab_overview:
    st.markdown("## 🧭 Dataset Overview")

    st.write("### Shape")
    st.write(df.shape)

    st.write("### Column Types")
    st.write(df.dtypes)

    st.write("### Missing Values")
    missing = df.isnull().sum().to_frame("missing_count")
    st.dataframe(missing, use_container_width=True)

    st.write("### Summary Statistics")
    st.dataframe(df.describe(include="all"), use_container_width=True)


# -----------------------------------------------------
# TAB 2 — Visualisations
# -----------------------------------------------------
with tab_visuals:
    st.markdown("## 📊 Visualisations")

    if is_pollution:
        st.markdown("### 🌫 Air Pollution Visualisations")

        # Pollutant columns
        pollutant_cols = [
            c for c in df.columns
            if any(p in c for p in ["pm25", "pm10", "aqi", "co", "no2", "o3"])
        ]

        if not pollutant_cols:
            st.warning("No pollutant columns detected.")
        else:
            pollutant = st.selectbox("Select pollutant:", pollutant_cols)

            # Histogram
            fig_hist = px.histogram(df, x=pollutant, title=f"Distribution of {pollutant}")
            st.plotly_chart(fig_hist, use_container_width=True)

            # Boxplot
            fig_box = px.box(df, y=pollutant, title=f"Boxplot of {pollutant}")
            st.plotly_chart(fig_box, use_container_width=True)

            # Correlation heatmap
            numeric_df = df.select_dtypes(include=np.number)
            if not numeric_df.empty:
                corr = numeric_df.corr()
                fig_corr = px.imshow(corr, text_auto=True, title="Pollutant Correlation Heatmap")
                st.plotly_chart(fig_corr, use_container_width=True)

    else:
        st.markdown("### 📊 General Visualisations")

        numeric_cols = df.select_dtypes(include=np.number).columns

        if len(numeric_cols) == 0:
            st.warning("No numeric columns to visualise.")
        else:
            col_x = st.selectbox("X-axis:", numeric_cols)
            col_y = st.selectbox("Y-axis:", numeric_cols)

            fig_scatter = px.scatter(df, x=col_x, y=col_y, title=f"{col_x} vs {col_y}")
            st.plotly_chart(fig_scatter, use_container_width=True)

            fig_hist = px.histogram(df, x=col_x, title=f"Distribution of {col_x}")
            st.plotly_chart(fig_hist, use_container_width=True)

            fig_box = px.box(df, y=col_x, title=f"Boxplot of {col_x}")
            st.plotly_chart(fig_box, use_container_width=True)


# -----------------------------------------------------
# TAB 3 — Advanced Analysis
# -----------------------------------------------------
with tab_advanced:
    st.markdown("## 🧪 Advanced Analysis")

    # Correlation heatmap for all numeric data
    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.empty:
        st.info("No numerical columns for advanced analysis.")
    else:
        corr = numeric_df.corr()
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title="Correlation Matrix"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

