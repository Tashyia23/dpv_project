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
# tab_global, tab_country, tab_compare = st.tabs(
#     ["🌍 Global Trend", "🇺🇳 Single Country", "🌐 Compare Countries"]
# )

tab_global, tab_country, tab_compare, tab_city = st.tabs(
    [
        "🌍 Global Trend",
        "🇺🇳 Single Country",
        "🌐 Compare Countries",
        "🏙 Snapshot AQI by City"
    ]
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

#___________

# -------------------------------------------------------------------
# TAB 4 — SNAPSHOT AQI BY CITY (Processed AQI)
# -------------------------------------------------------------------
with tab_city:
    st.markdown("## 🏙 Snapshot AQI by City")

    # Load processed AQI dataset directly from uploaded file
    try:
        aqi_df = pd.read_csv("/mnt/data/global_air_pollution.csv")
    except:
        st.error("Processed AQI dataset not found.")
        st.stop()

    # Clean column names
    aqi_df.columns = [c.strip() for c in aqi_df.columns]

    required_cols = ["Country", "City"]
    if not all(col in aqi_df.columns for col in required_cols):
        st.error("Processed AQI dataset missing Country/City columns.")
        st.stop()

    # Select country
    countries = sorted(aqi_df["Country"].dropna().unique())
    selected_country = st.selectbox("Select Country:", countries, key="city_country")

    # Select city
    city_list = sorted(
        aqi_df[aqi_df["Country"] == selected_country]["City"].dropna().unique()
    )
    selected_city = st.selectbox("Select City:", city_list, key="city_name")

    # Filter row
    row = aqi_df[
        (aqi_df["Country"] == selected_country) &
        (aqi_df["City"] == selected_city)
    ].head(1)

    if row.empty:
        st.warning("No AQI data available for this city.")
        st.stop()

    pollutant_cols = [
        "PM2.5 AQI Value", "PM10 AQI Value", "NO2 AQI Value",
        "Ozone AQI Value", "CO AQI Value"
    ]
    available = [c for c in pollutant_cols if c in aqi_df.columns]

    pollutant_values = row[available].iloc[0].astype(float)

    st.markdown(f"### 🌬 AQI Snapshot: **{selected_city}**, {selected_country}")

    # ---------------------------
    # BAR CHART
    # ---------------------------
    bar_df = pd.DataFrame({
        "Pollutant": available,
        "AQI": pollutant_values.values
    })

    fig_bar = px.bar(
        bar_df,
        x="Pollutant",
        y="AQI",
        color="AQI",
        color_continuous_scale="Reds",
        title=f"AQI Levels in {selected_city}",
    )
    fig_bar.update_layout(height=350)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------------------
    # RADAR CHART
    # ---------------------------
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=pollutant_values.values,
        theta=available,
        fill="toself",
        line=dict(color="#F43F5E"),
        name="AQI Levels"
    ))
    fig_radar.update_layout(
        title="Pollution Profile (Radar Chart)",
        polar=dict(radialaxis=dict(visible=True)),
        height=450
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ---------------------------
    # CATEGORY BADGES
    # ---------------------------
    st.markdown("### 📛 AQI Category Summary")

    category_cols = [c.replace("Value", "Category") for c in available]

    for val_col, cat_col in zip(available, category_cols):
        if cat_col in row.columns:
            cat = row[cat_col].iloc[0]
            val = float(row[val_col].iloc[0])
            st.markdown(
                f"""
                <div style='padding:10px;margin:8px 0;border-radius:8px;
                background:#f3f4f6;border:1px solid #e5e7eb;'>
                    <b>{val_col.replace(" AQI Value","")}</b>:  
                    <span style='color:#dc2626;font-weight:700;'>{val}</span>  
                    — <i>{cat}</i>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.info(
        "This section shows **current AQI levels** for each pollutant, not a time series. "
        "Use the tabs above to explore PM₂.₅ trends over time."
    )
