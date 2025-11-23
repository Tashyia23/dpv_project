import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from utils.loader import load_base_data
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------
# Mini horizontal bar chart (Option B)
# ---------------------------------------------------
def mini_bar_chart(values, labels, max_width=130, height=6, colors=None):
    """
    Mini horizontal bars using pure CSS (Streamlit-safe).
    Bars scale correctly relative to max(values) 
    and maintain pollutant order.
    """
    if colors is None:
        colors = ["#8B5CF6", "#0EA5E9", "#F59E0B", "#EF4444", "#10B981"]

    values = list(values)
    labels = list(labels)

    max_val = max(values) if max(values) > 0 else 1

    rows = []
    for i, v in enumerate(values):
        bar_width = int((v / max_val) * max_width) if max_val else 0
        color = colors[i % len(colors)]

        rows.append(
            f"""
            <div style="display:flex; align-items:center; margin-bottom:4px;">
                <div style="width:150px; font-size:0.75rem; color:#374151; white-space:nowrap;">
                    {labels[i]}
                </div>
                <div style="background:{color};
                            height:{height}px;
                            width:{bar_width}px;
                            border-radius:4px;
                            margin-right:6px;">
                </div>
                <div style="font-size:0.70rem; color:#6B7280;">
                    {v:.2f}
                </div>
            </div>
            """
        )
    return "<div>" + "".join(rows) + "</div>"


# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
df = load_base_data()

header(
    "⚠ Health & Pollution Risk Index",
    "Combine multiple pollutants into a single risk score per country, with health-based interpretation."
)

if "country" not in df.columns:
    st.error("Dataset missing required column: 'country'")
    st.stop()


# ---------------------------------------------------
# 1. Configure Risk Score
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 1. Configure Risk Score")

pollutant_info = {
    "pm25_aqi_value": ("🟤", "PM2.5 (Fine Particles)"),
    "pm10_aqi_value": ("🟠", "PM10 (Coarse Particles)"),
    "no2_aqi_value": ("💛", "NO₂ (Nitrogen Dioxide)"),
    "ozone_aqi_value": ("💜", "O₃ (Ozone)"),
    "co_aqi_value": ("🔥", "CO (Carbon Monoxide)"),
}

pollutant_options = [c for c in df.columns if c.endswith("_aqi_value")]

pretty_labels = {
    col: f"{pollutant_info[col][0]} {pollutant_info[col][1]}"
    for col in pollutant_options
}

selected_pollutants = st.multiselect(
    "Pollutants to include",
    pollutant_options,
    default=pollutant_options,
    format_func=lambda col: pretty_labels[col],
)

if not selected_pollutants:
    st.warning("Please select at least one pollutant.")
    st.stop()


# ---------------------------------------------------
# Weight Presets
# ---------------------------------------------------
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


# Compute final weights
if preset == "Beginner Mode (equal weights)":
    norm_weights = equal_weights

elif preset == "WHO Health Severity":
    total = sum(who_weights[c] for c in selected_pollutants)
    norm_weights = {c: who_weights[c] / total for c in selected_pollutants}

elif preset == "EPA Danger Scale":
    total = sum(epa_weights[c] for c in selected_pollutants)
    norm_weights = {c: epa_weights[c] / total for c in selected_pollutants}

else:
    st.markdown("#### ⚙ Expert Mode – Fine Tune Pollutant Weights")
    weights = {}
    total_w = 0
    for col in selected_pollutants:
        w = st.slider(
            f"Weight for {pretty_labels[col]}",
            0.0, 10.0, 1.0, 0.1, key=f"w_{col}"
        )
        weights[col] = w
        total_w += w
    norm_weights = (
        equal_weights if total_w == 0 else
        {c: weights[c] / total_w for c in selected_pollutants}
    )

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# 2. Compute Risk Index
# ---------------------------------------------------
agg_df = df[["country"] + selected_pollutants].groupby("country").mean().reset_index()

scaled = {}
for col in selected_pollutants:
    series = agg_df[col].astype(float)
    lo, hi = series.min(), series.max()
    scaled[col] = (series - lo) / (hi - lo) if hi > lo else np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)

agg_df["risk_index"] = sum(
    scaled_df[c] * norm_weights[c] for c in selected_pollutants
)

q1, q2, q3 = np.percentile(agg_df["risk_index"], [25, 50, 75])


def classify(r):
    if r <= q1: return "Low"
    if r <= q2: return "Moderate"
    if r <= q3: return "High"
    return "Very High"


agg_df["risk_level"] = agg_df["risk_index"].apply(classify)


# ---------------------------------------------------
# 3. KPI Overview with Mini Bars (CLEANED)
# ---------------------------------------------------

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 🌍 Global Pollution Risk Overview")

avg_risk = agg_df["risk_index"].mean()
worst_row = agg_df.loc[agg_df["risk_index"].idxmax()]
best_row = agg_df.loc[agg_df["risk_index"].idxmin()]

labels = [pollutant_info[c][1] for c in selected_pollutants]
worst_vals = [float(worst_row[c]) for c in selected_pollutants]
best_vals = [float(best_row[c]) for c in selected_pollutants]

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Global Average Risk</div>
            <div class="kpi-value">{avg_risk:.2f}</div>
            <div class="kpi-sub">Scaled index (0–1)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Highest Risk Country</div>
            <div class="kpi-value">{worst_row['country']}</div>
            <div class="kpi-sub">
                Index {worst_row['risk_index']:.2f} ({worst_row['risk_level']})
            </div>
            {mini_bar_chart(worst_vals, labels)}
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Lowest Risk Country</div>
            <div class="kpi-value">{best_row['country']}</div>
            <div class="kpi-sub">
                Index {best_row['risk_index']:.2f} ({best_row['risk_level']})
            </div>
            {mini_bar_chart(best_vals, labels)}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# 4. Country Ranking Chart
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 3. Country Risk Ranking")

top_n = st.slider("Show top N highest-risk countries", 5, 30, 10)

top_df = agg_df.sort_values("risk_index", ascending=False).head(top_n)

fig = px.bar(
    top_df,
    x="country",
    y="risk_index",
    color="risk_level",
    title=f"Top {top_n} Highest-Risk Countries",
    color_discrete_map={
        "Low": "#22c55e",
        "Moderate": "#eab308",
        "High": "#f97316",
        "Very High": "#ef4444",
    }
)
fig.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show full table"):
    st.dataframe(
        agg_df.sort_values("risk_index", ascending=False)[
            ["country", "risk_index", "risk_level"] + selected_pollutants
        ]
    )

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# 5. Interpretation
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 4. How to interpret the risk index?")
st.markdown(
    """
- **Risk Index 0–1:** 0 = cleanest, 1 = highest-risk  
- **Normalised pollutants** allow fair country-to-country comparison  
- **Risk levels** come from dataset quartiles  
- **Preset modes** simulate different scientific models  
"""
)
st.markdown("</div>", unsafe_allow_html=True)




