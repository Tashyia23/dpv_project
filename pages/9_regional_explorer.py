# pages/3_Regional_Explorer.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.loader import load_master_data
from utils.loader import load_base_data
from utils.ui import header
from utils.regions import REGION_COLORS

st.set_page_config(layout="wide")

# df = load_base_data()
df = load_master_data()


header(
    "🌎 Regional Explorer",
    "Compare air pollution health risk across regions and countries."
)

if "region" not in df.columns:
    df["region"] = "Other"

pollutant_cols = [c for c in df.columns if c.endswith("_aqi_value")]

# Aggregate country-level
country_df = (
    df[["country", "region"] + pollutant_cols]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

# Simple overall risk: mean of all pollutant AQIs (no weights here for clarity)
country_df["avg_pollution"] = country_df[pollutant_cols].mean(axis=1)

# -----------------------------
# Controls
# -----------------------------
regions = sorted(country_df["region"].unique())
selected_region = st.selectbox("Select region", regions)

region_subset = country_df[country_df["region"] == selected_region].copy()

if region_subset.empty:
    st.warning("No data for this region.")
    st.stop()

left, right = st.columns([1.2, 1])

with left:
    st.markdown(f"### {selected_region} – Overview")

    # Region-level bar: avg risk by country
    fig_region = px.bar(
        region_subset.sort_values("avg_pollution", ascending=False),
        x="country",
        y="avg_pollution",
        title=f"{selected_region}: Average Pollution (all pollutants)",
        color="country",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_region.update_layout(
        showlegend=False,
        height=420,
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis_title="Country",
        yaxis_title="Average AQI across pollutants",
    )
    st.plotly_chart(fig_region, use_container_width=True)

with right:
    st.markdown("### Region Summary")

    region_mean = region_subset["avg_pollution"].mean()
    best_row = region_subset.loc[region_subset["avg_pollution"].idxmin()]
    worst_row = region_subset.loc[region_subset["avg_pollution"].idxmax()]

    st.metric("Region mean AQI (all pollutants)", f"{region_mean:.1f}")
    st.metric("Lowest pollution country", f"{best_row['country']} ({best_row['avg_pollution']:.1f})")
    st.metric("Highest pollution country", f"{worst_row['country']} ({worst_row['avg_pollution']:.1f})")

    st.markdown("#### Average pollutant levels (region-wide)")
    pollutant_means = region_subset[pollutant_cols].mean().reset_index()
    pollutant_means.columns = ["pollutant", "mean_aqi"]

    fig_poll = px.bar(
        pollutant_means,
        x="pollutant",
        y="mean_aqi",
        title="Average AQI per pollutant",
        color="pollutant",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_poll.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title="Pollutant",
        yaxis_title="Mean AQI",
    )
    st.plotly_chart(fig_poll, use_container_width=True)

st.markdown("---")

# -----------------------------
# Heatmap Region × Pollutant
# -----------------------------
st.markdown("### Heatmap: Country vs Pollutant in Selected Region")

heat_df = region_subset.set_index("country")[pollutant_cols]

fig_heat = px.imshow(
    heat_df,
    labels=dict(x="Pollutant", y="Country", color="AQI"),
    aspect="auto",
    color_continuous_scale="RdYlGn_r",
)
fig_heat.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))

st.plotly_chart(fig_heat, use_container_width=True)
