"""
Functions to integrate data from different sources.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.mapping import TECH_MAPPING, TECH_REVERSE_MAPPING
from config.settings import GPS_MATCH_THRESHOLD, DEFAULT_TIME_WINDOW
from src.data_processing.cleaner import match_address_confidence, standardize_address

def map_tech_codes_to_devices(df, tech_col='TechCode'):
    """
    Map technician codes in ServiceDesk data to GPS device names.
    
    Args:
        df: DataFrame containing technician codes
        tech_col: Column name containing technician codes
        
    Returns:
        DataFrame with added 'Device' column
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Add Device column based on TechCode mapping
    result_df['Device'] = result_df[tech_col].apply(
        lambda x: TECH_REVERSE_MAPPING.get(x, 'UNKNOWN') if x in TECH_REVERSE_MAPPING else 'UNKNOWN'
    )
    
    return result_df

def match_jobs_to_gps_stops(job_df, gps_df, time_window_minutes=DEFAULT_TIME_WINDOW):
    """
    Match service jobs to GPS stops based on location and time.
    
    Args:
        job_df: DataFrame with job data (must have Device, Address, FirstAppmnt columns)
        gps_df: DataFrame with GPS stop data (must have Device, Address, Start Time, End Time columns)
        time_window_minutes: Minutes before/after scheduled time to look for GPS stops
        
    Returns:
        DataFrame with job data and matched GPS stop information
    """
    # Create a copy of the job DataFrame to store results
    result_df = job_df.copy()
    
    # Add columns for GPS match data
    result_df['GPS_StartTime'] = pd.NaT
    result_df['GPS_EndTime'] = pd.NaT
    result_df['GPS_Duration'] = np.nan
    result_df['GPS_Address'] = ''
    result_df['GPS_MatchConfidence'] = 0.0
    
    # Process each job
    for idx, job in result_df.iterrows():
        # Skip if no device assigned or no appointment time
        if job['Device'] == 'UNKNOWN' or pd.isna(job['FirstAppmnt']):
            continue
        
        # Get scheduled time and create time window
        scheduled_time = job['FirstAppmnt']
        time_window_start = scheduled_time - timedelta(minutes=time_window_minutes)
        time_window_end = scheduled_time + timedelta(minutes=time_window_minutes)
        
        # Filter GPS data for the matching device and within time window
        device_stops = gps_df[
            (gps_df['Device'] == job['Device']) & 
            (gps_df['Start Time'] >= time_window_start) & 
            (gps_df['Start Time'] <= time_window_end)
        ]
        
        # Skip if no stops found in time window
        if len(device_stops) == 0:
            continue
        
        # Find best address match among stops in time window
        best_match = None
        best_confidence = 0
        
        for _, stop in device_stops.iterrows():
            # Calculate address match confidence
            confidence = match_address_confidence(job['Address'], stop['Address'])
            
            # Update best match if this is better
            if confidence > best_confidence and confidence >= GPS_MATCH_THRESHOLD * 100:
                best_match = stop
                best_confidence = confidence
        
        # If a match was found, update the job record
        if best_match is not None:
            result_df.at[idx, 'GPS_StartTime'] = best_match['Start Time']
            result_df.at[idx, 'GPS_EndTime'] = best_match['End Time']
            result_df.at[idx, 'GPS_Duration'] = (best_match['End Time'] - best_match['Start Time']).total_seconds() / 60  # Minutes
            result_df.at[idx, 'GPS_Address'] = best_match['Address']
            result_df.at[idx, 'GPS_MatchConfidence'] = best_confidence
    
    return result_df

def merge_sales_with_jobs(jobs_df, sales_df):
    """
    Merge sales journal data with job data.
    
    Args:
        jobs_df: DataFrame with job data
        sales_df: DataFrame with sales data
        
    Returns:
        DataFrame with combined data
    """
    print(f"Beginning merge with {len(jobs_df)} job records and {len(sales_df)} sales records")
    
    # Create copies to avoid modifying the originals
    jobs_df = jobs_df.copy()
    sales_df = sales_df.copy()
    
    # Ensure we have the required columns to join
    jobs_cols = jobs_df.columns
    sales_cols = sales_df.columns
    
    # First, check for technician columns and create a common joining field
    if 'TechCode' in jobs_cols and 'Technician' in sales_cols and 'TechCode' not in sales_cols:
        # Copy Technician to TechCode in sales_df for joining
        sales_df['TechCode'] = sales_df['Technician'].astype(str).str.strip().str.upper()
    
    if 'Technician' in jobs_cols and 'TechCode' in sales_cols and 'Technician' not in sales_cols:
        # Copy TechCode to Technician in sales_df for joining
        sales_df['Technician'] = sales_df['TechCode'].astype(str).str.strip().str.upper()
    
    # CRITICAL: Deduplicate sales data to prevent double counting revenue
    if 'InvoiceNumber' in sales_cols and 'TechCode' in sales_cols:
        # Count before deduplication
        print(f"Before sales deduplication: {len(sales_df)} sales records")
        
        # Keep only one record per invoice and technician
        sales_df = sales_df.drop_duplicates(subset=['TechCode', 'InvoiceNumber'], keep='first')
        
        # Count after deduplication
        print(f"After sales deduplication: {len(sales_df)} sales records")
    
    # Now check for job number / invoice number joining fields
    if 'JobNumber' in jobs_cols and 'InvoiceNumber' in sales_cols:
        # We can join on JobNumber = InvoiceNumber
        
        # Convert both to strings for joining
        jobs_df['JobNumber'] = jobs_df['JobNumber'].astype(str).str.strip()
        sales_df['InvoiceNumber'] = sales_df['InvoiceNumber'].astype(str).str.strip()
        
        # Print a sample of the join keys for debugging
        print("Sample job numbers (first 5):", jobs_df['JobNumber'].head().tolist())
        print("Sample invoice numbers (first 5):", sales_df['InvoiceNumber'].head().tolist())
        
        # Get only the necessary columns from sales data to avoid duplication
        # We only want the revenue columns, not everything
        sales_cols_for_merge = ['TechCode', 'InvoiceNumber']
        for col in ['LaborSold', 'PartsSold', 'SCallSold', 'MerchandiseSold', 'TotalSale']:
            if col in sales_cols:
                sales_cols_for_merge.append(col)
        
        # Merge only the needed columns
        sales_df_slim = sales_df[sales_cols_for_merge]
        
        # Prepare jobs DataFrame by removing any columns that will be overwritten by sales data
        # This is CRITICAL to prevent double-counting
        for col in ['LaborSold', 'PartsSold', 'SCallSold', 'MerchandiseSold', 'TotalSale']:
            if col in jobs_df.columns:
                print(f"Removing {col} from jobs data to prevent double-counting")
                jobs_df = jobs_df.drop(columns=[col])
        
        # If jobs data has Type6 revenue columns but we'll be getting Sales Journal data,
        # zero out the Type6 columns to prevent double-counting
        if any(col in sales_cols_for_merge[2:] for col in sales_cols_for_merge):
            for col in ['TotalLaborInSale', 'TotalMaterialInSale', 'TotalMateriaInSale']:
                if col in jobs_df.columns:
                    print(f"Zeroing out {col} in jobs data to prevent double-counting with Sales Journal data")
                    jobs_df[col] = 0
        
        # Try exact match first
        merged_df = pd.merge(
            jobs_df,
            sales_df_slim,
            left_on=['TechCode', 'JobNumber'],
            right_on=['TechCode', 'InvoiceNumber'],
            how='left',
            suffixes=('', '_sales')
        )
        
        # Count matches for debugging
        match_count = merged_df['InvoiceNumber'].notna().sum()
        print(f"Matched {match_count} of {len(merged_df)} jobs to sales records")
        
        # Fix the Total Material column name typo if needed
        if 'TotalMateriaInSale' in merged_df.columns and 'TotalMaterialInSale' not in merged_df.columns:
            merged_df['TotalMaterialInSale'] = merged_df['TotalMateriaInSale']
        
        return merged_df
    
    # Alternative: if we can't match on job/invoice numbers, at least get the technician data
    if 'TechCode' in jobs_cols and 'TechCode' in sales_cols:
        print("Warning: Couldn't match on job numbers, using technician-level merge instead")
        
        # Prepare jobs DataFrame by removing any columns that will be overwritten by sales data
        # This is CRITICAL to prevent double-counting
        for col in ['LaborSold', 'PartsSold', 'SCallSold', 'MerchandiseSold', 'TotalSale']:
            if col in jobs_df.columns:
                print(f"Removing {col} from jobs data to prevent double-counting")
                jobs_df = jobs_df.drop(columns=[col])
        
        # Group sales by technician and sum key metrics
        sales_summary = sales_df.groupby('TechCode').agg({
            col: 'sum' for col in ['LaborSold', 'PartsSold', 'SCallSold', 'MerchandiseSold', 'TotalSale'] 
            if col in sales_cols
        }).reset_index()
        
        # Merge the sales summary with jobs based only on technician
        merged_df = pd.merge(
            jobs_df,
            sales_summary,
            on='TechCode',
            how='left'
        )
        
        return merged_df
    
    # If we couldn't merge, return the original jobs dataframe
    print("Warning: Could not determine how to merge sales with jobs. Returning job data only.")
    return jobs_df

def add_alert_data_to_techs(tech_df, alert_df):
    """
    Add alert summary data to technician records.
    
    Args:
        tech_df: DataFrame with technician data (must have Device column)
        alert_df: DataFrame with alert data (must have Device, Time, Alert columns)
        
    Returns:
        DataFrame with technician data and alert counts
    """
    # Create a copy to avoid modifying the original
    result_df = tech_df.copy()
    
    # Create columns for alert counts if they don't exist
    alert_types = alert_df['Alert'].unique()
    for alert_type in alert_types:
        col_name = f'Alert_{alert_type.replace(" ", "_")}'
        if col_name not in result_df.columns:
            result_df[col_name] = 0
    
    # Add total alerts column
    if 'Total_Alerts' not in result_df.columns:
        result_df['Total_Alerts'] = 0
    
    # Group alerts by device and type
    alert_counts = alert_df.groupby(['Device', 'Alert']).size().reset_index(name='count')
    
    # Update technician records with alert counts
    for idx, tech in result_df.iterrows():
        # Get device alerts
        device_alerts = alert_counts[alert_counts['Device'] == tech['Device']]
        
        # Update alert counts
        for _, alert in device_alerts.iterrows():
            col_name = f'Alert_{alert["Alert"].replace(" ", "_")}'
            result_df.at[idx, col_name] = alert['count']
        
        # Update total alerts
        result_df.at[idx, 'Total_Alerts'] = device_alerts['count'].sum() if len(device_alerts) > 0 else 0
    
    return result_df 