import os
import pandas as pd

RAW_DATA_DIR = "data/raw"

@st.cache_data(show_spinner=False)
def load_raw_files():
    """Load all CSV files inside data/raw/ as a dict."""
    datasets = {}
    for file in os.listdir(RAW_DATA_DIR):
        if file.endswith(".csv"):
            path = os.path.join(RAW_DATA_DIR, file)
            try:
                df = pd.read_csv(path)
                datasets[file.replace(".csv", "")] = df
            except Exception as e:
                print(f"⚠ Failed to load {file}: {e}")
    return datasets


def detect_schema(df):
    """Returns dataset type based on column patterns."""
    cols = df.columns.str.lower()

    if "year" in cols:
        return "time_series"

    if "pm2" in cols.sum():
        return "pollutant_index"

    if "risk_index" in cols:
        return "risk_index"

    return "unknown"


@st.cache_data(show_spinner=False)
def load_master_dataset():
    """Unified dataset loader for entire dashboard."""

    all_data = load_raw_files()

    master = {}

    for name, df in all_data.items():
        df_type = detect_schema(df)
        master[df_type] = df

    return master
