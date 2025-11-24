import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_raw_dataset, load_processed_dataset
from utils.ui import header
from utils.regions import assign_region, REGION_COLORS

# Function to load custom CSS (ensure it's loaded for every page)
def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS in each page (this ensures the styles are applied across pages)
load_css()

st.set_page_config(layout="wide")

# -----------------------------------------------------------------------------
# Mini gradient + animated bar component (same style family as 7/8)
# -----------------------------------------------------------------------------
def mini_bar_chart(values, labels, max_width=220, height=10):
    """Return HTML for a vertical stack of animated gradient bars."""
    if not values:
        return "<div>No data</div>"

    max_val = max(values) if max(values) else 1

    gradients = [
        "linear-gradient(90deg, #c084fc, #8b5cf6)",   # purple
        "linear-gradient(90deg, #67e8f9, #0ea5e9)",   # blue
        "linear-gradient(90deg, #fcd34d, #f59e0b)",   # orange
        "linear-gradient(90deg, #f9a8d4, #ef4444)",   # red
        "linear-gradient(90deg, #6ee7b7, #10b981)",   # green
    ]

    html = "<div style='margin-top:8px;'>"

    for i, v in enumerate(values):
        width_pct = 0 if max_val == 0 else (v / max_val) * 100
        bar_color = gradients[i % len(gradients)]

        html += (
            "<div style='margin-bottom:16px;'>"
            # Label
            f"<div style='font-size:0.80rem;color:#374151;font-weight:600;margin-bottom:6px;'>{labels[i]}</div>"
            # Outer bar
            f"<div style='background:#E5E7EB;border-radius:999px;height:{height}px;width:{max_width}px;overflow:hidden;'>"
            # Inner bar (animated)
            f"<div style='background:{bar_color};height:{height}px;border-radius:999px;"
            f"width:0%;animation:grow{i} 1.0s ease-out forwards;'></div>"
            "</div>"
            # Value
            f"<div style='font-size:0.75rem;color:#4B5563;margin-top:4px;text-align:right;width:{max_width}px;'>{v:.2f}</div>"
            "</div>"
            f"<style>@keyframes grow{i} {{ from {{ width:0%; }} to {{ width:{width_pct}%; }} }}</style>"
        )

    html += "</div>"
    return html


# -----------------------------------------------------------------------------
# LOAD RAW + PROCESSED DATASETS
# -----------------------------------------------------------------------------
raw_g, raw_pm25 = load_raw_dataset()
processed_df = load_processed_dataset()

if raw_g is None or processed_df is None:
    st.error("❌ Dataset is empty or failed to load.")
    st.stop()

# Standard check for raw dataset
if "Country" not in raw_g.columns:
    st.error("❌ Raw dataset requires a 'Country' column.")
    st.stop()

# Standard check for processed dataset
if "country" not in processed_df.columns:
    st.error("❌ Processed dataset requires a 'country' column.")
    st.stop()

# Add region labels
raw_g["region"] = raw_g["Country"].apply(assign_region)
processed_df["region"] = processed_df["country"].apply(assign_region)

header(
    "🌎 Regional Explorer",
    "Compare air pollution and health risk across regions using raw data and processed risk index."
)

# -----------------------------------------------------------------------------
# POLLUTANT DEFINITIONS
# -----------------------------------------------------------------------------
# Raw pollutant columns (before processing)
raw_pollutant_info = {
    "PM2.5 AQI Value": ("🟤", "PM2.5 (Fine Particles)"),
    "PM10 AQI Value": ("🟠", "PM10 (Coarse Particles)"),
    "NO2 AQI Value": ("💛", "NO₂ (Nitrogen Dioxide)"),
    "Ozone AQI Value": ("💜", "O₃ (Ozone)"),
    "CO AQI Value": ("🔥", "CO (Carbon Monoxide)"),
}

available_raw = [c for c in raw_pollutant_info.keys() if c in raw_g.columns]
# Keep only numeric columns to avoid agg errors
raw_numeric = [c for c in available_raw if np.issubdtype(raw_g[c].dtype, np.number)]

if not raw_numeric:
    st.error("No numeric raw AQI pollutant columns found in the raw dataset.")
    st.stop()

pretty_raw_labels = {
    c: f"{raw_pollutant_info[c][0]} {raw_pollutant_info[c][1]}"
    for c in raw_numeric
}

# Processed pollutant columns (after processing)
proc_pollutant_info = {
    "pm25_aqi_value": ("🟤", "PM2.5 (Fine Particles)"),
    "pm10_aqi_value": ("🟠", "PM10 (Coarse Particles)"),
    "no2_aqi_value": ("💛", "NO₂ (Nitrogen Dioxide)"),
    "ozone_aqi_value": ("💜", "O₃ (Ozone)"),
    "co_aqi_value": ("🔥", "CO (Carbon Monoxide)"),
}

proc_available = [c for c in proc_pollutant_info.keys() if c in processed_df.columns]
proc_numeric = [c for c in proc_available if np.issubdtype(processed_df[c].dtype, np.number)]

if not proc_numeric:
    st.error("No numeric *_aqi_value pollutant columns found in the processed dataset.")
    st.stop()

pretty_proc_labels = {
    c: f"{proc_pollutant_info[c][0]} {proc_pollutant_info[c][1]}"
    for c in proc_numeric
}

# -----------------------------------------------------------------------------
# BEFORE / AFTER TOGGLE
# -----------------------------------------------------------------------------
view_mode = st.radio(
    "View Mode:",
    ["Before Processing (Raw AQI)", "After Processing (Normalised Risk Index)"],
    horizontal=True,
)

# =============================================================================
# MODE 1 — BEFORE PROCESSING (RAW AQI)
# =============================================================================
if view_mode.startswith("Before"):

    st.subheader("📌 Regional Overview — Raw AQI Dataset")

    # Aggregate to country-level for raw data
    raw_country = (
        raw_g[["Country", "region"] + raw_numeric]
        .groupby(["Country", "region"], as_index=False)
        .mean()
    )
    raw_country["avg_pollution"] = raw_country[raw_numeric].mean(axis=1)

    regions = sorted(raw_country["region"].unique())

    tab_overview, tab_radar, tab_heatmap, tab_compare = st.tabs(
        ["Overview", "Radar View", "Heatmap", "Region Comparison"]
    )

    # -------------------------------------------------------------------------
    # TAB 1 — OVERVIEW (bar chart + summary)
    # -------------------------------------------------------------------------

    with tab_overview:
        selected_region = st.selectbox("Select region", regions, key="raw_region_overview")
        region_subset = raw_country[raw_country["region"] == selected_region].copy()

        if region_subset.empty:
            st.warning("No data for this region.")
        else:
            left, right = st.columns([1.25, 1])

            with left:
                st.markdown(f"### {selected_region} – Overview (Raw AQI)")
                fig_region = px.bar(
                    region_subset.sort_values("avg_pollution", ascending=False),
                    x="Country",
                    y="avg_pollution",
                    title=f"{selected_region}: Average Pollution (all raw pollutants)",
                    color="Country",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig_region.update_layout(
                    showlegend=False,
                    height=420,
                    margin=dict(l=0, r=0, t=50, b=0),
                    xaxis_title="Country",
                    yaxis_title="Average raw AQI across pollutants",
                )
                st.plotly_chart(fig_region, use_container_width=True)

                with st.expander("📘 Insight — Regional Country Ranking (Raw AQI)"):
                    st.markdown(f"""
- Countries with **taller bars** have **higher average raw pollution** across all tracked pollutants.  
- A steep drop between bars suggests **large inequality in air quality** within **{selected_region}**.  
- Use this chart to quickly spot **regional pollution hotspots** that may need priority intervention.  
                    """)

            with right:
                st.markdown("### Region Summary (Raw)")
                region_mean = region_subset["avg_pollution"].mean()
                best_row = region_subset.loc[region_subset["avg_pollution"].idxmin()]
                worst_row = region_subset.loc[region_subset["avg_pollution"].idxmax()]

                st.metric("Region mean raw AQI", f"{region_mean:.1f}")
                st.metric("Lowest pollution country", f"{best_row['Country']} ({best_row['avg_pollution']:.1f})")
                st.metric("Highest pollution country", f"{worst_row['Country']} ({worst_row['avg_pollution']:.1f})")

                st.markdown("#### Average pollutant levels (region-wide, raw)")
                pollutant_means = region_subset[raw_numeric].mean().reset_index()
                pollutant_means.columns = ["pollutant", "mean_aqi"]

                fig_poll = px.bar(
                    pollutant_means,
                    x="pollutant",
                    y="mean_aqi",
                    title="Average raw AQI per pollutant",
                    color="pollutant",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_poll.update_layout(
                    showlegend=False,
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis_title="Pollutant",
                    yaxis_title="Mean raw AQI",
                )
                st.plotly_chart(fig_poll, use_container_width=True)

                with st.expander("📘 Insight — Pollutant Mix (Raw AQI)"):
                    st.markdown("""
- Taller bars highlight pollutants that **dominate regional air quality**.  
- If one pollutant is much higher than others, it may indicate a **specific emission source** (e.g. traffic, industry, dust).  
- A more balanced profile suggests a **multi-pollutant burden** affecting the region.  
                    """)


    # -------------------------------------------------------------------------
    # TAB 2 — RADAR VIEW (Raw)
    # -------------------------------------------------------------------------

    with tab_radar:
        st.markdown("### Radar View – Region-Level Raw AQI Profile")

        selected_region_radar = st.selectbox(
            "Select region for radar view",
            regions,
            key="raw_region_radar",
        )
        region_subset_radar = raw_country[raw_country["region"] == selected_region_radar]

        if region_subset_radar.empty:
            st.info("No data available for this region.")
        else:
            # Region-level mean per pollutant
            region_means = region_subset_radar[raw_numeric].mean()
            r_vals = [region_means[c] for c in raw_numeric]
            theta_labels = [pretty_raw_labels[c] for c in raw_numeric]

            fig_radar_raw = go.Figure()
            fig_radar_raw.add_trace(
                go.Scatterpolar(
                    r=r_vals,
                    theta=theta_labels,
                    fill="toself",
                    name=selected_region_radar,
                    line=dict(color="#8b5cf6"),
                )
            )
            fig_radar_raw.update_layout(
                title=f"Raw AQI Radar – {selected_region_radar}",
                polar=dict(radialaxis=dict(visible=True)),
                height=480,
            )
            st.plotly_chart(fig_radar_raw, use_container_width=True)

            with st.expander("📘 Insight — Radar Profile (Raw AQI)"):
                st.markdown(f"""
- The shape of the radar plot shows **{selected_region_radar}'s pollution signature**.  
- Long spikes on a few axes indicate **one or two dominant pollutants** driving poor air quality.  
- A wide, rounded shape means **elevated levels across many pollutants**, signalling a **broad air-quality issue** rather than a single source.  
                """)


    # -------------------------------------------------------------------------
    # TAB 3 — HEATMAP (Raw)
    # -------------------------------------------------------------------------

    with tab_heatmap:
        st.markdown("### Heatmap – Country vs Pollutant (Raw AQI)")

        selected_region_heat = st.selectbox(
            "Select region for heatmap",
            regions,
            key="raw_region_heatmap",
        )
        region_subset_heat = raw_country[raw_country["region"] == selected_region_heat]

        if region_subset_heat.empty:
            st.info("No data available for this region.")
        else:
            heat_df = region_subset_heat.set_index("Country")[raw_numeric]
            fig_heat_raw = px.imshow(
                heat_df,
                labels=dict(x="Pollutant", y="Country", color="Raw AQI"),
                aspect="auto",
                color_continuous_scale="RdYlGn_r",
            )
            fig_heat_raw.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=40, b=0),
                title=f"Raw AQI Heatmap – {selected_region_heat}",
            )
            st.plotly_chart(fig_heat_raw, use_container_width=True)

            with st.expander("📘 Insight — Regional Heatmap (Raw AQI)"):
                st.markdown(f"""
- Darker cells show **higher raw AQI** for a specific pollutant–country pair.  
- Countries with many dark cells are **multi-pollutant hotspots** within **{selected_region_heat}**.  
- Columns that are mostly dark indicate pollutants that are **problematic across most countries in the region**.  
                """)


    # -------------------------------------------------------------------------
    # TAB 4 — REGION COMPARISON (Side-by-Side, Raw)
    # -------------------------------------------------------------------------
    with tab_compare:
        st.markdown("### Side-by-Side Region Comparison (Raw AQI)")

        colA, colB = st.columns(2)
        with colA:
            region_a = st.selectbox("Select Region A", regions, key="raw_region_a")
        with colB:
            region_b = st.selectbox("Select Region B", regions, key="raw_region_b")

        if region_a == region_b:
            st.warning("⚠ Please select two different regions for comparison.")
        else:
            # Region-level summary (mean over countries within that region)
            region_group = raw_country.groupby("region")[raw_numeric + ["avg_pollution"]].mean()

            if region_a not in region_group.index or region_b not in region_group.index:
                st.error("One of the selected regions has no data.")
            else:
                a_vals = region_group.loc[region_a, raw_numeric].tolist()
                b_vals = region_group.loc[region_b, raw_numeric].tolist()
                labels = [pretty_raw_labels[c] for c in raw_numeric]

                avg_a = region_group.loc[region_a, "avg_pollution"]
                avg_b = region_group.loc[region_b, "avg_pollution"]

                left, right = st.columns(2)

                with left:
                    st.markdown(
                        f"""
                        <div style="padding:18px;border-radius:12px;border:1px solid #E5E7EB;background:white;">
                            <div style="font-size:1.1rem;font-weight:600;color:#1F2937;">{region_a}</div>
                            <div style="font-size:1.8rem;font-weight:700;color:#4F46E5;">{avg_a:.1f}</div>
                            <div style="font-size:0.9rem;color:#6B7280;">Mean raw AQI (all pollutants)</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("#### Pollutant Breakdown (Raw)")
                    st.markdown(mini_bar_chart(a_vals, labels), unsafe_allow_html=True)

                with right:
                    st.markdown(
                        f"""
                        <div style="padding:18px;border-radius:12px;border:1px solid #E5E7EB;background:white;">
                            <div style="font-size:1.1rem;font-weight:600;color:#1F2937;">{region_b}</div>
                            <div style="font-size:1.8rem;font-weight:700;color:#4F46E5;">{avg_b:.1f}</div>
                            <div style="font-size:0.9rem;color:#6B7280;">Mean raw AQI (all pollutants)</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("#### Pollutant Breakdown (Raw)")
                    st.markdown(mini_bar_chart(b_vals, labels), unsafe_allow_html=True)

                st.markdown("### 🔍 Interpretation")
                higher = region_a if avg_a > avg_b else region_b
                gap = abs(avg_a - avg_b)
                st.markdown(
                    f"""
                    - **Higher overall raw pollution:** `{higher}`  
                    - **Gap in mean raw AQI:** `{gap:.1f}` units  
                    """
                )

    st.info(
        "You are currently viewing **raw AQI values by region and country**.\n\n"
        "Switch to **After Processing (Normalised Risk Index)** above to explore the "
        "composite risk index and normalised regional comparisons."
    )

    st.stop()


# =============================================================================
# MODE 2 — AFTER PROCESSING (NORMALISED RISK INDEX)
# =============================================================================

st.subheader("📌 Regional Overview — Normalised Risk Index (Processed Dataset)")

# Country-level aggregation from processed dataset
proc_country = (
    processed_df[["country", "region"] + proc_numeric]
    .groupby(["country", "region"], as_index=False)
    .mean()
)

# Build normalised per-pollutant scores (0–1) across all countries
scaled = {}
for col in proc_numeric:
    s = proc_country[col].astype(float)
    lo, hi = s.min(), s.max()
    scaled[col] = (s - lo) / (hi - lo) if hi > lo else np.zeros_like(s)

scaled_df = pd.DataFrame(scaled)
proc_country["risk_index"] = scaled_df.mean(axis=1)
proc_country["risk_percentile"] = proc_country["risk_index"].rank(pct=True)

# Risk levels by quartile
q1, q2, q3 = np.percentile(proc_country["risk_index"], [25, 50, 75])

def classify_risk(x):
    if x <= q1:
        return "Low"
    if x <= q2:
        return "Moderate"
    if x <= q3:
        return "High"
    return "Very High"

proc_country["risk_level"] = proc_country["risk_index"].apply(classify_risk)

regions_proc = sorted(proc_country["region"].unique())

tab_overview_p, tab_compare_p, tab_heatmap_p = st.tabs(
    ["Overview", "Region Comparison", "Heatmap"]
)

# -------------------------------------------------------------------------
# TAB A — OVERVIEW (Processed)
# -------------------------------------------------------------------------

with tab_overview_p:
    selected_region_p = st.selectbox(
        "Select region",
        regions_proc,
        key="proc_region_overview",
    )
    region_proc = proc_country[proc_country["region"] == selected_region_p]

    if region_proc.empty:
        st.warning("No data for this region in processed dataset.")
    else:
        left, right = st.columns([1.25, 1])

        with left:
            st.markdown(f"### {selected_region_p} – Country Risk (0–1 Index)")
            fig_proc_region = px.bar(
                region_proc.sort_values("risk_index", ascending=False),
                x="country",
                y="risk_index",
                color="risk_index",
                color_continuous_scale="Reds",
                title=f"{selected_region_p}: Composite Risk Index by Country",
            )
            fig_proc_region.update_layout(
                height=430,
                margin=dict(l=0, r=0, t=50, b=0),
                xaxis_title="Country",
                yaxis_title="Risk Index (0–1)",
            )
            st.plotly_chart(fig_proc_region, use_container_width=True)

            with st.expander("📘 Insight — Regional Risk Ranking (Processed)"):
                st.markdown(f"""
- Countries with higher bars have a **higher composite risk index**, meaning **worse air quality relative to others** in this dataset.  
- A big gap between the top and bottom bars suggests **unequal environmental health risk** inside **{selected_region_p}**.  
- This chart summarises multiple pollutants into **one comparable risk score per country**.  
                """)

        with right:
            st.markdown("### Region Risk Summary")
            region_mean = region_proc["risk_index"].mean()
            best_row = region_proc.loc[region_proc["risk_index"].idxmin()]
            worst_row = region_proc.loc[region_proc["risk_index"].idxmax()]

            st.metric("Mean risk index", f"{region_mean:.2f}")
            st.metric("Lowest-risk country", f"{best_row['country']} ({best_row['risk_index']:.2f})")
            st.metric("Highest-risk country", f"{worst_row['country']} ({worst_row['risk_index']:.2f})")

            st.markdown("#### Average pollutant levels (processed, not normalised)")
            pollutant_means_p = region_proc[proc_numeric].mean().reset_index()
            pollutant_means_p.columns = ["pollutant", "mean_aqi"]

            fig_poll_p = px.bar(
                pollutant_means_p,
                x="pollutant",
                y="mean_aqi",
                title="Average processed AQI per pollutant",
                color="pollutant",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_poll_p.update_layout(
                showlegend=False,
                height=300,
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Pollutant",
                yaxis_title="Mean AQI (processed)",
            )
            st.plotly_chart(fig_poll_p, use_container_width=True)

            with st.expander("📘 Insight — Pollutant Mix (Processed)"):
                st.markdown("""
- Shows which pollutants are **driving the risk index** in this region after processing and cleaning.  
- A single dominant bar suggests **one main pollutant** (e.g. PM₂.₅) is the key concern.  
- A flatter profile indicates a **multi-pollutant burden** that may require more holistic policy responses.  
                """)


# -------------------------------------------------------------------------
# TAB B — REGION COMPARISON (Side-by-Side, Processed)
# -------------------------------------------------------------------------

with tab_compare_p:
    st.markdown("### Side-by-Side Region Comparison (Normalised Risk Index)")

    colA_p, colB_p = st.columns(2)
    with colA_p:
        region_a_p = st.selectbox("Select Region A", regions_proc, key="proc_region_a")
    with colB_p:
        region_b_p = st.selectbox("Select Region B", regions_proc, key="proc_region_b")

    if region_a_p == region_b_p:
        st.warning("⚠ Please select two different regions for comparison.")
    else:
        # Region-level mean over countries
        region_group_p = proc_country.groupby("region")[proc_numeric + ["risk_index"]].mean()

        if region_a_p not in region_group_p.index or region_b_p not in region_group_p.index:
            st.error("One of the selected regions has no data in processed dataset.")
        else:
            a_vals_p = region_group_p.loc[region_a_p, proc_numeric].tolist()
            b_vals_p = region_group_p.loc[region_b_p, proc_numeric].tolist()
            labels_p = [pretty_proc_labels[c] for c in proc_numeric]

            avg_a_p = region_group_p.loc[region_a_p, "risk_index"]
            avg_b_p = region_group_p.loc[region_b_p, "risk_index"]

            left_p, right_p = st.columns(2)

            with left_p:
                st.markdown(
                    f"""
                    <div style="padding:18px;border-radius:12px;border:1px solid #E5E7EB;background:white;">
                        <div style="font-size:1.1rem;font-weight:600;color:#1F2937;">{region_a_p}</div>
                        <div style="font-size:1.8rem;font-weight:700;color:#4F46E5;">{avg_a_p:.2f}</div>
                        <div style="font-size:0.9rem;color:#6B7280;">Mean composite risk index (0–1)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("#### Pollutant Breakdown (Processed)")
                st.markdown(mini_bar_chart(a_vals_p, labels_p), unsafe_allow_html=True)

            with right_p:
                st.markdown(
                    f"""
                    <div style="padding:18px;border-radius:12px;border:1px solid #E5E7EB;background:white;">
                        <div style="font-size:1.1rem;font-weight:600;color:#1F2937;">{region_b_p}</div>
                        <div style="font-size:1.8rem;font-weight:700;color:#4F46E5;">{avg_b_p:.2f}</div>
                        <div style="font-size:0.9rem;color:#6B7280;">Mean composite risk index (0–1)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("#### Pollutant Breakdown (Processed)")
                st.markdown(mini_bar_chart(b_vals_p, labels_p), unsafe_allow_html=True)

            st.markdown("### 🔍 Interpretation")
            higher_p = region_a_p if avg_a_p > avg_b_p else region_b_p
            gap_p = abs(avg_a_p - avg_b_p)
            st.markdown(
                f"""
                - **Higher overall risk index:** `{higher_p}`  
                - **Risk index gap:** `{gap_p:.2f}` (0 = identical, 1 = max possible gap in this dataset)  
                """
            )



# -------------------------------------------------------------------------
# TAB C — HEATMAP (Processed)
# -------------------------------------------------------------------------
with tab_heatmap_p:
    st.markdown("### Heatmap – Country vs Pollutant (Processed Dataset)")

    selected_region_heat_p = st.selectbox(
        "Select region for heatmap",
        regions_proc,
        key="proc_region_heatmap",
    )
    region_proc_heat = proc_country[proc_country["region"] == selected_region_heat_p]

    if region_proc_heat.empty:
        st.info("No data available for this region in processed dataset.")
    else:
        heat_df_p = region_proc_heat.set_index("country")[proc_numeric]
        fig_heat_p = px.imshow(
            heat_df_p,
            labels=dict(x="Pollutant", y="Country", color="AQI (processed)"),
            aspect="auto",
            color_continuous_scale="Reds",
        )
        fig_heat_p.update_layout(
            height=500,
            margin=dict(l=0, r=0, t=40, b=0),
            title=f"Processed AQI Heatmap – {selected_region_heat_p}",
        )
        st.plotly_chart(fig_heat_p, use_container_width=True)

        with st.expander("📘 Insight — Processed Regional Heatmap"):
            st.markdown(f"""
- Darker cells show **higher processed AQI values**, after cleaning and standardisation.  
- Countries with many dark cells are **high-risk across several pollutants** within **{selected_region_heat_p}**.  
- Pollutants forming consistently dark columns are **region-wide challenges** that may need **coordinated policy action**.  
            """)


# -------------------------------------------------------------------------
# TAB C — HEATMAP (Processed)
# -------------------------------------------------------------------------
with tab_heatmap_p:
    st.markdown("### Heatmap – Country vs Pollutant (Processed Dataset)")

    selected_region_heat_p = st.selectbox(
        "Select region for heatmap",
        regions_proc,
        key="proc_region_heatmap",
    )
    region_proc_heat = proc_country[proc_country["region"] == selected_region_heat_p]

    if region_proc_heat.empty:
        st.info("No data available for this region in processed dataset.")
    else:
        heat_df_p = region_proc_heat.set_index("country")[proc_numeric]
        fig_heat_p = px.imshow(
            heat_df_p,
            labels=dict(x="Pollutant", y="Country", color="AQI (processed)"),
            aspect="auto",
            color_continuous_scale="Reds",
        )
        fig_heat_p.update_layout(
            height=500,
            margin=dict(l=0, r=0, t=40, b=0),
            title=f"Processed AQI Heatmap – {selected_region_heat_p}",
        )
        st.plotly_chart(fig_heat_p, use_container_width=True)



