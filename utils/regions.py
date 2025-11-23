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

# utils/regions.py

from typing import Dict, Set
from pathlib import Path
import json

# -------------------------------
# 1. Region Groups (by country)
# -------------------------------
REGION_MAP: Dict[str, Set[str]] = {
    "Asia": {
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
        "Cambodia", "China", "Georgia", "India", "Indonesia",
        "Iran (Islamic Republic of)", "Iraq", "Israel", "Japan", "Jordan",
        "Kazakhstan", "Kuwait", "Kyrgyzstan",
        "Lao People's Democratic Republic", "Lebanon", "Malaysia", "Maldives",
        "Mongolia", "Myanmar", "Nepal", "Oman", "Pakistan", "Philippines", "Qatar",
        "Republic of Korea", "Saudi Arabia", "Singapore",
        "Sri Lanka", "State of Palestine", "Syrian Arab Republic",
        "Tajikistan", "Thailand", "Turkey", "Turkmenistan",
        "United Arab Emirates", "Uzbekistan", "Viet Nam", "Yemen",
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
        "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau",
        "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
        "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique",
        "Namibia", "Niger", "Nigeria", "Rwanda", "Senegal", "Seychelles",
        "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan",
        "Togo", "Tunisia", "Uganda", "United Republic of Tanzania",
        "Zambia", "Zimbabwe",
    },

    "North America": {
        "Canada", "United States of America", "Mexico",
        "Belize", "Costa Rica", "Cuba", "Dominican Republic", "El Salvador",
        "Guatemala", "Haiti", "Honduras", "Nicaragua", "Panama",
        "Jamaica", "Trinidad and Tobago",
        "Barbados", "Saint Kitts and Nevis", "Saint Lucia", "Aruba",
    },

    "South America": {
        "Argentina", "Bolivia (Plurinational State of)", "Brazil", "Chile",
        "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru",
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

# -------------------------------
# 2. Cache file (hybrid option)
# -------------------------------

_CACHE_PATH = Path(__file__).with_name("region_cache.json")


def _load_cache() -> Dict[str, str]:
    """
    Safely load region cache from JSON.
    - Returns {} if file is missing, empty, or invalid JSON.
    - Prevents JSONDecodeError from crashing Streamlit.
    """
    if not _CACHE_PATH.exists():
        return {}

    try:
        text = _CACHE_PATH.read_text(encoding="utf-8").strip()
        if not text:
            # Empty file → treat as no cache
            return {}
        data = json.loads(text)
        if isinstance(data, dict):
            return data
        return {}
    except (json.JSONDecodeError, OSError, ValueError):
        # Broken / partial / corrupted JSON → ignore
        return {}


def _save_cache(cache: Dict[str, str]) -> None:
    """
    Save cache back to JSON file (best-effort; silently ignore I/O errors).
    """
    try:
        _CACHE_PATH.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        # If we can't write (permissions, etc.), just skip.
        pass


# -------------------------------
# 3. Static lookup + hybrid assign
# -------------------------------

def _lookup_static_region(country: str) -> str | None:
    """Check REGION_MAP for an exact country match."""
    for region, countries in REGION_MAP.items():
        if country in countries:
            return region
    return None


def assign_region(country: str) -> str:
    """
    Hybrid region assignment:
    1. Try static REGION_MAP
    2. Try local JSON cache (region_cache.json)
    3. Fallback → 'Other' and store in cache for consistency
    """
    if not isinstance(country, str) or not country.strip():
        return "Other"

    country = country.strip()

    # 1) Static dictionary mapping
    region = _lookup_static_region(country)
    if region:
        return region

    # 2) Cache lookup
    cache = _load_cache()
    if country in cache:
        return cache[country]

    # 3) Fallback – treat as "Other"
    region = "Other"
    cache[country] = region
    _save_cache(cache)

    return region


