import pandas as pd
import numpy as np

def assign_regions(df, region_map):
    df["region"] = df["country"].map(region_map).fillna("Other")
    return df

def scale_columns(df, cols):
    scaled = df.copy()
    for col in cols:
        series = scaled[col].astype(float)
        lo, hi = series.min(), series.max()
        scaled[col + "_scaled"] = (series - lo) / (hi - lo) if hi > lo else 0
    return scaled

def compute_risk_index(df, pollutants, weights):
    df = df.copy()
    for col in pollutants:
        s = df[col].astype(float)
        lo, hi = s.min(), s.max()
        df[col + "_norm"] = (s - lo) / (hi - lo) if hi > lo else 0

    df["risk_index"] = sum(
        df[col + "_norm"] * weights[col] for col in pollutants
    )
    return df

def merge_datasets(global_df, pm25_df):
    return global_df.merge(pm25_df, on=["country", "year"], how="left")
