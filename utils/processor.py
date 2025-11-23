# utils/processor.py
import pandas as pd
import numpy as np
from utils.preprocess import minmax_scale

def add_risk_index(df):
    """
    Computes a basic 0–1 scaled risk index from *_aqi_value columns.
    """
    pollutant_cols = [c for c in df.columns if c.endswith("_aqi_value")]

    if not pollutant_cols:
        df["risk_index"] = np.nan
        return df

    scaled = {}
    for col in pollutant_cols:
        series = pd.to_numeric(df[col], errors="coerce")
        scaled[col] = minmax_scale(series)

    scaled_df = pd.DataFrame(scaled)
    df["risk_index"] = scaled_df.mean(axis=1)
    return df
