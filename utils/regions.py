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

import pycountry
from rapidfuzz import process

# --------------------------------
# 1. Region lookup using pycountry
# --------------------------------
def get_country_region(country_name: str) -> str:
    """
    Attempts to detect a country's region automatically:
    - Handles alternate spellings
    - Handles abbreviations
    - Uses fuzzy matching for inconsistent names
    """

    if not isinstance(country_name, str) or country_name.strip() == "":
        return "Other"

    # Try exact match first
    try:
        country = pycountry.countries.lookup(country_name)
    except LookupError:
        country = None

    # If lookup fails → fuzzy match from pycountry list
    if country is None:
        names = [c.name for c in pycountry.countries]
        match, score, _ = process.extractOne(country_name, names)

        if score >= 85:  # strong match threshold
            country = pycountry.countries.get(name=match)

    if country is None:
        return "Other"

    # Now detect region via pycountry subdivisions
    try:
        # Some countries have a single default subdivision listing region
        subdivisions = list(pycountry.subdivisions.get(country_code=country.alpha_2))
        if subdivisions:
            region = subdivisions[0].type
            if region in ["Asia", "Europe", "Africa", "Americas", "Oceania"]:
                return region
    except Exception:
        pass

    # Manual continent mapping fallback
    continent_map = {
        "AF": "Africa",
        "AS": "Asia",
        "EU": "Europe",
        "NA": "North America",
        "SA": "South America",
        "OC": "Oceania",
    }

    country_continent = getattr(country, "region", None)

    # If pycountry detected region internally (depends on dataset)
    if country_continent in continent_map.values():
        return country_continent

    # Alpha-2 to continent fallback
    return continent_map.get(getattr(country, "alpha_2", ""), "Other")


# Public function for Streamlit use
def assign_region(name: str) -> str:
    return get_country_region(name)



