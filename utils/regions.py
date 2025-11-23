# utils/regions.py

from typing import Dict, Set

# -------------------------------
# 1. Region Groups (by country)
# -------------------------------
REGION_GROUPS: Dict[str, Set[str]] = {
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

# -------------------------------
# 2. Region Colours
# -------------------------------
REGION_COLORS: Dict[str, str] = {
    "Asia": "#EF4444",           # red
    "Europe": "#3B82F6",         # blue
    "Africa": "#10B981",         # green
    "North America": "#F59E0B",  # amber
    "South America": "#8B5CF6",  # violet
    "Oceania": "#EC4899",        # pink
    "Other": "#6B7280",          # grey fallback
}


def assign_region(country: str) -> str:
    """
    Map a country name to a world region.
    If not found, returns 'Other'.
    """
    if not isinstance(country, str):
        return "Other"

    for region, countries in REGION_GROUPS.items():
        if country in countries:
            return region
    return "Other"

