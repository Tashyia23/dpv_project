import numpy as np
import pandas as pd

def clean_missing(df, strategy="none"):
    if strategy == "drop":
        return df.dropna()
    elif strategy == "mean":
        num = df.select_dtypes(include="number")
        df[num.columns] = num.fillna(num.mean())
    elif strategy == "median":
        num = df.select_dtypes(include="number")
        df[num.columns] = num.fillna(num.median())
    return df


def scale_column(df, col, method="none"):
    if method == "minmax":
        df[f"{col}_scaled"] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        return df, f"{col}_scaled"
    elif method == "zscore":
        df[f"{col}_z"] = (df[col] - df[col].mean()) / df[col].std()
        return df, f"{col}_z"
    return df, col


def percentile_filter(df, col, low, high):
    q_low = np.percentile(df[col].dropna(), low)
    q_high = np.percentile(df[col].dropna(), high)
    return df[(df[col] >= q_low) & (df[col] <= q_high)]
