# utils/merged_datasets.py

import pandas as pd
import os

def load_raw_global():
    """Load raw global air pollution dataset."""
    path = os.path.join("data", "raw", "global_air_pollution.csv")
    return pd.read_csv(path)

def load_raw_pm25():
    """Load raw PM2.5 time-series dataset."""
    path = os.path.join("data", "raw", "pm25-air-pollution.csv")
    return pd.read_csv(path)

def load_merged_dataset():
    """
    Returns combined dataset:
    - global pollution raw data
    - PM2.5 time-series raw data
    No preprocessing is done here.
    """
    try:
        df_global = load_raw_global()
    except Exception:
        df_global = pd.DataFrame()

    try:
        df_pm25 = load_raw_pm25()
    except Exception:
        df_pm25 = pd.DataFrame()

    if not df_global.empty:
        df_global["source"] = "global_pollution"

    if not df_pm25.empty:
        df_pm25["source"] = "pm25_timeseries"

    merged_df = pd.concat([df_global, df_pm25], ignore_index=True, sort=False)

    return merged_df

