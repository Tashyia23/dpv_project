import os
import io
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.ui import header

st.set_page_config(layout="wide")

# Function to load custom CSS (ensure it's loaded for every page)
def load_css():
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS in each page (this ensures the styles are applied across pages)
load_css()

# =============================================================================
# 1. UNIVERSAL CSV LOADER
# =============================================================================


def load_uploaded_csv(file) -> pd.DataFrame | None:
    """
    Load any CSV reliably:
    - Handles UTF-8, latin1, mixed encodings
    - Skips malformed lines (WAQI datasets & API dumps)
    - Handles large files reasonably
    """
    loaders = [
        {"encoding": "utf-8", "engine": "c"},
        {"encoding": "latin1", "engine": "c"},
        {"encoding": "latin1", "engine": "python"},
    ]

    for opt in loaders:
        try:
            file.seek(0)
            df = pd.read_csv(
                file,
                encoding=opt["encoding"],
                engine=opt["engine"],
                on_bad_lines="skip",
                low_memory=False,
            )
            return df
        except Exception:
            continue

    return None


# =============================================================================
# 2. DETECTION HELPERS (GEO / TIME / POLLUTANTS)
# =============================================================================


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
    - prefers already datetime columns
    - otherwise tries to parse Year/Date/Time-like columns
    Returns column name or None.
    """
    # 1. Already datetime
    for c in df.columns:
        if np.issubdtype(df[c].dtype, np.datetime64):
            return c

    # 2. Name-based
    name_candidates = [
        c
        for c in df.columns
        if any(x in c.lower() for x in ["year", "date", "time"])
    ]

    for c in name_candidates:
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

    pollution_keywords = [
        "aqi",
        "pm25",
        "pm2.5",
        "pm10",
        "no2",
        "ozone",
        "co",
        "so2",
        "pollution",
    ]

    pollutant_cols = [
        c
        for c in numeric_cols
        if any(k in c.lower() for k in pollution_keywords)
    ]

    return pollutant_cols or numeric_cols


# =============================================================================
# 3. PAGE HEADER & FILE UPLOAD
# =============================================================================

header(
    "📤 Upload & Analyse Your Dataset",
    "Upload any CSV file for automatic cleaning, feature engineering, and visualisation.",
)

st.markdown("## Upload a dataset to begin:")

uploaded_file = st.file_uploader(
    "Choose a CSV file:",
    type=["csv"],
    help="Supports large CSV files, including WAQI & scientific datasets.",
)

if not uploaded_file:
    st.info("📂 Upload a CSV file to continue.")
    st.stop()

df_raw = load_uploaded_csv(uploaded_file)

if df_raw is None or df_raw.empty:
    st.error("❌ Could not read the file. Please ensure it's a valid CSV.")
    st.stop()

st.success("✅ File successfully loaded!")

# Work on copies
df_cleaned = df_raw.copy()
df_feat = df_cleaned.copy()

# =============================================================================
# 4. AUTOMATIC CLEANING TOOLS
# =============================================================================

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
    ],
)

# 1. Drop rows with missing values
if "Drop rows with missing values" in clean_choice:
    df_cleaned = df_cleaned.dropna()

# 2. Drop columns with too many missing values
if "Drop columns with >30% missing" in clean_choice and len(df_cleaned) > 0:
    threshold = 0.3 * len(df_cleaned)
    df_cleaned = df_cleaned.dropna(axis=1, thresh=threshold)

# Re-identify numeric / categorical after structure changes
num_cols = df_cleaned.select_dtypes(include=["number"]).columns.tolist()
cat_cols = df_cleaned.select_dtypes(include=["object"]).columns.tolist()

# 3. Fill numeric missing values
if "Fill numeric missing values (mean)" in clean_choice and num_cols:
    df_cleaned[num_cols] = df_cleaned[num_cols].fillna(df_cleaned[num_cols].mean())

if "Fill numeric missing values (median)" in clean_choice and num_cols:
    df_cleaned[num_cols] = df_cleaned[num_cols].fillna(df_cleaned[num_cols].median())

if "Fill numeric missing values (zero)" in clean_choice and num_cols:
    df_cleaned[num_cols] = df_cleaned[num_cols].fillna(0)

# 4. Fill categorical missing values
if "Fill categorical missing values (mode)" in clean_choice and cat_cols:
    for col in cat_cols:
        mode_vals = df_cleaned[col].mode()
        if not mode_vals.empty:
            df_cleaned[col] = df_cleaned[col].fillna(mode_vals[0])

if "Fill categorical missing values ('Unknown')" in clean_choice and cat_cols:
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

# 8. Convert date-looking text to datetime
if "Convert date-looking text → datetime" in clean_choice:
    for col in df_cleaned.columns:
        try:
            converted = pd.to_datetime(df_cleaned[col], errors="coerce")
            if converted.notna().sum() > 0:
                df_cleaned[col] = converted
        except Exception:
            continue

st.success("✅ Cleaning applied successfully!")

# =============================================================================
# 5. FEATURE ENGINEERING TOOLS
# =============================================================================

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
    ],
)

df_feat = df_cleaned.copy()

# Re-identify numeric cols on cleaned data
num_cols_cleaned = df_feat.select_dtypes(include=["number"]).columns.tolist()

# 1. Extract datetime features
if "Extract datetime features" in feat_choice:
    date_cols = df_feat.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
    for col in date_cols:
        df_feat[col + "_year"] = df_feat[col].dt.year
        df_feat[col + "_month"] = df_feat[col].dt.month
        df_feat[col + "_day"] = df_feat[col].dt.day
        df_feat[col + "_weekday"] = df_feat[col].dt.day_name()

# 2. Rolling means
if "Compute rolling mean (3-period)" in feat_choice:
    for col in num_cols_cleaned:
        df_feat[col + "_roll3"] = df_feat[col].rolling(3, min_periods=1).mean()

if "Compute rolling mean (7-period)" in feat_choice:
    for col in num_cols_cleaned:
        df_feat[col + "_roll7"] = df_feat[col].rolling(7, min_periods=1).mean()

# 3. Rate of change
if "Compute rate of change (%)" in feat_choice:
    for col in num_cols_cleaned:
        df_feat[col + "_pct_change"] = df_feat[col].pct_change() * 100

# 4. Normalization
if "Normalize numeric columns (0–1)" in feat_choice:
    for col in num_cols_cleaned:
        col_min, col_max = df_feat[col].min(), df_feat[col].max()
        if pd.notna(col_min) and pd.notna(col_max) and col_max > col_min:
            df_feat[col + "_norm"] = (df_feat[col] - col_min) / (col_max - col_min)

# 5. Z-score standardization
if "Standardize (z-score)" in feat_choice:
    for col in num_cols_cleaned:
        mean_val, std_val = df_feat[col].mean(), df_feat[col].std()
        if std_val and not np.isclose(std_val, 0):
            df_feat[col + "_zscore"] = (df_feat[col] - mean_val) / std_val

st.success("✅ Feature engineering applied!")

# Final dataset used for analysis / export
df_final = df_feat.copy()

# =============================================================================
# 6. TABS: OVERVIEW / MINI DASHBOARD / EXPORT
# =============================================================================

tab_overview, tab_dashboard, tab_export = st.tabs(
    ["🧹 Overview & Cleaning", "📊 Mini Dashboard", "📄 Export HTML Report"]
)

# ---------------------------------------------------------------------
# TAB 1 — OVERVIEW & CLEANING
# ---------------------------------------------------------------------
with tab_overview:
    st.markdown("### 📊 Dataset Overview (After Cleaning & Features)")

    n_rows, n_cols = df_final.shape
    missing_pct = df_final.isnull().mean().mean() * 100 if n_rows > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{n_rows:,}")
    col2.metric("Columns", f"{n_cols:,}")
    col3.metric("Missing Values (%)", f"{missing_pct:.2f}%")

    st.markdown("#### 🔎 Preview (First 50 Rows)")
    st.dataframe(df_final.head(50), use_container_width=True)

    # Missing-value heatmap (safe guard for very large frames)
    st.markdown("### 🩺 Missing Value Map")
    try:
        if n_rows * n_cols > 10000:
            st.info("Dataset is large; skipping heatmap for performance.")
        else:
            missing_map = df_final.isnull().astype(int)
            fig_missing = px.imshow(
                missing_map,
                aspect="auto",
                color_continuous_scale=["#ffffff", "#ff4b4b"],
                labels={"color": "Missing"},
                title="Missing Values Heatmap (1 = missing)",
            )
            fig_missing.update_layout(height=400)
            st.plotly_chart(fig_missing, use_container_width=True)

            with st.expander("📘 Insight — Missing Value Pattern"):
                st.markdown(
                    """
- Each red cell indicates a **missing entry** for a particular row–column combination.  
- Columns with many red cells may require **imputation or removal**, depending on their importance.  
- If missingness appears concentrated in specific rows, it may indicate **data entry or ingestion issues** limited to certain records.  
                    """
                )
    except Exception:
        st.info("Unable to render missing-value heatmap for this dataset.")

    # Column type summary
    st.markdown("### 🧬 Column Type Summary")
    dtype_counts = df_final.dtypes.astype(str).value_counts()
    st.bar_chart(dtype_counts)

    with st.expander("📘 Insight — Data Type Composition"):
        st.markdown(
            """
- A higher count of **numeric columns** enables richer statistical analysis and modelling.  
- Many **object / string columns** may represent categorical variables that could benefit from **encoding or cleaning**.  
- The balance of types gives a quick indication of whether this dataset is more suited for **descriptive analytics** or **predictive modelling**.  
            """
        )

    # Column-wise statistics
    st.markdown("### 📈 Column Statistics")
    selected_col = st.selectbox("Select a column to analyse:", df_final.columns)

    if pd.api.types.is_numeric_dtype(df_final[selected_col]):
        st.markdown(f"#### 📏 Numeric Analysis — {selected_col}")

        colA, colB, colC, colD = st.columns(4)
        colA.metric("Mean", f"{df_final[selected_col].mean():.3f}")
        colB.metric("Median", f"{df_final[selected_col].median():.3f}")
        colC.metric("Std Dev", f"{df_final[selected_col].std():.3f}")
        colD.metric(
            "Missing (%)", f"{df_final[selected_col].isnull().mean() * 100:.2f}%"
        )

        fig_hist = px.histogram(
            df_final,
            x=selected_col,
            nbins=40,
            title=f"Distribution of {selected_col}",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        fig_box = px.box(
            df_final,
            y=selected_col,
            title=f"Boxplot of {selected_col}",
        )
        st.plotly_chart(fig_box, use_container_width=True)

        with st.expander(f"📘 Insight — Distribution & Outliers for `{selected_col}`"):
            st.markdown(
                f"""
- The **histogram** helps assess whether `{selected_col}` is **symmetric, skewed, or multi-modal`, which affects the choice of statistical tests and models.  
- The **boxplot** highlights **outliers** and shows how concentrated the central 50% of values are (interquartile range).  
- Strong skewness or heavy tails may suggest the need for **transformation** (e.g. log, square-root) before modelling.  
                """
            )

    else:
        st.markdown(f"#### 🏷 Categorical Analysis — {selected_col}")
        value_counts = df_final[selected_col].value_counts().head(20)

        fig_cat = px.bar(
            value_counts,
            x=value_counts.index,
            y=value_counts.values,
            title=f"Top 20 categories in '{selected_col}'",
        )
        fig_cat.update_layout(xaxis_title="Category", yaxis_title="Count")
        st.plotly_chart(fig_cat, use_container_width=True)

        with st.expander(f"📘 Insight — Category Distribution for `{selected_col}`"):
            st.markdown(
                f"""
- Taller bars indicate **frequent categories**, which may dominate statistical patterns or model learning.  
- Very rare categories may need to be **grouped**, **relabelled**, or **excluded**, depending on the analysis goal.  
- Highly imbalanced distributions can influence **classification performance** and may require **resampling or weighting strategies**.  
                """
            )

    # Download cleaned/featured data
    st.markdown("### 📥 Download Processed Dataset (CSV)")

    cleaned_csv = df_final.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Processed CSV",
        cleaned_csv,
        file_name="processed_dataset.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------
# TAB 2 — MINI DASHBOARD (MAP + TIME SERIES + RISK INDEX)
# ---------------------------------------------------------------------
with tab_dashboard:
    st.markdown("### 📊 Auto-Generated Mini Dashboard")

    # Detect from final dataset
    lat_col, lon_col, country_col, city_col = detect_geo_columns(df_final)
    time_col = detect_time_column(df_final.copy())  # safe copy
    pollutant_cols = detect_pollutant_columns(df_final)

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

    metric_series = pd.to_numeric(df_final[metric_col], errors="coerce")
    lo, hi = metric_series.min(), metric_series.max()
    if pd.isna(lo) or pd.isna(hi) or hi <= lo:
        df_final["risk_index_rel"] = np.nan
    else:
        df_final["risk_index_rel"] = (metric_series - lo) / (hi - lo)

    colA, colB, colC = st.columns(3)
    colA.metric("Mean metric", f"{metric_series.mean():.3f}")
    colB.metric("Max metric", f"{metric_series.max():.3f}")
    colC.metric(
        "Mean relative risk index (0–1)",
        f"{df_final['risk_index_rel'].mean():.3f}",
    )

    st.markdown("---")

    # --------------------- 1) MAP VIEW -------------------------
    st.markdown("#### 🌍 Map View")

    if lat_col and lon_col:
        map_df = df_final[[lat_col, lon_col, metric_col]].copy()
        if country_col in df_final.columns:
            map_df["country"] = df_final[country_col]
        if city_col in df_final.columns:
            map_df["city"] = df_final[city_col]

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

        with st.expander(f"📘 Insight — Spatial Pattern of `{metric_col}`"):
            st.markdown(
                f"""
- Darker or more intense colours indicate **higher values of `{metric_col}`**, signalling potential hotspots.  
- Clusters of high values in specific regions may point to **shared environmental, socio-economic, or policy factors**.  
- If the pattern appears random, it may suggest that `{metric_col}` is **weakly structured by geography**, and other predictors may be more important.  
                """
            )

    elif country_col:
        map_df = (
            df_final.groupby(country_col)[metric_col]
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

        with st.expander(f"📘 Insight — Country-Level Variation in `{metric_col}`"):
            st.markdown(
                f"""
- Darker countries exhibit **higher average levels of `{metric_col}`**, highlighting priority regions for intervention.  
- Large contrasts between neighbouring countries may reveal **policy, industrial, or monitoring differences**.  
- A relatively uniform map suggests that `{metric_col}` is **similar across countries**, reducing geographic bias in the dataset.  
                """
            )
    else:
        st.info(
            "No latitude/longitude or country column found — map view is disabled for this file."
        )

    st.markdown("---")

    # --------------------- 2) TIME SERIES VIEW -----------------
    st.markdown("#### ⏱ Time-Series View")

    if time_col is None:
        st.info("No date/year column detected — cannot generate time-series plot.")
    else:
        ts_df = df_final.copy()
        ts_df = ts_df.dropna(subset=[time_col])

        if ts_df.empty:
            st.info("No valid time data after cleaning.")
        else:
            # If datetime, aggregate by year; otherwise group by the column directly
            if np.issubdtype(ts_df[time_col].dtype, np.datetime64):
                ts_df["__year__"] = ts_df[time_col].dt.year
                group_col = "__year__"
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

            with st.expander(f"📘 Insight — Temporal Trend of `{metric_col}`"):
                st.markdown(
                    f"""
- An upward trend in `{metric_col}` suggests **worsening conditions over time**, whereas a downward trend may indicate **improvement or successful interventions**.  
- Comparing `{metric_col}` with the **relative risk index** highlights whether high raw values also translate into **consistently high risk within this dataset**.  
- Structural breaks or sudden jumps may correspond to **policy changes, external shocks, or data collection updates** that warrant further investigation.  
                """
                )

    st.markdown("---")

    # --------------------- 3) RISK INDEX DISTRIBUTION ----------
    st.markdown("#### ⚠ Relative Risk Index Distribution")

    if df_final["risk_index_rel"].notna().sum() == 0:
        st.info(
            "Risk index could not be computed (metric column constant or invalid)."
        )
    else:
        fig_risk = px.histogram(
            df_final,
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

        with st.expander("📘 Insight — Relative Risk Profile"):
            st.markdown(
                """
- A distribution concentrated near **0** indicates that most records are relatively **low-risk** within this dataset.  
- A heavy right tail (values near 1) shows the presence of **high-risk observations**, which may be of special interest for case studies or targeted policies.  
- A broad, flat distribution suggests **strong heterogeneity in risk**, implying that segmentation or clustering may reveal meaningful subgroups.  
                """
            )

    st.info(
        "🔍 The mini-dashboard above is **auto-generated** from your uploaded columns.\n\n"
        "- Map uses **lat/lon** when available, or **country names**.\n"
        "- Time series uses any detected **Year/Date** column.\n"
        "- Relative risk index is a **0–1 normalisation** of the selected metric within this dataset."
    )

# ---------------------------------------------------------------------
# TAB 3 — HTML REPORT EXPORT (NO EXTRA LIBRARIES)
# ---------------------------------------------------------------------
with tab_export:
    st.markdown("### 📄 Export HTML Report")

    st.write(
        "This will generate a **self-contained HTML report** summarising:\n"
        "- File name & generated time\n"
        "- Rows / columns / missing values\n"
        "- Cleaning & feature engineering steps applied\n"
        "- A small sample of the processed dataset\n\n"
        "You (or your lecturer) can open it in a browser and **save as PDF**."
    )

    def build_html_report(
        df_original: pd.DataFrame,
        df_processed: pd.DataFrame,
        cleaning_steps: list[str],
        feature_steps: list[str],
        filename: str,
    ) -> str:
        """Create a simple HTML report string."""
        n_rows_o, n_cols_o = df_original.shape
        n_rows_p, n_cols_p = df_processed.shape

        missing_o = (
            df_original.isnull().mean().mean() * 100 if n_rows_o > 0 else 0.0
        )
        missing_p = (
            df_processed.isnull().mean().mean() * 100 if n_rows_p > 0 else 0.0
        )

        cleaning_html = (
            "<ul>"
            + "".join(f"<li>{step}</li>" for step in cleaning_steps)
            + "</ul>"
            if cleaning_steps
            else "<p><em>No cleaning operations applied.</em></p>"
        )

        feature_html = (
            "<ul>"
            + "".join(f"<li>{step}</li>" for step in feature_steps)
            + "</ul>"
            if feature_steps
            else "<p><em>No feature engineering operations applied.</em></p>"
        )

        sample_html = df_processed.head(50).to_html(index=False, border=0)

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Data Processing & Visualisation Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 30px;
                    color: #111827;
                    background: #f9fafb;
                }}
                h1, h2, h3 {{
                    color: #111827;
                }}
                .card {{
                    background: #ffffff;
                    border-radius: 10px;
                    padding: 16px 20px;
                    margin-bottom: 20px;
                    border: 1px solid #e5e7eb;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    background: white;
                }}
                th, td {{
                    border: 1px solid #e5e7eb;
                    padding: 6px 8px;
                    font-size: 12px;
                    text-align: left;
                }}
                th {{
                    background: #f3f4f6;
                }}
                .small-note {{
                    font-size: 11px;
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <h1>Data Processing & Visualisation Report</h1>
            <p class="small-note">
                Generated from Upload & Analyse module · {generated_at}
            </p>

            <div class="card">
                <h2>1. File Information</h2>
                <p><strong>File name:</strong> {filename}</p>
                <p><strong>Original shape:</strong> {n_rows_o:,} rows × {n_cols_o:,} columns</p>
                <p><strong>Processed shape:</strong> {n_rows_p:,} rows × {n_cols_p:,} columns</p>
                <p><strong>Original missing (%):</strong> {missing_o:.2f}%</p>
                <p><strong>Processed missing (%):</strong> {missing_p:.2f}%</p>
            </div>

            <div class="card">
                <h2>2. Cleaning Steps Applied</h2>
                {cleaning_html}
            </div>

            <div class="card">
                <h2>3. Feature Engineering Steps Applied</h2>
                {feature_html}
            </div>

            <div class="card">
                <h2>4. Sample of Processed Dataset (First 50 Rows)</h2>
                {sample_html}
                <p class="small-note">
                    Note: This is only a preview of the first 50 rows for documentation purposes.
                </p>
            </div>
        </body>
        </html>
        """
        return html

    report_html = build_html_report(
        df_original=df_raw,
        df_processed=df_final,
        cleaning_steps=clean_choice,
        feature_steps=feat_choice,
        filename=uploaded_file.name,
    )

    st.download_button(
        label="📥 Download HTML Report",
        data=report_html.encode("utf-8"),
        file_name="data_visualisation_report.html",
        mime="text/html",
    )

    st.info(
        "💡 Open the downloaded **HTML file** in a browser, then use **Print → Save as PDF** "
        "to submit a proper PDF report to your lecturer."
    )
