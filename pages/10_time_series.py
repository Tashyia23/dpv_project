# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# from utils.merged_dataset import load_merged_dataset
# from utils.ui import header

# st.set_page_config(layout="wide")

# # ---------------------------------------------------------
# # 1. Load merged global dataset (MASTER)
# # ---------------------------------------------------------
# df = load_merged_dataset()

# header(
#     "📈 Time-Series Explorer",
#     "How pollution levels evolve over time by country and region (before vs after processing)."
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
# # 4. Ensure / assign region column (if possible)
# # ---------------------------------------------------------
# if "region" not in df.columns:
#     try:
#         from utils.regions import assign_region
#         df["region"] = df["country"].apply(assign_region)
#     except Exception:
#         df["region"] = np.nan

# # ---------------------------------------------------------
# # 5. Detect pollutant columns automatically (raw concentrations)
# # ---------------------------------------------------------
# def find_first_existing_column(candidates):
#     for c in candidates:
#         if c in df.columns:
#             return c
#     return None

# pollutant_meta: dict[str, dict] = {}

# # PM2.5
# pm25_col = find_first_existing_column([
#     "pm25", "pm25_concentration", "pm25_mean",
#     "PM2.5", "PM₂․₅",
#     "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total",
# ])
# if pm25_col:
#     pollutant_meta["PM₂.₅ (Fine Particles)"] = {
#         "column": pm25_col,
#         "color": "#2563EB",
#         "unit": "μg/m³",
#     }

# # PM10
# pm10_col = find_first_existing_column([
#     "pm10", "PM10", "pm10_concentration",
# ])
# if pm10_col:
#     pollutant_meta["PM₁₀ (Coarse Particles)"] = {
#         "column": pm10_col,
#         "color": "#f97316",
#         "unit": "μg/m³",
#     }

# # NO2
# no2_col = find_first_existing_column([
#     "no2", "NO2", "no2_mean", "no2_concentration",
# ])
# if no2_col:
#     pollutant_meta["NO₂ (Nitrogen Dioxide)"] = {
#         "column": no2_col,
#         "color": "#F59E0B",
#         "unit": "μg/m³",
#     }

# # Ozone
# o3_col = find_first_existing_column([
#     "o3", "O3", "ozone", "ozone_mean", "ozone_concentration",
# ])
# if o3_col:
#     pollutant_meta["O₃ (Ozone)"] = {
#         "column": o3_col,
#         "color": "#0EA5E9",
#         "unit": "μg/m³",
#     }

# # CO
# co_col = find_first_existing_column([
#     "co", "CO", "co_mean", "co_concentration",
# ])
# if co_col:
#     pollutant_meta["CO (Carbon Monoxide)"] = {
#         "column": co_col,
#         "color": "#7C3AED",
#         "unit": "mg/m³",
#     }

# if not pollutant_meta:
#     st.error("Could not detect any pollutant concentration columns in the merged dataset.")
#     st.stop()

# # ---------------------------------------------------------
# # 6. Compute risk index for time series (0–1, equal weights)
# # ---------------------------------------------------------
# pollutant_cols = [meta["column"] for meta in pollutant_meta.values()]
# scaled: dict[str, np.ndarray] = {}

# for col in pollutant_cols:
#     if col not in df.columns:
#         continue
#     series = pd.to_numeric(df[col], errors="coerce")
#     lo, hi = series.min(), series.max()
#     if pd.isna(lo) or pd.isna(hi) or hi <= lo:
#         scaled[col] = np.zeros(len(series))
#     else:
#         scaled[col] = (series - lo) / (hi - lo)

# scaled_df = pd.DataFrame(scaled, index=df.index)

# if not scaled_df.empty:
#     weight = 1.0 / len(scaled_df.columns)
#     df["risk_index_ts"] = np.zeros(len(df))
#     for col in scaled_df.columns:
#         df["risk_index_ts"] += scaled_df[col].fillna(0) * weight
# else:
#     df["risk_index_ts"] = np.nan

# # ---------------------------------------------------------
# # 7. BEFORE / AFTER TOGGLE (main view)
# # ---------------------------------------------------------
# data_mode = st.radio(
#     "Data View:",
#     [
#         "Before Processing (Raw Concentrations)",
#         "After Processing (Normalised Risk Index)",
#     ],
#     horizontal=True,
# )

# st.caption(
#     "• **Before**: plots original pollutant levels over time (optionally with risk index overlay).  \n"
#     "• **After**: plots the **composite risk index (0–1)** over time, with a selected pollutant on the secondary axis."
# )

# # ---------------------------------------------------------
# # 8. Sidebar Controls
# # ---------------------------------------------------------
# st.sidebar.header("🔎 Time-Series Controls")

# view_mode = st.sidebar.radio(
#     "View mode:",
#     ["Global Trend", "Single Country", "Compare Countries", "Regional Trend"],
# )

# pollutant_label = st.sidebar.selectbox("Pollutant:", list(pollutant_meta.keys()))
# pollutant_info = pollutant_meta[pollutant_label]
# value_col = pollutant_info["column"]
# unit = pollutant_info["unit"]
# line_color = pollutant_info["color"]

# # In BEFORE mode, default to showing risk overlay; in AFTER mode, default to showing pollutant overlay
# default_show_risk = True
# if data_mode.startswith("After"):
#     default_show_risk = True  # we want both risk + pollutant

# show_secondary = st.sidebar.checkbox(
#     "Show secondary series (risk / pollutant)", value=default_show_risk
# )

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

# # ---------------------------------------------------------
# # 9. Helper: dual-axis time-series
# # ---------------------------------------------------------
# def dual_axis_time_series(
#     data: pd.DataFrame,
#     title_prefix: str = "",
#     color: str = "#2563EB",
#     group_by: str | None = None,
# ):
#     """
#     - BEFORE mode:
#         primary  = pollutant (value_col), secondary = risk_index_ts (if enabled)
#     - AFTER mode:
#         primary  = risk_index_ts, secondary = pollutant (value_col, if enabled)
#     """
#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     # Decide which is primary vs secondary based on data_mode
#     if data_mode.startswith("Before"):
#         primary_col = value_col
#         primary_name = pollutant_label
#         primary_unit = unit
#         primary_color = color

#         secondary_col = "risk_index_ts" if show_secondary and "risk_index_ts" in data.columns else None
#         secondary_name = "Risk Index"
#         secondary_color = "#EF4444"
#         secondary_unit = "0–1"
#     else:
#         primary_col = "risk_index_ts"
#         primary_name = "Risk Index"
#         primary_unit = "0–1"
#         primary_color = "#EF4444"

#         secondary_col = value_col if show_secondary and value_col in data.columns else None
#         secondary_name = pollutant_label
#         secondary_color = color
#         secondary_unit = unit

#     # Helper to add a line (optionally grouped)
#     def add_primary_traces(group_col: str | None):
#         if group_col is None:
#             series = data.sort_values("year")
#             fig.add_trace(
#                 go.Scatter(
#                     x=series["year"],
#                     y=series[primary_col],
#                     mode="lines+markers",
#                     name=primary_name,
#                     line=dict(color=primary_color),
#                 ),
#                 secondary_y=False,
#             )
#         else:
#             for g, subset in data.groupby(group_col):
#                 subset = subset.sort_values("year")
#                 fig.add_trace(
#                     go.Scatter(
#                         x=subset["year"],
#                         y=subset[primary_col],
#                         mode="lines+markers",
#                         name=str(g),
#                     ),
#                     secondary_y=False,
#                 )

#     # Primary series
#     add_primary_traces(group_by)

#     # Secondary series (aggregated across groups if necessary)
#     if secondary_col is not None:
#         if group_by is None:
#             s = data.sort_values("year")
#             fig.add_trace(
#                 go.Scatter(
#                     x=s["year"],
#                     y=s[secondary_col],
#                     mode="lines+markers",
#                     name=secondary_name,
#                     line=dict(color=secondary_color, dash="dash"),
#                 ),
#                 secondary_y=True,
#             )
#         else:
#             sec_df = (
#                 data.groupby("year")[secondary_col]
#                 .mean()
#                 .reset_index()
#                 .sort_values("year")
#             )
#             fig.add_trace(
#                 go.Scatter(
#                     x=sec_df["year"],
#                     y=sec_df[secondary_col],
#                     mode="lines",
#                     name=f"Avg {secondary_name}",
#                     line=dict(color=secondary_color, width=2, dash="dash"),
#                 ),
#                 secondary_y=True,
#             )

#     title = f"{title_prefix} {primary_name} Trend Over Time".strip()
#     fig.update_layout(
#         title=title,
#         margin=dict(l=40, r=40, t=60, b=40),
#         legend_title_text="",
#     )
#     fig.update_xaxes(title_text="Year")
#     fig.update_yaxes(
#         title_text=f"{primary_name} ({primary_unit})",
#         secondary_y=False,
#     )
#     if secondary_col is not None:
#         fig.update_yaxes(
#             title_text=f"{secondary_name} ({secondary_unit})",
#             secondary_y=True,
#         )

#     return fig

# # ---------------------------------------------------------
# # 10. VIEW MODES
# # ---------------------------------------------------------

# # ---------- GLOBAL TREND ----------
# if view_mode == "Global Trend":
#     main_label = "Risk Index" if data_mode.startswith("After") else pollutant_label
#     st.subheader(f"🌍 Global {main_label} Trend Over Time")

#     agg_cols = ["risk_index_ts", value_col]
#     existing_cols = [c for c in agg_cols if c in df.columns]

#     global_df = (
#         df.groupby("year")[existing_cols]
#         .mean()
#         .reset_index()
#         .sort_values("year")
#     )

#     fig = dual_axis_time_series(
#         global_df,
#         title_prefix="Global",
#         group_by=None,
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     if data_mode.startswith("After"):
#         summary_col = "risk_index_ts"
#         summary_title = "Mean Risk Index"
#     else:
#         summary_col = value_col
#         summary_title = f"Mean {pollutant_label}"

#     summary = global_df[["year", summary_col]].rename(
#         columns={summary_col: "mean_level"}
#     )
#     st.markdown(f"### 📊 Summary Statistics (Global — {summary_title})")
#     st.dataframe(summary, use_container_width=True)

# # ---------- SINGLE COUNTRY ----------
# elif view_mode == "Single Country":
#     main_label = "Risk Index" if data_mode.startswith("After") else pollutant_label
#     st.subheader(f"🇺🇳 Single Country — {main_label} Over Time")

#     countries = sorted(df["country"].unique())
#     country = st.selectbox("Select a country:", countries)

#     cdf = df[df["country"] == country]

#     fig = dual_axis_time_series(
#         cdf,
#         title_prefix=country,
#         group_by=None,
#     )
#     st.plotly_chart(fig, use_container_width=True)

#     if data_mode.startswith("After"):
#         summary_col = "risk_index_ts"
#     else:
#         summary_col = value_col

#     summary = (
#         cdf.groupby("year")[summary_col]
#         .agg(mean_level="mean", min_level="min", max_level="max")
#         .reset_index()
#     )
#     st.markdown(f"### 📊 Summary Statistics — {country}")
#     st.dataframe(summary, use_container_width=True)

# # ---------- COMPARE COUNTRIES ----------
# elif view_mode == "Compare Countries":
#     main_label = "Risk Index" if data_mode.startswith("After") else pollutant_label
#     st.subheader(f"🌐 Compare Countries — {main_label}")

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

#         if data_mode.startswith("After"):
#             summary_col = "risk_index_ts"
#         else:
#             summary_col = value_col

#         summary = (
#             comp_df.groupby(["country", "year"])[summary_col]
#             .mean()
#             .reset_index()
#             .rename(columns={summary_col: "mean_level"})
#         )
#         st.markdown("### 📊 Summary by Country & Year")
#         st.dataframe(summary, use_container_width=True)

# # ---------- REGIONAL TREND ----------
# elif view_mode == "Regional Trend":
#     if "region" not in df.columns or df["region"].isna().all():
#         st.warning("No valid 'region' data found in dataset, so regional view is disabled.")
#     else:
#         main_label = "Risk Index" if data_mode.startswith("After") else pollutant_label
#         st.subheader(f"🌎 Regional {main_label} Trends")

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

#             if data_mode.startswith("After"):
#                 summary_col = "risk_index_ts"
#             else:
#                 summary_col = value_col

#             summary = (
#                 rdf.groupby(["region", "year"])[summary_col]
#                 .mean()
#                 .reset_index()
#                 .rename(columns={summary_col: "mean_level"})
#             )
#             st.markdown("### 📊 Summary by Region & Year")
#             st.dataframe(summary, use_container_width=True)

#_____________________________________________-

from utils.data_loader import load_processed_dataset

processed_df = load_processed_dataset()

st.write("### Columns in processed_df")
st.write(list(processed_df.columns))

st.write("### Preview of processed_df")
st.dataframe(processed_df.head())
