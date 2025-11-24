# import streamlit as st
# import os
# import plotly.express as px
# import pandas as pd

# # Function to load custom CSS (ensure it's loaded for every page)
# def load_css():
#     with open("styles/custom.css") as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# # Load the CSS in each page (this ensures the styles are applied across pages)
# load_css()

# from utils.data_loader import load_raw_dataset, load_processed_dataset


# st.set_page_config(layout="wide")

# # Load all datasets
# raw_g, raw_p = load_raw_dataset()
# processed_df = load_processed_dataset()


# # ----------------------------------------------------------
# # MODE SELECTOR
# # ----------------------------------------------------------
# view_mode = st.radio(
#     "Select data view:",
#     ["Before Processing", "After Processing", "Compare Before vs After"],
#     horizontal=True
# )

# st.title("🗺 Global Air Pollution Map")
# st.caption("Explore spatial patterns using raw and processed AQI datasets.")


# # =====================================================================
# # 🟥 MODE 1 — BEFORE PROCESSING (RAW) — NOW WITH MAPPING
# # =====================================================================
# if view_mode == "Before Processing":

#     st.subheader("📄 Raw Global Air Pollution Dataset (Before Processing)")
#     st.dataframe(raw_g, use_container_width=True)

#     st.subheader("🌍 Raw PM2.5 WHO Dataset")
#     st.dataframe(raw_p, use_container_width=True)

#     st.markdown("---")

#     # Raw pollutant columns
#     raw_pollutants = [
#         "AQI Value",
#         "PM2.5 AQI Value",
#         "NO2 AQI Value",
#         "Ozone AQI Value",
#         "CO AQI Value",
#     ]

#     available_raw_cols = [c for c in raw_pollutants if c in raw_g.columns]

#     st.subheader("🧪 Choose Raw Pollutant to Map")
#     selected_raw = st.selectbox("Pollutant:", available_raw_cols)

#     # Aggregate by country
#     raw_agg = (
#         raw_g.groupby("Country", as_index=False)[selected_raw].mean()
#     )

#     # Choropleth map
#     fig = px.choropleth(
#         raw_agg,
#         locations="Country",
#         locationmode="country names",
#         color=selected_raw,
#         title=f"Raw Data Map — {selected_raw}",
#         color_continuous_scale="RdYlBu_r",
#     )

#     fig.update_geos(showframe=False, projection_type="natural earth")
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Insight Section
#     mean_val = raw_agg[selected_raw].mean()
#     max_country = raw_agg.loc[raw_agg[selected_raw].idxmax(), "Country"]
#     max_val = raw_agg[selected_raw].max()

#     st.markdown(f"""
#     ### 📘 Insight  
#     - The average **{selected_raw}** level across all countries is `{mean_val:.2f}`.  
#     - The highest recorded value is in **{max_country}**, with a value of `{max_val:.2f}`.  
#     - Countries with darker shades indicate higher pollutant concentration and greater potential health risks.  
#     """)
   
#     st.stop()


# # =====================================================================
# # 🟩 MODE 2 — AFTER PROCESSING
# # =====================================================================
# if view_mode == "After Processing":

#     st.subheader("📄 Processed Dataset (After Cleaning & Merging)")
#     st.dataframe(processed_df, use_container_width=True)

#     # Detect AQI cols
#     pollutant_cols = [c for c in processed_df.columns if c.endswith("_aqi_value") or c == "pm25_value"]

#     selected = st.selectbox("Select pollutant to map:", pollutant_cols)

#     agg = (
#         processed_df.groupby("country", as_index=False)[selected].mean()
#     )

#     fig = px.choropleth(
#         agg,
#         locations="country",
#         locationmode="country names",
#         color=selected,
#         title=f"Processed Map — {selected}",
#         color_continuous_scale="RdYlBu_r",
#     )

#     fig.update_geos(showframe=False)
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Insight Section
#     mean_val = agg[selected].mean()
#     max_country = agg.loc[agg[selected].idxmax(), "country"]
#     max_val = agg[selected].max()

#     st.markdown(f"""
#     ### 📘 Insight  
#     - The processed dataset shows an average **{selected}** value of `{mean_val:.2f}` across all countries.  
#     - **{max_country}** records the highest pollution level after normalisation (`{max_val:.2f}`).  
#     - The processed map displays scaled/cleaned values, enabling more accurate cross-country comparison.  
#     """)

#     st.stop()


# # =====================================================================
# # 🟧 MODE 3 — COMPARE BEFORE vs AFTER
# # =====================================================================
# if view_mode == "Compare Before vs After":

#     st.header("📊 Before vs After Data Processing Comparison")

#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Before Processing")
#         st.dataframe(raw_g.head(), use_container_width=True)

#     with col2:
#         st.subheader("After Processing")
#         st.dataframe(processed_df.head(), use_container_width=True)

#     st.subheader("🔍 Column Comparison")
#     before_cols = set(raw_g.columns)
#     after_cols = set(processed_df.columns)

#     colA, colB = st.columns(2)
#     with colA:
#         st.write("🟥 **Raw Columns Only:**")
#         st.write(list(before_cols - after_cols))

#     with colB:
#         st.write("🟩 **Processed Columns Only:**")
#         st.write(list(after_cols - before_cols))

#     # Stats comparison
#     st.subheader("📈 Pollutant Summary Statistics (Before vs After)")
#     summary_before = raw_g.describe(include='all')
#     summary_after = processed_df.describe(include='all')

#     st.write("### Before Processing")
#     st.dataframe(summary_before)

#     st.write("### After Processing")
#     st.dataframe(summary_after)

#     # Comparison Insight
#     st.markdown("""
#     ### 📘 Interpretation  
#     - The *Before Processing* dataset may contain inconsistencies, missing values, or unscaled pollutant readings.  
#     - The *After Processing* dataset reflects cleaned, standardised, and merged information for improved accuracy.  
#     - Differences in column structure highlight transformations such as renaming, normalisation, and risk-index preparation.  
#     """)

    #_________________________________________


import streamlit as st
import os
import plotly.express as px
import pandas as pd

# Function to load custom CSS (ensure it's loaded for every page)
def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

from utils.data_loader import load_raw_dataset, load_processed_dataset

st.set_page_config(layout="wide")

# Load all datasets
raw_g, raw_p = load_raw_dataset()
processed_df = load_processed_dataset()

# Pollutant info box (shared across pages)
pollutant_info = {
    "AQI Value": "General Air Quality Index, representing overall air pollution.",
    "PM2.5 AQI Value": "Fine inhalable particles (<2.5 µm). Highly harmful as they penetrate deep into lungs.",
    "NO2 AQI Value": "Nitrogen dioxide, mainly from vehicle and industrial emissions.",
    "Ozone AQI Value": "Ground-level ozone formed via photochemical reactions; irritates lungs.",
    "CO AQI Value": "Carbon monoxide from combustion and vehicles; reduces oxygen delivery in the body."
}

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
# 🟥 MODE 1 — BEFORE PROCESSING
# =====================================================================
if view_mode == "Before Processing":

    st.subheader("📄 Raw Global Air Pollution Dataset (Before Processing)")
    st.dataframe(raw_g, use_container_width=True)

    st.subheader("🌍 Raw PM2.5 WHO Dataset")
    st.dataframe(raw_p, use_container_width=True)

    st.markdown("---")

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

    # Pollutant description
    st.info(f"**{selected_raw}:** {pollutant_info.get(selected_raw, 'No description available.')}")

    raw_agg = raw_g.groupby("Country", as_index=False)[selected_raw].mean()

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

    # Legend explanation
    st.caption("🔵 Blue = Lower pollution  |  🔴 Red = Higher pollution")

    # About this map
    with st.expander("ℹ️ About This Map"):
        st.write("""
        This map shows the raw pollutant concentration averaged by country.
        Darker red regions indicate higher pollution levels. These raw values
        reflect unprocessed data directly from the input dataset.
        """)

    # Insights + Stats
    mean_val = raw_agg[selected_raw].mean()
    max_country = raw_agg.loc[raw_agg[selected_raw].idxmax(), "Country"]
    max_val = raw_agg[selected_raw].max()
    desc = raw_agg[selected_raw].describe()

    direction = "↑ Higher than average" if max_val > mean_val else "↓ Lower than average"

    st.markdown(f"""
    ### 📘 Insight  
    - Global average **{selected_raw}**: `{mean_val:.2f}`  
    - Highest level: **{max_country}** (`{max_val:.2f}`) — **{direction}**  
    - Median: `{desc['50%']:.2f}`  
    - Standard deviation: `{desc['std']:.2f}`  
    """)

    st.stop()


# =====================================================================
# 🟩 MODE 2 — AFTER PROCESSING
# =====================================================================
if view_mode == "After Processing":

    st.subheader("📄 Processed Dataset (After Cleaning & Merging)")
    st.dataframe(processed_df, use_container_width=True)

    pollutant_cols = [c for c in processed_df.columns if c.endswith("_aqi_value") or c == "pm25_value"]
    selected = st.selectbox("Select pollutant to map:", pollutant_cols)

    # Pollutant description
    cleaned_name = selected.replace("_aqi_value", "").replace("_", "").upper()
    st.info(f"**{cleaned_name}:** Represents pollutant levels after cleaning, scaling, and merging.")

    agg = processed_df.groupby("country", as_index=False)[selected].mean()

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

    # Legend explanation
    st.caption("🔵 Blue = Lower processed value  |  🔴 Red = Higher processed value")

    with st.expander("ℹ️ About This Map"):
        st.write("""
        This map shows cleaned and normalised pollutant values. These adjusted
        values allow fairer cross-country comparison by removing raw data
        inconsistencies and scaling differences.
        """)

    # Insights + stats
    mean_val = agg[selected].mean()
    max_country = agg.loc[agg[selected].idxmax(), "country"]
    max_val = agg[selected].max()
    desc = agg[selected].describe()

    direction = "↑ Above global mean" if max_val > mean_val else "↓ Below global mean"

    st.markdown(f"""
    ### 📘 Insight  
    - Global average (processed) for **{selected}**: `{mean_val:.2f}`  
    - Highest value: **{max_country}** (`{max_val:.2f}`) — **{direction}**  
    - Median: `{desc['50%']:.2f}`  
    - Standard deviation: `{desc['std']:.2f}`  
    """)

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
    st.write("### Before Processing")
    st.dataframe(raw_g.describe(include='all'))

    st.write("### After Processing")
    st.dataframe(processed_df.describe(include='all'))

    st.markdown("""
    ### 📘 Interpretation  
    - Raw data may contain inconsistencies, missing values, or unscaled pollutant readings.  
    - Processed data reflects cleaned, standardised, and merged values for improved accuracy.  
    - The difference in column names highlights transformations such as renaming, normalisation, and preparation for risk-index computation.  
    """)


