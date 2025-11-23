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
import pycountry
from rapidfuzz import fuzz, process

# -------------------------
# UN M49 Region Mapping
# -------------------------
UN_REGION_MAP = {
    "Africa": ["AF", "011", "012", "013", "014", "017", "018"],
    "Asia": ["AS", "030", "034", "035", "143", "145"],
    "Europe": ["EU", "039", "151", "154", "155"],
    "North America": ["019", "021", "013"],       # includes Caribbean + Central America
    "South America": ["005"],
    "Oceania": ["009", "053", "054", "057", "061"],
}

def get_region_from_un_m49(country_name: str):
    try:
        result = pycountry.countries.search_fuzzy(country_name)[0]
        country_alpha2 = result.alpha_2
        country_numeric = result.numeric
    except Exception:
        return "Other"

    # Match via numeric region codes
    for region, codes in UN_REGION_MAP.items():
        if country_numeric in codes:
            return region

    # If not found directly — fallback
    return "Other"


# -------------------------
# Fuzzy Matching Wrapper
# -------------------------
def assign_region(country_name: str):
    if not isinstance(country_name, str) or not country_name.strip():
        return "Other"

    # Try direct UN region lookup
    region = get_region_from_un_m49(country_name)
    if region != "Other":
        return region

    # Fuzzy rescue for odd names (e.g. "United States", "Viet Nam")
    all_countries = [c.name for c in pycountry.countries]
    best, score, _ = process.extractOne(country_name, all_countries, scorer=fuzz.WRatio)

    if score > 85:  # Strong match
        return get_region_from_un_m49(best)

    return "Other"

