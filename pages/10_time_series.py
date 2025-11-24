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

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.ui import header

st.set_page_config(layout="wide")


# -------------------------------------------------------------------
# Helper: robust loader for WHO PM2.5 time-series file
# -------------------------------------------------------------------
def load_who_pm25():
    """
    Try several common locations for the WHO PM2.5 time-series file.
    Returns a cleaned DataFrame with columns:
        country, year, pm25_value
    or None if nothing can be loaded.
    """
    candidates = [
        "data/raw/pm25-air-pollution.csv",
        "data/pm25_air_pollution.csv",
        "data/pm25-air-pollution.csv",
        "pm25-air-pollution.csv",
        "/mnt/data/pm25-air-pollution.csv",
    ]

    df = None
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except Exception:
                continue

    if df is None:
        return None

    # Expect: Entity, Code, Year,
    #   "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total"
    col_name = "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total"

    if "Entity" not in df.columns or "Year" not in df.columns or col_name not in df.columns:
        return None

    out = df[["Entity", "Year", col_name]].copy()
    out.rename(
        columns={
            "Entity": "country",
            "Year": "year",
            col_name: "pm25_value",
        },
        inplace=True,
    )

    # clean numeric
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["pm25_value"] = pd.to_numeric(out["pm25_value"], errors="coerce")
    out = out.dropna(subset=["year", "pm25_value"])
    out["year"] = out["year"].astype(int)

    # Health-risk index relative to WHO guideline 25 μg/m³
    out["who_index"] = out["pm25_value"] / 25.0

    # % change vs first available year (per country)
    base = (
        out.sort_values("year")
        .groupby("country")["pm25_value"]
        .first()
        .rename("base_pm25")
    )
    out = out.merge(base, on="country", how="left")
    out["pct_change_since_base"] = (
        (out["pm25_value"] - out["base_pm25"]) / out["base_pm25"]
    ) * 100.0

    return out


# -------------------------------------------------------------------
# 1. Load data
# -------------------------------------------------------------------
who_df = load_who_pm25()

header(
    "📈 Time-Series Explorer",
    "Explore WHO PM₂.₅ trends before and after health-risk transformation."
)

if who_df is None or who_df.empty:
    st.error(
        "Could not load WHO PM₂.₅ time-series file "
        "(`pm25-air-pollution.csv`). Please check that it exists in the repo."
    )
    st.stop()

# -------------------------------------------------------------------
# 2. View mode: Before vs After
# -------------------------------------------------------------------
view_mode = st.radio(
    "Select data view:",
    [
        "Before Processing: Raw PM₂.₅ Concentration (μg/m³)",
        "After Processing: WHO Health-Risk Index (PM₂.₅ / 25)",
    ],
    horizontal=True,
)

# Metric options inside each view
if view_mode.startswith("Before"):
    metric_options = {
        "Raw PM₂.₅ concentration (μg/m³)": "pm25_value",
        "Percentage change since first year (%)": "pct_change_since_base",
    }
    default_metric = "pm25_value"
    metric_label_suffix = ""
    secondary_series = "who_index"  # optional for dual-axis
else:
    metric_options = {
        "WHO health-risk index (PM₂.₅ / 25)": "who_index",
        "Raw PM₂.₅ concentration (μg/m³)": "pm25_value",
        "Percentage change since first year (%)": "pct_change_since_base",
    }
    default_metric = "who_index"
    metric_label_suffix = " (WHO Index)"
    secondary_series = "pm25_value"  # optional dual-axis

# -------------------------------------------------------------------
# 3. Tabs for different exploration modes
# -------------------------------------------------------------------
tab_global, tab_country, tab_compare = st.tabs(
    ["🌍 Global Trend", "🇺🇳 Single Country", "🌐 Compare Countries"]
)


# -------------------------------------------------------------------
# Utility: build dual-axis time series
# -------------------------------------------------------------------
def build_dual_axis(
    df,
    primary_col,
    secondary_col=None,
    title="",
    primary_name="Metric",
    secondary_name="Secondary",
):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    series = df.sort_values("year")
    fig.add_trace(
        go.Scatter(
            x=series["year"],
            y=series[primary_col],
            mode="lines+markers",
            name=primary_name,
            line=dict(color="#2563EB"),
        ),
        secondary_y=False,
    )

    if secondary_col is not None and secondary_col in series.columns:
        fig.add_trace(
            go.Scatter(
                x=series["year"],
                y=series[secondary_col],
                mode="lines+markers",
                name=secondary_name,
                line=dict(color="#EF4444", dash="dash"),
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title=title,
        margin=dict(l=40, r=40, t=60, b=40),
        legend_title_text="",
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text=primary_name, secondary_y=False)
    if secondary_col is not None:
        fig.update_yaxes(title_text=secondary_name, secondary_y=True)

    return fig


# -------------------------------------------------------------------
# TAB 1 — GLOBAL TREND
# -------------------------------------------------------------------
with tab_global:
    st.markdown("## 🌍 Global Trend")

    metric_key = st.selectbox(
        "Select metric:",
        list(metric_options.keys()),
        index=list(metric_options.values()).index(default_metric),
        key="global_metric",
    )
    metric_col = metric_options[metric_key]

    # Aggregate global values (mean across countries per year)
    global_df = (
        who_df.groupby("year")[["pm25_value", "who_index", "pct_change_since_base"]]
        .mean()
        .reset_index()
    )

    if view_mode.startswith("Before"):
        primary_name = metric_key
        secondary_name = (
            "WHO Health-Risk Index (PM₂.₅ / 25)" if secondary_series == "who_index" else "PM₂.₅ (μg/m³)"
        )
    else:
        primary_name = metric_key
        secondary_name = (
            "PM₂.₅ concentration (μg/m³)" if secondary_series == "pm25_value" else "WHO Index"
        )

    fig_global = build_dual_axis(
        global_df,
        primary_col=metric_col,
        secondary_col=secondary_series,
        title=f"Global {metric_key} Over Time{metric_label_suffix}",
        primary_name=primary_name,
        secondary_name=secondary_name,
    )
    st.plotly_chart(fig_global, use_container_width=True)

    # Summary metrics
    latest_year = global_df["year"].max()
    latest_row = global_df[global_df["year"] == latest_year].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            f"Latest year in data",
            int(latest_year),
        )
    with col2:
        st.metric(
            f"{metric_key} ({latest_year})",
            f"{latest_row[metric_col]:.2f}",
        )
    with col3:
        if metric_col != "pct_change_since_base":
            change_col = "pct_change_since_base"
            st.metric(
                "Global % change since first year",
                f"{latest_row[change_col]:.1f}%",
            )


# -------------------------------------------------------------------
# TAB 2 — SINGLE COUNTRY
# -------------------------------------------------------------------
with tab_country:
    st.markdown("## 🇺🇳 Single Country View")

    countries = sorted(who_df["country"].unique())
    country = st.selectbox("Select a country:", countries, key="single_country")

    metric_key = st.selectbox(
        "Select metric:",
        list(metric_options.keys()),
        index=list(metric_options.values()).index(default_metric),
        key="country_metric",
    )
    metric_col = metric_options[metric_key]

    cdf = who_df[who_df["country"] == country].copy()

    if cdf.empty:
        st.info("No data available for this country.")
    else:
        if view_mode.startswith("Before"):
            primary_name = metric_key
            secondary_name = (
                "WHO Health-Risk Index (PM₂.₅ / 25)" if secondary_series == "who_index" else "PM₂.₅ (μg/m³)"
            )
        else:
            primary_name = metric_key
            secondary_name = (
                "PM₂.₅ concentration (μg/m³)" if secondary_series == "pm25_value" else "WHO Index"
            )

        fig_country = build_dual_axis(
            cdf,
            primary_col=metric_col,
            secondary_col=secondary_series,
            title=f"{country} – {metric_key} Over Time{metric_label_suffix}",
            primary_name=primary_name,
            secondary_name=secondary_name,
        )
        st.plotly_chart(fig_country, use_container_width=True)

        # Summary table
        summary = (
            cdf[["year", "pm25_value", "who_index", "pct_change_since_base"]]
            .sort_values("year")
            .rename(
                columns={
                    "pm25_value": "PM₂.₅ (μg/m³)",
                    "who_index": "WHO index (PM₂.₅/25)",
                    "pct_change_since_base": "% change vs first year",
                }
            )
        )
        st.markdown(f"### 📊 Yearly Summary — {country}")
        st.dataframe(summary, use_container_width=True)


# -------------------------------------------------------------------
# TAB 3 — COMPARE COUNTRIES
# -------------------------------------------------------------------
with tab_compare:
    st.markdown("## 🌐 Compare Countries")

    metric_key = st.selectbox(
        "Select metric:",
        list(metric_options.keys()),
        index=list(metric_options.values()).index(default_metric),
        key="compare_metric",
    )
    metric_col = metric_options[metric_key]

    countries = sorted(who_df["country"].unique())
    default_selection = [c for c in ["Afghanistan", "India", "China", "Malaysia"] if c in countries]

    selected = st.multiselect(
        "Choose countries to compare:",
        countries,
        default=default_selection,
    )

    if not selected:
        st.info("Select at least one country to compare.")
    else:
        comp_df = who_df[who_df["country"].isin(selected)].copy()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for c in selected:
            subset = comp_df[comp_df["country"] == c].sort_values("year")
            fig.add_trace(
                go.Scatter(
                    x=subset["year"],
                    y=subset[metric_col],
                    mode="lines+markers",
                    name=c,
                ),
                secondary_y=False,
            )

        # Optional global average risk line
        if secondary_series in comp_df.columns:
            risk_df = (
                comp_df.groupby("year")[secondary_series]
                .mean()
                .reset_index()
                .sort_values("year")
            )
            fig.add_trace(
                go.Scatter(
                    x=risk_df["year"],
                    y=risk_df[secondary_series],
                    mode="lines",
                    name="Global Avg Risk Index",
                    line=dict(color="#EF4444", dash="dash"),
                ),
                secondary_y=True,
            )

        fig.update_layout(
            title=f"Comparison of {metric_key} Across Countries{metric_label_suffix}",
            margin=dict(l=40, r=40, t=60, b=40),
            legend_title_text="",
        )
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text=metric_key, secondary_y=False)
        fig.update_yaxes(
            title_text="Global Avg WHO Index" if secondary_series == "who_index" else "Global Avg PM₂.₅",
            secondary_y=True,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Compact summary table
        summary = (
            comp_df.groupby(["country", "year"])[metric_col]
            .mean()
            .reset_index()
            .rename(columns={metric_col: "value"})
            .pivot(index="year", columns="country", values="value")
        )
        st.markdown("### 📊 Comparison Table")
        st.dataframe(summary, use_container_width=True)

