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

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.loader import load_base_data
from utils.ui import header
from utils.regions import assign_region, REGION_COLORS

st.set_page_config(layout="wide")

# -------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------
df = load_base_data()

header("🌎 Regional Explorer", "Compare pollution & health risk across regions and countries.")

if df is None or df.empty:
    st.error("Dataset is empty or failed to load.")
    st.stop()

if "country" not in df.columns:
    st.error("Dataset must contain 'country' column.")
    st.stop()

# Region auto-assignment
df["region"] = df["country"].apply(assign_region)

# Identify pollutants
pollutants = [c for c in df.columns if c.endswith("_aqi_value")]

if not pollutants:
    st.error("No pollutant AQI columns found.")
    st.stop()

# -------------------------------------------------------------
# BEFORE vs AFTER PROCESSING TOGGLE
# -------------------------------------------------------------
mode = st.radio(
    "View dataset in:",
    ["Raw AQI (Before Processing)", "Risk-Processed (After Normalisation)"],
    horizontal=True
)

# =============================================================
# RAW MODE (no scaling, no risk index)
# =============================================================
raw_country = (
    df[["country", "region"] + pollutants]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

raw_country["avg_pollution"] = raw_country[pollutants].mean(axis=1)

if mode == "Raw AQI (Before Processing)":

    st.subheader("📌 Raw AQI Regional Analysis (Before Processing)")

    regions = sorted(raw_country["region"].unique())
    region = st.selectbox("Select Region", regions)

    region_df = raw_country[raw_country["region"] == region]

    left, right = st.columns([1.3, 1])

    # --------------------- COUNTRY BAR CHART ---------------------
    with left:
        fig = px.bar(
            region_df.sort_values("avg_pollution", ascending=False),
            x="country",
            y="avg_pollution",
            title=f"{region} — Average AQI (Raw)",
            color="country",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=430, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # --------------------- SUMMARY CARDS -------------------------
    with right:
        st.markdown("### Region Summary (Raw)")
        reg_mean = region_df["avg_pollution"].mean()
        best = region_df.loc[region_df["avg_pollution"].idxmin()]
        worst = region_df.loc[region_df["avg_pollution"].idxmax()]

        st.metric("Mean AQI", f"{reg_mean:.1f}")
        st.metric("Lowest AQI Country", f"{best['country']} ({best['avg_pollution']:.1f})")
        st.metric("Highest AQI Country", f"{worst['country']} ({worst['avg_pollution']:.1f})")

        st.markdown("#### Average per Pollutant (Raw)")
        pollutant_means = region_df[pollutants].mean().reset_index()
        pollutant_means.columns = ["pollutant", "mean_aqi"]

        fig2 = px.bar(
            pollutant_means,
            x="pollutant", y="mean_aqi",
            title="Regional Pollutant Breakdown",
            color="pollutant",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig2.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Heatmap
    st.markdown("### Heatmap — Country × Pollutant (Raw)")
    heat_df = region_df.set_index("country")[pollutants]

    fig3 = px.imshow(
        heat_df,
        aspect="auto",
        color_continuous_scale="RdYlGn_r",
        title="Pollutant Heatmap"
    )
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)

    st.stop()

# =============================================================
# RISK-PROCESSED MODE (normalized + risk index)
# =============================================================
st.subheader("📌 Region Analysis — Normalised Risk Index")

# --- Normalisation (0–1 scale per pollutant) ---
proc_country = (
    df[["country", "region"] + pollutants]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

scaled = {}
for col in pollutants:
    s = proc_country[col].astype(float)
    lo, hi = s.min(), s.max()
    scaled[col] = (s - lo) / (hi - lo) if hi > lo else np.zeros_like(s)

scaled_df = pd.DataFrame(scaled)
proc_country["risk_index"] = scaled_df.mean(axis=1)
proc_country["risk_percentile"] = proc_country["risk_index"].rank(pct=True)

# REGION SELECTION
regions = sorted(proc_country["region"].unique())
region = st.selectbox("Select Region", regions)

region_df = proc_country[proc_country["region"] == region]

left, right = st.columns([1.3, 1])

# =============================================================
# LEFT PLOT — RISK BAR CHART
# =============================================================
with left:
    st.markdown(f"### {region} — Country Risk (Normalised 0–1)")

    fig4 = px.bar(
        region_df.sort_values("risk_index", ascending=False),
        x="country",
        y="risk_index",
        color="risk_index",
        color_continuous_scale="Reds",
        title=f"{region}: Risk Index"
    )
    fig4.update_layout(height=430)
    st.plotly_chart(fig4, use_container_width=True)

# =============================================================
# RIGHT — RISK SUMMARY
# =============================================================
with right:
    st.markdown("### Region Risk Summary")

    reg_mean = region_df["risk_index"].mean()
    best = region_df.loc[region_df["risk_index"].idxmin()]
    worst = region_df.loc[region_df["risk_index"].idxmax()]

    st.metric("Mean Risk Index", f"{reg_mean:.2f}")
    st.metric("Lowest-Risk", f"{best['country']} ({best['risk_index']:.2f})")
    st.metric("Highest-Risk", f"{worst['country']} ({worst['risk_index']:.2f})")

    st.markdown("#### Region-Wide Average Pollutant Scores (normalised)")
    avg_poll = scaled_df.mean().reset_index()
    avg_poll.columns = ["pollutant", "value"]

    fig5 = px.bar(
        avg_poll,
        x="pollutant",
        y="value",
        color="pollutant",
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Normalised Pollutant Levels"
    )
    fig5.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# =============================================================
# HEATMAP (Risk-Processed)
# =============================================================
st.markdown("### Heatmap — Country × Pollutant (Normalised)")

heat_df2 = region_df.set_index("country")[pollutants]

fig6 = px.imshow(
    heat_df2,
    aspect="auto",
    color_continuous_scale="Reds",
    title="Normalised Heatmap (0–1 Scale)"
)
fig6.update_layout(height=500)
st.plotly_chart(fig6, use_container_width=True)
