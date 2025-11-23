# utils/merged_dataset.py
import pandas as pd
import os

DATA_DIR = "data/merged"

def load_merged_dataset():
    """Load the merged dataset (if exists)."""
    merged_path = os.path.join(DATA_DIR, "merged_master.csv")

    if not os.path.exists(merged_path):
        return None  # Let loader.py build it

    try:
        df = pd.read_csv(merged_path)
        return df
    except Exception as e:
        print("Error loading merged dataset:", e)
        return None


def build_master_dataset():
    """
    Automatically scans data/merged/ for all CSV files and merges them.
    """
    if not os.path.exists(DATA_DIR):
        return None

    csv_files = [
        f for f in os.listdir(DATA_DIR)
        if f.endswith(".csv") and "master" not in f
    ]

    if not csv_files:
        return None

    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, f))
            dfs.append(df)
        except:
            pass

    if not dfs:
        return None

    # merge on common columns only
    base = dfs[0]
    for df in dfs[1:]:
        common = list(set(base.columns).intersection(set(df.columns)))
        if not common:
            continue
        base = pd.merge(base, df, on=common, how="outer")

    # Save master file
    master_path = os.path.join(DATA_DIR, "merged_master.csv")
    base.to_csv(master_path, index=False)

    return base

