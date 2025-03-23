"""
Data cleaning and standardization functions.
"""

import re
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import sys
import os

# Add the project root to the path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.mapping import TECH_MAPPING, TECH_REVERSE_MAPPING

def standardize_address(address_str):
    """
    Standardize address format for better matching.
    
    Args:
        address_str: Raw address string
        
    Returns:
        Standardized address string
    """
    if pd.isna(address_str) or address_str == '':
        return ''
    
    address = str(address_str).strip().upper()
    
    # Standardize common abbreviations
    abbrev_map = {
        'STREET': 'ST',
        'AVENUE': 'AVE',
        'BOULEVARD': 'BLVD',
        'DRIVE': 'DR',
        'LANE': 'LN',
        'ROAD': 'RD',
        'COURT': 'CT',
        'CIRCLE': 'CIR',
        'PLACE': 'PL',
        'HIGHWAY': 'HWY',
        'APARTMENT': 'APT',
        'SUITE': 'STE',
        'CALIFORNIA': 'CA'
    }
    
    for full, abbr in abbrev_map.items():
        # Replace full version with abbreviation
        address = re.sub(r'\b' + full + r'\b', abbr, address)
        # Replace abbreviation with period with standard abbreviation
        address = re.sub(r'\b' + abbr + r'\.', abbr, address)
    
    # Remove extra spaces, commas, and periods
    address = re.sub(r'\s+', ' ', address)
    address = re.sub(r',\s*,', ',', address)
    address = re.sub(r'\.\s*\.', '.', address)
    
    # Remove USA at the end
    address = re.sub(r',\s*USA$', '', address)
    
    return address.strip()

def standardize_tech_code(tech_code):
    """
    Standardize technician code format.
    
    Args:
        tech_code: Raw technician code
        
    Returns:
        Standardized technician code
    """
    if pd.isna(tech_code) or tech_code == '':
        return 'UNKNOWN'
    
    # Convert to string, uppercase, and strip spaces
    tech = str(tech_code).strip().upper()
    
    # Handle common variations
    tech_variations = {
        'ROBERT': 'RR',
        'RICK': 'RR',
        'RICARDO': 'RR',
        'JAMES': 'JS',
        'JIM': 'JS',
        'JOSEPH': 'JD',
        'JOEY': 'JD',
        'DANIEL': 'DM',
        'DANNY': 'DM',
        'SHANE': 'SS',
        'SHAWN': 'SF',
        'SEAN': 'SF',
        'BIANCA': 'BB',
        'ADAM': 'AP',
        'PORTER': 'AP'
    }
    
    # Check if tech code matches any variation
    if tech in tech_variations:
        return tech_variations[tech]
    
    # If it's already a valid code, return it
    valid_codes = set(TECH_REVERSE_MAPPING.keys()) | set(TECH_MAPPING.keys())
    if tech in valid_codes:
        return tech
    
    # Otherwise, return as is
    return tech

def standardize_appliance_type(appliance_type):
    """
    Standardize appliance type names.
    
    Args:
        appliance_type: Raw appliance type string
        
    Returns:
        Standardized appliance type
    """
    if pd.isna(appliance_type) or appliance_type == '':
        return 'UNKNOWN'
    
    # Convert to string, uppercase, and strip spaces
    appliance = str(appliance_type).strip().upper()
    
    # Define common categories
    categories = {
        'REFRIGERATOR': ['REFRIG', 'FRIDGE', 'FRIG', 'REFRIGERATOR', 'FREEZER'],
        'WASHER': ['WASH', 'WASHER', 'CLOTHES WASHER'],
        'DRYER': ['DRYER', 'CLOTHES DRYER'],
        'DISHWASHER': ['DISH', 'DISHW', 'DISHWASHER'],
        'OVEN': ['OVEN', 'RANGE', 'STOVE', 'COOKTOP'],
        'MICROWAVE': ['MICRO', 'MICROWAVE'],
        'DISPOSAL': ['DISP', 'DISPOSAL', 'GARBAGE DISPOSAL'],
        'OTHER': []
    }
    
    # Find the best match
    for category, keywords in categories.items():
        if any(keyword in appliance for keyword in keywords):
            return category
    
    # If no match found, return the original
    return appliance

def match_address_confidence(address1, address2):
    """
    Calculate confidence score for address matching.
    
    Args:
        address1: First address string
        address2: Second address string
        
    Returns:
        Confidence score between 0-100
    """
    if pd.isna(address1) or pd.isna(address2) or address1 == '' or address2 == '':
        return 0
    
    # Standardize both addresses
    std_addr1 = standardize_address(address1)
    std_addr2 = standardize_address(address2)
    
    # If they're identical after standardization, return 100
    if std_addr1 == std_addr2:
        return 100
    
    # Calculate fuzzy matching score
    ratio = fuzz.token_sort_ratio(std_addr1, std_addr2)
    
    # For very short addresses, we need more confidence
    min_len = min(len(std_addr1), len(std_addr2))
    if min_len < 10:
        # Adjust score down for very short addresses
        ratio = ratio * 0.8
    
    return ratio

def extract_zip_code(address):
    """
    Extract zip code from address string.
    
    Args:
        address: Address string
        
    Returns:
        Zip code as string or empty string if not found
    """
    if pd.isna(address) or address == '':
        return ''
    
    # Look for 5-digit zip code pattern
    zip_match = re.search(r'(\d{5})(?:-\d{4})?', address)
    if zip_match:
        return zip_match.group(1)
    
    return '' 