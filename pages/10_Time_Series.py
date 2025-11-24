import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from utils.ui import header

st.set_page_config(layout="wide")

# Function to load custom CSS (ensure it's loaded for every page)
def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS in each page (this ensures the styles are applied across pages)
load_css()

# -------------------------------------------------------------------
# Helper: robust loader for WHO PM2.5 time-series file
# -------------------------------------------------------------------
def load_who_pm25():
    candidates = [
        "data/raw/pm25-air-pollution.csv",
        "data/pm25_air_pollution.csv",
        "data/pm25-air-pollution.csv",
        "pm25-air-pollution.csv",
        "/mnt/data/pm25-air-pollution.csv",
    ]

    df = None
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except Exception:
                continue

    if df is None:
        return None

    col_name = "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total"

    if "Entity" not in df.columns or "Year" not in df.columns or col_name not in df.columns:
        return None

    out = df[["Entity", "Year", col_name]].copy()
    out.rename(
        columns={
            "Entity": "country",
            "Year": "year",
            col_name: "pm25_value",
        },
        inplace=True,
    )

    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["pm25_value"] = pd.to_numeric(out["pm25_value"], errors="coerce")
    out = out.dropna(subset=["year", "pm25_value"])
    out["year"] = out["year"].astype(int)

    out["who_index"] = out["pm25_value"] / 25.0

    base = (
        out.sort_values("year")
        .groupby("country")["pm25_value"]
        .first()
        .rename("base_pm25")
    )
    out = out.merge(base, on="country", how="left")
    out["pct_change_since_base"] = (
        (out["pm25_value"] - out["base_pm25"]) / out["base_pm25"]
    ) * 100.0

    return out

# -------------------------------------------------------------------
# 1. Load data
# -------------------------------------------------------------------
who_df = load_who_pm25()

header(
    "📈 Time-Series Explorer",
    "Explore WHO PM₂.₅ trends before and after health-risk transformation."
)

if who_df is None or who_df.empty:
    st.error(
        "Could not load WHO PM₂.₅ time-series file "
        "(`pm25-air-pollution.csv`). Please check that it exists in the repo."
    )
    st.stop()

# -------------------------------------------------------------------
# 2. View mode: Before vs After
# -------------------------------------------------------------------
view_mode = st.radio(
    "Select data view:",
    [
        "Before Processing: Raw PM₂.₅ Concentration (μg/m³)",
        "After Processing: WHO Health-Risk Index (PM₂.₅ / 25)",
    ],
    horizontal=True,
)

if view_mode.startswith("Before"):
    metric_options = {
        "Raw PM₂.₅ concentration (μg/m³)": "pm25_value",
        "Percentage change since first year (%)": "pct_change_since_base",
    }
    default_metric = "pm25_value"
    metric_label_suffix = ""
    secondary_series = "who_index"
else:
    metric_options = {
        "WHO health-risk index (PM₂.₅ / 25)": "who_index",
        "Raw PM₂.₅ concentration (μg/m³)": "pm25_value",
        "Percentage change since first year (%)": "pct_change_since_base",
    }
    default_metric = "who_index"
    metric_label_suffix = " (WHO Index)"
    secondary_series = "pm25_value"

# -------------------------------------------------------------------
# 3. Tabs for different exploration modes
# -------------------------------------------------------------------
tab_global, tab_country, tab_compare, tab_snapshot = st.tabs(
    ["🌍 Global Trend", "🇺🇳 Single Country", "🌐 Compare Countries", "🏙 Snapshot AQI by City"]
)

# -------------------------------------------------------------------
# Utility: build dual-axis time series
# -------------------------------------------------------------------
def build_dual_axis(
    df,
    primary_col,
    secondary_col=None,
    title="",
    primary_name="Metric",
    secondary_name="Secondary",
):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    series = df.sort_values("year")
    fig.add_trace(
        go.Scatter(
            x=series["year"],
            y=series[primary_col],
            mode="lines+markers",
            name=primary_name,
            line=dict(color="#2563EB"),
        ),
        secondary_y=False,
    )

    if secondary_col is not None and secondary_col in series.columns:
        fig.add_trace(
            go.Scatter(
                x=series["year"],
                y=series[secondary_col],
                mode="lines+markers",
                name=secondary_name,
                line=dict(color="#EF4444", dash="dash"),
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title=title,
        margin=dict(l=40, r=40, t=60, b=40),
        legend_title_text="",
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text=primary_name, secondary_y=False)
    if secondary_col is not None:
        fig.update_yaxes(title_text=secondary_name, secondary_y=True)

    return fig

# -------------------------------------------------------------------
# TAB 1 — GLOBAL TREND
# -------------------------------------------------------------------
with tab_global:
    st.markdown("## 🌍 Global Trend")
    metric_key = st.selectbox(
        "Select metric:",
        list(metric_options.keys()),
        index=list(metric_options.values()).index(default_metric),
        key="global_metric",
    )
    metric_col = metric_options[metric_key]

    global_df = (
        who_df.groupby("year")[["pm25_value", "who_index", "pct_change_since_base"]]
        .mean()
        .reset_index()
    )

    if view_mode.startswith("Before"):
        primary_name = metric_key
        secondary_name = (
            "WHO Health-Risk Index (PM₂.₅ / 25)" if secondary_series == "who_index" else "PM₂.₅ (μg/m³)"
        )
    else:
        primary_name = metric_key
        secondary_name = (
            "PM₂.₅ concentration (μg/m³)" if secondary_series == "pm25_value" else "WHO Index"
        )

    fig_global = build_dual_axis(
        global_df,
        primary_col=metric_col,
        secondary_col=secondary_series,
        title=f"Global {metric_key} Over Time{metric_label_suffix}",
        primary_name=primary_name,
        secondary_name=secondary_name,
    )
    st.plotly_chart(fig_global, use_container_width=True)

# -------------------------------------------------------------------
# TAB 2 — SINGLE COUNTRY
# -------------------------------------------------------------------
with tab_country:
    st.markdown("## 🇺🇳 Single Country View")
    countries = sorted(who_df["country"].unique())
    country = st.selectbox("Select a country:", countries, key="single_country")
    metric_key = st.selectbox(
        "Select metric:",
        list(metric_options.keys()),
        index=list(metric_options.values()).index(default_metric),
        key="country_metric",
    )
    metric_col = metric_options[metric_key]
    cdf = who_df[who_df["country"] == country].copy()

    if cdf.empty:
        st.info("No data available for this country.")
    else:
        fig_country = build_dual_axis(
            cdf,
            primary_col=metric_col,
            secondary_col=secondary_series,
            title=f"{country} – {metric_key} Over Time{metric_label_suffix}",
            primary_name=primary_name,
            secondary_name=secondary_name,
        )
        st.plotly_chart(fig_country, use_container_width=True)

# -------------------------------------------------------------------
# TAB 3 — COMPARE COUNTRIES
# -------------------------------------------------------------------
with tab_compare:
    st.markdown("## 🌐 Compare Countries")
    metric_key = st.selectbox(
        "Select metric:",
        list(metric_options.keys()),
        index=list(metric_options.values()).index(default_metric),
        key="compare_metric",
    )
    metric_col = metric_options[metric_key]
    countries = sorted(who_df["country"].unique())
    selected = st.multiselect(
        "Choose countries to compare:", countries, default=["Afghanistan", "India", "China", "Malaysia"]
    )

    if selected:
        comp_df = who_df[who_df["country"].isin(selected)].copy()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for c in selected:
            subset = comp_df[comp_df["country"] == c].sort_values("year")
            fig.add_trace(
                go.Scatter(
                    x=subset["year"],
                    y=subset[metric_col],
                    mode="lines+markers",
                    name=c,
                ),
                secondary_y=False,
            )
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# TAB 4 — SNAPSHOT AQI BY CITY (ONLY IN THIS TAB)
# -------------------------------------------------------------------
with tab_snapshot:
    st.markdown("## 🏙 Snapshot AQI by City")
    st.write("This section is for AQI by city-specific data.")

    # ---------------------------------------------------------------
    # Load city-level AQI dataset (your uploaded file)
    # ---------------------------------------------------------------
    def load_city_aqi():
        candidates = [
            "/mnt/data/global_air_pollution.csv",
            "data/global_air_pollution.csv",
            "data/raw/global_air_pollution.csv",
            "global_air_pollution.csv",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    return df
                except:
                    pass
        return None

    city_df = load_city_aqi()

    if city_df is None or city_df.empty:
        st.error("❌ Processed AQI dataset not found (`global_air_pollution.csv`).")
        st.stop()

    # ---------------------------------------------------------------
    # Clean column names
    # ---------------------------------------------------------------
    rename_map = {
        "Country": "country",
        "City": "city",
        "AQI Value": "aqi",
        "CO AQI Value": "co",
        "Ozone AQI Value": "ozone",
        "NO2 AQI Value": "no2",
        "PM2.5 AQI Value": "pm25",
        "PM2.5 AQI Category": "pm25_cat",
        "NO2 AQI Category": "no2_cat",
        "Ozone AQI Category": "ozone_cat",
        "CO AQI Category": "co_cat",
    }
    city_df = city_df.rename(columns=rename_map)

    # Identify pollutant columns
    pollutant_cols = ["pm25", "no2", "ozone", "co", "aqi"]
    pollutant_options = {
        "🌫 PM₂.₅ (Fine Particles)": "pm25",
        "🟧 NO₂": "no2",
        "💜 Ozone (O₃)": "ozone",
        "🔥 CO": "co",
        "⭐ Overall AQI": "aqi",
    }

    # ---------------------------------------------------------------
    # User selection
    # ---------------------------------------------------------------
    pollutant_label = st.selectbox(
        "Choose pollutant:",
        list(pollutant_options.keys()),
    )
    pollutant_col = pollutant_options[pollutant_label]

    top_n = st.slider(
        "Show top N most polluted cities",
        5, 50, 15
    )

    # ---------------------------------------------------------------
    # Top-N Most Polluted Cities (bar chart)
    # ---------------------------------------------------------------
    st.markdown(f"### 🌆 Top {top_n} Most Polluted Cities — {pollutant_label}")

    plot_df = (
        city_df[["country", "city", pollutant_col]]
        .dropna()
        .sort_values(by=pollutant_col, ascending=False)
        .head(top_n)
    )

    fig_top = go.Figure(
        go.Bar(
            x=plot_df["city"],
            y=plot_df[pollutant_col],
            marker_color="#ef4444",
        )
    )
    fig_top.update_layout(
        height=420,
        xaxis_title="City",
        yaxis_title=f"{pollutant_label}",
        title=f"Top {top_n} Cities by {pollutant_label}",
        xaxis_tickangle=45
    )
    st.plotly_chart(fig_top, use_container_width=True)

    # ---------------------------------------------------------------
    # AQI Category Distribution
    # ---------------------------------------------------------------
    st.markdown("### 🟩 AQI Category Distribution")

    if "AQI Category" in city_df.columns:
        cat_counts = city_df["AQI Category"].value_counts()

        fig_pi = go.Figure(
            go.Pie(
                labels=cat_counts.index,
                values=cat_counts.values,
                hole=0.4
            )
        )
        fig_pi.update_layout(height=380)
        st.plotly_chart(fig_pi, use_container_width=True)

    # ---------------------------------------------------------------
    # City Map (if lat/lon exist)
    # ---------------------------------------------------------------
    if {"Latitude", "Longitude"}.issubset(city_df.columns):
        st.markdown("### 🗺 City-Level Pollution Map")

        fig_map = px.scatter_geo(
            city_df,
            lat="Latitude",
            lon="Longitude",
            size=pollutant_col,
            color=pollutant_col,
            hover_name="city",
            color_continuous_scale="Reds",
        )
        fig_map.update_layout(height=520)
        st.plotly_chart(fig_map, use_container_width=True)

    # ---------------------------------------------------------------
    # Raw table
    # ---------------------------------------------------------------
    st.markdown("### 📄 Full City-Level AQI Table")
    st.dataframe(city_df, use_container_width=True)
