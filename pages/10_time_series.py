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
# YEAR FIX (Your dataset uses 'Year')
# ---------------------------------------------------------
if "Year" in df.columns:
    df["year"] = df["Year"]
else:
    st.error("The dataset must contain a 'Year' column.")
    st.stop()

df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# ---------------------------------------------------------
# Rename country column
# ---------------------------------------------------------
if "Entity" in df.columns:
    df.rename(columns={"Entity": "country"}, inplace=True)

if "country" not in df.columns:
    st.error("Dataset missing 'country' column.")
    st.stop()

# ---------------------------------------------------------
# Detect PM2.5 column
# ---------------------------------------------------------
value_cols = [
    c for c in df.columns
    if "pm2" in c.lower() or "fine" in c.lower()
]

if len(value_cols) == 0:
    st.error("No PM₂.₅ concentration column detected.")
    st.stop()

pm_col = value_cols[0]  # first detected PM2.5 column

# ---------------------------------------------------------
# Region Auto-Assignment
# ---------------------------------------------------------
region_map = {
    "Afghanistan": "Asia",
    "India": "Asia",
    "China": "Asia",
    "Japan": "Asia",
    "Saudi Arabia": "Middle East",
    "Iran (Islamic Republic of)": "Middle East",
    "Qatar": "Middle East",
    "United States of America": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Brazil": "South America",
    "Argentina": "South America",
    "Chile": "South America",
    "France": "Europe",
    "Germany": "Europe",
    "United Kingdom of Great Britain and Northern Ireland": "Europe",
    "Australia": "Oceania",
    "New Zealand": "Oceania",
    "South Africa": "Africa",
    "Egypt": "Africa",
    "Nigeria": "Africa",
}

df["region"] = df["country"].map(region_map).fillna("Other")

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.header("🔎 View Options")
mode = st.sidebar.radio(
    "Choose mode:",
    [
        "Global Trend",
        "Single Country",
        "Compare Multiple Countries",
        "Regional Trend (NEW)",
        "Pollutant Trend (NEW)"
    ]
)

# ---------------------------------------------------------
# 1. GLOBAL TREND
# ---------------------------------------------------------
if mode == "Global Trend":
    st.subheader("🌍 Global PM₂.₅ Trend Over Time")

    global_df = df.groupby("year")[pm_col].mean().reset_index()

    fig = px.line(
        global_df, x="year", y=pm_col, markers=True,
        title="Global Average PM₂.₅ Over Time",
        labels={pm_col: "PM₂.₅ Concentration (µg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 2. SINGLE COUNTRY TREND
# ---------------------------------------------------------
elif mode == "Single Country":

    st.subheader("🇦🇺 Single Country Trend")

    countries = sorted(df["country"].unique())
    country = st.selectbox("Select country:", countries)

    cdf = df[df["country"] == country]

    fig = px.line(
        cdf, x="year", y=pm_col, markers=True,
        title=f"PM₂.₅ Trend — {country}",
        labels={pm_col: "PM₂.₅ Concentration (µg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 3. COMPARE MULTIPLE COUNTRIES (MISSING BEFORE)
# ---------------------------------------------------------
elif mode == "Compare Multiple Countries":

    st.subheader("🌐 Compare PM₂.₅ Levels Across Countries")

    countries = sorted(df["country"].unique())
    selected = st.multiselect(
        "Select countries:",
        countries,
        default=["China", "India", "United States of America"]
    )

    if not selected:
        st.info("Select at least one country.")
        st.stop()

    comp_df = df[df["country"].isin(selected)]

    fig = px.line(
        comp_df, x="year", y=pm_col,
        color="country", markers=True,
        title="Country Comparison — PM₂.₅ Trends",
        labels={pm_col: "PM₂.₅ Concentration (µg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 4. REGIONAL TREND
# ---------------------------------------------------------
elif mode == "Regional Trend (NEW)":

    st.subheader("🌍 Regional PM₂.₅ Trend")

    regions = sorted(df["region"].unique())
    selected_regions = st.multiselect(
        "Select regions:",
        regions,
        default=["Asia", "Europe", "Africa"]
    )

    rdf = df[df["region"].isin(selected_regions)]

    fig = px.line(
        rdf.groupby(["year", "region"])[pm_col].mean().reset_index(),
        x="year", y=pm_col,
        color="region", markers=True,
        title="PM₂.₅ Trends by Region",
        labels={pm_col: "PM₂.₅ Concentration (µg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 5. POLLUTANT TREND (NEW)
# ---------------------------------------------------------
elif mode == "Pollutant Trend (NEW)":

    st.subheader("🧪 Pollutant-Level Trend (PM₂.₅ only for now)")

    fig = px.line(
        df.groupby("year")[pm_col].mean().reset_index(),
        x="year", y=pm_col, markers=True,
        title="PM₂.₅ (Fine Particles) — Global Trend",
        labels={pm_col: "PM₂.₅ Concentration (µg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Summary Statistics
# ---------------------------------------------------------
st.markdown("### 📊 Summary Statistics")

summary = df.groupby("year")[pm_col].agg(
    mean_level="mean",
    min_level="min",
    max_level="max"
).reset_index()

st.dataframe(summary, use_container_width=True)


