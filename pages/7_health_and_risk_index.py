# import streamlit as st
# import numpy as np
# import pandas as pd
# import plotly.express as px
# from utils.loader import load_master_data
# from utils.loader import load_base_data
# from utils.ui import header

# st.set_page_config(layout="wide")

# # ------------------------------------------------------------------------------------
# # Mini Bar UI
# # ------------------------------------------------------------------------------------
# def mini_bar_chart(values, labels, max_width=160, height=8, colors=None):
#     if colors is None:
#         colors = ["#7C3AED", "#0EA5E9", "#F59E0B", "#EF4444", "#10B981"]

#     html = "<div>"
#     max_val = max(values) if max(values) else 1

#     for i, v in enumerate(values):
#         width = int((v / max_val) * max_width)
#         color = colors[i % len(colors)]
#         html += f"""
#         <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
#             <div style='width:150px;font-size:0.80rem;font-weight:500;color:#374151;'>{labels[i]}</div>
#             <div style='flex-grow:1;max-width:{max_width}px;background:#E5E7EB;border-radius:4px;height:{height}px;'>
#                 <div style='background:{color};width:{width}px;height:{height}px;border-radius:4px;'></div>
#             </div>
#             <div style='width:45px;text-align:right;font-size:0.80rem;color:#374151;'>{v:.2f}</div>
#         </div>
#         """
#     html += "</div>"
#     return html


# # ------------------------------------------------------------------------------------
# # Load Data
# # ------------------------------------------------------------------------------------
# # df = load_base_data()
# df = load_master_data()


# header("⚠ Health & Pollution Risk Index", "Combine multiple pollutants into a single risk score per country.")

# if "country" not in df.columns:
#     st.error("Dataset missing column 'country'")
#     st.stop()

# if "region" not in df.columns:
#     df["region"] = "Other" 
    
# # ------------------------------------------------------------------------------------
# # 1. Configure Risk Score
# # ------------------------------------------------------------------------------------
# st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
# st.markdown("### 1. Configure Risk Score")

# pollutant_info = {
#     "pm25_aqi_value": ("🟤", "PM2.5 (Fine Particles)"),
#     "pm10_aqi_value": ("🟠", "PM10 (Coarse Particles)"),
#     "no2_aqi_value": ("💛", "NO₂ (Nitrogen Dioxide)"),
#     "ozone_aqi_value": ("💜", "O₃ (Ozone)"),
#     "co_aqi_value": ("🔥", "CO (Carbon Monoxide)"),
# }

# pollutant_options = [c for c in df.columns if c.endswith("_aqi_value")]
# pretty_labels = {c: f"{pollutant_info[c][0]} {pollutant_info[c][1]}" for c in pollutant_options}

# selected_pollutants = st.multiselect(
#     "Pollutants to include",
#     pollutant_options,
#     default=pollutant_options,
#     format_func=lambda col: pretty_labels[col],
# )

# if not selected_pollutants:
#     st.warning("⚠ Please select at least one pollutant.")
#     st.stop()


# # ------------------------------------------------------------------------------------
# # Weight Presets
# # ------------------------------------------------------------------------------------
# st.markdown("#### 🔧 Select a preset (optional)")

# preset = st.radio("", ["Beginner Mode (equal weights)", "WHO Health Severity", "EPA Danger Scale", "Expert Mode"])

# equal_weights = {c: 1 / len(selected_pollutants) for c in selected_pollutants}

# who_weights = {
#     "pm25_aqi_value": 0.40,
#     "no2_aqi_value": 0.25,
#     "ozone_aqi_value": 0.20,
#     "pm10_aqi_value": 0.10,
#     "co_aqi_value": 0.05,
# }

# epa_weights = {
#     "pm25_aqi_value": 0.35,
#     "pm10_aqi_value": 0.20,
#     "no2_aqi_value": 0.20,
#     "ozone_aqi_value": 0.15,
#     "co_aqi_value": 0.10,
# }

# if preset == "Beginner Mode (equal weights)":
#     norm_weights = equal_weights

# elif preset == "WHO Health Severity":
#     total = sum(who_weights[c] for c in selected_pollutants)
#     norm_weights = {c: who_weights[c] / total for c in selected_pollutants}

# elif preset == "EPA Danger Scale":
#     total = sum(epa_weights[c] for c in selected_pollutants)
#     norm_weights = {c: epa_weights[c] / total for c in selected_pollutants}

# else:
#     st.markdown("#### ⚙ Expert Mode – Fine Tune Pollutant Weights")
#     weights, total_w = {}, 0
#     for col in selected_pollutants:
#         w = st.slider(f"Weight for {pretty_labels[col]}", 0.0, 10.0, 1.0)
#         weights[col] = w
#         total_w += w
#     norm_weights = equal_weights if total_w == 0 else {c: weights[c] / total_w for c in selected_pollutants}

# st.markdown("</div>", unsafe_allow_html=True)


# # ------------------------------------------------------------------------------------
# # 2. Compute Risk Index
# # ------------------------------------------------------------------------------------
# agg_df = df[["country"] + selected_pollutants].groupby("country").mean().reset_index()

# scaled = {}
# for col in selected_pollutants:
#     series = agg_df[col].astype(float)
#     lo, hi = series.min(), series.max()
#     scaled[col] = (series - lo) / (hi - lo) if hi > lo else np.zeros_like(series)

# scaled_df = pd.DataFrame(scaled)
# agg_df["risk_index"] = sum(scaled_df[c] * norm_weights[c] for c in selected_pollutants)

# q1, q2, q3 = np.percentile(agg_df["risk_index"], [25, 50, 75])

# def classify(r):
#     if r <= q1: return "Low"
#     if r <= q2: return "Moderate"
#     if r <= q3: return "High"
#     return "Very High"

# agg_df["risk_level"] = agg_df["risk_index"].apply(classify)


# # ====================================================================================
# # 3. RISK LEVEL TABS
# # ====================================================================================
# st.markdown("### 🌡 Risk-Level Explorer")

# tab1, tab2, tab3, tab4, tab5 = st.tabs(["Very High", "High", "Moderate", "Low", "All"])

# for tab, level in zip([tab1, tab2, tab3, tab4], ["Very High", "High", "Moderate", "Low"]):
#     with tab:
#         sub = agg_df[agg_df["risk_level"] == level]
#         st.subheader(f"{level} Risk Countries")
#         if sub.empty:
#             st.info("No countries in this category.")
#         else:
#             fig = px.bar(sub.sort_values("risk_index", ascending=False),
#                          x="country", y="risk_index",
#                          title=f"{level} Risk Level",
#                          color_discrete_sequence=["#ef4444" if level=="Very High" else "#f97316"])
#             st.plotly_chart(fig, use_container_width=True)
#             st.dataframe(sub)

# with tab5:
#     st.subheader("All Countries")
#     st.dataframe(agg_df)


# # ====================================================================================
# # 4. INTERACTIVE WORLD MAP
# # ====================================================================================
# st.markdown("### 🗺 World Risk Map (Choropleth)")

# map_fig = px.choropleth(
#     agg_df,
#     locations="country",
#     locationmode="country names",
#     color="risk_index",
#     color_continuous_scale=["green", "yellow", "orange", "red"],
#     title="Global Pollution Risk Map",
# )
# map_fig.update_layout(height=500)
# st.plotly_chart(map_fig, use_container_width=True)


# # ====================================================================================
# # 5. AUTO INSIGHTS
# # ====================================================================================
# st.markdown("### 🤖 Auto Insights")

# avg = agg_df["risk_index"].mean()
# worst = agg_df.loc[agg_df["risk_index"].idxmax()]
# best = agg_df.loc[agg_df["risk_index"].idxmin()]

# st.markdown(f"""
# #### Key Insights
# - 🌍 **Global average risk index:** `{avg:.2f}`
# - 🚨 **Highest-risk country:** `{worst['country']}` with score `{worst['risk_index']:.2f}`  
# - 🌱 **Lowest-risk country:** `{best['country']}` with score `{best['risk_index']:.2f}`  
# - 📊 **Most influential pollutant** (weighted): **{max(norm_weights, key=norm_weights.get)}**
# - ⚠ Countries with **Very High risk** tend to have elevated **PM2.5 + NO₂** levels.
# """)

# # ====================================================================================
# # 6. COMPARE COUNTRIES SIDE-BY-SIDE
# # ====================================================================================
# st.markdown("### 🆚 Compare Two Countries (Side-by-Side Analysis)")

# colA, colB = st.columns(2)

# with colA:
#     country_a = st.selectbox(
#         "Select Country A",
#         agg_df["country"].sort_values().unique(),
#         key="country_a"
#     )

# with colB:
#     country_b = st.selectbox(
#         "Select Country B",
#         agg_df["country"].sort_values().unique(),
#         key="country_b"
#     )

# # Avoid same-country comparison
# if country_a == country_b:
#     st.warning("⚠ Please choose two different countries for comparison.")
# else:
#     a_row = agg_df[agg_df["country"] == country_a].iloc[0]
#     b_row = agg_df[agg_df["country"] == country_b].iloc[0]

#     labels = [pollutant_info[c][1] for c in selected_pollutants]
#     a_vals = [float(a_row[c]) for c in selected_pollutants]
#     b_vals = [float(b_row[c]) for c in selected_pollutants]

#     # --------------------------------------------------------------------------
#     # SIDE-BY-SIDE UI
#     # --------------------------------------------------------------------------
#     cA, cB = st.columns(2)

#     with cA:
#         st.markdown(f"""
#         <div class="kpi-card">
#             <div class="kpi-label">{country_a}</div>
#             <div class="kpi-value">{a_row['risk_index']:.2f}</div>
#             <div class="kpi-sub">Risk Level: {a_row['risk_level']}</div>
#         </div>
#         """, unsafe_allow_html=True)
#         st.markdown("#### Pollutant Breakdown")
#         st.markdown(mini_bar_chart(a_vals, labels), unsafe_allow_html=True)

#     with cB:
#         st.markdown(f"""
#         <div class="kpi-card">
#             <div class="kpi-label">{country_b}</div>
#             <div class="kpi-value">{b_row['risk_index']:.2f}</div>
#             <div class="kpi-sub">Risk Level: {b_row['risk_level']}</div>
#         </div>
#         """, unsafe_allow_html=True)
#         st.markdown("#### Pollutant Breakdown")
#         st.markdown(mini_bar_chart(b_vals, labels), unsafe_allow_html=True)

#     # --------------------------------------------------------------------------
#     # AUTO INTERPRETATION
#     # --------------------------------------------------------------------------
#     st.markdown("### 🔍 Interpretation")

#     diff = a_row["risk_index"] - b_row["risk_index"]
#     higher = country_a if diff > 0 else country_b
#     gap = abs(diff)

#     st.markdown(f"""
#     **Comparison Summary**
#     - **Higher risk:** `{higher}`  
#     - **Risk gap:** `{gap:.2f}`  
#     - **Key pollutant difference:** `{labels[np.argmax(np.abs(np.array(a_vals)-np.array(b_vals)))]}`  
#     """)

#     # Detailed breakdown table
#     comp_df = pd.DataFrame({
#         "Pollutant": labels,
#         country_a: a_vals,
#         country_b: b_vals,
#         "Difference": np.array(a_vals) - np.array(b_vals)
#     })

#     st.dataframe(comp_df.style.format({country_a: "{:.2f}", country_b: "{:.2f}", "Difference": "{:.2f}"}))


# # ---------------------------------------------------
# # 3. Country Risk Ranking (WITH 2 TOGGLES)
# # ---------------------------------------------------

# st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
# st.markdown("### 3. Country Risk Ranking")

# # -------------------------------
# # 🔹 TOGGLE 1 – Ranking Type
# # -------------------------------

# ranking_mode = st.radio(
#     "Select ranking type:",
#     ["Highest Risk", "Lowest Risk", "Average", "Custom Percentile"],
#     horizontal=True
# )

# # -------------------------------
# # 🔹 TOGGLE 2 – Pollutant Selector
# # -------------------------------
# pollutant_choices = {
#     "Overall Risk Index": "risk_index",
#     "PM₂.₅ (Fine Particles)": "pm25_aqi_value",
#     "NO₂ (Nitrogen Dioxide)": "no2_aqi_value",
#     "O₃ (Ozone)": "ozone_aqi_value",
#     "CO (Carbon Monoxide)": "co_aqi_value",
#     "PM₁₀ (Coarse Particles)": "pm10_aqi_value"
# }

# pollutant_selected = st.selectbox(
#     "Pollutant used for ranking:",
#     list(pollutant_choices.keys())
# )

# metric_col = pollutant_choices[pollutant_selected]

# # If pollutant is not risk_index, compute new scaled metric
# if metric_col != "risk_index":
#     col_vals = agg_df[metric_col].astype(float)
#     lo, hi = col_vals.min(), col_vals.max()
#     agg_df["metric_scaled"] = (col_vals - lo) / (hi - lo) if hi > lo else 0
# else:
#     agg_df["metric_scaled"] = agg_df["risk_index"]

# # -------------------------------
# # 🔹 Ranking Logic
# # -------------------------------
# if ranking_mode == "Highest Risk":
#     filtered = agg_df.sort_values("metric_scaled", ascending=False)

# elif ranking_mode == "Lowest Risk":
#     filtered = agg_df.sort_values("metric_scaled", ascending=True)

# elif ranking_mode == "Average":
#     # Rank by closeness to global mean
#     global_mean = agg_df["metric_scaled"].mean()
#     filtered = agg_df.iloc[(agg_df["metric_scaled"] - global_mean).abs().argsort()]

# else:  # Custom Percentile
#     percentile = st.slider("Select percentile (Top X%)", 1, 50, 10)
#     cutoff = np.percentile(agg_df["metric_scaled"], 100 - percentile)
#     filtered = agg_df[agg_df["metric_scaled"] >= cutoff].sort_values("metric_scaled", ascending=False)

# # Let user choose N items
# top_n = st.slider("Show top N countries", 5, 30, 10)

# final_df = filtered.head(top_n)

# # -------------------------------
# # 🔹 Plotly Bar Chart
# # -------------------------------
# fig = px.bar(
#     final_df,
#     x="country",
#     y="metric_scaled",
#     color="risk_level",
#     title=f"Top {top_n} Countries ({ranking_mode} — {pollutant_selected})",
#     color_discrete_map={
#         "Low": "#22c55e",
#         "Moderate": "#eab308",
#         "High": "#f97316",
#         "Very High": "#ef4444",
#     }
# )

# fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
# fig.update_xaxes(tickangle=45)

# st.plotly_chart(fig, use_container_width=True)

# # Show table
# with st.expander("Show full data"):
#     st.dataframe(final_df)

# st.markdown("</div>", unsafe_allow_html=True)


# # ====================================================================================
# # 7. Interpretation
# # ====================================================================================
# st.markdown("""
# ### 4. How to interpret the risk index?
# - **0–1 scale:** 0 = cleanest, 1 = highest risk  
# - Normalised pollutant scores enable fair comparisons  
# - Risk levels come from dataset quartiles  
# - Presets follow scientific frameworks (WHO, EPA)  
# """)


#_____________________________________________

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from utils.loader import load_base_data   # ✅ single, stable loader import
from utils.ui import header

st.set_page_config(layout="wide")

# ------------------------------------------------------------------------------------
# Mini Bar UI
# ------------------------------------------------------------------------------------
def mini_bar_chart(values, labels, max_width=160, height=8, colors=None):
    if colors is None:
        colors = ["#7C3AED", "#0EA5E9", "#F59E0B", "#EF4444", "#10B981"]

    html = "<div>"
    max_val = max(values) if max(values) else 1

    for i, v in enumerate(values):
        width = int((v / max_val) * max_width)
        color = colors[i % len(colors)]
        html += f"""
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
            <div style='width:150px;font-size:0.80rem;font-weight:500;color:#374151;'>{labels[i]}</div>
            <div style='flex-grow:1;max-width:{max_width}px;background:#E5E7EB;border-radius:4px;height:{height}px;'>
                <div style='background:{color};width:{width}px;height:{height}px;border-radius:4px;'></div>
            </div>
            <div style='width:45px;text-align:right;font-size:0.80rem;color:#374151;'>{v:.2f}</div>
        </div>
        """
    html += "</div>"
    return html


# ------------------------------------------------------------------------------------
# Load Data (RAW – before processing)
# ------------------------------------------------------------------------------------
df = load_base_data()

header(
    "⚠ Health & Pollution Risk Index",
    "Combine multiple pollutants into a single risk score per country."
)

if df is None or df.empty:
    st.error("Base dataset could not be loaded or is empty.")
    st.stop()

if "country" not in df.columns:
    st.error("Dataset missing column 'country'.")
    st.stop()

# Ensure region exists (some pages may rely on it)
if "region" not in df.columns:
    df["region"] = "Other"


# ------------------------------------------------------------------------------------
# 1. Configure Risk Score (pollutants + weights)
# ------------------------------------------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 1. Configure Risk Score")

pollutant_info = {
    "pm25_aqi_value": ("🟤", "PM2.5 (Fine Particles)"),
    "pm10_aqi_value": ("🟠", "PM10 (Coarse Particles)"),
    "no2_aqi_value": ("💛", "NO₂ (Nitrogen Dioxide)"),
    "ozone_aqi_value": ("💜", "O₃ (Ozone)"),
    "co_aqi_value": ("🔥", "CO (Carbon Monoxide)"),
}

# Only use pollutants that actually exist in the dataframe
pollutant_options = [c for c in pollutant_info.keys() if c in df.columns]

if not pollutant_options:
    st.error("No pollutant *_aqi_value columns found in the dataset.")
    st.stop()

pretty_labels = {
    c: f"{pollutant_info[c][0]} {pollutant_info[c][1]}"
    for c in pollutant_options
}

selected_pollutants = st.multiselect(
    "Pollutants to include",
    pollutant_options,
    default=pollutant_options,
    format_func=lambda col: pretty_labels[col],
)

if not selected_pollutants:
    st.warning("⚠ Please select at least one pollutant.")
    st.stop()


# ------------------------------------------------------------------------------------
# Weight Presets
# ------------------------------------------------------------------------------------
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

st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------------
# 2. BEFORE vs AFTER TOGGLE
# ------------------------------------------------------------------------------------
st.markdown("### 🧪 Data View Mode — Before vs After Processing")

view_mode = st.radio(
    "Choose how to explore the data:",
    ["Raw AQI Data (Before Processing)", "Computed Risk Index (After Processing)"],
    horizontal=True,
)

# Aggregate pollutants by country (RAW)
raw_agg = df[["country"] + selected_pollutants].groupby("country").mean().reset_index()

if view_mode == "Raw AQI Data (Before Processing)":
    # -------------------------------------------------------------------------
    # RAW VIEW (Before Processing)
    # -------------------------------------------------------------------------
    st.markdown("#### 🌫 Raw Pollutant AQI by Country (Before Processing)")

    raw_pollutant = st.selectbox(
        "Select pollutant to inspect (raw AQI):",
        selected_pollutants,
        format_func=lambda col: pretty_labels[col],
        key="raw_pollutant_choice"
    )

    raw_plot_df = raw_agg.sort_values(raw_pollutant, ascending=False).head(30)

    fig_raw = px.bar(
        raw_plot_df,
        x="country",
        y=raw_pollutant,
        title=f"Top 30 Countries by Raw {pretty_labels[raw_pollutant]}",
        labels={raw_pollutant: "AQI (Raw)"},
    )
    fig_raw.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
    fig_raw.update_xaxes(tickangle=45)
    st.plotly_chart(fig_raw, use_container_width=True)

    with st.expander("Show raw aggregated table"):
        st.dataframe(raw_agg, use_container_width=True)

    st.info(
        "You are currently viewing **raw AQI values (before processing)**.\n\n"
        "Switch to **'Computed Risk Index (After Processing)'** above to see the weighted, "
        "normalised risk index, risk levels, world map, and comparisons."
    )

    # ❗ Stop here so the rest of the page (risk index stuff) doesn't run
    st.stop()


# ====================================================================================
# FROM THIS POINT ON: AFTER PROCESSING (Risk Index)
# ====================================================================================

# ------------------------------------------------------------------------------------
# 3. Compute Risk Index (AFTER processing)
# ------------------------------------------------------------------------------------
agg_df = raw_agg.copy()  # start from the RAW aggregated values

scaled = {}
for col in selected_pollutants:
    series = agg_df[col].astype(float)
    lo, hi = series.min(), series.max()
    scaled[col] = (series - lo) / (hi - lo) if hi > 0 and hi > lo else np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)
agg_df["risk_index"] = sum(scaled_df[c] * norm_weights[c] for c in selected_pollutants)

q1, q2, q3 = np.percentile(agg_df["risk_index"], [25, 50, 75])

def classify(r):
    if r <= q1:
        return "Low"
    if r <= q2:
        return "Moderate"
    if r <= q3:
        return "High"
    return "Very High"

agg_df["risk_level"] = agg_df["risk_index"].apply(classify)


# ====================================================================================
# 4. RISK LEVEL TABS
# ====================================================================================
st.markdown("### 🌡 Risk-Level Explorer (After Processing)")

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
# 5. INTERACTIVE WORLD MAP
# ====================================================================================
st.markdown("### 🗺 World Risk Map (Choropleth)")

map_fig = px.choropleth(
    agg_df,
    locations="country",
    locationmode="country names",
    color="risk_index",
    color_continuous_scale=["green", "yellow", "orange", "red"],
    title="Global Pollution Risk Map",
)
map_fig.update_layout(height=500)
st.plotly_chart(map_fig, use_container_width=True)


# ====================================================================================
# 6. AUTO INSIGHTS
# ====================================================================================
st.markdown("### 🤖 Auto Insights")

avg = agg_df["risk_index"].mean()
worst = agg_df.loc[agg_df["risk_index"].idxmax()]
best = agg_df.loc[agg_df["risk_index"].idxmin()]

st.markdown(f"""
#### Key Insights
- 🌍 **Global average risk index:** `{avg:.2f}`
- 🚨 **Highest-risk country:** `{worst['country']}` with score `{worst['risk_index']:.2f}`  
- 🌱 **Lowest-risk country:** `{best['country']}` with score `{best['risk_index']:.2f}`  
- 📊 **Most influential pollutant** (weighted): **{max(norm_weights, key=norm_weights.get)}**
- ⚠ Countries with **Very High risk** tend to have elevated **PM2.5 + NO₂** levels.
""")


# ====================================================================================
# 7. COMPARE COUNTRIES SIDE-BY-SIDE
# ====================================================================================
st.markdown("### 🆚 Compare Two Countries (Side-by-Side Analysis)")

colA, colB = st.columns(2)

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

if country_a == country_b:
    st.warning("⚠ Please choose two different countries for comparison.")
else:
    a_row = agg_df[agg_df["country"] == country_a].iloc[0]
    b_row = agg_df[agg_df["country"] == country_b].iloc[0]

    labels = [pollutant_info[c][1] for c in selected_pollutants]
    a_vals = [float(a_row[c]) for c in selected_pollutants]
    b_vals = [float(b_row[c]) for c in selected_pollutants]

    cA, cB = st.columns(2)

    with cA:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-label">{country_a}</div>
            <div class="kpi-value">{a_row['risk_index']:.2f}</div>
            <div class="kpi-sub">Risk Level: {a_row['risk_level']}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("#### Pollutant Breakdown")
        st.markdown(mini_bar_chart(a_vals, labels), unsafe_allow_html=True)

    with cB:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-label">{country_b}</div>
            <div class="kpi-value">{b_row['risk_index']:.2f}</div>
            <div class="kpi-sub">Risk Level: {b_row['risk_level']}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("#### Pollutant Breakdown")
        st.markdown(mini_bar_chart(b_vals, labels), unsafe_allow_html=True)

    st.markdown("### 🔍 Interpretation")

    diff = a_row["risk_index"] - b_row["risk_index"]
    higher = country_a if diff > 0 else country_b
    gap = abs(diff)

    st.markdown(
        f"""
    **Comparison Summary**
    - **Higher risk:** `{higher}`  
    - **Risk gap:** `{gap:.2f}`  
    - **Key pollutant difference:** `{labels[np.argmax(np.abs(np.array(a_vals) - np.array(b_vals)))]}`  
    """
    )

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


# ---------------------------------------------------
# 8. Country Risk Ranking (WITH 2 TOGGLES)
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 3. Country Risk Ranking")

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

with st.expander("Show full data"):
    st.dataframe(final_df)

st.markdown("</div>", unsafe_allow_html=True)


# ====================================================================================
# 9. Interpretation
# ====================================================================================
st.markdown(
    """
### 4. How to interpret the risk index?
- **0–1 scale:** 0 = cleanest, 1 = highest risk  
- Normalised pollutant scores enable fair comparisons  
- Risk levels come from dataset quartiles  
- Presets follow scientific frameworks (WHO, EPA)  
"""
)

