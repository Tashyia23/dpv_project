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
# Pollutant icons + display labels (UPDATED)
# -----------------------------------------------------------

pollutant_info = {
    "pm25_aqi_value": ("🟤", "PM2.5 (Fine Particles)"),
    "pm10_aqi_value": ("🟠", "PM10 (Coarse Particles)"),
    "no2_aqi_value": ("💛", "NO₂ (Nitrogen Dioxide)"),
    "ozone_aqi_value": ("💜", "O₃ (Ozone)"),
    "co_aqi_value": ("🔥", "CO (Carbon Monoxide)"),     # FIXED HERE
}

pollutant_options = [c for c in df.columns if c.endswith("_aqi_value")]

if not pollutant_options:
    st.error("No pollutant AQI columns found.")
    st.stop()

# PRETTY LABELS — CLEAN, NO DUPLICATION, NO "CO CO"
pretty_labels = {
    col: f"{pollutant_info[col][0]} {pollutant_info[col][1]}"
    for col in pollutant_options
}

selected_pollutants = st.multiselect(
    "Pollutants to include",
    pollutant_options,
    default=pollutant_options,
    format_func=lambda col: pretty_labels.get(col, col),
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
    total = sum(who_weights.get(c, 0) for c in selected_pollutants)
    norm_weights = {c: who_weights[c] / total for c in selected_pollutants}

elif preset == "EPA Danger Scale":
    total = sum(epa_weights.get(c, 0) for c in selected_pollutants)
    norm_weights = {c: epa_weights[c] / total for c in selected_pollutants}

else:
    # Expert mode → sliders
    st.markdown("#### ⚙ Expert Mode – Fine-tune pollutant weighting")
    st.caption("Adjust weights manually. Weights are normalised automatically.")

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
group_cols = ["country"]
agg_df = df[group_cols + selected_pollutants].groupby("country", as_index=False).mean()

scaled = {}
for col in selected_pollutants:
    series = agg_df[col].astype(float)
    col_min, col_max = series.min(), series.max()
    scaled[col] = (series - col_min) / (col_max - col_min) if col_max > col_min else np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)
risk_values = np.zeros(len(agg_df))

for col in selected_pollutants:
    risk_values += scaled_df[col].to_numpy() * norm_weights[col]

agg_df["risk_index"] = risk_values

q1, q2, q3 = np.percentile(agg_df["risk_index"], [25, 50, 75])

def classify_risk(r):
    if r <= q1: return "Low"
    elif r <= q2: return "Moderate"
    elif r <= q3: return "High"
    else: return "Very High"

agg_df["risk_level"] = agg_df["risk_index"].apply(classify_risk)

# ---------------------------------------------------
# 3. Global risk overview
# ---------------------------------------------------

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

st.markdown("""
<div style='font-size: 22px; font-weight: 800; margin-bottom: 12px;'>
    🌍 Global Pollution Risk Overview
</div>
""", unsafe_allow_html=True)

# Helper — convert country name to emoji flag
def country_to_flag(country):
    try:
        return ''.join(chr(127397 + ord(c.upper())) for c in country if c.isalpha())
    except:
        return "🏳"

avg_risk = agg_df["risk_index"].mean()
worst_row = agg_df.loc[agg_df["risk_index"].idxmax()]
best_row = agg_df.loc[agg_df["risk_index"].idxmin()]

# Create sparkline helper
def sparkline(values):
    import matplotlib.pyplot as plt
    import io, base64

    fig, ax = plt.subplots(figsize=(3, 0.4))
    ax.plot(values, linewidth=2)
    ax.set_axis_off()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", transparent=True)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()

# Generate mini sparkline for top/bottom country
worst_spark = sparkline(worst_row[selected_pollutants].values)
best_spark = sparkline(best_row[selected_pollutants].values)

kpi1, kpi2, kpi3 = st.columns(3)

# ==========================
# GLOBAL AVERAGE CARD
# ==========================
with kpi1:
    st.markdown(f"""
    <div class="kpi-card" style="
        text-align: center;
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border-left: 6px solid #3b82f6;
    ">
        <div class="kpi-label">🌐 Global Average Risk</div>
        <div class="kpi-value" style="font-size: 1.7rem;">{avg_risk:.2f}</div>
        <div class="kpi-sub">Scaled index (0–1)</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================
# HIGHEST RISK CARD
# ==========================
with kpi2:
    flag = country_to_flag(worst_row["country"])
    st.markdown(f"""
    <div class="kpi-card" style="
        background: linear-gradient(135deg, #fecaca, #fca5a5);
        border-left: 6px solid #ef4444;
    ">
        <div class="kpi-label">🔥 Highest Risk Country</div>
        <div class="kpi-value" style="font-size: 1.2rem;">
            {flag} {worst_row['country']}
        </div>
        <div class="kpi-sub">
            Index {worst_row['risk_index']:.2f} ({worst_row['risk_level']})
        </div>

        <div style="margin-top: 8px; font-size: 0.7rem; color: #7f1d1d;">
            <strong>Top ranked (#1)</strong> · Highest combined pollutant burden
        </div>

        <img src="data:image/png;base64,{worst_spark}" 
             style="width:100%; margin-top:6px;" />
    </div>
    """, unsafe_allow_html=True)

# ==========================
# LOWEST RISK CARD
# ==========================
with kpi3:
    flag = country_to_flag(best_row["country"])
    st.markdown(f"""
    <div class="kpi-card" style="
        background: linear-gradient(135deg, #bbf7d0, #86efac);
        border-left: 6px solid #22c55e;
    ">
        <div class="kpi-label">🍃 Lowest Risk Country</div>
        <div class="kpi-value" style="font-size: 1.2rem;">
            {flag} {best_row['country']}
        </div>
        <div class="kpi-sub">
            Index {best_row['risk_index']:.2f} ({best_row['risk_level']})
        </div>

        <div style="margin-top: 8px; font-size: 0.7rem; color: #065f46;">
            <strong>#1 Cleanest</strong> · Lowest combined pollutant exposure
        </div>

        <img src="data:image/png;base64,{best_spark}" 
             style="width:100%; margin-top:6px;" />
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)



# ---------------------------------------------------
# 4. Bar chart
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("#### 3. Country risk ranking")

top_n = st.slider("Show top N highest-risk countries", 5, 30, 10, 1)
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
)
fig_bar.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("Show full risk table for all countries"):
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
st.markdown("#### 4. How to interpret the risk index?")
st.markdown(
    """
- The **risk index** is a *relative* score between 0 and 1, combining the selected pollutant AQI values.
- Each pollutant is **normalised** so all countries are compared fairly.
- You can adjust **included pollutants** and **weightings** to study different scenarios.
- **Risk bands** (Low→Very High) are based on dataset quartiles.
"""
)
st.markdown("</div>", unsafe_allow_html=True)

