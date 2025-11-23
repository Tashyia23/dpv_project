import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.loader import load_master_data
from utils.loader import load_base_data
from utils.ui import header
from utils.regions import assign_region

st.set_page_config(layout="wide")

# ---------------------------------------------
# Load data
# ---------------------------------------------
# df = load_base_data()
df = load_master_data()


if "country" not in df.columns:
    st.error("Dataset must contain 'country' column.")
    st.stop()

df["region"] = df["country"].apply(assign_region)

header(
    "📊 Risk Explorer (Advanced Analytics)",
    "Deep-dive into country risk, pollutant behaviour, regions, and cross-country comparison."
)

# ---------------------------------------------
# Precompute mean values per country
# ---------------------------------------------
pollutants = [c for c in df.columns if c.endswith("_aqi_value")]

agg_df = df[["country"] + pollutants].groupby("country").mean().reset_index()

# Normalized risk index
scaled = {}
for col in pollutants:
    series = agg_df[col].astype(float)
    lo, hi = series.min(), series.max()
    scaled[col] = (series - lo) / (hi - lo) if hi > lo else np.zeros_like(series)

scaled_df = pd.DataFrame(scaled)

agg_df["risk_index"] = scaled_df.mean(axis=1)
agg_df["risk_index_raw"] = scaled_df.sum(axis=1)

# Percentile ranking
agg_df["risk_percentile"] = agg_df["risk_index"].rank(pct=True)

# ---------------------------------------------
# 🟦 SECTION 1 — Ranking Toggles
# ---------------------------------------------
st.subheader("1. Country Ranking Controls")

colA, colB = st.columns(2)

with colA:
    ranking_mode = st.selectbox(
        "Risk Ranking Mode",
        ["Highest Risk", "Lowest Risk", "Average (Middle)", "Custom Percentile Range"]
    )

with colB:
    metric_mode = st.selectbox(
        "Pollutant Ranking Mode",
        ["Overall Risk Index"] + pollutants
    )


# Custom percentile filter
if ranking_mode == "Custom Percentile Range":
    pct_min, pct_max = st.slider("Select Percentile Range", 0.0, 1.0, (0.20, 0.80), 0.01)
else:
    pct_min, pct_max = 0.0, 1.0

# Apply ranking filter
rank_df = agg_df.copy()

if ranking_mode == "Highest Risk":
    rank_df = rank_df.sort_values("risk_index", ascending=False)
elif ranking_mode == "Lowest Risk":
    rank_df = rank_df.sort_values("risk_index", ascending=True)
elif ranking_mode == "Average (Middle)":
    rank_df = rank_df[(rank_df["risk_percentile"] > 0.33) & (rank_df["risk_percentile"] < 0.66)]
elif ranking_mode == "Custom Percentile Range":
    rank_df = rank_df[
        (rank_df["risk_percentile"] >= pct_min) &
        (rank_df["risk_percentile"] <= pct_max)
    ]

# Metric column
metric_col = "risk_index" if metric_mode == "Overall Risk Index" else metric_mode

# Show bar chart
st.subheader("2. Ranked Countries")
top_n = st.slider("Show Top N", 5, 40, 10)

plot_df = rank_df.head(top_n)

fig = px.bar(
    plot_df,
    x="country",
    y=metric_col,
    title=f"Top {top_n} Countries ({metric_mode})",
    color="risk_index",
    color_continuous_scale="Reds"
)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------
# 🟩 SECTION 2 — Dual-Axis Risk vs Pollutant
# ---------------------------------------------
st.subheader("3. Dual-Axis Comparison (Risk vs Pollutant)")

col1, col2 = st.columns(2)

with col1:
    pollutant_choice = st.selectbox("Select Pollutant", pollutants)

with col2:
    num_compare = st.slider("Top N Countries to Compare", 5, 25, 10)

dual_df = agg_df.sort_values("risk_index", ascending=False).head(num_compare)

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=dual_df["country"],
    y=dual_df["risk_index"],
    name="Risk Index",
    marker_color="#ef4444"
))

fig2.add_trace(go.Scatter(
    x=dual_df["country"],
    y=dual_df[pollutant_choice],
    name=pollutant_choice,
    mode="lines+markers",
    yaxis="y2",
    marker=dict(color="#0ea5e9"),
    line=dict(width=3)
))

fig2.update_layout(
    height=450,
    yaxis=dict(title="Risk Index"),
    yaxis2=dict(title="Pollutant", overlaying="y", side="right")
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------
# 🟧 SECTION 3 — Heatmap
# ---------------------------------------------
st.subheader("4. Pollutant Heatmap (Countries × Pollutants)")

heat_df = agg_df.set_index("country")[pollutants]

fig3 = px.imshow(
    heat_df,
    aspect="auto",
    color_continuous_scale="Reds",
    title="Pollutant Heatmap"
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------
# 🟪 SECTION 4 — Radar Chart (Compare Countries)
# ---------------------------------------------
st.subheader("5. Radar Chart — Compare Countries")

compare_countries = st.multiselect(
    "Choose up to 3 countries",
    agg_df["country"].unique(),
    default=agg_df["country"].head(3).tolist()
)

if compare_countries:
    radar_df = agg_df[agg_df["country"].isin(compare_countries)]

    categories = pollutants

    fig4 = go.Figure()

    for _, row in radar_df.iterrows():
        fig4.add_trace(go.Scatterpolar(
            r=[row[p] for p in categories],
            theta=categories,
            fill='toself',
            name=row["country"]
        ))

    fig4.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        height=500
    )

    st.plotly_chart(fig4, use_container_width=True)
