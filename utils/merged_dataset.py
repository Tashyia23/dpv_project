# utils/merged_datasets.py

import pandas as pd
import os

# -------------------------------------------------------------------
# Load raw datasets (no cleaning, no preprocessing)
# -------------------------------------------------------------------
def load_raw_global():
    """Load global air pollution dataset in raw form."""
    path = os.path.join("data", "global_air_pollution.csv")
    return pd.read_csv(path)

def load_raw_pm25():
    """Load PM2.5 time-series dataset in raw form."""
    path = os.path.join("data", "pm25-air-pollution.csv")
    return pd.read_csv(path)

# -------------------------------------------------------------------
# Combine both datasets into a single DataFrame (row-wise)
# -------------------------------------------------------------------
def load_merged_dataset():
    """
    Returns a combined dataset containing:
      - global_air_pollution.csv raw rows
      - pm25-air-pollution.csv raw rows

    NO preprocessing happens here.
    All cleaning and processing is done inside Streamlit pages.
    """
    df_global = load_raw_global()
    df_pm25 = load_raw_pm25()

    # Add identifiers to avoid confusion
    df_global["source"] = "global_pollution"
    df_pm25["source"] = "pm25_timeseries"

    # Stack them together
    merged_df = pd.concat([df_global, df_pm25], ignore_index=True, sort=False)

    return merged_df
