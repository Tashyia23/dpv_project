# utils/regions.py

# ----------------------------------------
# Region Auto-Assignment Dictionary for region mapping
# ----------------------------------------

REGION_MAP = {
    # --- AFRICA ---
    "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa",
    "Botswana": "Africa", "Burkina Faso": "Africa", "Burundi": "Africa",
    "Cabo Verde": "Africa", "Cameroon": "Africa", "Central African Republic": "Africa",
    "Chad": "Africa", "Comoros": "Africa", "Congo": "Africa",
    "Democratic Republic of the Congo": "Africa",
    "Côte d'Ivoire": "Africa", "Egypt": "Africa",
    "Equatorial Guinea": "Africa", "Eritrea": "Africa",
    "Eswatini": "Africa", "Ethiopia": "Africa", "Gabon": "Africa",
    "Gambia": "Africa", "Ghana": "Africa", "Guinea": "Africa",
    "Guinea-Bissau": "Africa", "Kenya": "Africa", "Lesotho": "Africa",
    "Liberia": "Africa", "Libya": "Africa", "Madagascar": "Africa",
    "Malawi": "Africa", "Mali": "Africa", "Mauritania": "Africa",
    "Mauritius": "Africa", "Morocco": "Africa", "Mozambique": "Africa",
    "Namibia": "Africa", "Niger": "Africa", "Nigeria": "Africa",
    "Rwanda": "Africa", "Senegal": "Africa", "Seychelles": "Africa",
    "Sierra Leone": "Africa", "Somalia": "Africa", "South Africa": "Africa",
    "South Sudan": "Africa", "Sudan": "Africa",
    "United Republic of Tanzania": "Africa",
    "Togo": "Africa", "Tunisia": "Africa", "Uganda": "Africa",
    "Zambia": "Africa", "Zimbabwe": "Africa",

    # --- ASIA ---
    "Afghanistan": "Asia", "Armenia": "Asia", "Azerbaijan": "Asia",
    "Bahrain": "Asia", "Bangladesh": "Asia", "Bhutan": "Asia",
    "Cambodia": "Asia", "China": "Asia", "Georgia": "Asia",
    "India": "Asia", "Indonesia": "Asia",
    "Iran (Islamic Republic of)": "Asia", "Iraq": "Asia", "Israel": "Asia",
    "Japan": "Asia", "Jordan": "Asia", "Kazakhstan": "Asia",
    "Kuwait": "Asia", "Kyrgyzstan": "Asia",
    "Lao People's Democratic Republic": "Asia",
    "Lebanon": "Asia", "Malaysia": "Asia", "Maldives": "Asia",
    "Mongolia": "Asia", "Myanmar": "Asia", "Nepal": "Asia",
    "Oman": "Asia", "Pakistan": "Asia", "Philippines": "Asia",
    "Qatar": "Asia", "Republic of Korea": "Asia",
    "Saudi Arabia": "Asia", "Singapore": "Asia",
    "Sri Lanka": "Asia", "State of Palestine": "Asia",
    "Syrian Arab Republic": "Asia", "Tajikistan": "Asia",
    "Thailand": "Asia", "Turkey": "Asia", "Turkmenistan": "Asia",
    "United Arab Emirates": "Asia", "Uzbekistan": "Asia",
    "Viet Nam": "Asia", "Yemen": "Asia",

    # --- EUROPE ---
    "Albania": "Europe", "Andorra": "Europe", "Austria": "Europe",
    "Belarus": "Europe", "Belgium": "Europe", "Bosnia and Herzegovina": "Europe",
    "Bulgaria": "Europe", "Croatia": "Europe", "Cyprus": "Europe",
    "Czechia": "Europe", "Denmark": "Europe", "Estonia": "Europe",
    "Finland": "Europe", "France": "Europe", "Germany": "Europe",
    "Greece": "Europe", "Hungary": "Europe", "Iceland": "Europe",
    "Ireland": "Europe", "Italy": "Europe", "Latvia": "Europe",
    "Lithuania": "Europe", "Luxembourg": "Europe",
    "Malta": "Europe", "Monaco": "Europe", "Montenegro": "Europe",
    "Netherlands": "Europe", "Norway": "Europe",
    "Poland": "Europe", "Portugal": "Europe", "Republic of Moldova": "Europe",
    "Romania": "Europe", "Russian Federation": "Europe",
    "Serbia": "Europe", "Slovakia": "Europe", "Slovenia": "Europe",
    "Spain": "Europe", "Sweden": "Europe", "Switzerland": "Europe",
    "Ukraine": "Europe",
    "United Kingdom of Great Britain and Northern Ireland": "Europe",

    # --- NORTH AMERICA ---
    "Canada": "North America", "United States of America": "North America",
    "Mexico": "North America", "Belize": "North America",
    "Costa Rica": "North America", "El Salvador": "North America",
    "Guatemala": "North America", "Honduras": "North America",
    "Nicaragua": "North America", "Panama": "North America",
    "Jamaica": "North America", "Cuba": "North America",
    "Haiti": "North America", "Dominican Republic": "North America",
    "Barbados": "North America", "Saint Lucia": "North America",
    "Saint Kitts and Nevis": "North America",
    "Trinidad and Tobago": "North America",

    # --- SOUTH AMERICA ---
    "Argentina": "South America",
    "Bolivia (Plurinational State of)": "South America",
    "Brazil": "South America", "Chile": "South America",
    "Colombia": "South America", "Ecuador": "South America",
    "Guyana": "South America", "Paraguay": "South America",
    "Peru": "South America", "Suriname": "South America",
    "Uruguay": "South America",
    "Venezuela (Bolivarian Republic of)": "South America",

    # --- OCEANIA ---
    "Australia": "Oceania", "New Zealand": "Oceania",
    "Papua New Guinea": "Oceania", "Solomon Islands": "Oceania",
    "Vanuatu": "Oceania", "Palau": "Oceania"
}

def assign_region(country: str) -> str:
    return REGION_MAP.get(country, "Other")
