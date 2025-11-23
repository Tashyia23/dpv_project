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

# ---------------------------------------------------------
# LOAD DATASETS
# ---------------------------------------------------------
raw_g, raw_pm25 = load_raw_dataset()
processed_df = load_processed_dataset()

header(
    "🌎 Regional Explorer",
    "Compare air pollution and health risk across regions using raw data and processed risk index."
)

if raw_g is None or processed_df is None:
    st.error("❌ Dataset failed to load.")
    st.stop()

# Standardize naming
if "Country" not in raw_g.columns:
    st.error("❌ Raw dataset must contain 'Country' column.")
    st.stop()

# Region assignment
raw_g["region"] = raw_g["Country"].apply(assign_region)
processed_df["region"] = processed_df["country"].apply(assign_region)

# SAFE pollutant extraction (numeric only)
raw_pollutants = [
    c for c in raw_g.columns
    if (
        ("aqi" in c.lower() or "value" in c.lower())
        and pd.api.types.is_numeric_dtype(raw_g[c])
    )
]

proc_pollutants = [
    c for c in processed_df.columns
    if c.lower().endswith("_aqi_value")
]

if len(raw_pollutants) == 0:
    st.error("❌ No numeric raw AQI pollutant columns found.")
    st.stop()

if len(proc_pollutants) == 0:
    st.error("❌ No numeric processed pollutant columns found.")
    st.stop()


# ---------------------------------------------------------
# BEFORE / AFTER TOGGLE
# ---------------------------------------------------------
view_mode = st.radio(
    "View Mode:",
    ["Before Processing (Raw AQI)", "After Processing (Normalised Risk Index)"],
    horizontal=True
)


# =========================================================
#  🌫 BEFORE PROCESSING — RAW AQI
# =========================================================
if view_mode.startswith("Before"):

    st.subheader("📌 Regional Overview — Raw AQI Dataset")

    # Aggregate raw country-level data
    raw_country = (
        raw_g[["Country", "region"] + raw_pollutants]
        .groupby(["Country", "region"], as_index=False)
        .mean()
    )

    raw_country["avg_pollution"] = raw_country[raw_pollutants].mean(axis=1)

    # ---------------------
    # REGION SELECTION
    # ---------------------
    regions = sorted(raw_country["region"].unique())
    selected_region = st.selectbox("Select Region", regions)

    region_df = raw_country[raw_country["region"] == selected_region]

    if region_df.empty:
        st.warning("No data for this region.")
        st.stop()

    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------
    left, right = st.columns([1.3, 1])

    # ---------------- LEFT: BAR CHART --------------------
    with left:
        st.markdown(f"### {selected_region} — Overview")

        fig_region = px.bar(
            region_df.sort_values("avg_pollution", ascending=False),
            x="Country",
            y="avg_pollution",
            title=f"{selected_region}: Average AQI (Raw)",
            color="Country",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_region.update_layout(
            showlegend=False,
            height=430,
            margin=dict(l=0, r=0, t=50, b=0),
            xaxis_title="Country",
            yaxis_title="Average AQI",
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # ---------------- RIGHT: SUMMARY ---------------------
    with right:
        st.markdown("### Region Summary")

        region_mean = region_df["avg_pollution"].mean()
        best = region_df.loc[region_df["avg_pollution"].idxmin()]
        worst = region_df.loc[region_df["avg_pollution"].idxmax()]

        st.metric("Region Mean AQI", f"{region_mean:.1f}")
        st.metric(
            "Lowest Pollution Country",
            f"{best['Country']} ({best['avg_pollution']:.1f})"
        )
        st.metric(
            "Highest Pollution Country",
            f"{worst['Country']} ({worst['avg_pollution']:.1f})"
        )

        st.markdown("#### Average AQI per Pollutant (Raw)")

        pollutant_means = region_df[raw_pollutants].mean().reset_index()
        pollutant_means.columns = ["pollutant", "mean_aqi"]

        fig_poll = px.bar(
            pollutant_means,
            x="pollutant",
            y="mean_aqi",
            color="pollutant",
            color_discrete_sequence=px.colors.qualitative.Set3,
            title="Average Pollutant Levels",
        )
        fig_poll.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_poll, use_container_width=True)

    st.markdown("---")

    # ---------------- HEATMAP ----------------------------
    st.markdown("### Heatmap: Country × Pollutant (Raw AQI)")

    heat_df = region_df.set_index("Country")[raw_pollutants]

    fig_heat = px.imshow(
        heat_df,
        labels=dict(x="Pollutant", y="Country", color="AQI"),
        aspect="auto",
        color_continuous_scale="RdYlGn_r",
    )
    fig_heat.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.stop()


# =========================================================
#  🟩 AFTER PROCESSING — NORMALISED RISK INDEX
# =========================================================
st.subheader("📌 Regional Overview — Normalised Risk Index")

# Country-level processed aggregation
proc_country = (
    processed_df[["country", "region"] + proc_pollutants]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

# Normalise pollutants (0–1)
scaled = {}
for col in proc_pollutants:
    s = proc_country[col].astype(float)
    lo, hi = s.min(), s.max()
    scaled[col] = (s - lo) / (hi - lo) if hi > lo else np.zeros_like(s)

scaled_df = pd.DataFrame(scaled)

proc_country["risk_index"] = scaled_df.mean(axis=1)

# REGION SELECTION
regions = sorted(proc_country["region"].unique())
selected_region = st.selectbox("Select Region (Processed)", regions)

region_df = proc_country[proc_country["region"] == selected_region]

left, right = st.columns([1.3, 1])

# ---------------- LEFT: RISK INDEX BAR CHART -------------------
with left:
    st.markdown(f"### {selected_region} — Risk Levels")

    fig_risk = px.bar(
        region_df.sort_values("risk_index", ascending=False),
        x="country",
        y="risk_index",
        color="risk_index",
        color_continuous_scale="Reds",
        title=f"{selected_region}: Composite Risk Index",
    )
    fig_risk.update_layout(height=430)
    st.plotly_chart(fig_risk, use_container_width=True)

# ---------------- RIGHT: SUMMARY METRICS -----------------------
with right:
    st.markdown("### Region Risk Summary")

    reg_mean = region_df["risk_index"].mean()
    best = region_df.loc[region_df["risk_index"].idxmin()]
    worst = region_df.loc[region_df["risk_index"].idxmax()]

    st.metric("Mean Risk Index", f"{reg_mean:.2f}")
    st.metric("Lowest Risk Country", f"{best['country']} ({best['risk_index']:.2f})")
    st.metric("Highest Risk Country", f"{worst['country']} ({worst['risk_index']:.2f})")

    st.markdown("#### Average Pollutant Scores (Normalised)")

    poll_means = scaled_df.mean().reset_index()
    poll_means.columns = ["pollutant", "value"]

    fig_poll2 = px.bar(
        poll_means,
        x="pollutant",
        y="value",
        color="pollutant",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_poll2.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig_poll2, use_container_width=True)

st.markdown("---")

# ---------------- HEATMAP PROCESSED ---------------------------
st.markdown("### Heatmap: Country × Pollutant (Normalised)")

heat_df2 = region_df.set_index("country")[proc_pollutants]

fig_heat2 = px.imshow(
    heat_df2,
    aspect="auto",
    color_continuous_scale="Reds",
)
fig_heat2.update_layout(height=500)
st.plotly_chart(fig_heat2, use_container_width=True)


