import streamlit as st
import os
import plotly.express as px
import pandas as pd

# Function to load custom CSS (ensure it's loaded for every page)
def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS in each page (this ensures the styles are applied across pages)
load_css()

from utils.data_loader import load_raw_dataset, load_processed_dataset


st.set_page_config(layout="wide")

# Load all datasets
raw_g, raw_p = load_raw_dataset()
processed_df = load_processed_dataset()


# ----------------------------------------------------------
# MODE SELECTOR
# ----------------------------------------------------------
view_mode = st.radio(
    "Select data view:",
    ["Before Processing", "After Processing", "Compare Before vs After"],
    horizontal=True
)

st.title("🗺 Global Air Pollution Map")
st.caption("Explore spatial patterns using raw and processed AQI datasets.")


# =====================================================================
# 🟥 MODE 1 — BEFORE PROCESSING (RAW) — NOW WITH MAPPING
# =====================================================================
if view_mode == "Before Processing":

    st.subheader("📄 Raw Global Air Pollution Dataset (Before Processing)")
    st.dataframe(raw_g, use_container_width=True)

    st.subheader("🌍 Raw PM2.5 WHO Dataset")
    st.dataframe(raw_p, use_container_width=True)

    st.markdown("---")

    # Raw pollutant columns
    raw_pollutants = [
        "AQI Value",
        "PM2.5 AQI Value",
        "NO2 AQI Value",
        "Ozone AQI Value",
        "CO AQI Value",
    ]

    available_raw_cols = [c for c in raw_pollutants if c in raw_g.columns]

    st.subheader("🧪 Choose Raw Pollutant to Map")
    selected_raw = st.selectbox("Pollutant:", available_raw_cols)

    # Aggregate by country
    raw_agg = (
        raw_g.groupby("Country", as_index=False)[selected_raw].mean()
    )

    # Choropleth map
    fig = px.choropleth(
        raw_agg,
        locations="Country",
        locationmode="country names",
        color=selected_raw,
        title=f"Raw Data Map — {selected_raw}",
        color_continuous_scale="RdYlBu_r",
    )

    fig.update_geos(showframe=False, projection_type="natural earth")
    st.plotly_chart(fig, use_container_width=True)

    st.stop()


# =====================================================================
# 🟩 MODE 2 — AFTER PROCESSING
# =====================================================================
if view_mode == "After Processing":

    st.subheader("📄 Processed Dataset (After Cleaning & Merging)")
    st.dataframe(processed_df, use_container_width=True)

    # Detect AQI cols
    pollutant_cols = [c for c in processed_df.columns if c.endswith("_aqi_value") or c == "pm25_value"]

    selected = st.selectbox("Select pollutant to map:", pollutant_cols)

    agg = (
        processed_df.groupby("country", as_index=False)[selected].mean()
    )

    fig = px.choropleth(
        agg,
        locations="country",
        locationmode="country names",
        color=selected,
        title=f"Processed Map — {selected}",
        color_continuous_scale="RdYlBu_r",
    )

    fig.update_geos(showframe=False)
    st.plotly_chart(fig, use_container_width=True)

    st.stop()


# =====================================================================
# 🟧 MODE 3 — COMPARE BEFORE vs AFTER
# =====================================================================
if view_mode == "Compare Before vs After":

    st.header("📊 Before vs After Data Processing Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Before Processing")
        st.dataframe(raw_g.head(), use_container_width=True)

    with col2:
        st.subheader("After Processing")
        st.dataframe(processed_df.head(), use_container_width=True)

    st.subheader("🔍 Column Comparison")
    before_cols = set(raw_g.columns)
    after_cols = set(processed_df.columns)

    colA, colB = st.columns(2)
    with colA:
        st.write("🟥 **Raw Columns Only:**")
        st.write(list(before_cols - after_cols))

    with colB:
        st.write("🟩 **Processed Columns Only:**")
        st.write(list(after_cols - before_cols))

    # Stats comparison
    st.subheader("📈 Pollutant Summary Statistics (Before vs After)")
    summary_before = raw_g.describe(include='all')
    summary_after = processed_df.describe(include='all')

    st.write("### Before Processing")
    st.dataframe(summary_before)

    st.write("### After Processing")
    st.dataframe(summary_after)

    

