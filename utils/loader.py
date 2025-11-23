# utils/loader.py
import pandas as pd
import os

from utils.merged_dataset import load_merged_dataset, build_master_dataset

RAW_DIR = "data/raw"


# -------------------------------------
# Base dataset (original project data)
# -------------------------------------
def load_base_data():
    """
    Loads the project's main dataset: data/raw/air_quality_data.csv
    """
    base_path = os.path.join(RAW_DIR, "air_quality_data.csv")

    if not os.path.exists(base_path):
        print("Base dataset not found:", base_path)
        return pd.DataFrame()

    try:
        return pd.read_csv(base_path)
    except Exception as e:
        print("Error loading base dataset:", e)
        return pd.DataFrame()


# -------------------------------------
# Master (merged) dataset
# -------------------------------------
def load_master_data():
    """
    The MAIN dataset used by all pages:
    - Try merged_master.csv
    - If missing, rebuild automatically
    - If still missing, fallback to base dataset
    """
    df = load_merged_dataset()

    if df is not None and not df.empty:
        return df

    # Try rebuilding
    rebuilt = build_master_dataset()
    if rebuilt is not None and not rebuilt.empty:
        return rebuilt

    # fallback
    return load_base_data()


# -------------------------------------
# PM2.5 dataset loader (optional module)
# -------------------------------------
def load_pm25_data():
    """
    Loads PM2.5 global data if available.
    """
    pm_path = os.path.join(RAW_DIR, "pm25-air-pollution.csv")

    if not os.path.exists(pm_path):
        return None

    try:
        return pd.read_csv(pm_path)
    except:
        return None

