# pages/10_time_series.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.loader import load_base_data
from utils.ui import header

st.set_page_config(layout="wide")


# ---------------------------------------------------
# Helper: Plotly line styling
# ---------------------------------------------------
def style_line_fig(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=50, b=0),
        legend_title=None,
        template="plotly_white",
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text=None)
    return fig


# ---------------------------------------------------
# Load base data
# ---------------------------------------------------
df = load_base_data()

header(
    "📈 Time-Series Explorer",
    "See how pollution levels evolve over time by country and region."
)

if "year" not in df.columns:
    st.error("The dataset does not contain a 'year' column. Please check your data.")
    st.stop()

# Make sure year is numeric (int) and sorted
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df = df.dropna(subset=["Year"])
df["Year"] = df["Year"].astype(int)

# Region safety (in case some rows are missing region)
if "region" not in df.columns:
    df["region"] = "Unknown"

# ---------------------------------------------------
# Pollutant options
# ---------------------------------------------------
pollutant_columns = [c for c in df.columns if c.endswith("_aqi_value")]

if not pollutant_columns:
    st.error("No pollutant *_aqi_value columns found in the dataset.")
    st.stop()

pretty_names = {
    "pm25_aqi_value": "PM₂.₅ (Fine Particles)",
    "pm10_aqi_value": "PM₁₀ (Coarse Particles)",
    "no2_aqi_value": "NO₂ (Nitrogen Dioxide)",
    "ozone_aqi_value": "O₃ (Ozone)",
    "co_aqi_value": "CO (Carbon Monoxide)",
}

def format_pollutant(col: str) -> str:
    return pretty_names.get(col, col)


# ---------------------------------------------------
# 1. Global Controls
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 1. Time-Series Controls")

col_p1, col_p2, col_p3 = st.columns([2, 1.2, 1.2])

with col_p1:
    pollutant = st.selectbox(
        "Pollutant to analyse",
        pollutant_columns,
        index=pollutant_columns.index("pm25_aqi_value")
        if "pm25_aqi_value" in pollutant_columns
        else 0,
        format_func=format_pollutant,
    )

with col_p2:
    agg_func_label = st.selectbox(
        "Aggregate by",
        ["Mean (average)", "Median", "90th percentile"],
    )
    if agg_func_label.startswith("Mean"):
        agg_func = np.mean
    elif agg_func_label.startswith("Median"):
        agg_func = np.median
    else:
        agg_func = lambda x: np.percentile(x, 90)

with col_p3:
    smooth_window = st.slider(
        "Rolling window (years)",
        min_value=1,
        max_value=5,
        value=1,
        help="Apply simple moving average smoothing over time.",
    )

st.markdown("</div>", unsafe_allow_html=True)

metric_label = format_pollutant(pollutant)


# ---------------------------------------------------
# 2. Global Trend over Time
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown(f"### 2. Global Trend of {metric_label} Over Time")

global_ts = (
    df.groupby("year")[pollutant]
    .agg(agg_func)
    .reset_index()
    .rename(columns={pollutant: "value"})
    .sort_values("year")
)

if smooth_window > 1:
    global_ts["value_smooth"] = (
        global_ts["value"].rolling(window=smooth_window, min_periods=1).mean()
    )
else:
    global_ts["value_smooth"] = global_ts["value"]

fig_global = px.line(
    global_ts,
    x="year",
    y="value_smooth",
    markers=True,
    title=f"Global {metric_label} ({agg_func_label})",
)

fig_global = style_line_fig(fig_global)
st.plotly_chart(fig_global, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# 3. Country & Multi-country Trends
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 3. Country Time-Series Views")

countries = sorted(df["country"].unique().tolist())

# Default: top 5 by latest year pollutant
latest_year = df["year"].max()
latest_df = df[df["year"] == latest_year]
top_by_latest = (
    latest_df.groupby("country")[pollutant]
    .mean()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

col_c1, col_c2 = st.columns(2)

# --- Single country view ---
with col_c1:
    st.markdown("#### a) Single Country vs Global Benchmark")
    sel_country = st.selectbox(
        "Select a country",
        countries,
        index=countries.index(top_by_latest[0]) if top_by_latest else 0,
        key="ts_single_country",
    )

    country_ts = (
        df[df["country"] == sel_country]
        .groupby("year")[pollutant]
        .agg(agg_func)
        .reset_index()
        .rename(columns={pollutant: "value"})
        .sort_values("year")
    )

    # Add global for reference
    merged = country_ts.merge(
        global_ts[["year", "value_smooth"]],
        on="year",
        how="left",
        suffixes=("_country", "_global"),
    )

    fig_country = px.line(
        merged,
        x="year",
        y=["value_country", "value_smooth"],
        markers=True,
        labels={
            "value_country": sel_country,
            "value_smooth": "Global",
        },
        title=f"{metric_label} in {sel_country} vs Global ({agg_func_label})",
    )
    fig_country = style_line_fig(fig_country)
    st.plotly_chart(fig_country, use_container_width=True)

# --- Multi-country comparison ---
with col_c2:
    st.markdown("#### b) Compare Multiple Countries")

    default_multi = top_by_latest[:3] if len(top_by_latest) >= 3 else countries[:3]

    sel_multi = st.multiselect(
        "Select countries to compare (max 6)",
        countries,
        default=default_multi,
        key="ts_multi_country",
    )

    sel_multi = sel_multi[:6]  # hard cap

    if sel_multi:
        multi_ts = (
            df[df["country"].isin(sel_multi)]
            .groupby(["country", "year"])[pollutant]
            .agg(agg_func)
            .reset_index()
            .rename(columns={pollutant: "value"})
            .sort_values(["country", "year"])
        )

        fig_multi = px.line(
            multi_ts,
            x="year",
            y="value",
            color="country",
            markers=True,
            title=f"{metric_label} – Multi-country Comparison ({agg_func_label})",
        )
        fig_multi = style_line_fig(fig_multi)
        st.plotly_chart(fig_multi, use_container_width=True)
    else:
        st.info("Select at least one country to view the comparison chart.")

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# 4. Regional Time-Series
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 4. Regional Time-Series")

regions = sorted(df["region"].unique().tolist())

col_r1, col_r2 = st.columns([2, 1])

with col_r1:
    sel_regions = st.multiselect(
        "Regions to compare",
        regions,
        default=regions if len(regions) <= 5 else regions[:5],
    )

with col_r2:
    normalize = st.checkbox(
        "Normalise each region (index to first year = 100)",
        value=False,
        help="Helps compare relative growth/decline rather than absolute levels.",
    )

if sel_regions:
    reg_ts = (
        df[df["region"].isin(sel_regions)]
        .groupby(["region", "year"])[pollutant]
        .agg(agg_func)
        .reset_index()
        .rename(columns={pollutant: "value"})
        .sort_values(["region", "year"])
    )

    if normalize:
        reg_ts["value_norm"] = reg_ts.groupby("region")["value"].apply(
            lambda x: (x / x.iloc[0]) * 100 if x.iloc[0] != 0 else x * 0
        )
        y_col = "value_norm"
        y_title = f"{metric_label} – indexed to first year (100)"
    else:
        y_col = "value"
        y_title = metric_label

    fig_region = px.line(
        reg_ts,
        x="year",
        y=y_col,
        color="region",
        markers=True,
        title=f"Regional {metric_label} Over Time ({agg_func_label})",
    )
    fig_region = style_line_fig(fig_region)
    fig_region.update_yaxes(title_text=y_title)

    st.plotly_chart(fig_region, use_container_width=True)
else:
    st.info("Choose at least one region to view regional time-series.")

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# 5. Data table (optional explorer)
# ---------------------------------------------------
with st.expander("🔍 Show underlying time-series data"):
    cols_to_show = ["country", "region", "year"] + pollutant_columns
    existing_cols = [c for c in cols_to_show if c in df.columns]
    st.dataframe(
        df[existing_cols]
        .sort_values(["country", "year"])
        .reset_index(drop=True)
    )
