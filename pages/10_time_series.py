import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.loader import load_pm25_data
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------------
# Load PM2.5 Dataset
# ---------------------------------------------------------
df = load_pm25_data()

header(
    "📈 Time-Series Explorer",
    "How pollution levels evolve over time by country and region."
)

if df is None:
    st.error("PM₂.₅ time-series dataset not found.")
    st.stop()

# ---------------------------------------------------------
# FIX YEAR COLUMN (Your dataset uses 'Year', not 'year')
# ---------------------------------------------------------
if "Year" in df.columns and "year" not in df.columns:
    df["year"] = df["Year"]
elif "year" not in df.columns:
    st.error("The dataset does not contain a 'Year' or 'year' column.")
    st.stop()

# Clean and normalize year column
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)
df = df.sort_values("year")

# ---------------------------------------------------------
# Ensure clean country column
# ---------------------------------------------------------
if "entity" in df.columns:
    df = df.rename(columns={"entity": "country"})

if "country" not in df.columns:
    st.error("The dataset must contain a 'country' column.")
    st.stop()

# ---------------------------------------------------------
# Detect PM2.5 values column
# ---------------------------------------------------------
value_cols = [c for c in df.columns if "pm25" in c or "pm2" in c]

if len(value_cols) == 0:
    st.error("Could not find PM2.5 concentration column.")
    st.stop()

pm_col = value_cols[0]  # first match

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")

mode = st.sidebar.radio(
    "Select View Mode:",
    ["Global Trend", "Single Country", "Compare Countries"]
)

# ---------------------------------------------------------
# GLOBAL TREND
# ---------------------------------------------------------
if mode == "Global Trend":
    st.subheader("🌍 Global PM₂.₅ Trend Over Time")

    global_df = df.groupby("year")[pm_col].mean().reset_index()

    fig = px.line(
        global_df,
        x="year",
        y=pm_col,
        markers=True,
        title="Global Average PM₂.₅ Over Time",
        labels={pm_col: "PM₂.₅ Concentration (μg/m³)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SINGLE COUNTRY MODE
# ---------------------------------------------------------
elif mode == "Single Country":

    st.subheader("🇨🇺 Country Trend Over Time")

    countries = sorted(df["country"].unique())
    country = st.selectbox("Select country:", countries)

    cdf = df[df["country"] == country]

    fig = px.line(
        cdf,
        x="year",
        y=pm_col,
        markers=True,
        title=f"PM₂.₅ Trend — {country}",
        labels={pm_col: "PM₂.₅ Concentration (μg/m³)"},
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# COMPARE MULTIPLE COUNTRIES
# ---------------------------------------------------------
elif mode == "Compare Countries":

    st.subheader("🌐 Compare Multiple Countries")

    countries = sorted(df["country"].unique())
    selected = st.multiselect(
        "Choose countries to compare:",
        countries,
        default=["Afghanistan", "India", "China"][:3]
    )

    if len(selected) < 1:
        st.info("Select at least one country.")
        st.stop()

    comp_df = df[df["country"].isin(selected)]

    fig = px.line(
        comp_df,
        x="year",
        y=pm_col,
        color="country",
        markers=True,
        title="Country Comparison — PM₂.₅ Levels",
        labels={pm_col: "PM₂.₅ Concentration (μg/m³)"},
    )

    fig.update_layout(legend_title_text="Country")

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Additional Summary Statistics
# ---------------------------------------------------------
st.markdown("### 📊 Summary Statistics")

summary = df.groupby("year")[pm_col].agg(["mean", "min", "max"]).reset_index()

st.dataframe(summary, use_container_width=True)

