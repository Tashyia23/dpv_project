import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from utils.loader import load_base_data
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------
# Load data
# ---------------------------------------------------
df = load_base_data()

header(
    "⚠ Health & Pollution Risk Index",
    "Combine multiple pollutants into a single risk score per country, with health-based interpretation."
)

if "country" not in df.columns:
    st.error("The base dataset is missing a 'country' column.")
    st.stop()

# -----------------------------------------------------------
# 1. Configure Risk Score 
# -----------------------------------------------------------
# -----------------------------------------------------------
# 1. Configure Risk Score (Upgraded: WHO/EPA presets + icons)
# -----------------------------------------------------------

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("### 1. Configure Risk Score")

st.markdown(
    """
    Select pollutants for the **Pollution Health Risk Index**.
    By default, all pollutants are equally weighted (Simple Mode).

    Use **WHO/EPA presets** for health-science based scoring,  
    or enable **Advanced Mode** for full control.
    """
)

# -----------------------------------------------------------
# Pollutant icons + descriptions for tooltips
# -----------------------------------------------------------
pollutant_info = {
    "pm25_aqi_value": ("🟤 PM2.5", "Fine particles linked to cardiovascular and lung diseases."),
    "pm10_aqi_value": ("🟠 PM10", "Coarse particles affecting upper respiratory tract."),
    "no2_aqi_value": ("💛 NO₂", "Nitrogen dioxide – asthma triggers & respiratory inflammation."),
    "ozone_aqi_value": ("💜 O₃", "Ground-level ozone – lung irritation, breathing difficulty."),
    "co_aqi_value": ("❤️ CO", "Carbon monoxide – reduces oxygen delivery to organs."),
}

pollutant_options = [c for c in df.columns if c.endswith("_aqi_value")]

if not pollutant_options:
    st.error("No pollutant AQI columns found.")
    st.stop()

# Pretty labels with icons
pretty_labels = {
    col: f"{pollutant_info[col][0]} {col.replace('_aqi_value', '').upper()}"
    for col in pollutant_options if col in pollutant_info
}

selected_pollutants = st.multiselect(
    "Pollutants to include",
    pollutant_options,
    default=pollutant_options,
    format_func=lambda x: pretty_labels.get(x, x),
)

if not selected_pollutants:
    st.warning("Please select at least one pollutant.")
    st.stop()

# -----------------------------------------------------------
# Preset profiles (Beginner / WHO / EPA / Expert)
# -----------------------------------------------------------
st.markdown("#### 🔧 Select a preset (optional)")

preset = st.radio(
    "",
    ["Beginner Mode (equal weights)", "WHO Health Severity", "EPA Danger Scale", "Expert Mode"],
)

# Default equal weights
equal_weights = {c: 1 / len(selected_pollutants) for c in selected_pollutants}

# WHO-based severity (scientific justification)
# Higher weight → more harmful to human health
who_weights = {
    "pm25_aqi_value": 0.40,
    "no2_aqi_value": 0.25,
    "ozone_aqi_value": 0.20,
    "pm10_aqi_value": 0.10,
    "co_aqi_value": 0.05,
}

# EPA-based danger classification
epa_weights = {
    "pm25_aqi_value": 0.35,
    "pm10_aqi_value": 0.20,
    "no2_aqi_value": 0.20,
    "ozone_aqi_value": 0.15,
    "co_aqi_value": 0.10,
}

# Override weights based on preset
if preset == "Beginner Mode (equal weights)":
    norm_weights = equal_weights

elif preset == "WHO Health Severity":
    # Only include selected pollutants
    total = sum(who_weights.get(c, 0) for c in selected_pollutants)
    norm_weights = {c: who_weights[c] / total for c in selected_pollutants}

elif preset == "EPA Danger Scale":
    total = sum(epa_weights.get(c, 0) for c in selected_pollutants)
    norm_weights = {c: epa_weights[c] / total for c in selected_pollutants}

else:
    # Expert mode → show advanced slider weights
    advanced_mode = True
    st.markdown("#### ⚙ Expert Mode – Fine-tune pollutant weighting")
    st.caption(
        "Adjust weights manually. Weights are normalised automatically."
    )

    weights = {}
    total_weight = 0.0

    for col in selected_pollutants:
        w = st.slider(
            f"Weight for {pretty_labels[col]}",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key=f"w_{col}",
        )
        weights[col] = w
        total_weight += w

    if total_weight == 0:
        norm_weights = equal_weights
    else:
        norm_weights = {c: w / total_weight for c, w in weights.items()}

# Simple modes don’t show sliders
if preset != "Expert Mode":
    st.caption(
        """
        **Note:**  
        - Beginner Mode → all pollutants contribute equally  
        - WHO Mode → prioritises health-harm severity  
        - EPA Mode → prioritises regulatory danger  
        """
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# 2. Compute country-level risk index
# ---------------------------------------------------
# Aggregate per country
group_cols = ["country"]
agg_df = df[group_cols + selected_pollutants].groupby("country", as_index=False).mean()

# Min–max scale each pollutant before combining
scaled = {}
for col in selected_pollutants:
    series = agg_df[col].astype(float)
    col_min, col_max = series.min(), series.max()
    if col_max > col_min:
        scaled[col] = (series - col_min) / (col_max - col_min)
    else:
        # Constant column
        scaled[col] = np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)
risk_values = np.zeros(len(agg_df))
for col in selected_pollutants:
    risk_values += scaled_df[col].to_numpy() * norm_weights[col]

agg_df["risk_index"] = risk_values

# Classify into risk bands based on percentiles
q1, q2, q3 = np.percentile(agg_df["risk_index"], [25, 50, 75])

def classify_risk(r):
    if r <= q1:
        return "Low"
    elif r <= q2:
        return "Moderate"
    elif r <= q3:
        return "High"
    else:
        return "Very High"

agg_df["risk_level"] = agg_df["risk_index"].apply(classify_risk)

# ---------------------------------------------------
# 3. Global KPIs + top/bottom countries
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("#### 2. Global risk overview")

avg_risk = agg_df["risk_index"].mean()
worst_row = agg_df.loc[agg_df["risk_index"].idxmax()]
best_row = agg_df.loc[agg_df["risk_index"].idxmin()]

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Global average risk</div>
            <div class="kpi-value">{avg_risk:.2f}</div>
            <div class="kpi-sub">Scaled index (0–1)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Highest risk</div>
            <div class="kpi-value">{worst_row['country']}</div>
            <div class="kpi-sub">Index {worst_row['risk_index']:.2f} ({worst_row['risk_level']})</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Lowest risk</div>
            <div class="kpi-value">{best_row['country']}</div>
            <div class="kpi-sub">Index {best_row['risk_index']:.2f} ({best_row['risk_level']})</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# 4. Visualise top N countries by risk
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("#### 3. Country risk ranking")

top_n = st.slider("Show top N highest-risk countries", min_value=5, max_value=30, value=10, step=1)
top_countries = agg_df.sort_values("risk_index", ascending=False).head(top_n)

fig_bar = px.bar(
    top_countries,
    x="country",
    y="risk_index",
    color="risk_level",
    color_discrete_map={
        "Low": "#22c55e",
        "Moderate": "#eab308",
        "High": "#f97316",
        "Very High": "#ef4444",
    },
    title=f"Top {top_n} countries by pollution risk index",
    labels={"risk_index": "Risk index (0–1)", "country": "Country"},
)
fig_bar.update_layout(
    height=450,
    margin=dict(l=0, r=0, t=40, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("Show full risk table for all countries"):
    st.dataframe(
        agg_df.sort_values("risk_index", ascending=False)[
            ["country", "risk_index", "risk_level"] + selected_pollutants
        ]
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# 5. Simple interpretation
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("#### 4. How to interpret the risk index?")
st.markdown(
    """
- The **risk index** is a *relative* score between 0 and 1, combining the selected pollutant AQI values.
- Each pollutant is **normalised (min–max)** so that countries can be fairly compared.
- You can change **which pollutants** are included, and their **relative weights**, to test different scenarios.
- **Risk levels** (Low, Moderate, High, Very High) are based on the distribution of all risk scores (quartiles), 
  so they adapt to the dataset.
"""
)
st.markdown("</div>", unsafe_allow_html=True)
