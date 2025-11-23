# utils/regions.py

from typing import Dict, Set

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

def assign_region(country: str):
    return REGION_MAP.get(country, "Other")


REGION_COLORS = {
    "North America": "#2563eb",
    "South America": "#059669",
    "Europe": "#db2777",
    "Asia": "#f59e0b",
    "Africa": "#7c3aed",
    "Oceania": "#e11d48",
    "Other": "#6b7280",
}


