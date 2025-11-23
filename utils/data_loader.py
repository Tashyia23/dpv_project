# utils/data_loader.py

import pandas as pd
import os

RAW_DIR = "data/raw"

# -------------------------------------------------------------
# 1. Load RAW DATA (Before Processing)
# -------------------------------------------------------------
def load_raw_dataset():
    """Return the unprocessed raw datasets separately."""
    global_path = os.path.join(RAW_DIR, "global_air_pollution.csv")
    pm25_path = os.path.join(RAW_DIR, "pm25-air-pollution.csv")

    if not os.path.exists(global_path) or not os.path.exists(pm25_path):
        print("Missing raw files.")
        return None, None

    try:
        g = pd.read_csv(global_path)
        p = pd.read_csv(pm25_path)
        return g, p
    except Exception as e:
        print("Error reading raw:", e)
        return None, None


# -------------------------------------------------------------
# 2. Load PROCESSED DATA (After Processing)
# -------------------------------------------------------------
def load_merged_dataset():
    """Load cleaned + standardized + merged version."""

    g, p = load_raw_dataset()
    if g is None or p is None:
        return None

    # --- Standardize Global Dataset ---
    rename_global = {
        "AQI Value": "aqi_value",
        "PM2.5 AQI Value": "pm25_aqi_value",
        "NO2 AQI Value": "no2_aqi_value",
        "Ozone AQI Value": "ozone_aqi_value",
        "CO AQI Value": "co_aqi_value",
        "Country": "country",
    }
    g = g.rename(columns=rename_global)

    pollutants = [
        "aqi_value", "pm25_aqi_value", "no2_aqi_value",
        "ozone_aqi_value", "co_aqi_value"
    ]
    for col in pollutants:
        if col in g.columns:
            g[col] = pd.to_numeric(g[col], errors="coerce")

    # --- Process PM2.5 dataset ---
    p = p.rename(columns={
        "Entity": "country",
        "Year": "year",
        "Concentrations of fine particulate matter (PM2.5) - Residence area type: Total": "pm25_value"
    })

    # Merge l
