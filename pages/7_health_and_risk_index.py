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

# ---------------------------------------------------
# 1. Choose pollutants and build a risk score
# ---------------------------------------------------
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.markdown("#### 1. Configure risk score")

# Try to detect pollutant columns
candidate_cols = []
for col in df.columns:
    if col.endswith("_aqi_value") or col in ["aqi_value"]:
        candidate_cols.append(col)

if not candidate_cols:
    st.warning("No pollutant AQI columns detected. Using all numeric columns as fallback.")
    candidate_cols = df.select_dtypes(include="number").columns.tolist()

# Let user choose which pollutants contribute to risk
selected_pollutants = st.multiselect(
    "Choose pollutant metrics to include in the risk index",
    options=candidate_cols,
    default=[c for c in candidate_cols if c != "aqi_value"] or candidate_cols,
    help="These should be AQI-based columns such as pm25_aqi_value, no2_aqi_value, ozone_aqi_value, etc.",
)

if not selected_pollutants:
    st.warning("Please select at least one pollutant metric.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Weighting scheme
st.markdown(
    "<div class='section-caption'>Assign weights to each pollutant (they will be normalised to sum to 1).</div>",
    unsafe_allow_html=True,
)

weights = {}
total_weight = 0.0
for col in selected_pollutants:
    w = st.number_input(
        f"Weight for {col}",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.1,
        key=f"w_{col}",
    )
    weights[col] = w
    total_weight += w

if total_weight == 0:
    # Avoid division by zero
    norm_weights = {c: 1 / len(selected_pollutants) for c in selected_pollutants}
else:
    norm_weights = {c: w / total_weight for c, w in weights.items()}

st.caption(
    "Weights are automatically normalised so that they sum to 1. "
    "This risk index is a weighted combination of the selected pollutant AQI values."
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
