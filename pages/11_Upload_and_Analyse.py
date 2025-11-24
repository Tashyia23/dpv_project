import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.ui import header

st.set_page_config(layout="wide")


# --------------------------------------------------------------------
# Robust universal CSV loader (handles WAQI, COVID, large messy files)
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


# --------------------------------------------------------------------
# Dataset Overview
# --------------------------------------------------------------------
st.success("✅ File successfully loaded!")
st.markdown("### 📊 Dataset Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{df.shape[0]:,}")
col2.metric("Columns", f"{df.shape[1]:,}")
col3.metric(
    "Missing Values (%)",
    f"{df.isnull().mean().mean() * 100:.2f}%"
)

st.dataframe(df.head(50), use_container_width=True)


# --------------------------------------------------------------------
# Missing Value Heatmap
# --------------------------------------------------------------------
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
except:
    st.info("Too many rows to display heatmap.")


# --------------------------------------------------------------------
# Column Type Summary
# --------------------------------------------------------------------
st.markdown("### 🧬 Column Type Summary")

dtype_counts = df.dtypes.astype(str).value_counts()
st.bar_chart(dtype_counts)


# --------------------------------------------------------------------
# Selection: Column-wise Statistics
# --------------------------------------------------------------------
st.markdown("### 📈 Column Statistics")

selected_col = st.selectbox(
    "Select a column to analyse:",
    df.columns
)

if pd.api.types.is_numeric_dtype(df[selected_col]):
    # ------------------------------
    # Numeric Column Visualisations
    # ------------------------------
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
    # ------------------------------
    # Categorical Column Visualisations
    # ------------------------------
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


# --------------------------------------------------------------------
# Optional: Download Cleaned Data
# --------------------------------------------------------------------
st.markdown("### 📥 Download Cleaned Dataset")

cleaned_csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Cleaned CSV",
    cleaned_csv,
    file_name="cleaned_dataset.csv",
    mime="text/csv"
)
