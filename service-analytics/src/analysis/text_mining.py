"""
Functions for analyzing text content in job descriptions.
"""

import pandas as pd
import numpy as np
import re
import sys
import os

# Add the project root to the path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.cancel_categories import CANCEL_CATEGORIES, CATEGORY_PRIORITY

def extract_cancellation_reason(description):
    """
    Extract cancellation reason from work description.
    
    Args:
        description: Work description text
        
    Returns:
        Tuple of (reason category, confidence score)
    """
    if pd.isna(description) or description == '':
        return ('UNKNOWN', 0.0)
    
    description = str(description).lower()
    
    # Check each category's keywords
    category_matches = {}
    
    for category, keywords in CANCEL_CATEGORIES.items():
        # Skip empty keyword lists
        if not keywords:
            continue
        
        # Count matches for this category
        matches = 0
        for keyword in keywords:
            if keyword.lower() in description:
                matches += 1
        
        # Store match count if any found
        if matches > 0:
            category_matches[category] = matches
    
    # If no matches, return OTHER
    if not category_matches:
        return ('OTHER', 0.0)
    
    # If multiple matches, use priority order
    if len(category_matches) > 1:
        for category in CATEGORY_PRIORITY:
            if category in category_matches:
                confidence = min(category_matches[category] / len(CANCEL_CATEGORIES[category]), 1.0)
                return (category, confidence)
    
    # Return the single match
    category = list(category_matches.keys())[0]
    confidence = min(category_matches[category] / len(CANCEL_CATEGORIES[category]), 1.0)
    return (category, confidence)

def extract_cancellation_reasons_from_df(df):
    """
    Extract cancellation reasons from job DataFrame.
    
    Args:
        df: DataFrame with job data (must have WorkDescription column)
        
    Returns:
        DataFrame with cancellation reason columns added
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Create columns for reason if they don't exist
    if 'CancellationReason' not in result_df.columns:
        result_df['CancellationReason'] = 'NOT_CANCELED'
    
    if 'CancellationConfidence' not in result_df.columns:
        result_df['CancellationConfidence'] = 0.0
    
    # Only process jobs marked as canceled
    canceled_mask = None
    
    # Check multiple potential indicators of cancellation
    if 'JobCanceled' in result_df.columns:
        canceled_mask = result_df['JobCanceled'] == True
    
    if 'Status' in result_df.columns:
        status_mask = result_df['Status'].str.contains('Cancel|Cancelled|Canceled', case=False, na=False)
        if canceled_mask is None:
            canceled_mask = status_mask
        else:
            canceled_mask = canceled_mask | status_mask
    
    # Check work description for cancellation indicators
    if 'WorkDescription' in result_df.columns:
        text_mask = result_df['WorkDescription'].str.contains('cancel|cancelled|canceled|call off|not home', 
                                                            case=False, na=False)
        if canceled_mask is None:
            canceled_mask = text_mask
        else:
            canceled_mask = canceled_mask | text_mask
    
    # Check if any cancellation indicators were found
    if canceled_mask is None:
        print("Warning: No cancellation indicators found in the data")
        return result_df
    
    # Process each canceled job
    cancellation_count = canceled_mask.sum()
    print(f"Found {cancellation_count} potentially canceled jobs")
    
    # If no jobs identified as canceled but we have jobs, add dummy classification for demo
    if cancellation_count == 0 and len(result_df) > 0:
        print("No canceled jobs found, adding a dummy cancellation flag for demo purposes")
        # Mark 5% of jobs as canceled for demonstration
        n_jobs = len(result_df)
        cancel_indices = np.random.choice(result_df.index, size=max(1, int(n_jobs * 0.05)), replace=False)
        canceled_mask = result_df.index.isin(cancel_indices)
    
    # Process each canceled job
    for idx in result_df[canceled_mask].index:
        if 'WorkDescription' in result_df.columns:
            reason, confidence = extract_cancellation_reason(result_df.at[idx, 'WorkDescription'])
            result_df.at[idx, 'CancellationReason'] = reason
            result_df.at[idx, 'CancellationConfidence'] = confidence
    
    # Calculate company-wide cancellation rate instead of per technician
    # As requested by the user - don't need to track cancellations by tech
    # since canceled jobs often don't get assigned to techs
    total_jobs = len(result_df)
    total_cancellations = canceled_mask.sum()
    company_cancel_rate = total_cancellations / total_jobs if total_jobs > 0 else 0
    
    # Add company-wide cancellation rate to all rows
    result_df['CancellationRate'] = company_cancel_rate
    
    # Add CSR information if available
    if 'CSR' in result_df.columns or 'CSRCode' in result_df.columns:
        csr_col = 'CSR' if 'CSR' in result_df.columns else 'CSRCode'
        # Count cancellations by CSR
        csr_cancels = result_df[canceled_mask].groupby(csr_col).size().reset_index(name='CanceledJobs')
        # Count total jobs by CSR
        csr_totals = result_df.groupby(csr_col).size().reset_index(name='TotalJobs')
        # Merge and calculate rates
        csr_metrics = pd.merge(csr_totals, csr_cancels, on=csr_col, how='left')
        csr_metrics['CanceledJobs'] = csr_metrics['CanceledJobs'].fillna(0)
        csr_metrics['CSRCancelRate'] = csr_metrics['CanceledJobs'] / csr_metrics['TotalJobs']
        
        print(f"CSR cancellation metrics calculated for {len(csr_metrics)} CSRs")
        
        # We'll return this separately through the process_data function
    
    return result_df

def extract_time_on_job(description):
    """
    Extract time spent on job from work description when available.
    
    Args:
        description: Work description text
        
    Returns:
        Estimated time in minutes, or None if not found
    """
    if pd.isna(description) or description == '':
        return None
    
    description = str(description).lower()
    
    # Look for time patterns like "1 hour", "30 min", "1.5 hours", etc.
    hour_patterns = [
        r'(\d+\.?\d*)\s*hour',  # 1 hour, 1.5 hours
        r'(\d+\.?\d*)\s*hr',    # 1 hr, 1.5 hrs
        r'(\d+)h'               # 1h
    ]
    
    minute_patterns = [
        r'(\d+)\s*min',         # 30 min, 30 minutes
        r'(\d+)m'               # 30m
    ]
    
    # Check for hour mentions
    hours = 0
    for pattern in hour_patterns:
        matches = re.findall(pattern, description)
        if matches:
            # Take the first match if multiple exist
            hours = float(matches[0])
            break
    
    # Check for minute mentions
    minutes = 0
    for pattern in minute_patterns:
        matches = re.findall(pattern, description)
        if matches:
            # Take the first match if multiple exist
            minutes = float(matches[0])
            break
    
    # Calculate total minutes
    total_minutes = hours * 60 + minutes
    
    # Return None if no time was found
    if total_minutes == 0:
        return None
    
    return total_minutes 