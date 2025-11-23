# import streamlit as st
# import plotly.express as px
# from utils.merged_dataset import load_merged_dataset
# from utils.ui import header


# st.set_page_config(layout="wide")

# df = load_merged_dataset()



# header(
#     "🗺 Global Air Pollution Map",
#     "Explore spatial patterns using choropleth mapping."
# )

# metric = st.selectbox(
#     "Choose pollutant",
#     ["aqi_value", "pm25_aqi_value", "no2_aqi_value", "co_aqi_value"],
# )

# # aggregate
# agg = base_df.groupby("country", as_index=False)[metric].mean()

# fig = px.choropleth(
#     agg,
#     locations="country",
#     locationmode="country names",
#     color=metric,
#     title="Global Pollution Levels",
#     color_continuous_scale="RdYlBu_r",
# )

# fig.update_geos(showframe=False, projection_type="natural earth")
# st.plotly_chart(fig, use_container_width=True)

#__________________

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.merged_dataset import load_merged_dataset
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------------
# 1. Load unified global dataset
# ---------------------------------------------------------
df = load_merged_dataset()

header(
    "🗺 Global Air Pollution Map",
    "Explore spatial patterns using choropleth mapping."
)

if df is None or df.empty:
    st.error("Could not load merged dataset.")
    st.stop()

# ---------------------------------------------------------
# 2. Detect pollutant columns automatically
# ---------------------------------------------------------
def find_pollutant_columns(df):
    candidates = [
        "aqi_value",
        "pm25_aqi_value", "pm10_aqi_value",
        "no2_aqi_value", "ozone_aqi_value",
        "co_aqi_value",
        # fallback: any column ending with _aqi_value
    ]

    detected = [c for c in candidates if c in df.columns]

    # Add AUTO-detect (_aqi_value)
    detected += [c for c in df.columns if c.endswith("_aqi_value")]

    # Remove duplicates
    detected = list(dict.fromkeys(detected))

    return detected


pollutant_columns = find_pollutant_columns(df)

if not pollutant_columns:
    st.error("No pollutant AQI columns detected in dataset.")
    st.stop()

# ---------------------------------------------------------
# 3. Select pollutant to map
# ---------------------------------------------------------
selected_metric = st.selectbox(
    "Choose pollutant to visualize:",
    pollutant_columns,
    format_func=lambda x: x.replace("_", " ").upper()
)

# ---------------------------------------------------------
# 4. Ensure country column exists
# ---------------------------------------------------------
country_col = None
for c in ["country", "Country", "Entity", "entity"]:
    if c in df.columns:
        country_col = c
        break

if not country_col:
    st.error("The dataset does not contain any country identifier column.")
    st.stop()

df["country"] = df[country_col]

# ---------------------------------------------------------
# 5. Aggregate pollutant values by country
# ---------------------------------------------------------
agg = (
    df[["country", selected_metric]]
    .groupby("country", as_index=False)
    .mean()
    .sort_values(selected_metric, ascending=False)
)

# ---------------------------------------------------------
# 6. Draw Choropleth Map
# ---------------------------------------------------------
fig = px.choropleth(
    agg,
    locations="country",
    locationmode="country names",
    color=selected_metric,
    title=f"Global Levels — {selected_metric.replace('_', ' ').upper()}",
    color_continuous_scale="RdYlBu_r",
)

fig.update_geos(showframe=False, projection_type="natural earth")
fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 7. Show Data Table
# ---------------------------------------------------------
st.markdown("### 📄 Data Summary (Country-Average)")
st.dataframe(agg, use_container_width=True)

