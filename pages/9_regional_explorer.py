# # pages/3_Regional_Explorer.py

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from utils.loader import load_master_data
# from utils.loader import load_base_data
# from utils.ui import header
# from utils.regions import REGION_COLORS

# st.set_page_config(layout="wide")

# # df = load_base_data()
# df = load_master_data()


# header(
#     "🌎 Regional Explorer",
#     "Compare air pollution health risk across regions and countries."
# )

# if "region" not in df.columns:
#     df["region"] = "Other"

# pollutant_cols = [c for c in df.columns if c.endswith("_aqi_value")]

# # Aggregate country-level
# country_df = (
#     df[["country", "region"] + pollutant_cols]
#     .groupby(["country", "region"], as_index=False)
#     .mean()
# )

# # Simple overall risk: mean of all pollutant AQIs (no weights here for clarity)
# country_df["avg_pollution"] = country_df[pollutant_cols].mean(axis=1)

# # -----------------------------
# # Controls
# # -----------------------------
# regions = sorted(country_df["region"].unique())
# selected_region = st.selectbox("Select region", regions)

# region_subset = country_df[country_df["region"] == selected_region].copy()

# if region_subset.empty:
#     st.warning("No data for this region.")
#     st.stop()

# left, right = st.columns([1.2, 1])

# with left:
#     st.markdown(f"### {selected_region} – Overview")

#     # Region-level bar: avg risk by country
#     fig_region = px.bar(
#         region_subset.sort_values("avg_pollution", ascending=False),
#         x="country",
#         y="avg_pollution",
#         title=f"{selected_region}: Average Pollution (all pollutants)",
#         color="country",
#         color_discrete_sequence=px.colors.qualitative.Set2,
#     )
#     fig_region.update_layout(
#         showlegend=False,
#         height=420,
#         margin=dict(l=0, r=0, t=50, b=0),
#         xaxis_title="Country",
#         yaxis_title="Average AQI across pollutants",
#     )
#     st.plotly_chart(fig_region, use_container_width=True)

# with right:
#     st.markdown("### Region Summary")

#     region_mean = region_subset["avg_pollution"].mean()
#     best_row = region_subset.loc[region_subset["avg_pollution"].idxmin()]
#     worst_row = region_subset.loc[region_subset["avg_pollution"].idxmax()]

#     st.metric("Region mean AQI (all pollutants)", f"{region_mean:.1f}")
#     st.metric("Lowest pollution country", f"{best_row['country']} ({best_row['avg_pollution']:.1f})")
#     st.metric("Highest pollution country", f"{worst_row['country']} ({worst_row['avg_pollution']:.1f})")

#     st.markdown("#### Average pollutant levels (region-wide)")
#     pollutant_means = region_subset[pollutant_cols].mean().reset_index()
#     pollutant_means.columns = ["pollutant", "mean_aqi"]

#     fig_poll = px.bar(
#         pollutant_means,
#         x="pollutant",
#         y="mean_aqi",
#         title="Average AQI per pollutant",
#         color="pollutant",
#         color_discrete_sequence=px.colors.qualitative.Set3,
#     )
#     fig_poll.update_layout(
#         showlegend=False,
#         height=300,
#         margin=dict(l=0, r=0, t=40, b=0),
#         xaxis_title="Pollutant",
#         yaxis_title="Mean AQI",
#     )
#     st.plotly_chart(fig_poll, use_container_width=True)

# st.markdown("---")

# # -----------------------------
# # Heatmap Region × Pollutant
# # -----------------------------
# st.markdown("### Heatmap: Country vs Pollutant in Selected Region")

# heat_df = region_subset.set_index("country")[pollutant_cols]

# fig_heat = px.imshow(
#     heat_df,
#     labels=dict(x="Pollutant", y="Country", color="AQI"),
#     aspect="auto",
#     color_continuous_scale="RdYlGn_r",
# )
# fig_heat.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))

# st.plotly_chart(fig_heat, use_container_width=True)

#_____________________

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

# --------------------------------------------------------------------
# LOAD RAW + PROCESSED DATASETS
# --------------------------------------------------------------------
raw_g, raw_pm25 = load_raw_dataset()
processed_df = load_processed_dataset()

if raw_g is None or processed_df is None:
    st.error("❌ Dataset is empty or failed to load.")
    st.stop()

# Validate raw dataset
if "Country" not in raw_g.columns:
    st.error("❌ Raw dataset requires a 'Country' column.")
    st.stop()

# Validate processed dataset
if "country" not in processed_df.columns:
    st.error("❌ Processed dataset requires a 'country' column.")
    st.stop()

# Add region labels to both datasets
raw_g["region"] = raw_g["Country"].apply(assign_region)
processed_df["region"] = processed_df["country"].apply(assign_region)

header(
    "🌎 Regional Explorer (Before vs After Processing)",
    "Compare pollution & health risk across regions and countries, using both raw and normalised data."
)

# Identify pollutant columns
raw_pollutants = [c for c in raw_g.columns if any(x in c.lower() for x in ["aqi", "value"])]
proc_pollutants = [c for c in processed_df.columns if c.endswith("_aqi_value")]

if not raw_pollutants:
    st.error("No raw AQI/value columns found in raw dataset.")
    st.stop()

if not proc_pollutants:
    st.error("No *_aqi_value columns found in processed dataset.")
    st.stop()

# --------------------------------------------------------------------
# BEFORE / AFTER TOGGLE
# --------------------------------------------------------------------
view_mode = st.radio(
    "Select Data Mode:",
    ["Before Processing (Raw AQI)", "After Processing (Normalised Risk Index)"],
    horizontal=True
)

# ====================================================================
# MODE 1 — BEFORE PROCESSING (RAW AQI)
# ====================================================================
if view_mode.startswith("Before"):

    st.subheader("🌫 Regional Patterns — Raw AQI (Before Processing)")

    # Region selector (including 'All Regions')
    all_regions = sorted(raw_g["region"].unique())
    region_choice = st.selectbox(
        "Select Region:",
        ["All Regions"] + all_regions
    )

    # Pollutant selector
    selected_pollutant = st.selectbox(
        "Select pollutant:",
        raw_pollutants
    )

    # -----------------------------
    # Aggregations
    # -----------------------------
    # Region-level aggregation
    region_agg = (
        raw_g.groupby("region", as_index=False)[raw_pollutants].mean()
    )

    # Country-level aggregation
    raw_country = (
        raw_g.groupby(["Country", "region"], as_index=False)[raw_pollutants].mean()
    )

    # -----------------------------
    # MAIN REGIONAL BAR CHART
    # -----------------------------
    if region_choice == "All Regions":
        st.markdown("### 1. Average Raw AQI by Region")

        plot_df = region_agg.sort_values(selected_pollutant, ascending=False)

        fig_region = px.bar(
            plot_df,
            x="region",
            y=selected_pollutant,
            color=selected_pollutant,
            color_continuous_scale="Reds",
            title=f"Average Raw {selected_pollutant} by Region"
        )
        fig_region.update_layout(height=430, xaxis_tickangle=20)
        st.plotly_chart(fig_region, use_container_width=True)

    else:
        st.markdown(f"### 1. Countries in {region_choice} — Raw {selected_pollutant}")

        sub = raw_country[raw_country["region"] == region_choice]

        fig_region = px.bar(
            sub.sort_values(selected_pollutant, ascending=False),
            x="Country",
            y=selected_pollutant,
            color=selected_pollutant,
            color_continuous_scale="Reds",
            title=f"{region_choice} — Raw {selected_pollutant} by Country"
        )
        fig_region.update_layout(height=430, xaxis_tickangle=45)
        st.plotly_chart(fig_region, use_container_width=True)

    # -----------------------------
    # SUMMARY METRICS
    # -----------------------------
    st.markdown("### 2. Regional Summary (Raw AQI)")

    if region_choice == "All Regions":
        # Global summary
        avg_val = region_agg[selected_pollutant].mean()
        best_region = region_agg.loc[region_agg[selected_pollutant].idxmin()]
        worst_region = region_agg.loc[region_agg[selected_pollutant].idxmax()]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean AQI across regions", f"{avg_val:.1f}")
        with col2:
            st.metric("Lowest AQI Region", f"{best_region['region']} ({best_region[selected_pollutant]:.1f})")
        with col3:
            st.metric("Highest AQI Region", f"{worst_region['region']} ({worst_region[selected_pollutant]:.1f})")

    else:
        # Within-region summary
        sub = raw_country[raw_country["region"] == region_choice]
        avg_val = sub[selected_pollutant].mean()
        best_cty = sub.loc[sub[selected_pollutant].idxmin()]
        worst_cty = sub.loc[sub[selected_pollutant].idxmax()]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{region_choice} — Mean AQI", f"{avg_val:.1f}")
        with col2:
            st.metric("Lowest AQI Country", f"{best_cty['Country']} ({best_cty[selected_pollutant]:.1f})")
        with col3:
            st.metric("Highest AQI Country", f"{worst_cty['Country']} ({worst_cty[selected_pollutant]:.1f})")

    st.markdown("---")

    # -----------------------------
    # HEATMAP: Country × Pollutant (Raw)
    # -----------------------------
    st.markdown("### 3. Heatmap — Country × Pollutant (Raw AQI)")

    if region_choice == "All Regions":
        heat_source = raw_country.copy()
    else:
        heat_source = raw_country[raw_country["region"] == region_choice].copy()

    if heat_source.empty:
        st.info("No data available for this region.")
    else:
        heat_df = heat_source.set_index("Country")[raw_pollutants]

        fig_heat = px.imshow(
            heat_df,
            aspect="auto",
            color_continuous_scale="RdYlGn_r",
            title=f"Raw AQI Heatmap — {region_choice}"
        )
        fig_heat.update_layout(height=500)
        st.plotly_chart(fig_heat, use_container_width=True)

    # -----------------------------
    # NOTE ABOUT AFTER-PROCESSING VIEW
    # -----------------------------
    st.info(
        "You are currently viewing **raw AQI data before any cleaning or normalisation**.\n\n"
        "Switch to **'After Processing (Normalised Risk Index)'** above to see composite risk indices, "
        "normalised pollutant levels, and regional risk rankings."
    )

    st.stop()

# ====================================================================
# MODE 2 — AFTER PROCESSING (NORMALISED RISK INDEX)
# ====================================================================

st.subheader("📌 Regional Analysis — Normalised Risk Index (After Processing)")

# Country-level aggregation from processed dataset
proc_country = (
    processed_df[["country", "region"] + proc_pollutants]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

# Normalise pollutants 0–1 across all countries
scaled = {}
for col in proc_pollutants:
    s = proc_country[col].astype(float)
    lo, hi = s.min(), s.max()
    scaled[col] = (s - lo) / (hi - lo) if hi > lo else np.zeros_like(s)

scaled_df = pd.DataFrame(scaled)

# Composite risk index per country (simple mean of normalised pollutants)
proc_country["risk_index"] = scaled_df.mean(axis=1)
proc_country["risk_percentile"] = proc_country["risk_index"].rank(pct=True)

# Region selector
regions_proc = sorted(proc_country["region"].unique())
region_choice_proc = st.selectbox("Select Region:", regions_proc)

region_df = proc_country[proc_country["region"] == region_choice_proc].copy()

if region_df.empty:
    st.warning("No processed data for this region.")
    st.stop()

left, right = st.columns([1.3, 1])

# =========================================================
# LEFT: COUNTRY RISK BAR CHART
# =========================================================
with left:
    st.markdown(f"### 1. Country Risk in {region_choice_proc} (Normalised 0–1)")

    fig_rank = px.bar(
        region_df.sort_values("risk_index", ascending=False),
        x="country",
        y="risk_index",
        color="risk_index",
        color_continuous_scale="Reds",
        title=f"{region_choice_proc} — Composite Risk Index by Country"
    )
    fig_rank.update_layout(height=430, xaxis_tickangle=45)
    st.plotly_chart(fig_rank, use_container_width=True)

# =========================================================
# RIGHT: REGION SUMMARY + POLLUTANT BREAKDOWN
# =========================================================
with right:
    st.markdown("### 2. Region Risk Summary")

    reg_mean = region_df["risk_index"].mean()
    best = region_df.loc[region_df["risk_index"].idxmin()]
    worst = region_df.loc[region_df["risk_index"].idxmax()]

    st.metric("Mean Risk Index", f"{reg_mean:.2f}")
    st.metric("Lowest-Risk Country", f"{best['country']} ({best['risk_index']:.2f})")
    st.metric("Highest-Risk Country", f"{worst['country']} ({worst['risk_index']:.2f})")

    st.markdown("#### Region-Wide Average Pollutant Levels (Normalised)")

    # Region-specific averages (using same scaling)
    region_scaled = scaled_df.loc[region_df.index]  # align rows
    avg_poll = region_scaled.mean().reset_index()
    avg_poll.columns = ["pollutant", "value"]

    fig_poll = px.bar(
        avg_poll,
        x="pollutant",
        y="value",
        color="pollutant",
        color_discrete_sequence=px.colors.qualitative.Set3,
        title=f"{region_choice_proc} — Normalised Pollutant Profile"
    )
    fig_poll.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_poll, use_container_width=True)

st.markdown("---")

# =========================================================
# HEATMAP (Normalised) — Country × Pollutant
# =========================================================
st.markdown("### 3. Heatmap — Country × Pollutant (Normalised)")

heat_df_norm = region_df.set_index("country")[proc_pollutants]

fig_heat2 = px.imshow(
    heat_df_norm,
    aspect="auto",
    color_continuous_scale="Reds",
    title=f"{region_choice_proc} — Normalised Pollutant Heatmap (0–1 Scale)"
)
fig_heat2.update_layout(height=500)
st.plotly_chart(fig_heat2, use_container_width=True)
