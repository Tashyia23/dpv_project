import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import (
    load_raw_dataset,
    load_processed_dataset
)
from utils.ui import header
from utils.regions import assign_region

st.set_page_config(layout="wide")

# ----------------------------------------------------------------
# LOAD BOTH RAW + PROCESSED DATASETS
# ----------------------------------------------------------------
raw_g, raw_pm25 = load_raw_dataset()
processed_df = load_processed_dataset()

if raw_g is None or processed_df is None:
    st.error("❌ Failed to load raw or processed dataset.")
    st.stop()

header(
    "📊 Risk Explorer (Advanced Analytics)",
    "Compare raw AQI data (before cleaning) vs processed risk index (after normalization)."
)

# Identify pollutant columns
raw_pollutants = [c for c in raw_g.columns if "AQI" in c or "Value" in c]
proc_pollutants = [c for c in processed_df.columns if c.endswith("_aqi_value")]

# Add region
raw_g["region"] = raw_g["Country"].apply(assign_region)
processed_df["region"] = processed_df["country"].apply(assign_region)

# ----------------------------------------------------------------
# BEFORE / AFTER TOGGLE
# ----------------------------------------------------------------
view_mode = st.radio(
    "Select Data Mode:",
    ["Before Processing (Raw AQI)", "After Processing (Normalised Risk Index)"],
    horizontal=True
)

# ================================================================
# MODE 1 — BEFORE PROCESSING (RAW AQI)
# ================================================================
if view_mode.startswith("Before"):

    st.subheader("🌫 Raw AQI — Before Processing")
    selected_pollutant = st.selectbox("Select pollutant:", raw_pollutants)

    raw_agg = raw_g.groupby("Country", as_index=False)[selected_pollutant].mean()
    top_raw = raw_agg.sort_values(selected_pollutant, ascending=False).head(25)

    fig_raw = px.bar(
        top_raw,
        x="Country",
        y=selected_pollutant,
        title=f"Top 25 Countries — Raw {selected_pollutant}",
        color=selected_pollutant,
        color_continuous_scale="Reds"
    )
    fig_raw.update_layout(height=450, xaxis_tickangle=45)
    st.plotly_chart(fig_raw, use_container_width=True)

    st.info(
        "You are currently viewing **raw AQI data before any cleaning**.\n\n"
        "Switch to *After Processing* to explore the fully normalised risk index and advanced analytics."
    )

    st.stop()

# ================================================================
# MODE 2 — AFTER PROCESSING (NORMALISED RISK)
# ================================================================
# Compute mean pollutants per country
agg_df = processed_df[["country"] + proc_pollutants].groupby("country").mean().reset_index()

# Normalised values
scaled = {}
for col in proc_pollutants:
    s = agg_df[col].astype(float)
    lo, hi = s.min(), s.max()
    scaled[col] = (s - lo) / (hi - lo) if hi > lo else np.zeros_like(s)

scaled_df = pd.DataFrame(scaled)

# Composite risk index
agg_df["risk_index"] = scaled_df.mean(axis=1)
agg_df["risk_percentile"] = agg_df["risk_index"].rank(pct=True)

# ================================================================
# SECTION 1 — RANKING CONTROLS
# ================================================================
st.subheader("1. Country Ranking Controls")

colA, colB = st.columns(2)

with colA:
    ranking_mode = st.selectbox(
        "Risk Ranking Mode",
        ["Highest Risk", "Lowest Risk", "Middle Range", "Custom Percentile Range"]
    )

with colB:
    metric_mode = st.selectbox(
        "Plot Metric",
        ["Overall Risk Index"] + proc_pollutants
    )

# Custom range slider
if ranking_mode == "Custom Percentile Range":
    pct_min, pct_max = st.slider("Select Percentile Range", 0.0, 1.0, (0.20, 0.80), 0.01)
else:
    pct_min, pct_max = 0.0, 1.0

rank_df = agg_df.copy()

if ranking_mode == "Highest Risk":
    rank_df = rank_df.sort_values("risk_index", ascending=False)
elif ranking_mode == "Lowest Risk":
    rank_df = rank_df.sort_values("risk_index", ascending=True)
elif ranking_mode == "Middle Range":
    rank_df = rank_df[(rank_df["risk_percentile"] > 0.33) & (rank_df["risk_percentile"] < 0.66)]
elif ranking_mode == "Custom Percentile Range":
    rank_df = rank_df[
        (rank_df["risk_percentile"] >= pct_min) &
        (rank_df["risk_percentile"] <= pct_max)
    ]

metric_col = "risk_index" if metric_mode == "Overall Risk Index" else metric_mode

# ================================================================
# SECTION 2 — RANKING BAR CHART
# ================================================================
st.subheader("2. Ranked Countries (Bar Chart)")

top_n = st.slider("Show Top N Countries", 5, 40, 15)
plot_df = rank_df.head(top_n)

fig_rank = px.bar(
    plot_df,
    x="country",
    y=metric_col,
    color="risk_index",
    color_continuous_scale="Reds",
    title=f"Top {top_n} Countries — {metric_mode}"
)
fig_rank.update_layout(height=450, xaxis_tickangle=45)
st.plotly_chart(fig_rank, use_container_width=True)

# ================================================================
# SECTION 3 — DUAL AXIS RISK vs POLLUTANT
# ================================================================
st.subheader("3. Dual-Axis Comparison (Risk vs Pollutant)")

col1, col2 = st.columns(2)

with col1:
    pollutant_choice = st.selectbox("Select Pollutant:", proc_pollutants)

with col2:
    dual_n = st.slider("Number of Countries", 5, 25, 10)

dual_df = agg_df.sort_values("risk_index", ascending=False).head(dual_n)

fig_dual = go.Figure()

fig_dual.add_trace(go.Bar(
    x=dual_df["country"],
    y=dual_df["risk_index"],
    name="Risk Index",
    marker_color="#ef4444"
))

fig_dual.add_trace(go.Scatter(
    x=dual_df["country"],
    y=dual_df[pollutant_choice],
    name=pollutant_choice,
    mode="lines+markers",
    yaxis="y2",
    marker=dict(color="#0ea5e9")
))

fig_dual.update_layout(
    height=450,
    yaxis=dict(title="Risk Index"),
    yaxis2=dict(title="Pollutant AQI", overlaying="y", side="right")
)

st.plotly_chart(fig_dual, use_container_width=True)

# ================================================================
# SECTION 4 — HEATMAP
# ================================================================
st.subheader("4. Pollutant Heatmap")

heat_df = agg_df.set_index("country")[proc_pollutants]

fig_heat = px.imshow(
    heat_df,
    aspect="auto",
    color_continuous_scale="Reds",
    title="Pollutant Heatmap"
)
st.plotly_chart(fig_heat, use_container_width=True)

# ================================================================
# SECTION 5 — RADAR CHART
# ================================================================
st.subheader("5. Radar Chart — Compare Countries")

compare_list = st.multiselect(
    "Select Countries (max 3)",
    agg_df["country"].unique(),
    default=agg_df["country"].head(3).tolist()
)

if compare_list:
    radar_df = agg_df[agg_df["country"].isin(compare_list)]
    categories = proc_pollutants

    fig_radar = go.Figure()

    for _, row in radar_df.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[p] for p in categories],
            theta=categories,
            fill="toself",
            name=row["country"]
        ))

    fig_radar.update_layout(
        height=530,
        polar=dict(radialaxis=dict(visible=True))
    )

    st.plotly_chart(fig_radar, use_container_width=True)
