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

from utils.data_loader import load_raw_dataset, load_processed_dataset
from utils.ui import header
from utils.regions import assign_region

st.set_page_config(layout="wide")

# --------------------------------------------------------
# LOAD BOTH RAW & PROCESSED DATASETS
# --------------------------------------------------------
raw_g, raw_pm25 = load_raw_dataset()
proc = load_processed_dataset()

header(
    "🌎 Regional Explorer",
    "Compare air pollution and health risk across regions using raw data and processed risk index."
)

if raw_g is None or proc is None:
    st.error("Dataset failed to load.")
    st.stop()

# Standard names
raw_g.rename(columns={"Country": "country"}, inplace=True)

# Add region
raw_g["region"] = raw_g["country"].apply(assign_region)
proc["region"] = proc["country"].apply(assign_region)

# Pollutant columns
raw_cols = [c for c in raw_g.columns if "AQI" in c or "Value" in c]
proc_cols = [c for c in proc.columns if c.endswith("_aqi_value")]

# --------------------------------------------------------
# MODE TOGGLE
# --------------------------------------------------------
mode = st.radio(
    "View Mode:",
    ["Before Processing (Raw AQI)", "After Processing (Normalised Risk Index)"],
    horizontal=True
)

# ========================================================
# BEFORE PROCESSING — RAW AQI
# ========================================================
if mode.startswith("Before"):

    st.subheader("📌 Regional Overview — Raw AQI Dataset")

    # Country-level average
    country_df = (
        raw_g[["country", "region"] + raw_cols]
        .groupby(["country", "region"], as_index=False)
        .mean()
    )

    # Simple average across pollutants
    country_df["avg_pollution"] = country_df[raw_cols].mean(axis=1)

    # Region selector
    regions = sorted(country_df["region"].unique())
    selected_region = st.selectbox("Select region", regions)

    region_subset = country_df[country_df["region"] == selected_region].copy()

    if region_subset.empty:
        st.warning("No data available.")
        st.stop()

    left, right = st.columns([1.2, 1])

    # -------------------------
    # LEFT — BAR CHART
    # -------------------------
    with left:
        st.markdown(f"### {selected_region} – Overview")

        fig_region = px.bar(
            region_subset.sort_values("avg_pollution", ascending=False),
            x="country",
            y="avg_pollution",
            title=f"{selected_region}: Average Pollution (Raw AQI)",
            color="country",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_region.update_layout(
            showlegend=False,
            height=420,
            margin=dict(l=0, r=0, t=50, b=0),
            xaxis_title="Country",
            yaxis_title="Average AQI",
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # -------------------------
    # RIGHT — SUMMARY
    # -------------------------
    with right:
        st.markdown("### Region Summary")

        region_mean = region_subset["avg_pollution"].mean()
        best_row = region_subset.loc[region_subset["avg_pollution"].idxmin()]
        worst_row = region_subset.loc[region_subset["avg_pollution"].idxmax()]

        st.metric("Region Mean AQI", f"{region_mean:.1f}")
        st.metric("Lowest Pollution Country", f"{best_row['country']} ({best_row['avg_pollution']:.1f})")
        st.metric("Highest Pollution Country", f"{worst_row['country']} ({worst_row['avg_pollution']:.1f})")

        st.markdown("#### Average pollutant levels (region-wide)")
        pollutant_means = region_subset[raw_cols].mean().reset_index()
        pollutant_means.columns = ["pollutant", "mean_aqi"]

        fig_poll = px.bar(
            pollutant_means,
            x="pollutant",
            y="mean_aqi",
            title="Average AQI per pollutant",
            color="pollutant",
            color_discrete_sequence=px.colors.qualitative.Set3
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

    # -------------------------
    # HEATMAP
    # -------------------------
    st.markdown("### Heatmap: Country vs Pollutant (Raw AQI)")

    heat_df = region_subset.set_index("country")[raw_cols]

    fig_heat = px.imshow(
        heat_df,
        labels=dict(x="Pollutant", y="Country", color="AQI"),
        aspect="auto",
        color_continuous_scale="RdYlGn_r"
    )
    fig_heat.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))

    st.plotly_chart(fig_heat, use_container_width=True)

    st.stop()

# ========================================================
# AFTER PROCESSING — NORMALISED RISK INDEX
# ========================================================
st.subheader("📌 Regional Overview — Normalised Risk Index (After Processing)")

# Country-level average
proc_country = (
    proc[["country", "region"] + proc_cols]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

# Normalise pollutants 0–1
scaled = {}
for col in proc_cols:
    series = proc_country[col].astype(float)
    lo, hi = series.min(), series.max()
    scaled[col] = (series - lo) / (hi - lo) if hi > lo else np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)
proc_country["risk_index"] = scaled_df.mean(axis=1)

regions_proc = sorted(proc_country["region"].unique())
selected_region = st.selectbox("Select region", regions_proc)

region_subset = proc_country[proc_country["region"] == selected_region].copy()

left, right = st.columns([1.2, 1])

# -------------------------
# LEFT — RISK BAR CHART
# -------------------------
with left:
    st.markdown(f"### {selected_region} – Risk Index Overview")

    fig_region = px.bar(
        region_subset.sort_values("risk_index", ascending=False),
        x="country",
        y="risk_index",
        title=f"{selected_region}: Composite Risk Index (0–1)",
        color="country",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_region.update_layout(
        showlegend=False,
        height=420,
        margin=dict(l=0, r=0, t=50, b=0),
        xaxis_title="Country",
        yaxis_title="Risk Index (0–1)",
    )
    st.plotly_chart(fig_region, use_container_width=True)

# -------------------------
# RIGHT — SUMMARY
# -------------------------
with right:
    st.markdown("### Region Summary")

    region_mean = region_subset["risk_index"].mean()
    best_row = region_subset.loc[region_subset["risk_index"].idxmin()]
    worst_row = region_subset.loc[region_subset["risk_index"].idxmax()]

    st.metric("Region Mean Risk Index", f"{region_mean:.2f}")
    st.metric("Lowest-Risk Country", f"{best_row['country']} ({best_row['risk_index']:.2f})")
    st.metric("Highest-Risk Country", f"{worst_row['country']} ({worst_row['risk_index']:.2f})")

    st.markdown("#### Average normalised pollutant levels (region-wide)")
    region_scaled = scaled_df.loc[region_subset.index]  # same rows
    avg_poll = region_scaled.mean().reset_index()
    avg_poll.columns = ["pollutant", "value"]

    fig_poll = px.bar(
        avg_poll,
        x="pollutant",
        y="value",
        title="Normalised Pollutant Levels (0–1)",
        color="pollutant",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_poll.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title="Pollutant",
        yaxis_title="Normalised Value",
    )
    st.plotly_chart(fig_poll, use_container_width=True)

st.markdown("---")

# -------------------------
# HEATMAP (NORMALISED)
# -------------------------
st.markdown("### Heatmap: Country vs Pollutant (Normalised)")

heat_df = region_subset.set_index("country")[proc_cols]

fig_heat = px.imshow(
    heat_df,
    labels=dict(x="Pollutant", y="Country", color="Risk"),
    aspect="auto",
    color_continuous_scale="Reds"
)
fig_heat.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))

st.plotly_chart(fig_heat, use_container_width=True)

