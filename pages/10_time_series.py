# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# from utils.merged_datasets import load_merged_dataset
# from utils.merged_datasets import load_master_dataset

# from utils.loader import load_base_data
# from utils.ui import header

# st.set_page_config(layout="wide")

# # ---------------------------------------------------------
# # 1. Load merged global dataset
# # ---------------------------------------------------------
# df = load_master_data()

# # df = load_base_data()

# header(
#     "📈 Time-Series Explorer",
#     "How pollution levels evolve over time by country and region."
# )

# if df is None or df.empty:
#     st.error("Global dataset could not be loaded.")
#     st.stop()

# # ---------------------------------------------------------
# # 2. Normalise YEAR column
# # ---------------------------------------------------------
# year_col = None
# for candidate in ["Year", "year", "YEAR"]:
#     if candidate in df.columns:
#         year_col = candidate
#         break

# if year_col is None:
#     st.error("The dataset must contain a 'Year' (or 'year') column.")
#     st.stop()

# df["year"] = pd.to_numeric(df[year_col], errors="coerce")
# df = df.dropna(subset=["year"])
# df["year"] = df["year"].astype(int)

# # ---------------------------------------------------------
# # 3. Normalise COUNTRY column
# # ---------------------------------------------------------
# country_col = None
# for candidate in ["country", "Country", "Entity", "entity"]:
#     if candidate in df.columns:
#         country_col = candidate
#         break

# if country_col is None:
#     st.error("The dataset must contain a country / entity column.")
#     st.stop()

# df["country"] = df[country_col].astype(str)

# # ---------------------------------------------------------
# # 4. Detect pollutant columns automatically
# # ---------------------------------------------------------
# def find_first_existing_column(candidates):
#     for c in candidates:
#         if c in df.columns:
#             return c
#     return None

# pollutant_meta = {}

# # PM2.5
# pm25_col = find_first_existing_column([
#     "pm25", "pm25_concentration", "pm25_mean",
#     "PM2.5", "PM₂․₅",
#     "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total"
# ])
# if pm25_col:
#     pollutant_meta["PM₂.₅ (Fine Particles)"] = {
#         "column": pm25_col,
#         "color": "#2563EB",
#         "unit": "μg/m³",
#     }

# # PM10
# pm10_col = find_first_existing_column([
#     "pm10", "PM10", "pm10_concentration"
# ])
# if pm10_col:
#     pollutant_meta["PM₁₀ (Coarse Particles)"] = {
#         "column": pm10_col,
#         "color": "#f97316",
#         "unit": "μg/m³",
#     }

# # NO2
# no2_col = find_first_existing_column([
#     "no2", "NO2", "no2_mean", "no2_concentration"
# ])
# if no2_col:
#     pollutant_meta["NO₂ (Nitrogen Dioxide)"] = {
#         "column": no2_col,
#         "color": "#F59E0B",
#         "unit": "μg/m³",
#     }

# # Ozone
# o3_col = find_first_existing_column([
#     "o3", "O3", "ozone", "ozone_mean", "ozone_concentration"
# ])
# if o3_col:
#     pollutant_meta["O₃ (Ozone)"] = {
#         "column": o3_col,
#         "color": "#0EA5E9",
#         "unit": "μg/m³",
#     }

# # CO
# co_col = find_first_existing_column([
#     "co", "CO", "co_mean", "co_concentration"
# ])
# if co_col:
#     pollutant_meta["CO (Carbon Monoxide)"] = {
#         "column": co_col,
#         "color": "#7C3AED",
#         "unit": "mg/m³",
#     }

# if not pollutant_meta:
#     st.error("Could not detect any pollutant concentration columns in the dataset.")
#     st.stop()

# # ---------------------------------------------------------
# # 5. Compute risk index for dual-axis plots (optional)
# #    - scaled 0–1 across the whole dataset
# #    - equal weights for all detected pollutants
# # ---------------------------------------------------------
# pollutant_cols = [meta["column"] for meta in pollutant_meta.values()]
# scaled = {}
# for col in pollutant_cols:
#     series = pd.to_numeric(df[col], errors="coerce")
#     lo, hi = series.min(), series.max()
#     if pd.isna(lo) or pd.isna(hi) or hi <= lo:
#         scaled[col] = np.zeros(len(series))
#     else:
#         scaled[col] = (series - lo) / (hi - lo)

# scaled_df = pd.DataFrame(scaled)

# if not scaled_df.empty:
#     weight = 1.0 / len(scaled_df.columns)
#     df["risk_index_ts"] = np.zeros(len(df))
#     for col in scaled_df.columns:
#         df["risk_index_ts"] += scaled_df[col].fillna(0) * weight
# else:
#     df["risk_index_ts"] = np.nan

# # ---------------------------------------------------------
# # 6. Sidebar Controls
# # ---------------------------------------------------------
# st.sidebar.header("🔎 Time-Series Controls")

# view_mode = st.sidebar.radio(
#     "View mode:",
#     ["Global Trend", "Single Country", "Compare Countries", "Regional Trend"]
# )

# pollutant_label = st.sidebar.selectbox(
#     "Pollutant:",
#     list(pollutant_meta.keys())
# )
# pollutant_info = pollutant_meta[pollutant_label]
# value_col = pollutant_info["column"]
# unit = pollutant_info["unit"]
# line_color = pollutant_info["color"]

# show_risk = st.sidebar.checkbox("Show risk index on secondary axis", value=True)

# # Optional global year filter
# min_year, max_year = int(df["year"].min()), int(df["year"].max())
# year_range = st.sidebar.slider(
#     "Year range:",
#     min_value=min_year,
#     max_value=max_year,
#     value=(min_year, max_year),
#     step=1,
# )
# df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

# # Helper to build dual-axis figure
# def dual_axis_time_series(
#     data,
#     title_prefix="",
#     color=line_color,
#     group_by=None,
# ):
#     """
#     If group_by is None: single line.
#     If group_by is not None: multiple lines (one per group) on the PRIMARY axis,
#     single aggregated risk_index on secondary.
#     """
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
#     if group_by is None:
#         # Single series
#         series = data.sort_values("year")
#         fig.add_trace(
#             go.Scatter(
#                 x=series["year"],
#                 y=series[value_col],
#                 mode="lines+markers",
#                 name=pollutant_label,
#                 line=dict(color=color),
#             ),
#             secondary_y=False,
#         )

#         if show_risk and "risk_index_ts" in series.columns:
#             fig.add_trace(
#                 go.Scatter(
#                     x=series["year"],
#                     y=series["risk_index_ts"],
#                     mode="lines+markers",
#                     name="Risk Index",
#                     line=dict(color="#EF4444", dash="dash"),
#                 ),
#                 secondary_y=True,
#             )

#     else:
#         # Grouped (countries or regions)
#         for g, subset in data.groupby(group_by):
#             subset = subset.sort_values("year")
#             fig.add_trace(
#                 go.Scatter(
#                     x=subset["year"],
#                     y=subset[value_col],
#                     mode="lines+markers",
#                     name=str(g),
#                 ),
#                 secondary_y=False,
#             )

#         if show_risk and "risk_index_ts" in data.columns:
#             risk_df = (
#                 data.groupby("year")["risk_index_ts"]
#                 .mean()
#                 .reset_index()
#                 .sort_values("year")
#             )
#             fig.add_trace(
#                 go.Scatter(
#                     x=risk_df["year"],
#                     y=risk_df["risk_index_ts"],
#                     mode="lines",
#                     name="Avg Risk Index",
#                     line=dict(color="#EF4444", width=2, dash="dash"),
#                 ),
#                 secondary_y=True,
#             )

#     title = f"{title_prefix} {pollutant_label} Trend Over Time".strip()
#     fig.update_layout(
#         title=title,
#         margin=dict(l=40, r=40, t=60, b=40),
#         legend_title_text="",
#     )
#     fig.update_xaxes(title_text="Year")
#     fig.update_yaxes(
#         title_text=f"{pollutant_label} ({unit})",
#         secondary_y=False,
#     )
#     if show_risk:
#         fig.update_yaxes(
#             title_text="Risk Index (0–1)",
#             secondary_y=True,
#         )

#     return fig

# # ---------------------------------------------------------
# # 7. VIEW MODES
# # ---------------------------------------------------------

# # ---------- GLOBAL TREND ----------
# if view_mode == "Global Trend":
#     st.subheader(f"🌍 Global {pollutant_label} Trend Over Time")

#     global_df = (
#         df.groupby("year")[["year", value_col, "risk_index_ts"]]
#         .mean()
#         .reset_index()
#     )

#     fig = dual_axis_time_series(
#         global_df,
#         title_prefix="Global",
#         group_by=None,
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     summary = global_df[["year", value_col]].rename(
#         columns={value_col: "mean_level"}
#     )
#     st.markdown("### 📊 Summary Statistics (Global)")
#     st.dataframe(summary, use_container_width=True)

# # ---------- SINGLE COUNTRY ----------
# elif view_mode == "Single Country":
#     st.subheader(f"🇺🇳 Single Country — {pollutant_label} Over Time")

#     countries = sorted(df["country"].unique())
#     country = st.selectbox("Select a country:", countries)

#     cdf = df[df["country"] == country]

#     fig = dual_axis_time_series(
#         cdf,
#         title_prefix=country,
#         group_by=None,
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     summary = (
#         cdf.groupby("year")[value_col]
#         .agg(mean_level="mean", min_level="min", max_level="max")
#         .reset_index()
#     )
#     st.markdown(f"### 📊 Summary Statistics — {country}")
#     st.dataframe(summary, use_container_width=True)

# # ---------- COMPARE COUNTRIES ----------
# elif view_mode == "Compare Countries":
#     st.subheader(f"🌐 Compare Countries — {pollutant_label}")

#     countries = sorted(df["country"].unique())
#     default_selection = [c for c in ["Afghanistan", "India", "China"] if c in countries]
#     selected = st.multiselect(
#         "Choose countries to compare:",
#         countries,
#         default=default_selection,
#     )

#     if not selected:
#         st.info("Select at least one country to compare.")
#     else:
#         comp_df = df[df["country"].isin(selected)]
#         fig = dual_axis_time_series(
#             comp_df,
#             title_prefix="Countries",
#             group_by="country",
#         )
#         st.plotly_chart(fig, use_container_width=True)

#         summary = (
#             comp_df.groupby(["country", "year"])[value_col]
#             .mean()
#             .reset_index()
#             .rename(columns={value_col: "mean_level"})
#         )
#         st.markdown("### 📊 Summary by Country & Year")
#         st.dataframe(summary, use_container_width=True)

# # ---------- REGIONAL TREND ----------
# elif view_mode == "Regional Trend":
#     if "region" not in df.columns:
#         st.warning("No 'region' column found in dataset, so regional view is disabled.")
#     else:
#         st.subheader(f"🌎 Regional {pollutant_label} Trends")

#         all_regions = sorted(df["region"].dropna().unique())
#         selected_regions = st.multiselect(
#             "Select regions:",
#             all_regions,
#             default=all_regions,
#         )

#         if not selected_regions:
#             st.info("Select at least one region to view trends.")
#         else:
#             rdf = df[df["region"].isin(selected_regions)]

#             fig = dual_axis_time_series(
#                 rdf,
#                 title_prefix="Regions",
#                 group_by="region",
#             )
#             st.plotly_chart(fig, use_container_width=True)

#             summary = (
#                 rdf.groupby(["region", "year"])[value_col]
#                 .mean()
#                 .reset_index()
#                 .rename(columns={value_col: "mean_level"})
#             )
#             st.markdown("### 📊 Summary by Region & Year")
#             st.dataframe(summary, use_container_width=True)

#______________________________________________

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.merged_datasets import load_master_dataset
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------------
# 1. Load merged global dataset (MASTER)
# ---------------------------------------------------------
df = load_master_dataset()

header(
    "📈 Time-Series Explorer",
    "How pollution levels evolve over time by country and region."
)

if df is None or df.empty:
    st.error("Global dataset could not be loaded.")
    st.stop()

# ---------------------------------------------------------
# 2. Normalise YEAR column
# ---------------------------------------------------------
year_col = None
for candidate in ["Year", "year", "YEAR"]:
    if candidate in df.columns:
        year_col = candidate
        break

if year_col is None:
    st.error("The dataset must contain a 'Year' (or 'year') column.")
    st.stop()

df["year"] = pd.to_numeric(df[year_col], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# ---------------------------------------------------------
# 3. Normalise COUNTRY column
# ---------------------------------------------------------
country_col = None
for candidate in ["country", "Country", "Entity", "entity"]:
    if candidate in df.columns:
        country_col = candidate
        break

if country_col is None:
    st.error("The dataset must contain a country / entity column.")
    st.stop()

df["country"] = df[country_col].astype(str)

# ---------------------------------------------------------
# 4. Ensure / assign region column (if possible)
# ---------------------------------------------------------
if "region" not in df.columns:
    try:
        from utils.regions import assign_region
        df["region"] = df["country"].apply(assign_region)
    except Exception:
        # if mapping module not available, still allow non-regional modes
        df["region"] = np.nan

# ---------------------------------------------------------
# 5. Detect pollutant columns automatically
# ---------------------------------------------------------
def find_first_existing_column(candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

pollutant_meta = {}

# PM2.5
pm25_col = find_first_existing_column([
    "pm25", "pm25_concentration", "pm25_mean",
    "PM2.5", "PM₂․₅",
    "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total"
])
if pm25_col:
    pollutant_meta["PM₂.₅ (Fine Particles)"] = {
        "column": pm25_col,
        "color": "#2563EB",
        "unit": "μg/m³",
    }

# PM10
pm10_col = find_first_existing_column([
    "pm10", "PM10", "pm10_concentration"
])
if pm10_col:
    pollutant_meta["PM₁₀ (Coarse Particles)"] = {
        "column": pm10_col,
        "color": "#f97316",
        "unit": "μg/m³",
    }

# NO2
no2_col = find_first_existing_column([
    "no2", "NO2", "no2_mean", "no2_concentration"
])
if no2_col:
    pollutant_meta["NO₂ (Nitrogen Dioxide)"] = {
        "column": no2_col,
        "color": "#F59E0B",
        "unit": "μg/m³",
    }

# Ozone
o3_col = find_first_existing_column([
    "o3", "O3", "ozone", "ozone_mean", "ozone_concentration"
])
if o3_col:
    pollutant_meta["O₃ (Ozone)"] = {
        "column": o3_col,
        "color": "#0EA5E9",
        "unit": "μg/m³",
    }

# CO
co_col = find_first_existing_column([
    "co", "CO", "co_mean", "co_concentration"
])
if co_col:
    pollutant_meta["CO (Carbon Monoxide)"] = {
        "column": co_col,
        "color": "#7C3AED",
        "unit": "mg/m³",
    }

if not pollutant_meta:
    st.error("Could not detect any pollutant concentration columns in the merged dataset.")
    st.stop()

# ---------------------------------------------------------
# 6. Compute risk index for time-series (0–1, equal weights)
# ---------------------------------------------------------
pollutant_cols = [meta["column"] for meta in pollutant_meta.values()]
scaled = {}

for col in pollutant_cols:
    if col not in df.columns:
        continue
    series = pd.to_numeric(df[col], errors="coerce")
    lo, hi = series.min(), series.max()
    if pd.isna(lo) or pd.isna(hi) or hi <= lo:
        scaled[col] = np.zeros(len(series))
    else:
        scaled[col] = (series - lo) / (hi - lo)

scaled_df = pd.DataFrame(scaled, index=df.index)

if not scaled_df.empty:
    weight = 1.0 / len(scaled_df.columns)
    df["risk_index_ts"] = np.zeros(len(df))
    for col in scaled_df.columns:
        df["risk_index_ts"] += scaled_df[col].fillna(0) * weight
else:
    df["risk_index_ts"] = np.nan

# ---------------------------------------------------------
# 7. Sidebar Controls
# ---------------------------------------------------------
st.sidebar.header("🔎 Time-Series Controls")

view_mode = st.sidebar.radio(
    "View mode:",
    ["Global Trend", "Single Country", "Compare Countries", "Regional Trend"]
)

pollutant_label = st.sidebar.selectbox(
    "Pollutant:",
    list(pollutant_meta.keys())
)
pollutant_info = pollutant_meta[pollutant_label]
value_col = pollutant_info["column"]
unit = pollutant_info["unit"]
line_color = pollutant_info["color"]

show_risk = st.sidebar.checkbox("Show risk index on secondary axis", value=True)

# Optional global year filter
min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1,
)
df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

# ---------------------------------------------------------
# 8. Helper: dual-axis time-series
# ---------------------------------------------------------
def dual_axis_time_series(
    data: pd.DataFrame,
    title_prefix: str = "",
    color: str = "#2563EB",
    group_by: str | None = None,
):
    """
    If group_by is None: single line.
    If group_by is not None: multiple lines on primary axis (one per group),
    and a single averaged risk_index_ts on secondary axis.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if group_by is None:
        series = data.sort_values("year")

        fig.add_trace(
            go.Scatter(
                x=series["year"],
                y=series[value_col],
                mode="lines+markers",
                name=pollutant_label,
                line=dict(color=color),
            ),
            secondary_y=False,
        )

        if show_risk and "risk_index_ts" in series.columns:
            fig.add_trace(
                go.Scatter(
                    x=series["year"],
                    y=series["risk_index_ts"],
                    mode="lines+markers",
                    name="Risk Index",
                    line=dict(color="#EF4444", dash="dash"),
                ),
                secondary_y=True,
            )

    else:
        for g, subset in data.groupby(group_by):
            subset = subset.sort_values("year")
            fig.add_trace(
                go.Scatter(
                    x=subset["year"],
                    y=subset[value_col],
                    mode="lines+markers",
                    name=str(g),
                ),
                secondary_y=False,
            )

        if show_risk and "risk_index_ts" in data.columns:
            risk_df = (
                data.groupby("year")["risk_index_ts"]
                .mean()
                .reset_index()
                .sort_values("year")
            )
            fig.add_trace(
                go.Scatter(
                    x=risk_df["year"],
                    y=risk_df["risk_index_ts"],
                    mode="lines",
                    name="Avg Risk Index",
                    line=dict(color="#EF4444", width=2, dash="dash"),
                ),
                secondary_y=True,
            )

    title = f"{title_prefix} {pollutant_label} Trend Over Time".strip()
    fig.update_layout(
        title=title,
        margin=dict(l=40, r=40, t=60, b=40),
        legend_title_text="",
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(
        title_text=f"{pollutant_label} ({unit})",
        secondary_y=False,
    )
    if show_risk:
        fig.update_yaxes(
            title_text="Risk Index (0–1)",
            secondary_y=True,
        )

    return fig

# ---------------------------------------------------------
# 9. VIEW MODES
# ---------------------------------------------------------

# ---------- GLOBAL TREND ----------
if view_mode == "Global Trend":
    st.subheader(f"🌍 Global {pollutant_label} Trend Over Time")

    global_df = (
        df.groupby("year")[[value_col, "risk_index_ts"]]
        .mean()
        .reset_index()
        .sort_values("year")
    )
    fig = dual_axis_time_series(
        global_df,
        title_prefix="Global",
        group_by=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    summary = global_df[["year", value_col]].rename(
        columns={value_col: "mean_level"}
    )
    st.markdown("### 📊 Summary Statistics (Global)")
    st.dataframe(summary, use_container_width=True)

# ---------- SINGLE COUNTRY ----------
elif view_mode == "Single Country":
    st.subheader(f"🇺🇳 Single Country — {pollutant_label} Over Time")

    countries = sorted(df["country"].unique())
    country = st.selectbox("Select a country:", countries)

    cdf = df[df["country"] == country]

    fig = dual_axis_time_series(
        cdf,
        title_prefix=country,
        group_by=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    summary = (
        cdf.groupby("year")[value_col]
        .agg(mean_level="mean", min_level="min", max_level="max")
        .reset_index()
    )
    st.markdown(f"### 📊 Summary Statistics — {country}")
    st.dataframe(summary, use_container_width=True)

# ---------- COMPARE COUNTRIES ----------
elif view_mode == "Compare Countries":
    st.subheader(f"🌐 Compare Countries — {pollutant_label}")

    countries = sorted(df["country"].unique())
    default_selection = [c for c in ["Afghanistan", "India", "China"] if c in countries]

    selected = st.multiselect(
        "Choose countries to compare:",
        countries,
        default=default_selection,
    )

    if not selected:
        st.info("Select at least one country to compare.")
    else:
        comp_df = df[df["country"].isin(selected)]

        fig = dual_axis_time_series(
            comp_df,
            title_prefix="Countries",
            group_by="country",
        )
        st.plotly_chart(fig, use_container_width=True)

        summary = (
            comp_df.groupby(["country", "year"])[value_col]
            .mean()
            .reset_index()
            .rename(columns={value_col: "mean_level"})
        )
        st.markdown("### 📊 Summary by Country & Year")
        st.dataframe(summary, use_container_width=True)

# ---------- REGIONAL TREND ----------
elif view_mode == "Regional Trend":
    if "region" not in df.columns or df["region"].isna().all():
        st.warning("No valid 'region' data found in dataset, so regional view is disabled.")
    else:
        st.subheader(f"🌎 Regional {pollutant_label} Trends")

        all_regions = sorted(df["region"].dropna().unique())
        selected_regions = st.multiselect(
            "Select regions:",
            all_regions,
            default=all_regions,
        )

        if not selected_regions:
            st.info("Select at least one region to view trends.")
        else:
            rdf = df[df["region"].isin(selected_regions)]

            fig = dual_axis_time_series(
                rdf,
                title_prefix="Regions",
                group_by="region",
            )
            st.plotly_chart(fig, use_container_width=True)

            summary = (
                rdf.groupby(["region", "year"])[value_col]
                .mean()
                .reset_index()
                .rename(columns={value_col: "mean_level"})
            )
            st.markdown("### 📊 Summary by Region & Year")
            st.dataframe(summary, use_container_width=True)
