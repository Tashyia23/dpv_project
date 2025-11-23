import streamlit as st
import pandas as pd
import plotly.express as px
from utils.loader import load_pm25_data
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------------
# Load dataset
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
# Validate essential columns
# ---------------------------------------------------------

if "year" not in df.columns:
    st.error("Dataset must contain a 'Year' column.")
    st.stop()

if "country" not in df.columns:
    st.error("Dataset must contain a 'country' column.")
    st.stop()

# Detect PM2.5 column
pm_cols = [c for c in df.columns if "pm2" in c.lower()]
if len(pm_cols) == 0:
    st.error("No PM₂.₅ column found in dataset.")
    st.stop()

pm_col = pm_cols[0]

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
# ---------------------------------------------------------
# View Mode Toggle (TOP AREA)
# ---------------------------------------------------------
st.subheader("📊 Choose Trend View")

mode = st.segmented_control(
    "Trend Mode",
    ["Global Trend", "Single Country", "Compare Countries"],
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
        labels={pm_col: "PM₂.₅ (μg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SINGLE COUNTRY
# ---------------------------------------------------------
elif mode == "Single Country":

    st.subheader("🚩 Country Trend Over Time")

    countries = sorted(df["country"].unique())
    country = st.selectbox("Select a country:", countries)

    cdf = df[df["country"] == country]

    fig = px.line(
        cdf,
        x="year",
        y=pm_col,
        markers=True,
        title=f"{country}: PM₂.₅ Trend",
        labels={pm_col: "PM₂.₅ (μg/m³)"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# MULTI-COUNTRY COMPARISON
# ---------------------------------------------------------
elif mode == "Compare Countries":

    st.subheader("🌐 Compare Multiple Countries")

    countries = sorted(df["country"].unique())

    selected = st.multiselect(
        "Choose countries:",
        countries,
        default=["Afghanistan", "India", "China"]
    )

    if len(selected) == 0:
        st.info("Select at least 1 country to compare.")
        st.stop()

    comp_df = df[df["country"].isin(selected)]

    fig = px.line(
        comp_df,
        x="year",
        y=pm_col,
        color="country",
        markers=True,
        title="PM₂.₅ Comparison Across Countries",
        labels={pm_col: "PM₂.₅ (μg/m³)"}
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
