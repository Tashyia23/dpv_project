import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.loader import load_pm25_data
from utils.ui import header

st.set_page_config(layout="wide")

# ---------------------------------------------------------
# Load PM2.5 Dataset
# ---------------------------------------------------------
df = load_pm25_data()

header(
    "📈 Time-Series Explorer",
    "How pollution levels evolve over time by country and region."
)

if df is None:
    st.error("PM₂.₅ time-series dataset not found.")
    st.stop()

# ---------------------------------------------------------
# YEAR COLUMN HANDLING  (dataset uses 'Year')
# ---------------------------------------------------------
if "Year" in df.columns and "year" not in df.columns:
    df["year"] = df["Year"]
elif "year" not in df.columns:
    st.error("Dataset must contain a 'Year' or 'year' column.")
    st.stop()

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)
df = df.sort_values("year")

# ---------------------------------------------------------
# Country column normalisation
# ---------------------------------------------------------
# Many World Bank / Our World In Data files use 'Entity'
if "Entity" in df.columns and "country" not in df.columns:
    df = df.rename(columns={"Entity": "country"})
elif "entity" in df.columns and "country" not in df.columns:
    df = df.rename(columns={"entity": "country"})

if "country" not in df.columns:
    st.error("The dataset must contain a 'country' or 'Entity' column.")
    st.stop()

# ---------------------------------------------------------
# Detect pollutant columns (PM2.5, NO2, O3, etc.)
# For now your file only has PM2.5, but this is future-proof.
# ---------------------------------------------------------
pollutant_candidates = {}

for col in df.columns:
    lc = col.lower()
    if "pm2.5" in lc or "pm25" in lc:
        pollutant_candidates["PM₂.₅ (Fine Particles)"] = col
    elif "no2" in lc:
        pollutant_candidates["NO₂ (Nitrogen Dioxide)"] = col
    elif "ozone" in lc or "o3" in lc:
        pollutant_candidates["O₃ (Ozone)"] = col
    elif lc.endswith("_aqi_value") and "pm10" in lc:
        pollutant_candidates["PM₁₀ (Coarse Particles)"] = col

if not pollutant_candidates:
    st.error("Could not find any pollutant concentration columns (PM₂.₅, NO₂, O₃, etc.).")
    st.stop()

# Default: first pollutant detected (PM₂.₅ in your current dataset)
default_pollutant_label = list(pollutant_candidates.keys())[0]

# ---------------------------------------------------------
# Region assignment (auto from utils.regions if available)
# ---------------------------------------------------------
if "region" not in df.columns:
    try:
        # optional helper you may have created earlier
        from utils.regions import assign_region
        df["region"] = df["country"].apply(assign_region)
    except Exception:
        # fallback: single global region
        df["region"] = "Global"

# ---------------------------------------------------------
# SIDEBAR – view mode + pollutant + basic filters
# ---------------------------------------------------------
st.sidebar.header("🔎 Time-Series Filters")

mode = st.sidebar.radio(
    "View mode:",
    ["Global Trend", "Single Country", "Compare Countries", "Regional Trend"]
)

pollutant_label = st.sidebar.selectbox(
    "Pollutant:",
    list(pollutant_candidates.keys()),
    index=list(pollutant_candidates.keys()).index(default_pollutant_label)
)

value_col = pollutant_candidates[pollutant_label]

min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range:",
    min_year, max_year,
    (min_year, max_year)
)

df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

# Nice axis label
y_label = f"{pollutant_label} (μg/m³)" if "PM" in pollutant_label else pollutant_label

# ---------------------------------------------------------
# GLOBAL TREND
# ---------------------------------------------------------
if mode == "Global Trend":
    st.subheader(f"🌍 Global {pollutant_label} Trend Over Time")

    global_df = df.groupby("year")[value_col].mean().reset_index()

    fig = px.line(
        global_df,
        x="year",
        y=value_col,
        markers=True,
        title=f"Global Average {pollutant_label} Over Time",
        labels={"year": "Year", value_col: y_label},
    )
    fig.update_traces(line_width=3)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SINGLE COUNTRY MODE
# ---------------------------------------------------------
elif mode == "Single Country":
    st.subheader(f"🇺🇳 Single Country — {pollutant_label} Trend")

    countries = sorted(df["country"].unique())
    country = st.selectbox("Select country:", countries)

    cdf = df[df["country"] == country]

    fig = px.line(
        cdf,
        x="year",
        y=value_col,
        markers=True,
        title=f"{pollutant_label} Trend — {country}",
        labels={"year": "Year", value_col: y_label},
    )
    fig.update_traces(line_width=3)
    st.plotly_chart(fig, use_container_width=True)

    # Quick country stats
    st.markdown("#### Country Summary")
    stats = {
        "First year": int(cdf["year"].min()),
        "Last year": int(cdf["year"].max()),
        "Average level": float(cdf[value_col].mean()),
        "Min level": float(cdf[value_col].min()),
        "Max level": float(cdf[value_col].max()),
        "Last available value": float(cdf.sort_values("year")[value_col].iloc[-1]),
    }
    stats_df = pd.DataFrame.from_dict(stats, orient="index", columns=["Value"])
    st.table(stats_df)

# ---------------------------------------------------------
# COMPARE MULTIPLE COUNTRIES
# ---------------------------------------------------------
elif mode == "Compare Countries":
    st.subheader(f"🌐 Compare Countries — {pollutant_label}")

    countries = sorted(df["country"].unique())
    default_countries = [c for c in ["Afghanistan", "India", "China"] if c in countries][:3]

    selected = st.multiselect(
        "Choose countries:",
        countries,
        default=default_countries
    )

    if len(selected) == 0:
        st.info("Select at least one country to compare.")
    else:
        comp_df = df[df["country"].isin(selected)]

        fig = px.line(
            comp_df,
            x="year",
            y=value_col,
            color="country",
            markers=True,
            title=f"{pollutant_label} Levels — Country Comparison",
            labels={"year": "Year", value_col: y_label, "country": "Country"},
        )
        fig.update_traces(line_width=3)
        fig.update_layout(legend_title_text="Country")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# REGIONAL TREND MODE
# ---------------------------------------------------------
elif mode == "Regional Trend":
    st.subheader(f"🗺 Regional Trends — {pollutant_label}")

    regions = sorted(df["region"].unique())
    default_regions = [r for r in ["Asia", "Europe", "Africa"] if r in regions]

    selected_regions = st.multiselect(
        "Select regions:",
        regions,
        default=default_regions or regions
    )

    if len(selected_regions) == 0:
        st.info("Select at least one region.")
    else:
        rdf = df[df["region"].isin(selected_regions)]

        reg_trend = (
            rdf.groupby(["region", "year"])[value_col]
            .mean()
            .reset_index()
        )

        fig = px.line(
            reg_trend,
            x="year",
            y=value_col,
            color="region",
            markers=True,
            title=f"{pollutant_label} Trend by Region",
            labels={"year": "Year", value_col: y_label, "region": "Region"},
        )
        fig.update_traces(line_width=3)
        fig.update_layout(legend_title_text="Region")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SUMMARY TABLE
# ---------------------------------------------------------
st.markdown("### 📊 Summary Statistics")

summary = (
    df.groupby("year")[value_col]
    .agg(["mean", "min", "max"])
    .reset_index()
    .rename(columns={"mean": "mean_level", "min": "min_level", "max": "max_level"})
)

st.dataframe(summary, use_container_width=True)


