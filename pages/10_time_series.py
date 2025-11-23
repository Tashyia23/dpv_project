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
# YEAR column fix (dataset uses 'Year')
# ---------------------------------------------------------
if "Year" in df.columns:
    df["year"] = pd.to_numeric(df["Year"], errors="coerce")
else:
    st.error("Dataset must contain a 'Year' column.")
    st.stop()

df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# Sort by year
df = df.sort_values("year")

# ---------------------------------------------------------
# Clean country column
# ---------------------------------------------------------
if "Entity" in df.columns:
    df = df.rename(columns={"Entity": "country"})
elif "entity" in df.columns:
    df = df.rename(columns={"entity": "country"})

if "country" not in df.columns:
    st.error("Dataset must contain a 'country' column.")
    st.stop()

# ---------------------------------------------------------
# Detect PM2.5 concentration column
# ---------------------------------------------------------
value_cols = [
    c for c in df.columns
    if "pm25" in c.lower() or "pm2" in c.lower() or "fine particulate" in c.lower()
]

if len(value_cols) == 0:
    st.error("Could not detect a PM₂.₅ concentration column.")
    st.stop()

pm_col = value_cols[0]  # use first detected column

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")
mode = st.sidebar.radio(
    "Select View Mode:",
    ["Global Trend", "Single Country", "Compare Countries"]
)

# ---------------------------------------------------------
# 1️⃣ GLOBAL TREND
# ---------------------------------------------------------
if mode == "Global Trend":
    st.subheader("🌍 Global PM₂.₅ Trend Over Time")

    global_df = df.groupby("year")[pm_col].mean().reset_index()

    fig = px.line(
        global_df,
        x="year",
        y=pm_col,
        markers=True,
        line_shape="spline",
        title="Global Average PM₂.₅ Concentration Over Time",
        labels={pm_col: "PM₂.₅ (μg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 2️⃣ SINGLE COUNTRY TREND
# ---------------------------------------------------------
elif mode == "Single Country":
    st.subheader("🇨🇺 Country Trend Over Time")

    countries = sorted(df["country"].unique())
    country = st.selectbox("Select a country:", countries)

    cdf = df[df["country"] == country]

    fig = px.line(
        cdf,
        x="year",
        y=pm_col,
        markers=True,
        line_shape="spline",
        title=f"PM₂.₅ Trend — {country}",
        labels={pm_col: "PM₂.₅ (μg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 3️⃣ MULTIPLE COUNTRY COMPARISON
# ---------------------------------------------------------
elif mode == "Compare Countries":
    st.subheader("🌐 Compare Multiple Countries")

    countries = sorted(df["country"].unique())
    selected = st.multiselect(
        "Choose countries to compare:",
        countries,
        default=["Afghanistan", "India", "China"]
    )

    if len(selected) == 0:
        st.info("Select at least one country.")
        st.stop()

    comp_df = df[df["country"].isin(selected)]

    fig = px.line(
        comp_df,
        x="year",
        y=pm_col,
        color="country",
        markers=True,
        line_shape="spline",
        title="PM₂.₅ Levels — Multi-Country Comparison",
        labels={pm_col: "PM₂.₅ (μg/m³)"}
    )
    fig.update_layout(legend_title="Country")

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Summary Statistics
# ---------------------------------------------------------
st.markdown("### 📊 Summary Statistics (Global Annual Stats)")

summary = df.groupby("year")[pm_col].agg(["mean", "min", "max"]).reset_index()
summary = summary.rename(columns={
    "mean": "Avg PM₂.₅",
    "min": "Min PM₂.₅",
    "max": "Max PM₂.₅"
})

st.dataframe(summary, use_container_width=True)
