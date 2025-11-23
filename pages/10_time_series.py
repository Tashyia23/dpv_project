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
    st.error("PM₂.₅ time-series dataset not found.\n\nExpected file:\n- data/raw/pm25-air-pollution.csv\n- OR pm25-air-pollution.csv\n")
    st.stop()

# ---------------------------------------------------------
# Fix YEAR column
# ---------------------------------------------------------
if "year" not in df.columns:
    st.error("Dataset must contain a 'Year' column.")
    st.stop()

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)
df = df.sort_values("year")

# ---------------------------------------------------------
# Standardize country column
# ---------------------------------------------------------
if "entity" in df.columns:
    df = df.rename(columns={"entity": "country"})

if "country" not in df.columns:
    st.error("Dataset must contain a 'country' or 'entity' column.")
    st.stop()

# ---------------------------------------------------------
# Detect PM2.5 values column
# ---------------------------------------------------------
value_cols = [c for c in df.columns if "pm" in c or "particulate" in c]

if len(value_cols) == 0:
    st.error("Could not find PM₂.₅ concentration column.")
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
# GLOBAL PM2.5 TREND
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
# SINGLE COUNTRY TREND
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
# MULTI-COUNTRY COMPARISON
# ---------------------------------------------------------
elif mode == "Compare Countries":

    st.subheader("🌐 Compare Multiple Countries")

    countries = sorted(df["country"].unique())
    selected = st.multiselect(
        "Choose countries to compare:",
        countries,
        default=["Afghanistan", "India", "China"]
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

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Summary Statistics
# ---------------------------------------------------------
st.markdown("### 📊 Summary Statistics")

summary = df.groupby("year")[pm_col].agg(["mean", "min", "max"]).reset_index()

st.dataframe(summary, use_container_width=True)

