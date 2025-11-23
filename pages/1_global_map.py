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
from utils.data_loader import load_raw_dataset, load_merged_dataset

from utils.ui import header

# st.set_page_config(layout="wide")

# # ---------------------------------------------------------
# # 1. Load unified global dataset
# # ---------------------------------------------------------
# df = load_merged_dataset()

# header(
#     "🗺 Global Air Pollution Map",
#     "Explore spatial patterns using choropleth mapping."
# )

# if df is None or df.empty:
#     st.error("Could not load merged dataset.")
#     st.stop()

# # ---------------------------------------------------------
# # 2. Detect pollutant columns automatically
# # ---------------------------------------------------------
# def find_pollutant_columns(df):
#     candidates = [
#         "aqi_value",
#         "pm25_aqi_value", "pm10_aqi_value",
#         "no2_aqi_value", "ozone_aqi_value",
#         "co_aqi_value",
#         # fallback: any column ending with _aqi_value
#     ]

#     detected = [c for c in candidates if c in df.columns]

#     # Add AUTO-detect (_aqi_value)
#     detected += [c for c in df.columns if c.endswith("_aqi_value")]

#     # Remove duplicates
#     detected = list(dict.fromkeys(detected))

#     return detected


# pollutant_columns = find_pollutant_columns(df)

# if not pollutant_columns:
#     st.error("No pollutant AQI columns detected in dataset.")
#     st.stop()

# # ---------------------------------------------------------
# # 3. Select pollutant to map
# # ---------------------------------------------------------
# selected_metric = st.selectbox(
#     "Choose pollutant to visualize:",
#     pollutant_columns,
#     format_func=lambda x: x.replace("_", " ").upper()
# )

# # ---------------------------------------------------------
# # 4. Ensure country column exists
# # ---------------------------------------------------------
# country_col = None
# for c in ["country", "Country", "Entity", "entity"]:
#     if c in df.columns:
#         country_col = c
#         break

# if not country_col:
#     st.error("The dataset does not contain any country identifier column.")
#     st.stop()

# df["country"] = df[country_col]

# # ---------------------------------------------------------
# # 5. Aggregate pollutant values by country
# # ---------------------------------------------------------
# agg = (
#     df[["country", selected_metric]]
#     .groupby("country", as_index=False)
#     .mean()
#     .sort_values(selected_metric, ascending=False)
# )

# # ---------------------------------------------------------
# # 6. Draw Choropleth Map
# # ---------------------------------------------------------
# fig = px.choropleth(
#     agg,
#     locations="country",
#     locationmode="country names",
#     color=selected_metric,
#     title=f"Global Levels — {selected_metric.replace('_', ' ').upper()}",
#     color_continuous_scale="RdYlBu_r",
# )

# fig.update_geos(showframe=False, projection_type="natural earth")
# fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

# st.plotly_chart(fig, use_container_width=True)

# # ---------------------------------------------------------
# # 7. Show Data Table
# # ---------------------------------------------------------
# st.markdown("### 📄 Data Summary (Country-Average)")
# st.dataframe(agg, use_container_width=True)

#____

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import (
    load_raw_dataset,
    load_processed_dataset
)

st.set_page_config(layout="wide")

# Load all datasets
raw_g, raw_p = load_raw_dataset()
processed_df = load_processed_dataset()


# ----------------------------------------------------------
# MODE SELECTOR
# ----------------------------------------------------------
view_mode = st.radio(
    "Select data view:",
    ["Before Processing", "After Processing", "Compare Before vs After"],
    horizontal=True
)

st.title("🗺 Global Air Pollution Map")
st.caption("Explore spatial patterns using raw and processed AQI datasets.")


# =====================================================================
# 🟥 MODE 1 — BEFORE PROCESSING (RAW) — NOW WITH MAPPING
# =====================================================================
if view_mode == "Before Processing":

    st.subheader("📄 Raw Global Air Pollution Dataset (Before Processing)")
    st.dataframe(raw_g, use_container_width=True)

    st.subheader("🌍 Raw PM2.5 WHO Dataset")
    st.dataframe(raw_p, use_container_width=True)

    st.markdown("---")

    # Raw pollutant columns
    raw_pollutants = [
        "AQI Value",
        "PM2.5 AQI Value",
        "NO2 AQI Value",
        "Ozone AQI Value",
        "CO AQI Value",
    ]

    available_raw_cols = [c for c in raw_pollutants if c in raw_g.columns]

    st.subheader("🧪 Choose Raw Pollutant to Map")
    selected_raw = st.selectbox("Pollutant:", available_raw_cols)

    # Aggregate by country
    raw_agg = (
        raw_g.groupby("Country", as_index=False)[selected_raw].mean()
    )

    # Choropleth map
    fig = px.choropleth(
        raw_agg,
        locations="Country",
        locationmode="country names",
        color=selected_raw,
        title=f"Raw Data Map — {selected_raw}",
        color_continuous_scale="RdYlBu_r",
    )

    fig.update_geos(showframe=False, projection_type="natural earth")
    st.plotly_chart(fig, use_container_width=True)

    st.stop()


# =====================================================================
# 🟩 MODE 2 — AFTER PROCESSING
# =====================================================================
if view_mode == "After Processing":

    st.subheader("📄 Processed Dataset (After Cleaning & Merging)")
    st.dataframe(processed_df, use_container_width=True)

    # Detect AQI cols
    pollutant_cols = [c for c in processed_df.columns if c.endswith("_aqi_value") or c == "pm25_value"]

    selected = st.selectbox("Select pollutant to map:", pollutant_cols)

    agg = (
        processed_df.groupby("country", as_index=False)[selected].mean()
    )

    fig = px.choropleth(
        agg,
        locations="country",
        locationmode="country names",
        color=selected,
        title=f"Processed Map — {selected}",
        color_continuous_scale="RdYlBu_r",
    )

    fig.update_geos(showframe=False)
    st.plotly_chart(fig, use_container_width=True)

    st.stop()


# =====================================================================
# 🟧 MODE 3 — COMPARE BEFORE vs AFTER
# =====================================================================
if view_mode == "Compare Before vs After":

    st.header("📊 Before vs After Data Processing Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Before Processing")
        st.dataframe(raw_g.head(), use_container_width=True)

    with col2:
        st.subheader("After Processing")
        st.dataframe(processed_df.head(), use_container_width=True)

    st.subheader("🔍 Column Comparison")
    before_cols = set(raw_g.columns)
    after_cols = set(processed_df.columns)

    colA, colB = st.columns(2)
    with colA:
        st.write("🟥 **Raw Columns Only:**")
        st.write(list(before_cols - after_cols))

    with colB:
        st.write("🟩 **Processed Columns Only:**")
        st.write(list(after_cols - before_cols))

    # Stats comparison
    st.subheader("📈 Pollutant Summary Statistics (Before vs After)")
    summary_before = raw_g.describe(include='all')
    summary_after = processed_df.describe(include='all')

    st.write("### Before Processing")
    st.dataframe(summary_before)

    st.write("### After Processing")
    st.dataframe(summary_after)

