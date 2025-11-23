# utils/loader.py

import os
import pandas as pd

from utils.merged_dataset import load_master_dataset 

# -----------------------------------------------------
# Helper: Safe CSV loader with fallback + clean errors
# -----------------------------------------------------
def safe_read_csv(path):
    """
    Safely read a CSV file.
    Returns:
        pd.DataFrame() (empty) if the file does not exist.
    """
    if not os.path.exists(path):
        print(f"[loader.py] WARNING: File not found -> {path}")
        return pd.DataFrame()  # Safe fallback

    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"[loader.py] ERROR loading CSV ({path}): {e}")
        return pd.DataFrame()


# -----------------------------------------------------
# LOADERS FOR INDIVIDUAL RAW DATASETS
# -----------------------------------------------------
def load_global_pollution():
    """Loads main global pollution dataset."""
    path = os.path.join("data", "raw", "global_air_pollution.csv")
    return safe_read_csv(path)


def load_pm25_time_series():
    """Loads PM2.5 long-format yearly dataset."""
    path = os.path.join("data", "raw", "pm25-air-pollution.csv")
    return safe_read_csv(path)


# -----------------------------------------------------
# MERGED DATASET (combines both without processing)
# -----------------------------------------------------
def load_master_data():
    """
    Loads and combines all raw datasets using merged_datasets.py.
    Returns a unified dataframe for dashboard-wide use.
    """
    try:
        from utils.merged_datasets import load_merged_dataset
    except Exception as e:
        print(f"[loader.py] ERROR: Could not import merged_datasets.py -> {e}")
        return pd.DataFrame()

    df = load_merged_dataset()

    if df.empty:
        print("[loader.py] WARNING: merged dataset is EMPTY.")
    else:
        print("[loader.py] Loaded merged dataset successfully.")

    return df


# -----------------------------------------------------
# SPECIALIZED LOADERS (used by pages)
# -----------------------------------------------------
def load_base_data():
    """
    Used by the Risk Index dashboard pages.
    Loads global_air_pollution.csv only.
    """
    df = load_global_pollution()

    if df.empty:
        print("[loader.py] WARNING: base data is EMPTY.")
    return df


def load_pm25_data():
    """
    Used by the Time-Series Explorer.
    Loads PM2.5 time-series only.
    """
    df = load_pm25_time_series()

    if df.empty:
        print("[loader.py] WARNING: PM2.5 dataset is EMPTY.")
    return df

