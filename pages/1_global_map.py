import streamlit as st
import plotly.express as px
from utils.loader import load_base_data
from utils.ui import header

st.set_page_config(layout="wide")

base_df = load_base_data()

header(
    "🗺 Global Air Pollution Map",
    "Explore spatial patterns using choropleth mapping."
)

metric = st.selectbox(
    "Choose pollutant",
    ["aqi_value", "pm25_aqi_value", "no2_aqi_value", "co_aqi_value"],
)

# aggregate
agg = base_df.groupby("country", as_index=False)[metric].mean()

fig = px.choropleth(
    agg,
    locations="country",
    locationmode="country names",
    color=metric,
    title="Global Pollution Levels",
    color_continuous_scale="RdYlBu_r",
)

fig.update_geos(showframe=False, projection_type="natural earth")
st.plotly_chart(fig, use_container_width=True)
