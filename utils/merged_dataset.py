# utils/merged_dataset.py
import pandas as pd
import os

RAW_DIR = "data/raw"

def load_merged_dataset():
    """
    Live merge of all CSV files in data/raw.
    Returns a fully unified dataset for mapping.
    """

    if not os.path.exists(RAW_DIR):
        print("RAW_DIR not found:", RAW_DIR)
        return None

    csv_files = [
        f for f in os.listdir(RAW_DIR)
        if f.endswith(".csv")
    ]

    if not csv_files:
        print("No CSV files in data/raw/")
        return None

    dfs = []
    for f in csv_files:
        path = os.path.join(RAW_DIR, f)
        try:
            df = pd.read_csv(path)
            df["source_file"] = f  # optional tracking
            dfs.append(df)
        except Exception as e:
            print("Error reading", f, ":", e)

    if not dfs:
        return None

    # Merge all files by common columns
    base = dfs[0]
    for df in dfs[1:]:
        common_cols = list(set(base.columns) & set(df.columns))
        if not common_cols:
            # If no common columns → append (outer union)
            base = pd.concat([base, df], ignore_index=True)
        else:
            # Outer merge on common fields
            base = pd.merge(base, df, on=common_cols, how="outer")

    return base
