# utils/preprocess.py
import pandas as pd
import numpy as np

def minmax_scale(series):
    lo, hi = series.min(), series.max()
    if hi <= lo:
        return np.zeros_like(series)
    return (series - lo) / (hi - lo)


def zscore(series):
    mean, std = series.mean(), series.std()
    if std == 0:
        return np.zeros_like(series)
    return (series - mean) / std


def fill_mean(df):
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].mean())
    return df


def fill_median(df):
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    return df

