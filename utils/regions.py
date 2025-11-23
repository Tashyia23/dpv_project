# # utils/regions.py

# from typing import Dict, Set

# REGION_MAP: Dict[str, Set[str]] = {
#     "Asia": {
#         "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
#         "Cambodia", "China", "Georgia", "India", "Indonesia",
#         "Iran (Islamic Republic of)", "Iraq", "Israel", "Japan", "Jordan",
#         "Kazakhstan", "Kuwait", "Kyrgyzstan",
#         "Lao People's Democratic Republic", "Lebanon", "Malaysia", "Maldives",
#         "Mongolia", "Myanmar", "Nepal", "Oman", "Pakistan", "Philippines", "Qatar",
#         "Republic of Korea", "Saudi Arabia", "Singapore",
#         "Sri Lanka", "State of Palestine", "Syrian Arab Republic",
#         "Tajikistan", "Thailand", "Turkey", "Turkmenistan",
#         "United Arab Emirates", "Uzbekistan", "Viet Nam", "Yemen",
#     },

#     "Europe": {
#         "Albania", "Andorra", "Austria", "Belarus", "Belgium",
#         "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Czechia", "Denmark",
#         "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
#         "Iceland", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
#         "Malta", "Monaco", "Montenegro", "Netherlands",
#         "Republic of Moldova", "Republic of North Macedonia",
#         "Norway", "Poland", "Portugal", "Romania",
#         "Russian Federation", "Serbia", "Slovakia", "Slovenia",
#         "Spain", "Sweden", "Switzerland", "Ukraine",
#         "United Kingdom of Great Britain and Northern Ireland", "Cyprus",
#     },

#     "Africa": {
#         "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
#         "Cabo Verde", "Cameroon", "Central African Republic", "Chad",
#         "Comoros", "Congo", "Côte d'Ivoire", "Democratic Republic of the Congo",
#         "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia",
#         "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau",
#         "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
#         "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique",
#         "Namibia", "Niger", "Nigeria", "Rwanda", "Senegal", "Seychelles",
#         "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan",
#         "Togo", "Tunisia", "Uganda", "United Republic of Tanzania",
#         "Zambia", "Zimbabwe",
#     },

#     "North America": {
#         "Canada", "United States of America", "Mexico",
#         "Belize", "Costa Rica", "Cuba", "Dominican Republic", "El Salvador",
#         "Guatemala", "Haiti", "Honduras", "Nicaragua", "Panama",
#         "Jamaica", "Trinidad and Tobago",
#         "Barbados", "Saint Kitts and Nevis", "Saint Lucia", "Aruba",
#     },

#     "South America": {
#         "Argentina", "Bolivia (Plurinational State of)", "Brazil", "Chile",
#         "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru",
#         "Suriname", "Uruguay", "Venezuela (Bolivarian Republic of)",
#     },

#     "Oceania": {
#         "Australia", "New Zealand", "Papua New Guinea",
#         "Solomon Islands", "Vanuatu", "Palau",
#     },
# }

# def assign_region(country: str):
#     """Return region name based on country."""
#     for region, countries in REGION_MAP.items():
#         if country in countries:
#             return region
#     return "Other"

# REGION_COLORS = {
#     "North America": "#2563eb",
#     "South America": "#059669",
#     "Europe": "#db2777",
#     "Asia": "#f59e0b",
#     "Africa": "#7c3aed",
#     "Oceania": "#e11d48",
#     "Other": "#6b7280",
# }


#_____________________________

import os
import json
import requests
from typing import Dict, Set

# ----------------------------------------------------
# 1. ORIGINAL MANUAL REGION MAP (fallback layer)
# ----------------------------------------------------
REGION_MAP: Dict[str, Set[str]] = {
    "Asia": {
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh",
        "Bhutan", "Cambodia", "China", "Georgia", "India", "Indonesia",
        "Iran (Islamic Republic of)", "Iraq", "Israel", "Japan", "Jordan",
        "Kazakhstan", "Kuwait", "Kyrgyzstan", "Lao People's Democratic Republic",
        "Lebanon", "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal",
        "Oman", "Pakistan", "Philippines", "Qatar", "Republic of Korea",
        "Saudi Arabia", "Singapore", "Sri Lanka", "State of Palestine",
        "Syrian Arab Republic", "Tajikistan", "Thailand", "Turkey",
        "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Viet Nam",
        "Yemen",
    },

    "Europe": {
        "Albania", "Andorra", "Austria", "Belarus", "Belgium",
        "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Czechia", "Denmark",
        "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
        "Iceland", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
        "Malta", "Monaco", "Montenegro", "Netherlands",
        "Republic of Moldova", "Republic of North Macedonia",
        "Norway", "Poland", "Portugal", "Romania",
        "Russian Federation", "Serbia", "Slovakia", "Slovenia",
        "Spain", "Sweden", "Switzerland", "Ukraine",
        "United Kingdom of Great Britain and Northern Ireland", "Cyprus",
    },

    "Africa": {
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi",
        "Cabo Verde", "Cameroon", "Central African Republic", "Chad",
        "Comoros", "Congo", "Côte d'Ivoire", "Democratic Republic of the Congo",
        "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia",
        "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya",
        "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali",
        "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
        "Nigeria", "Rwanda", "Senegal", "Seychelles", "Sierra Leone", "Somalia",
        "South Africa", "South Sudan", "Sudan", "Togo", "Tunisia", "Uganda",
        "United Republic of Tanzania", "Zambia", "Zimbabwe",
    },

    "North America": {
        "Canada", "United States of America", "Mexico", "Belize",
        "Costa Rica", "Cuba", "Dominican Republic", "El Salvador",
        "Guatemala", "Haiti", "Honduras", "Nicaragua", "Panama",
        "Jamaica", "Trinidad and Tobago", "Barbados", "Saint Kitts and Nevis",
        "Saint Lucia", "Aruba",
    },

    "South America": {
        "Argentina", "Bolivia (Plurinational State of)", "Brazil",
        "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru",
        "Suriname", "Uruguay", "Venezuela (Bolivarian Republic of)",
    },

    "Oceania": {
        "Australia", "New Zealand", "Papua New Guinea",
        "Solomon Islands", "Vanuatu", "Palau",
    },
}

REGION_COLORS = {
    "North America": "#2563eb",
    "South America": "#059669",
    "Europe": "#db2777",
    "Asia": "#f59e0b",
    "Africa": "#7c3aed",
    "Oceania": "#e11d48",
    "Other": "#6b7280",
}

# ----------------------------------------------------
# 2. CACHE FILE PATH
# ----------------------------------------------------
CACHE_PATH = os.path.join(os.path.dirname(__file__), "region_cache.json")

def _load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

# ----------------------------------------------------
# 3. API LOOKUP FUNCTION
# ----------------------------------------------------
def fetch_region_from_api(country: str) -> str:
    """
    Uses the public API at RESTCountries to detect region.
    Example endpoint:
      https://restcountries.com/v3.1/name/Malaysia?fields=region
    """
    try:
        url = f"https://restcountries.com/v3.1/name/{country}?fields=region"
        res = requests.get(url, timeout=3)

        if res.status_code != 200:
            return None

        data = res.json()
        if isinstance(data, list) and "region" in data[0]:
            return data[0]["region"]

        return None

    except Exception:
        return None

# ----------------------------------------------------
# 4. HYBRID REGION DETECTOR
# ----------------------------------------------------
def assign_region(country: str) -> str:
    """
    Hybrid region detection:
    1) Try cache
    2) Try API
    3) Try dictionary
    4) Else → Other
    """
    if not country or not isinstance(country, str):
        return "Other"

    country = country.strip()

    # ----- (1) Check cache -----
    cache = _load_cache()
    if country in cache:
        return cache[country]

    # ----- (2) Try API -----
    api_region = fetch_region_from_api(country)
    if api_region:
        cache[country] = api_region
        _save_cache(cache)
        return api_region

    # ----- (3) Try dictionary -----
    for region, countries in REGION_MAP.items():
        if country in countries:
            cache[country] = region
            _save_cache(cache)
            return region

    # ----- (4) Fallback -----
    cache[country] = "Other"
    _save_cache(cache)
    return "Other"




