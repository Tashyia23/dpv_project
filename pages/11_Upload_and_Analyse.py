import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.ui import header

st.set_page_config(layout="wide")


# --------------------------------------------------------------------
# Robust universal CSV loader (handles WAQI, WHO, large messy files)
# --------------------------------------------------------------------
def load_uploaded_csv(file):
    """
    Load any CSV reliably:
    - Handles UTF-8, latin1, mixed encodings
    - Skips malformed lines (WAQI datasets & API dumps)
    - Handles huge files (up to 200MB)
    """
    loaders = [
        {"encoding": "utf-8", "engine": "c"},
        {"encoding": "latin1", "engine": "c"},
        {"encoding": "latin1", "engine": "python"},
    ]

    for opt in loaders:
        try:
            file.seek(0)
            return pd.read_csv(
                file,
                encoding=opt["encoding"],
                engine=opt["engine"],
                on_bad_lines="skip",
                low_memory=False,
            )
        except Exception:
            continue

    return None  # All attempts failed


# --------------------------------------------------------------------
# Helpers: auto-detect columns for mini dashboard
# --------------------------------------------------------------------
def detect_geo_columns(df: pd.DataFrame):
    """Return (lat_col, lon_col, country_col, city_col) if found."""
    cols = list(df.columns)

    # Latitude / Longitude
    lat_candidates = ["lat", "latitude", "Latitude", "LATITUDE"]
    lon_candidates = ["lon", "lng", "long", "longitude", "Longitude", "LONGITUDE"]

    lat_col = next((c for c in cols if c in lat_candidates), None)
    lon_col = next((c for c in cols if c in lon_candidates), None)

    # Country / City
    country_candidates = ["country", "Country", "COUNTRY", "Entity", "nation", "Nation"]
    city_candidates = ["city", "City", "CITY", "town", "Town"]

    country_col = next((c for c in cols if c in country_candidates), None)
    city_col = next((c for c in cols if c in city_candidates), None)

    return lat_col, lon_col, country_col, city_col


def detect_time_column(df: pd.DataFrame):
    """
    Try to detect a time column:
    - prefers datetime columns
    - then columns named like Year/Date
    Returns column name or None.
    """
    # 1. Already datetime
    for c in df.columns:
        if np.issubdtype(df[c].dtype, np.datetime64):
            return c

    # 2. Name-based hints
    name_candidates = [c for c in df.columns if any(x in c.lower() for x in ["year", "date", "time"])]
    for c in name_candidates:
        # try parsing
        try:
            parsed = pd.to_datetime(df[c], errors="coerce")
            if parsed.notna().sum() > 0:
                df[c] = parsed
                return c
        except Exception:
            continue

    return None


def detect_pollutant_columns(df: pd.DataFrame):
    """
    Find numeric pollution / AQI-like columns.
    Returns list of column names.
    """
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        return []

    pollution_keywords = ["aqi", "pm25", "pm2.5", "pm10", "no2", "ozone", "co", "so2", "pollution"]

    pollutant_cols = [
        c for c in numeric_cols
        if any(k in c.lower() for k in pollution_keywords)
    ]

    # fallback to all numeric if nothing matched
    return pollutant_cols or numeric_cols


# --------------------------------------------------------------------
# Page Header
# --------------------------------------------------------------------
header(
    "📤 Upload & Analyse Your Dataset",
    "Upload any CSV file for automatic cleaning, profiling, and visualisation."
)

# --------------------------------------------------------------------
# File Upload UI
# --------------------------------------------------------------------
st.markdown("## Upload a dataset to begin:")

uploaded_file = st.file_uploader(
    "Choose a CSV file:",
    type=["csv"],
    help="Supports large CSV files up to 200MB, including WAQI & scientific datasets."
)

if not uploaded_file:
    st.info("📂 Upload a CSV file to continue.")
    st.stop()

# --------------------------------------------------------------------
# Load file using robust loader
# --------------------------------------------------------------------
df = load_uploaded_csv(uploaded_file)

if df is None:
    st.error("❌ Could not read the file. Please ensure it's a valid CSV encoding.")
    st.stop()

st.success("✅ File successfully loaded!")

# Tabs: 1) Overview & Cleaning, 2) Mini Dashboard
tab_overview, tab_dashboard = st.tabs(["🧹 Overview & Cleaning", "📊 Mini Dashboard"])

# ===============================================================
# 🧹 SECTION: AUTOMATIC CLEANING TOOLS
# ===============================================================

st.header("🧹 Automatic Data Cleaning")

clean_choice = st.multiselect(
    "Choose cleaning steps to apply:",
    [
        "Drop rows with missing values",
        "Drop columns with >30% missing",
        "Fill numeric missing values (mean)",
        "Fill numeric missing values (median)",
        "Fill numeric missing values (zero)",
        "Fill categorical missing values (mode)",
        "Fill categorical missing values ('Unknown')",
        "Remove duplicate rows",
        "Remove duplicate columns",
        "Convert numeric-looking text → numeric",
        "Convert date-looking text → datetime",
    ]
)

df_cleaned = df.copy()

# 1. Drop rows with missing values
if "Drop rows with missing values" in clean_choice:
    df_cleaned = df_cleaned.dropna()

# 2. Drop columns with too many missing values
if "Drop columns with >30% missing" in clean_choice:
    threshold = 0.3 * len(df_cleaned)
    df_cleaned = df_cleaned.dropna(axis=1, thresh=threshold)

# 3. Fill numeric missing values
num_cols = df_cleaned.select_dtypes(include=['int64','float64']).columns

if "Fill numeric missing values (mean)" in clean_choice:
    df_cleaned[num_cols] = df_cleaned[num_cols].fillna(df_cleaned[num_cols].mean())

if "Fill numeric missing values (median)" in clean_choice:
    df_cleaned[num_cols] = df_cleaned[num_cols].fillna(df_cleaned[num_cols].median())

if "Fill numeric missing values (zero)" in clean_choice:
    df_cleaned[num_cols] = df_cleaned[num_cols].fillna(0)

# 4. Fill categorical missing values
cat_cols = df_cleaned.select_dtypes(include=['object']).columns

if "Fill categorical missing values (mode)" in clean_choice:
    for col in cat_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])

if "Fill categorical missing values ('Unknown')" in clean_choice:
    df_cleaned[cat_cols] = df_cleaned[cat_cols].fillna("Unknown")

# 5. Remove duplicate rows
if "Remove duplicate rows" in clean_choice:
    df_cleaned = df_cleaned.drop_duplicates()

# 6. Remove duplicate columns
if "Remove duplicate columns" in clean_choice:
    df_cleaned = df_cleaned.loc[:, ~df_cleaned.T.duplicated()]

# 7. Convert numeric-like text to numeric
if "Convert numeric-looking text → numeric" in clean_choice:
    for col in df_cleaned.columns:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="ignore")

# 8. Convert to datetime
if "Convert date-looking text → datetime" in clean_choice:
    for col in df_cleaned.columns:
        try:
            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors="ignore")
        except:
            pass

st.success("Cleaning applied successfully!")
st.dataframe(df_cleaned)

# ===============================================================
# 🧪 SECTION: FEATURE ENGINEERING TOOLS
# ===============================================================

st.header("🧪 Feature Engineering Tools")

feat_choice = st.multiselect(
    "Select features to generate:",
    [
        "Extract datetime features",
        "Compute rolling mean (3-period)",
        "Compute rolling mean (7-period)",
        "Compute rate of change (%)",
        "Normalize numeric columns (0–1)",
        "Standardize (z-score)",
    ]
)

df_feat = df_cleaned.copy()

# 1. Extract datetime features
if "Extract datetime features" in feat_choice:
    date_cols = df_feat.select_dtypes(include=["datetime64"]).columns
    for col in date_cols:
        df_feat[col + "_year"] = df_feat[col].dt.year
        df_feat[col + "_month"] = df_feat[col].dt.month
        df_feat[col + "_day"] = df_feat[col].dt.day
        df_feat[col + "_weekday"] = df_feat[col].dt.day_name()

# 2. Rolling means
if "Compute rolling mean (3-period)" in feat_choice:
    for col in num_cols:
        df_feat[col + "_roll3"] = df_feat[col].rolling(3).mean()

if "Compute rolling mean (7-period)" in feat_choice:
    for col in num_cols:
        df_feat[col + "_roll7"] = df_feat[col].rolling(7).mean()

# 3. Rate of change
if "Compute rate of change (%)" in feat_choice:
    for col in num_cols:
        df_feat[col + "_pct_change"] = df_feat[col].pct_change() * 100

# 4. Normalization
if "Normalize numeric columns (0–1)" in feat_choice:
    for col in num_cols:
        df_feat[col + "_norm"] = (df_feat[col] - df_feat[col].min()) / (df_feat[col].max() - df_feat[col].min())

# 5. Z-score standardization
if "Standardize (z-score)" in feat_choice:
    for col in num_cols:
        df_feat[col + "_zscore"] = (df_feat[col] - df_feat[col].mean()) / df_feat[col].std()

st.success("Feature engineering applied!")
st.dataframe(df_feat)


# ====================================================================
# TAB 1 — OVERVIEW & CLEANING
# ====================================================================
with tab_overview:
    st.markdown("### 📊 Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", f"{df.shape[1]:,}")
    col3.metric(
        "Missing Values (%)",
        f"{df.isnull().mean().mean() * 100:.2f}%"
    )

    st.dataframe(df.head(50), use_container_width=True)

    # ---------------------- Missing value heatmap ----------------------
    st.markdown("### 🩺 Missing Value Map")
    missing_map = df.isnull().astype(int)

    try:
        fig_missing = px.imshow(
            missing_map,
            aspect="auto",
            color_continuous_scale=["#ffffff", "#ff4b4b"],
            labels={"color": "Missing"},
            title="Missing Values Heatmap (1 = missing)"
        )
        fig_missing.update_layout(height=400)
        st.plotly_chart(fig_missing, use_container_width=True)
    except Exception:
        st.info("Too many rows/columns to display missing-value heatmap.")

    # ---------------------- Column type summary -----------------------
    st.markdown("### 🧬 Column Type Summary")

    dtype_counts = df.dtypes.astype(str).value_counts()
    st.bar_chart(dtype_counts)

    # ---------------------- Column-wise statistics --------------------
    st.markdown("### 📈 Column Statistics")

    selected_col = st.selectbox(
        "Select a column to analyse:",
        df.columns
    )

    if pd.api.types.is_numeric_dtype(df[selected_col]):
        st.markdown(f"#### 📏 Numeric Analysis — {selected_col}")

        colA, colB, colC, colD = st.columns(4)
        colA.metric("Mean", f"{df[selected_col].mean():.3f}")
        colB.metric("Median", f"{df[selected_col].median():.3f}")
        colC.metric("Std Dev", f"{df[selected_col].std():.3f}")
        colD.metric("Missing (%)", f"{df[selected_col].isnull().mean() * 100:.2f}%")

        fig_hist = px.histogram(df, x=selected_col, nbins=40,
                                title=f"Distribution of {selected_col}")
        st.plotly_chart(fig_hist, use_container_width=True)

        fig_box = px.box(df, y=selected_col, title=f"Boxplot of {selected_col}")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.markdown(f"#### 🏷 Categorical Analysis — {selected_col}")

        value_counts = df[selected_col].value_counts().head(20)
        fig_cat = px.bar(
            value_counts,
            x=value_counts.index,
            y=value_counts.values,
            title=f"Top 20 categories in '{selected_col}'"
        )
        fig_cat.update_layout(xaxis_title="Category", yaxis_title="Count")
        st.plotly_chart(fig_cat, use_container_width=True)

    # ---------------------- Download cleaned data ---------------------
    st.markdown("### 📥 Download Cleaned Dataset")

    cleaned_csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Cleaned CSV",
        cleaned_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )


# ====================================================================
# TAB 2 — MINI DASHBOARD (Map + Time Series + Risk Index)
# ====================================================================
with tab_dashboard:
    st.markdown("### 📊 Auto-Generated Mini Dashboard")

    # Detect columns
    lat_col, lon_col, country_col, city_col = detect_geo_columns(df)
    time_col = detect_time_column(df.copy())  # copy so we can safely parse
    pollutant_cols = detect_pollutant_columns(df)

    # Quick badges telling the user what we detected
    detected_geo = (
        f"Lat/Lon: {lat_col or '—'} / {lon_col or '—'}  •  "
        f"Country: {country_col or '—'}  •  City: {city_col or '—'}"
    )
    detected_time = time_col or "—"
    st.markdown(
        f"> **Detected columns**  \n"
        f"> 🌍 Geo → {detected_geo}  \n"
        f"> ⏱ Time → {detected_time}"
    )

    if not pollutant_cols:
        st.warning("No numeric / pollution-like columns found to build a dashboard.")
        st.stop()

    metric_col = st.selectbox(
        "Select metric to explore (AQI / pollutant column):",
        pollutant_cols,
    )

    # Compute relative risk index (0–1 scaling within uploaded dataset)
    metric_series = pd.to_numeric(df[metric_col], errors="coerce")
    lo, hi = metric_series.min(), metric_series.max()
    if pd.isna(lo) or pd.isna(hi) or hi <= lo:
        df["risk_index_rel"] = np.nan
    else:
        df["risk_index_rel"] = (metric_series - lo) / (hi - lo)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Mean metric", f"{metric_series.mean():.3f}")
    col_b.metric("Max metric", f"{metric_series.max():.3f}")
    col_c.metric("Mean relative risk index (0–1)", f"{df['risk_index_rel'].mean():.3f}")

    st.markdown("---")

    # ------------------------------------------------------------
    # 1) MAP VIEW
    # ------------------------------------------------------------
    st.markdown("#### 🌍 Map View")

    if lat_col and lon_col:
        # Use point map if lat/lon available
        map_df = df[[lat_col, lon_col, metric_col]].copy()
        if country_col in df.columns:
            map_df["country"] = df[country_col]
        if city_col in df.columns:
            map_df["city"] = df[city_col]

        hover_name = None
        if "city" in map_df.columns:
            hover_name = "city"
        elif "country" in map_df.columns:
            hover_name = "country"

        fig_map = px.scatter_geo(
            map_df,
            lat=lat_col,
            lon=lon_col,
            color=metric_col,
            hover_name=hover_name,
            color_continuous_scale="Reds",
            title=f"Global Map — {metric_col}",
        )
        fig_map.update_layout(height=430)
        st.plotly_chart(fig_map, use_container_width=True)

    elif country_col:
        # Fallback: country-level choropleth
        map_df = (
            df.groupby(country_col)[metric_col]
            .mean()
            .reset_index()
            .rename(columns={country_col: "country"})
        )

        fig_map = px.choropleth(
            map_df,
            locations="country",
            locationmode="country names",
            color=metric_col,
            color_continuous_scale="Reds",
            title=f"Country-Level Map — {metric_col}",
        )
        fig_map.update_layout(height=430)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No latitude/longitude or country column found — map view is disabled for this file.")

    st.markdown("---")

    # ------------------------------------------------------------
    # 2) TIME SERIES VIEW
    # ------------------------------------------------------------
    st.markdown("#### ⏱ Time-Series View")

    if time_col is None:
        st.info("No date/year column detected — cannot generate time-series plot.")
    else:
        ts_df = df.copy()
        ts_df = ts_df.dropna(subset=[time_col])
        # If datetime, resample by year; if year-like numeric, group directly
        if np.issubdtype(ts_df[time_col].dtype, np.datetime64):
            ts_df["year"] = ts_df[time_col].dt.year
            group_col = "year"
        else:
            group_col = time_col

        ts_agg = (
            ts_df.groupby(group_col)[[metric_col, "risk_index_rel"]]
            .mean()
            .reset_index()
            .sort_values(group_col)
        )

        fig_ts = px.line(
            ts_agg,
            x=group_col,
            y=[metric_col, "risk_index_rel"],
            markers=True,
            title=f"Trend of {metric_col} and Relative Risk Index Over Time",
        )
        fig_ts.update_layout(
            legend_title_text="Series",
            xaxis_title=str(group_col),
            yaxis_title="Value / Relative Risk (0–1)",
            height=430,
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------
    # 3) RISK INDEX DISTRIBUTION
    # ------------------------------------------------------------
    st.markdown("#### ⚠ Relative Risk Index Distribution")

    if df["risk_index_rel"].notna().sum() == 0:
        st.info("Risk index could not be computed (metric column constant or invalid).")
    else:
        fig_risk = px.histogram(
            df,
            x="risk_index_rel",
            nbins=40,
            title="Distribution of Relative Risk Index (0 = lowest in dataset, 1 = highest)",
        )
        fig_risk.update_layout(
            xaxis_title="Relative Risk Index (0–1)",
            yaxis_title="Count",
            height=380,
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    st.info(
        "🔍 The mini-dashboard above is **auto-generated** from your uploaded columns.\n\n"
        "- Map uses **lat/lon** when available, or **country names**.\n"
        "- Time series uses any detected **Year/Date** column.\n"
        "- Relative risk index is a **0–1 normalisation** of the selected metric within this dataset."
    )
