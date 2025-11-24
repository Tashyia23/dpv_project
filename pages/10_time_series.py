# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# from utils.data_loader import load_raw_dataset
# from utils.ui import header

# st.set_page_config(layout="wide")

# # ============================================================
# # 1. LOAD RAW DATASETS
# # ============================================================
# raw_g, raw_pm25 = load_raw_dataset()

# header(
#     "📈 Time-Series Explorer",
#     "Before: WHO PM₂.₅ concentration trends (μg/m³).  After: WHO-based health-risk index over time."
# )

# if raw_pm25 is None or raw_pm25.empty:
#     st.error("WHO PM₂.₅ dataset could not be loaded.")
#     st.stop()

# # ============================================================
# # 2. NORMALISE COLUMNS FROM WHO PM₂.₅ DATA
# # ============================================================
# df = raw_pm25.copy()

# # Identify year column
# year_col = None
# for cand in ["Year", "year", "YEAR"]:
#     if cand in df.columns:
#         year_col = cand
#         break

# if year_col is None:
#     st.error("The WHO PM₂.₅ dataset must contain a 'Year' column.")
#     st.stop()

# # Identify PM2.5 μg/m³ column
# pm_col = None
# for c in df.columns:
#     if "PM2.5" in c or "particulate matter" in c:
#         pm_col = c
#         break

# if pm_col is None:
#     st.error("Could not detect the PM₂.₅ concentration column in the WHO dataset.")
#     st.stop()

# # Clean year
# df["year"] = pd.to_numeric(df[year_col], errors="coerce")
# df = df.dropna(subset=["year"])
# df["year"] = df["year"].astype(int)

# # Normalise "Entity" -> "country"
# if "Entity" in df.columns:
#     df["country"] = df["Entity"].astype(str)
# else:
#     df["country"] = df.iloc[:, 0].astype(str)  # fallback

# # Load region mapping if available
# try:
#     from utils.regions import assign_region
#     df["region"] = df["country"].apply(assign_region)
# except Exception:
#     df["region"] = np.nan  # regional mode will be disabled if all NaN

# # Concentration (μg/m³)
# df["pm25_ugm3"] = pd.to_numeric(df[pm_col], errors="coerce")

# # Drop rows with missing PM2.5 values
# df = df.dropna(subset=["pm25_ugm3"])

# # ============================================================
# # 3. BUILD WHO-BASED HEALTH-RISK INDEX
# #    Risk index = PM2.5 / WHO_threshold (25 μg/m³ here)
# # ============================================================
# WHO_PM25_THRESHOLD = 25.0  # same as elsewhere in your dashboard

# df["risk_index"] = df["pm25_ugm3"] / WHO_PM25_THRESHOLD

# # ============================================================
# # 4. VIEW MODE (BEFORE vs AFTER PROCESSING)
# # ============================================================
# mode = st.radio(
#     "Select data view:",
#     [
#         "Before Processing: PM₂.₅ Concentration (μg/m³)",
#         "After Processing: WHO Health-Risk Index",
#     ],
#     horizontal=True,
# )

# # ============================================================
# # 5. SIDEBAR CONTROLS (SHARED)
# # ============================================================
# st.sidebar.header("🔎 Time-Series Controls")

# view_mode = st.sidebar.radio(
#     "View mode:",
#     ["Global Trend", "Single Country", "Compare Countries", "Regional Trend"],
# )

# # Year filter
# min_year, max_year = int(df["year"].min()), int(df["year"].max())
# year_range = st.sidebar.slider(
#     "Year range:",
#     min_value=min_year,
#     max_value=max_year,
#     value=(min_year, max_year),
#     step=1,
# )

# base = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])].copy()

# # Toggle secondary axis
# show_secondary = st.sidebar.checkbox(
#     "Show secondary series on 2nd axis",
#     value=True,
#     help=(
#         "In BEFORE mode, secondary = WHO risk index.\n"
#         "In AFTER mode, secondary = raw PM₂.₅ concentration."
#     ),
# )

# # Decide which column is main vs secondary based on mode
# if mode.startswith("Before"):
#     main_col = "pm25_ugm3"
#     sec_col = "risk_index"
#     main_label = "PM₂.₅ Concentration (μg/m³)"
#     sec_label = "WHO Health-Risk Index (PM₂.₅ / 25)"
#     main_color = "#2563EB"
#     sec_color = "#EF4444"
#     st.subheader("🌫 BEFORE Processing — WHO PM₂.₅ Time-Series (μg/m³)")
# else:
#     main_col = "risk_index"
#     sec_col = "pm25_ugm3"
#     main_label = "WHO Health-Risk Index (PM₂.₅ / 25)"
#     sec_label = "PM₂.₅ Concentration (μg/m³)"
#     main_color = "#EF4444"
#     sec_color = "#2563EB"
#     st.subheader("❤️ AFTER Processing — WHO-Based Health-Risk Trend")

# # ============================================================
# # 6. HELPER: DUAL-AXIS TIME-SERIES PLOT
# # ============================================================
# def make_time_series(
#     data: pd.DataFrame,
#     title_prefix: str = "",
#     group_by: str | None = None,
# ):
#     """
#     If group_by is None:
#         - Single line on primary axis (main_col)
#         - Optional single line on secondary axis (sec_col)
#     If group_by is not None:
#         - One line per group on primary axis (main_col)
#         - Average secondary series over all groups on secondary axis (sec_col)
#     """
#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     if group_by is None:
#         series = data.sort_values("year")

#         fig.add_trace(
#             go.Scatter(
#                 x=series["year"],
#                 y=series[main_col],
#                 mode="lines+markers",
#                 name=main_label,
#                 line=dict(color=main_color),
#             ),
#             secondary_y=False,
#         )

#         if show_secondary:
#             fig.add_trace(
#                 go.Scatter(
#                     x=series["year"],
#                     y=series[sec_col],
#                     mode="lines+markers",
#                     name=sec_label,
#                     line=dict(color=sec_color, dash="dash"),
#                 ),
#                 secondary_y=True,
#             )

#     else:
#         # Primary axis: one line per group (country or region)
#         for g, subset in data.groupby(group_by):
#             subset = subset.sort_values("year")
#             if subset.empty:
#                 continue
#             fig.add_trace(
#                 go.Scatter(
#                     x=subset["year"],
#                     y=subset[main_col],
#                     mode="lines+markers",
#                     name=str(g),
#                 ),
#                 secondary_y=False,
#             )

#         if show_secondary:
#             # Secondary axis: global average secondary series across groups
#             sec_df = (
#                 data.groupby("year")[sec_col]
#                 .mean()
#                 .reset_index()
#                 .sort_values("year")
#             )
#             fig.add_trace(
#                 go.Scatter(
#                     x=sec_df["year"],
#                     y=sec_df[sec_col],
#                     mode="lines",
#                     name=f"Mean {sec_label}",
#                     line=dict(color=sec_color, width=2, dash="dash"),
#                 ),
#                 secondary_y=True,
#             )

#     title = f"{title_prefix} {main_label} Over Time".strip()
#     fig.update_layout(
#         title=title,
#         margin=dict(l=40, r=40, t=60, b=40),
#         legend_title_text="",
#     )
#     fig.update_xaxes(title_text="Year")
#     fig.update_yaxes(
#         title_text=main_label,
#         secondary_y=False,
#     )
#     if show_secondary:
#         fig.update_yaxes(
#             title_text=sec_label,
#             secondary_y=True,
#         )

#     return fig

# # ============================================================
# # 7. VIEW MODES
# # ============================================================

# # ---------- GLOBAL TREND ----------
# if view_mode == "Global Trend":
#     st.markdown("### 🌍 Global Trend")

#     global_df = (
#         base.groupby("year")[[main_col, sec_col]]
#         .mean()
#         .reset_index()
#         .sort_values("year")
#     )

#     fig = make_time_series(global_df, title_prefix="Global")
#     st.plotly_chart(fig, use_container_width=True)

#     # Summary table
#     st.markdown("### 📊 Summary Statistics (Global)")
#     summary = global_df[["year", main_col]].rename(
#         columns={main_col: "mean_value"}
#     )
#     st.dataframe(summary, use_container_width=True)

# # ---------- SINGLE COUNTRY ----------
# elif view_mode == "Single Country":
#     st.markdown("### 🇺🇳 Single Country Trend")

#     countries = sorted(base["country"].unique())
#     country = st.selectbox("Select a country:", countries)

#     cdf = base[base["country"] == country]

#     if cdf.empty:
#         st.info("No data for this country in the selected year range.")
#     else:
#         fig = make_time_series(cdf, title_prefix=country, group_by=None)
#         st.plotly_chart(fig, use_container_width=True)

#         summary = (
#             cdf.groupby("year")[main_col]
#             .agg(mean_value="mean", min_value="min", max_value="max")
#             .reset_index()
#         )
#         st.markdown(f"### 📊 Summary Statistics — {country}")
#         st.dataframe(summary, use_container_width=True)

# # ---------- COMPARE COUNTRIES ----------
# elif view_mode == "Compare Countries":
#     st.markdown("### 🌐 Compare Countries")

#     countries = sorted(base["country"].unique())
#     default_c = [c for c in ["Afghanistan", "India", "China"] if c in countries]

#     selected = st.multiselect(
#         "Choose countries to compare:",
#         countries,
#         default=default_c,
#     )

#     if not selected:
#         st.info("Select at least one country to compare.")
#     else:
#         comp_df = base[base["country"].isin(selected)]

#         if comp_df.empty:
#             st.info("No data available for the selected countries in this year range.")
#         else:
#             fig = make_time_series(
#                 comp_df,
#                 title_prefix="Countries —",
#                 group_by="country",
#             )
#             st.plotly_chart(fig, use_container_width=True)

#             summary = (
#                 comp_df.groupby(["country", "year"])[main_col]
#                 .mean()
#                 .reset_index()
#                 .rename(columns={main_col: "mean_value"})
#             )
#             st.markdown("### 📊 Summary by Country & Year")
#             st.dataframe(summary, use_container_width=True)

# # ---------- REGIONAL TREND ----------
# elif view_mode == "Regional Trend":
#     if "region" not in base.columns or base["region"].isna().all():
#         st.warning(
#             "No valid 'region' data found in WHO PM₂.₅ dataset, "
#             "so regional view is disabled."
#         )
#     else:
#         st.markdown("### 🌎 Regional Trends")

#         all_regions = sorted(base["region"].dropna().unique())
#         selected_regions = st.multiselect(
#             "Select regions:",
#             all_regions,
#             default=all_regions,
#         )

#         if not selected_regions:
#             st.info("Select at least one region to view trends.")
#         else:
#             rdf = base[base["region"].isin(selected_regions)]

#             if rdf.empty:
#                 st.info("No data available for the selected regions in this year range.")
#             else:
#                 fig = make_time_series(
#                     rdf,
#                     title_prefix="Regions —",
#                     group_by="region",
#                 )
#                 st.plotly_chart(fig, use_container_width=True)

#                 summary = (
#                     rdf.groupby(["region", "year"])[main_col]
#                     .mean()
#                     .reset_index()
#                     .rename(columns={main_col: "mean_value"})
#                 )
#                 st.markdown("### 📊 Summary by Region & Year")
#                 st.dataframe(summary, use_container_width=True)

# # ============================================================
# # 8. FOOTNOTE / EXPLANATION
# # ============================================================
# st.markdown(
#     """
# ---
# ### ℹ How to read these two time-series?

# - **Before Processing (PM₂.₅ μg/m³)**  
#   Shows the **raw WHO concentration** of fine particulate matter in micrograms per cubic meter.

# - **After Processing (WHO Health-Risk Index)**  
#   We convert PM₂.₅ into a **relative health-risk index**:  
#   \n
#   `risk index = PM₂.₅ / 25`, where **25 μg/m³** is the WHO reference threshold used elsewhere in this dashboard.  
#   - A value **≈1.0** means around the WHO threshold  
#   - Values **>1.0** indicate increasing health concern.
# """
# )

#_______________________________________________

import pandas as pd

df1 = pd.read_csv("/mnt/data/pm25-air-pollution.csv")
df2 = pd.read_csv("/mnt/data/global_air_pollution.csv")

df1.columns, df2.columns
