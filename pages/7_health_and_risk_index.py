import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from utils.data_loader import load_raw_dataset, load_processed_dataset
from utils.ui import header

import streamlit.components.v1 as components


st.set_page_config(layout="wide")

# ------------------------------------------------------------------------------------
# Mini Bar UI
# ------------------------------------------------------------------------------------

# def mini_bar_chart(values, labels, max_width=220, height=10):
#     html = "<div>"
#     max_val = max(values) if max(values) else 1

#     colors = ["#8B5CF6", "#0EA5E9", "#F59E0B", "#EF4444", "#10B981"]

#     for i, v in enumerate(values):
#         width = int((v / max_val) * max_width)
#         color = colors[i % len(colors)]

#         html += (
#             "<div style='margin-bottom:14px;'>"
#             f"<div style='font-size:0.85rem;color:#374151;font-weight:600;margin-bottom:4px;'>{labels[i]}</div>"
#             f"<div style='background:#E5E7EB;border-radius:6px;height:{height}px;width:{max_width}px;'>"
#             f"<div style='background:{color};width:{width}px;height:{height}px;border-radius:6px;'></div>"
#             "</div>"
#             f"<div style='font-size:0.75rem;color:#4B5563;margin-top:3px;text-align:right;width:{max_width}px;'>{v:.2f}</div>"
#             "</div>"
#         )

#     html += "</div>"
#     return html

#_________________

def mini_bar_chart(values, labels, max_width=220, height=10):
    max_val = max(values) if max(values) else 1

    gradients = [
        "linear-gradient(90deg, #c084fc, #8b5cf6)",   # PM2.5   purple gradient
        "linear-gradient(90deg, #67e8f9, #0ea5e9)",   # NO2     blue gradient
        "linear-gradient(90deg, #fcd34d, #f59e0b)",   # Ozone   orange gradient
        "linear-gradient(90deg, #f9a8d4, #ef4444)",   # CO      red gradient
        "linear-gradient(90deg, #6ee7b7, #10b981)"    # fallback
    ]

    html = "<div style='margin-top:10px;'>"

    for i, v in enumerate(values):
        width_pct = (v / max_val) * 100
        bar_color = gradients[i % len(gradients)]

        html += (
            "<div style='margin-bottom:16px;'>"

                # LABEL
                f"<div style='font-size:0.85rem;color:#374151;font-weight:600;margin-bottom:6px;'>{labels[i]}</div>"

                # OUTER BAR
                f"<div style='background:#E5E7EB;border-radius:10px;height:{height}px;width:{max_width}px;overflow:hidden;'>"
                
                    # INNER BAR WITH ANIMATION + GRADIENT
                    f"<div style='background:{bar_color};"
                    f"height:{height}px;border-radius:10px;"
                    f"width:0%;"
                    f"animation:grow{i} 1.1s ease-out forwards;'>"
                    "</div>"
                "</div>"

                # VALUE
                f"<div style='font-size:0.75rem;color:#4B5563;margin-top:4px;"
                f"text-align:right;width:{max_width}px;'>{v:.2f}</div>"

            "</div>"

            # ✨ Keyframe animations for each bar (prevents conflict)
            f"<style>@keyframes grow{i} {{ from {{ width:0%; }} to {{ width:{width_pct}%; }} }}</style>"
        )

    html += "</div>"
    return html


# ------------------------------------------------------------------------------------
# Load Data
# ------------------------------------------------------------------------------------
raw_g, raw_p = load_raw_dataset()
df = load_processed_dataset()  # AFTER-processing dataset

header(
    "⚠ Health & Pollution Risk Index",
    "Compare raw AQI values vs a weighted health risk index, with WHO health-impact scoring."
)

if df is None or df.empty:
    st.error("Processed dataset could not be loaded or is empty.")
    st.stop()

# Ensure country column exists in processed data
if "country" not in df.columns:
    # try fallback from raw
    if raw_g is not None and "Country" in raw_g.columns:
        df["country"] = raw_g["Country"]
    else:
        st.error("Processed dataset is missing 'country' column.")
        st.stop()

# ------------------------------------------------------------------------------------
# View mode: Before vs After
# ------------------------------------------------------------------------------------
view_mode = st.radio(
    "Select data view:",
    [
        "Before Processing: Raw AQI & WHO Health Impact",
        "After Processing: Risk Index & Advanced Analytics",
    ],
    horizontal=True,
)

# ====================================================================================
# 🟥 MODE 1 — BEFORE PROCESSING: RAW AQI + WHO HEALTH IMPACT
# ====================================================================================
if view_mode.startswith("Before"):

    if raw_g is None or raw_g.empty:
        st.error("Raw global air pollution dataset could not be loaded.")
        st.stop()

    st.subheader("📄 Raw Global Air Pollution Dataset (Before Processing)")
    st.dataframe(raw_g, use_container_width=True)

    if raw_p is not None and not raw_p.empty:
        st.subheader("🌍 Raw PM2.5 WHO Dataset")
        st.dataframe(raw_p, use_container_width=True)

    st.markdown("---")

    # Raw pollutant columns & WHO thresholds (AQI-approx equivalents)
    raw_pollutant_info = {
        "PM2.5 AQI Value": ("🟤", "PM2.5 (Fine Particles)", 25),
        "PM10 AQI Value": ("🟠", "PM10 (Coarse Particles)", 50),
        "NO2 AQI Value": ("💛", "NO₂ (Nitrogen Dioxide)", 33),
        "Ozone AQI Value": ("💜", "O₃ (Ozone)", 70),
        "CO AQI Value": ("🔥", "CO (Carbon Monoxide)", 50),
    }

    available_raw_cols = [c for c in raw_pollutant_info.keys() if c in raw_g.columns]

    if not available_raw_cols:
        st.error("No raw AQI pollutant columns found in the raw dataset.")
        st.stop()

    pretty_raw_labels = {
        c: f"{raw_pollutant_info[c][0]} {raw_pollutant_info[c][1]}"
        for c in available_raw_cols
    }

    st.markdown("### 1. Raw Pollutant Distribution (Before Processing)")
    selected_raw = st.selectbox(
        "Select raw AQI pollutant:",
        available_raw_cols,
        format_func=lambda col: pretty_raw_labels[col],
        key="raw_pollutant_choice",
    )

    # Aggregate by country
    raw_agg = (
        raw_g.groupby("Country", as_index=False)[available_raw_cols].mean()
    )

    # Simple bar chart for chosen pollutant
    top_raw = raw_agg.sort_values(selected_raw, ascending=False).head(30)

    fig_raw = px.bar(
        top_raw,
        x="Country",
        y=selected_raw,
        title=f"Top 30 Countries by {pretty_raw_labels[selected_raw]} (Raw AQI)",
        labels={selected_raw: "AQI (Raw)"},
    )
    fig_raw.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
    fig_raw.update_xaxes(tickangle=45)
    st.plotly_chart(fig_raw, use_container_width=True)

    with st.expander("Show raw aggregated table per country"):
        st.dataframe(raw_agg, use_container_width=True)

    # -------------------------------------------------------------------------
    # WHO Health-Impact Scoring on RAW AQI
    # -------------------------------------------------------------------------
    st.markdown("### 2. WHO Health-Impact Scoring (Raw AQI)")

    # Compute WHO impact scores per pollutant
    who_impact_raw = {}
    for col in available_raw_cols:
        (_, _, threshold) = raw_pollutant_info[col]
        who_impact_raw[col] = raw_agg[col] / threshold

    who_impact_df = pd.DataFrame(who_impact_raw)
    # Equal weights across available pollutants
    who_raw_index = who_impact_df.mean(axis=1)

    raw_agg["who_health_index_raw"] = who_raw_index

    def classify_health(idx):
        if idx < 1:
            return "Safe"
        if idx < 2:
            return "Moderate Risk"
        if idx < 3:
            return "High Risk"
        return "Severe Health Risk"

    raw_agg["who_health_level_raw"] = raw_agg["who_health_index_raw"].apply(classify_health)

    # WHO Impact Map (Raw)
    who_fig_raw = px.choropleth(
        raw_agg,
        locations="Country",
        locationmode="country names",
        color="who_health_index_raw",
        color_continuous_scale=["green", "yellow", "orange", "red", "darkred"],
        title="WHO Health Impact Index (Raw AQI, Before Processing)",
    )
    who_fig_raw.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(who_fig_raw, use_container_width=True)

    # Top WHO health-risk countries (Raw)
    st.markdown("#### 🚨 Highest WHO Health-Risk Countries (Raw AQI)")
    top_who_raw = raw_agg.sort_values("who_health_index_raw", ascending=False).head(15)
    st.dataframe(
        top_who_raw[
            ["Country", "who_health_index_raw", "who_health_level_raw"] + available_raw_cols
        ],
        use_container_width=True,
    )

    # Insights
    worst_raw = top_who_raw.iloc[0]
    best_raw = raw_agg.loc[raw_agg["who_health_index_raw"].idxmin()]

    st.markdown(
        f"""
**WHO Health Insights (Before Processing)**  
- 🚨 Highest WHO health risk (raw AQI): `{worst_raw['Country']}` with index `{worst_raw['who_health_index_raw']:.2f}`  
- 🌱 Lowest WHO health risk (raw AQI): `{best_raw['Country']}` with index `{best_raw['who_health_index_raw']:.2f}`  
- ℹ Raw AQI values are **not yet normalised or combined** into a single risk index.  
"""
    )

    st.info(
        "You are currently viewing **raw AQI values and WHO-based health impact (before any processing)**.\n\n"
        "Switch to **'After Processing: Risk Index & Advanced Analytics'** above to see the "
        "weighted, normalised risk index, risk levels, world map, comparisons, and rankings."
    )

    # Stop here so AFTER-processing analytics don't run
    st.stop()


# ====================================================================================
# 🟩 MODE 2 — AFTER PROCESSING: RISK INDEX + WHO + ADVANCED ANALYTICS
# ====================================================================================

st.markdown("### 1. Configure Risk Score (Processed Dataset)")

# Pollutant metadata for processed dataset
pollutant_info = {
    "pm25_aqi_value": ("🟤", "PM2.5 (Fine Particles)"),
    "pm10_aqi_value": ("🟠", "PM10 (Coarse Particles)"),
    "no2_aqi_value": ("💛", "NO₂ (Nitrogen Dioxide)"),
    "ozone_aqi_value": ("💜", "O₃ (Ozone)"),
    "co_aqi_value": ("🔥", "CO (Carbon Monoxide)"),
}

pollutant_options = [c for c in pollutant_info.keys() if c in df.columns]

if not pollutant_options:
    st.error("No pollutant *_aqi_value columns found in the processed dataset.")
    st.stop()

pretty_labels = {
    c: f"{pollutant_info[c][0]} {pollutant_info[c][1]}"
    for c in pollutant_options
}

selected_pollutants = st.multiselect(
    "Pollutants to include in the composite risk index:",
    pollutant_options,
    default=pollutant_options,
    format_func=lambda col: pretty_labels[col],
)

if not selected_pollutants:
    st.warning("⚠ Please select at least one pollutant.")
    st.stop()

# Weight presets
st.markdown("#### 🔧 Select a preset (optional)")

preset = st.radio(
    "",
    ["Beginner Mode (equal weights)", "WHO Health Severity", "EPA Danger Scale", "Expert Mode"],
)

equal_weights = {c: 1 / len(selected_pollutants) for c in selected_pollutants}

who_weights = {
    "pm25_aqi_value": 0.40,
    "no2_aqi_value": 0.25,
    "ozone_aqi_value": 0.20,
    "pm10_aqi_value": 0.10,
    "co_aqi_value": 0.05,
}

epa_weights = {
    "pm25_aqi_value": 0.35,
    "pm10_aqi_value": 0.20,
    "no2_aqi_value": 0.20,
    "ozone_aqi_value": 0.15,
    "co_aqi_value": 0.10,
}

if preset == "Beginner Mode (equal weights)":
    norm_weights = equal_weights

elif preset == "WHO Health Severity":
    total = sum(who_weights.get(c, 0) for c in selected_pollutants)
    norm_weights = {c: who_weights[c] / total for c in selected_pollutants} if total > 0 else equal_weights

elif preset == "EPA Danger Scale":
    total = sum(epa_weights.get(c, 0) for c in selected_pollutants)
    norm_weights = {c: epa_weights[c] / total for c in selected_pollutants} if total > 0 else equal_weights

else:
    st.markdown("#### ⚙ Expert Mode – Fine Tune Pollutant Weights")
    weights, total_w = {}, 0
    for col in selected_pollutants:
        w = st.slider(f"Weight for {pretty_labels[col]}", 0.0, 10.0, 1.0)
        weights[col] = w
        total_w += w
    norm_weights = equal_weights if total_w == 0 else {c: weights[c] / total_w for c in selected_pollutants}

# ------------------------------------------------------------------------------------
# 2. Compute Risk Index (After Processing)
# ------------------------------------------------------------------------------------
agg_df = df[["country"] + selected_pollutants].groupby("country").mean().reset_index()

scaled = {}
for col in selected_pollutants:
    series = agg_df[col].astype(float)
    lo, hi = series.min(), series.max()
    scaled[col] = (series - lo) / (hi - lo) if hi > lo else np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)
agg_df["risk_index"] = sum(scaled_df[c] * norm_weights[c] for c in selected_pollutants)

q1, q2, q3 = np.percentile(agg_df["risk_index"], [25, 50, 75])

def classify_risk(r):
    if r <= q1:
        return "Low"
    if r <= q2:
        return "Moderate"
    if r <= q3:
        return "High"
    return "Very High"

agg_df["risk_level"] = agg_df["risk_index"].apply(classify_risk)

# ====================================================================================
# 3. WHO Health-Impact Scoring (Processed AQI)
# ====================================================================================
st.markdown("### 2. WHO Health-Impact Scoring (Processed AQI)")

who_thresholds_proc = {
    "pm25_aqi_value": 25,
    "pm10_aqi_value": 50,
    "no2_aqi_value": 33,
    "ozone_aqi_value": 70,
    "co_aqi_value": 50,
}

impact_scores = {}
for col in selected_pollutants:
    if col in agg_df.columns:
        threshold = who_thresholds_proc.get(col, None)
        if threshold:
            impact_scores[col] = agg_df[col] / threshold
        else:
            impact_scores[col] = agg_df[col] * 0  # fallback

impact_df = pd.DataFrame(impact_scores)
agg_df["who_health_index"] = impact_df.mean(axis=1)

def classify_health(idx):
    if idx < 1:
        return "Safe"
    if idx < 2:
        return "Moderate Risk"
    if idx < 3:
        return "High Risk"
    return "Severe Health Risk"

agg_df["who_health_level"] = agg_df["who_health_index"].apply(classify_health)

who_fig = px.choropleth(
    agg_df,
    locations="country",
    locationmode="country names",
    color="who_health_index",
    color_continuous_scale=["green", "yellow", "orange", "red", "darkred"],
    title="WHO Health Impact Index (Processed AQI, After Processing)",
)
who_fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(who_fig, use_container_width=True)

# ====================================================================================
# 4. Risk-Level Explorer
# ====================================================================================
st.markdown("### 3. Risk-Level Explorer (Composite Risk Index)")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Very High", "High", "Moderate", "Low", "All"])

for tab, level in zip([tab1, tab2, tab3, tab4], ["Very High", "High", "Moderate", "Low"]):
    with tab:
        sub = agg_df[agg_df["risk_level"] == level]
        st.subheader(f"{level} Risk Countries")
        if sub.empty:
            st.info("No countries in this category.")
        else:
            fig = px.bar(
                sub.sort_values("risk_index", ascending=False),
                x="country",
                y="risk_index",
                title=f"{level} Risk Level",
                color_discrete_sequence=["#ef4444" if level == "Very High" else "#f97316"],
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(sub)

with tab5:
    st.subheader("All Countries")
    st.dataframe(agg_df)

# ====================================================================================
# 5. World Risk Map (Composite Index)
# ====================================================================================
st.markdown("### 4. World Risk Map (Composite Risk Index)")

map_fig = px.choropleth(
    agg_df,
    locations="country",
    locationmode="country names",
    color="risk_index",
    color_continuous_scale=["green", "yellow", "orange", "red"],
    title="Global Pollution Risk Map (Composite Index)",
)
map_fig.update_layout(height=500)
st.plotly_chart(map_fig, use_container_width=True)

# ====================================================================================
# 6. Auto Insights
# ====================================================================================
st.markdown("### 5. Auto Insights")

avg = agg_df["risk_index"].mean()
worst = agg_df.loc[agg_df["risk_index"].idxmax()]
best = agg_df.loc[agg_df["risk_index"].idxmin()]

st.markdown(
    f"""
- 🌍 **Global average composite risk index:** `{avg:.2f}`  
- 🚨 **Highest-risk country (composite):** `{worst['country']}` with score `{worst['risk_index']:.2f}`  
- 🌱 **Lowest-risk country (composite):** `{best['country']}` with score `{best['risk_index']:.2f}`  
- 📊 **Most influential pollutant (weight):** **{max(norm_weights, key=norm_weights.get)}**  
"""
)

# ----------------------------------------------
# 6. Compare Two Countries (Side-by-Side)
# ----------------------------------------------
# st.markdown("### 6. Compare Two Countries (Side-by-Side Analysis)")

# colA, colB = st.columns(2)

# with colA:
#     country_a = st.selectbox(
#         "Select Country A",
#         agg_df["country"].sort_values().unique(),
#         key="country_a",
#     )

# with colB:
#     country_b = st.selectbox(
#         "Select Country B",
#         agg_df["country"].sort_values().unique(),
#         key="country_b",
#     )

# if country_a == country_b:
#     st.warning("⚠ Please choose two different countries for comparison.")
# else:
#     import streamlit.components.v1 as components

#     # Fetch rows
#     a_row = agg_df[agg_df["country"] == country_a].iloc[0]
#     b_row = agg_df[agg_df["country"] == country_b].iloc[0]

#     # Get pollutant labels + values
#     labels = [pollutant_info[c][1] for c in selected_pollutants]
#     a_vals = [float(a_row[c]) for c in selected_pollutants]
#     b_vals = [float(b_row[c]) for c in selected_pollutants]

#     # --- 2 Internal side-by-side columns ---
#     cA, cB = st.columns(2)

#     # --------------------------------------
#     # LEFT COUNTRY CARD
#     # --------------------------------------
#     with cA:
#         st.markdown(
#             f"""
#             <div class="kpi-card">
#                 <div class="kpi-label">{country_a}</div>
#                 <div class="kpi-value">{a_row['risk_index']:.2f}</div>
#                 <div class="kpi-sub">Risk Level: {a_row['risk_level']}</div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#         st.markdown("#### Pollutant Breakdown")
#         components.html(mini_bar_chart(a_vals, labels), height=240)

#     # --------------------------------------
#     # RIGHT COUNTRY CARD
#     # --------------------------------------
#     with cB:
#         st.markdown(
#             f"""
#             <div class="kpi-card">
#                 <div class="kpi-label">{country_b}</div>
#                 <div class="kpi-value">{b_row['risk_index']:.2f}</div>
#                 <div class="kpi-sub">Risk Level: {b_row['risk_level']}</div>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )

#         st.markdown("#### Pollutant Breakdown")
#         components.html(mini_bar_chart(b_vals, labels), height=240)

#     # --------------------------------------
#     # INTERPRETATION
#     # --------------------------------------
#     st.markdown("### 🔍 Interpretation")

#     diff = a_row["risk_index"] - b_row["risk_index"]
#     higher = country_a if diff > 0 else country_b
#     gap = abs(diff)

#     key_pollutant = labels[
#         np.argmax(np.abs(np.array(a_vals) - np.array(b_vals)))
#     ]

#     st.markdown(
#         f"""
#         **Comparison Summary**
#         - **Higher composite risk:** `{higher}`  
#         - **Risk gap:** `{gap:.2f}`  
#         - **Key differing pollutant:** `{key_pollutant}`  
#         """
#     )

#     comp_df = pd.DataFrame(
#         {
#             "Pollutant": labels,
#             country_a: a_vals,
#             country_b: b_vals,
#             "Difference": np.array(a_vals) - np.array(b_vals),
#         }
#     )

#     st.dataframe(
#         comp_df.style.format(
#             {country_a: "{:.2f}", country_b: "{:.2f}", "Difference": "{:.2f}"}
#         )
#     )

#_______________

st.markdown("## 6. Compare Two Countries (Side-by-Side Analysis)")

colA, colB = st.columns(2)

# Country Selectors
with colA:
    country_a = st.selectbox(
        "Select Country A",
        agg_df["country"].sort_values().unique(),
        key="country_a",
    )

with colB:
    country_b = st.selectbox(
        "Select Country B",
        agg_df["country"].sort_values().unique(),
        key="country_b",
    )

# If same country → warn
if country_a == country_b:
    st.warning("⚠ Please choose two different countries for comparison.")
    st.stop()

# Extract rows
a_row = agg_df[agg_df["country"] == country_a].iloc[0]
b_row = agg_df[agg_df["country"] == country_b].iloc[0]

labels = [pollutant_info[c][1] for c in selected_pollutants]
a_vals = [float(a_row[c]) for c in selected_pollutants]
b_vals = [float(b_row[c]) for c in selected_pollutants]

# UI Layout – Beautiful clean card design
left, right = st.columns(2)

# ---------------- CARD A ----------------
with left:
    st.markdown(
        f"""
        <div style="padding:20px;border-radius:12px;border:1px solid #E5E7EB;background:white;">
            <div style="font-size:1.3rem;font-weight:600;color:#1F2937;">{country_a}</div>
            <div style="font-size:2rem;font-weight:700;color:#4F46E5;">{a_row['risk_index']:.2f}</div>
            <div style="font-size:1rem;color:#6B7280;">Risk Level: <b>{a_row['risk_level']}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Pollutant Breakdown")
    st.markdown(mini_bar_chart(a_vals, labels), unsafe_allow_html=True)

# ---------------- CARD B ----------------
with right:
    st.markdown(
        f"""
        <div style="padding:20px;border-radius:12px;border:1px solid #E5E7EB;background:white;">
            <div style="font-size:1.3rem;font-weight:600;color:#1F2937;">{country_b}</div>
            <div style="font-size:2rem;font-weight:700;color:#4F46E5;">{b_row['risk_index']:.2f}</div>
            <div style="font-size:1rem;color:#6B7280;">Risk Level: <b>{b_row['risk_level']}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Pollutant Breakdown")
    st.markdown(mini_bar_chart(b_vals, labels), unsafe_allow_html=True)


# ---------------- INTERPRETATION ----------------
st.markdown("### 🔍 Interpretation")

diff = a_row["risk_index"] - b_row["risk_index"]
higher = country_a if diff > 0 else country_b
gap = abs(diff)

key_pollutant = labels[
    np.argmax(np.abs(np.array(a_vals) - np.array(b_vals)))
]

st.markdown(
    f"""
    **Comparison Summary**
    - **Higher composite risk:** `{higher}`
    - **Risk gap:** `{gap:.2f}`
    - **Key differing pollutant:** `{key_pollutant}`
    """
)

# Detailed Table
comp_df = pd.DataFrame(
    {
        "Pollutant": labels,
        country_a: a_vals,
        country_b: b_vals,
        "Difference": np.array(a_vals) - np.array(b_vals),
    }
)

st.dataframe(
    comp_df.style.format(
        {country_a: "{:.2f}", country_b: "{:.2f}", "Difference": "{:.2f}"}
    )
)


# ====================================================================================
# 8. Country Risk Ranking
# ====================================================================================
st.markdown("### 7. Country Risk Ranking")

ranking_mode = st.radio(
    "Select ranking type:",
    ["Highest Risk", "Lowest Risk", "Average", "Custom Percentile"],
    horizontal=True,
)

pollutant_choices = {
    "Overall Risk Index": "risk_index",
    "PM₂.₅ (Fine Particles)": "pm25_aqi_value",
    "NO₂ (Nitrogen Dioxide)": "no2_aqi_value",
    "O₃ (Ozone)": "ozone_aqi_value",
    "CO (Carbon Monoxide)": "co_aqi_value",
    "PM₁₀ (Coarse Particles)": "pm10_aqi_value",
}

pollutant_selected = st.selectbox(
    "Pollutant used for ranking:",
    list(pollutant_choices.keys()),
)

metric_col = pollutant_choices[pollutant_selected]

if metric_col != "risk_index":
    if metric_col not in agg_df.columns:
        st.error(f"Column '{metric_col}' not found in dataset.")
        st.stop()
    col_vals = agg_df[metric_col].astype(float)
    lo, hi = col_vals.min(), col_vals.max()
    agg_df["metric_scaled"] = (col_vals - lo) / (hi - lo) if hi > lo else 0
else:
    agg_df["metric_scaled"] = agg_df["risk_index"]

if ranking_mode == "Highest Risk":
    filtered = agg_df.sort_values("metric_scaled", ascending=False)
elif ranking_mode == "Lowest Risk":
    filtered = agg_df.sort_values("metric_scaled", ascending=True)
elif ranking_mode == "Average":
    global_mean = agg_df["metric_scaled"].mean()
    filtered = agg_df.iloc[(agg_df["metric_scaled"] - global_mean).abs().argsort()]
else:  # Custom Percentile
    percentile = st.slider("Select percentile (Top X%)", 1, 50, 10)
    cutoff = np.percentile(agg_df["metric_scaled"], 100 - percentile)
    filtered = agg_df[agg_df["metric_scaled"] >= cutoff].sort_values(
        "metric_scaled", ascending=False
    )

top_n = st.slider("Show top N countries", 5, 30, 10)
final_df = filtered.head(top_n)

fig = px.bar(
    final_df,
    x="country",
    y="metric_scaled",
    color="risk_level",
    title=f"Top {top_n} Countries ({ranking_mode} — {pollutant_selected})",
    color_discrete_map={
        "Low": "#22c55e",
        "Moderate": "#eab308",
        "High": "#f97316",
        "Very High": "#ef4444",
    },
)

fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Show full ranking data"):
    st.dataframe(final_df)

# ====================================================================================
# 9. Interpretation
# ====================================================================================
st.markdown(
    """
### 8. How to interpret the indices?
- **Composite risk index (0–1):**  
  0 = lowest relative risk, 1 = highest relative risk in this dataset.  
- **WHO health-impact index:**  
  Values > 1.0 indicate exposure **above WHO safe thresholds**.  
- **Risk levels (Low / Moderate / High / Very High)** come from dataset quartiles.  
- **Health levels (Safe / Moderate / High / Severe)** come from WHO-based exceedance.  
"""
)
