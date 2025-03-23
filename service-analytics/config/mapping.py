"""
Mapping between different system identifiers.
"""

# Mapping between GPS device names and ServiceDesk technician codes
TECH_MAPPING = {
    "James": "JS",
    "Joe": "JD",
    "Bianca": "BB",
    "Ricardo (NEW)": "RR",
    "Shane": "SS",
    "Porter": "AP",
    "Dane": "DM",
    "Sean": "SF"
}

# Reverse mapping for convenience
TECH_REVERSE_MAPPING = {v: k for k, v in TECH_MAPPING.items()}

# Staff with no GPS tracking
STAFF_NO_GPS = {
    "MK": "Mark",  # Owner
    "AJ": "Abby",  # CSR
    "KH": "Kendra",  # CSR
    "LL": "Laura",  # CSR
    "XX": "Online"  # Online scheduling
}

# Known locations
KNOWN_LOCATIONS = {
    "SHOP": "466 Primero Ct, Cotati, CA 94931, USA",
    # Add technician home addresses here
    # "JS_HOME": "...",
} 