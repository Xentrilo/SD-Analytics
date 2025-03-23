"""
Data import functions for various file formats.
"""

import os
import pandas as pd
from datetime import datetime

def load_type6_report(filepath):
    """
    Load and preprocess Type6report.csv
    
    Args:
        filepath: Path to the Type6report CSV file
        
    Returns:
        DataFrame with processed Type6 data
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                print(f"Attempting to load with {encoding} encoding...")
                df = pd.read_csv(filepath, encoding=encoding, low_memory=False, on_bad_lines='skip')
                print(f"Successfully loaded with {encoding} encoding")
                break
            except Exception as e:
                print(f"Failed with {encoding} encoding: {e}")
                continue
        
        if df is None:
            raise Exception("Failed to load file with any encoding")
        
        # Convert date columns to datetime
        date_columns = ['OriginDate', 'FirstAppmnt', 'CmpltnDate']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert boolean columns
        bool_columns = ['ShopJob?', 'CurrentAppmnt?', 'Triaged?', 'CompletedOnFirstTrip', 'JobCanceled']
        for col in bool_columns:
            if col in df.columns:
                # Handle various representations of boolean values
                df[col] = df[col].map({'True': True, 'False': False, 'Yes': True, 'No': False, 
                                      'true': True, 'false': False, 'yes': True, 'no': False})
        
        # Clean up text fields
        text_columns = ['NmLst', 'NmFrst', 'Address', 'CityStateZip', 'WorkDescription']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        print(f"Successfully loaded Type6 report with {len(df)} records")
        return df
    
    except Exception as e:
        print(f"Error loading Type6 report: {e}")
        return pd.DataFrame()

def load_sales_journal(filepath):
    """
    Load and preprocess Sales Journal data
    
    Args:
        filepath: Path to the Sales Journal CSV file
        
    Returns:
        DataFrame with processed Sales Journal data
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                print(f"Attempting to load with {encoding} encoding...")
                df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                print(f"Successfully loaded with {encoding} encoding")
                break
            except Exception as e:
                print(f"Failed with {encoding} encoding: {e}")
                continue
        
        if df is None:
            raise Exception("Failed to load file with any encoding")
            
        # Convert date columns to datetime
        if 'DateRecorded' in df.columns:
            df['DateRecorded'] = pd.to_datetime(df['DateRecorded'], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['MerchandiseSold', 'PartsSold', 'SCallSold', 'LaborSold', 
                           'ImpliedTax', 'TotalSale']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean up technician codes and invoice numbers
        if 'Technician' in df.columns:
            df['Technician'] = df['Technician'].astype(str).str.strip().str.upper()
        
        if 'InvoiceNumber' in df.columns:
            df['InvoiceNumber'] = df['InvoiceNumber'].astype(str).str.strip()
        
        print(f"Successfully loaded Sales Journal with {len(df)} records")
        return df
    
    except Exception as e:
        print(f"Error loading Sales Journal: {e}")
        return pd.DataFrame()

def load_gps_tracking(filepath, file_type):
    """
    Load and preprocess GPS tracking data
    
    Args:
        filepath: Path to the GPS CSV file
        file_type: Type of GPS data ('drives_stops', 'day_engine', 'idle_time', 'alert')
        
    Returns:
        DataFrame with processed GPS data
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                print(f"Attempting to load with {encoding} encoding...")
                df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                print(f"Successfully loaded with {encoding} encoding")
                break
            except Exception as e:
                print(f"Failed with {encoding} encoding: {e}")
                continue
        
        if df is None:
            raise Exception("Failed to load file with any encoding")
        
        # Process based on file type
        if file_type == 'day_start_end':
            # Process day start/end breakdown
            time_columns = ['Start Time', 'End Time']
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Convert time columns to datetime
            for col in time_columns:
                if col in df.columns:
                    # Combine date and time
                    df[col] = pd.to_datetime(
                        df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df[col],
                        errors='coerce'
                    )
            
        elif file_type == 'drives_stops':
            # Process drives and stops data
            time_columns = ['Start Time', 'End Time']
            
            # Convert time columns to datetime
            for col in time_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['Length (mi)', 'Top speed (mph)', 'Avg Speed (mph)', 'Odometer (mi)']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
        elif file_type == 'day_engine':
            # Process engine hours data
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Convert duration columns to seconds
            if 'Daily Hours Accumulated' in df.columns:
                df['Daily Hours Accumulated'] = df['Daily Hours Accumulated'].apply(
                    lambda x: convert_duration_to_seconds(x)
                )
            
            if 'Lifetime Hours' in df.columns:
                df['Lifetime Hours'] = df['Lifetime Hours'].apply(
                    lambda x: convert_duration_to_seconds(x)
                )
            
        elif file_type == 'idle_time':
            # Process idle time data
            time_columns = ['Start Time', 'End Time']
            
            # Convert time columns to datetime
            for col in time_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert duration column to seconds
            if 'Duration' in df.columns:
                df['Duration Seconds'] = df['Duration'].apply(
                    lambda x: convert_duration_to_seconds(x)
                )
                
        elif file_type == 'alert':
            # Process alert data
            if 'Date & Time' in df.columns:
                df['Date & Time'] = pd.to_datetime(df['Date & Time'], errors='coerce')
            
            # Convert speed columns to numeric
            speed_columns = ['Posted Speed', 'Speed']
            for col in speed_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean up Device column for all GPS data types
        if 'Device' in df.columns:
            df['Device'] = df['Device'].astype(str).str.strip()
        
        print(f"Successfully loaded GPS {file_type} data with {len(df)} records")
        return df
    
    except Exception as e:
        print(f"Error loading GPS {file_type} data: {e}")
        return pd.DataFrame()

def convert_duration_to_seconds(duration_str):
    """
    Convert a duration string like '2:30:15' to seconds
    
    Args:
        duration_str: Duration string in format 'HH:MM:SS' or 'MM:SS'
        
    Returns:
        Duration in seconds
    """
    try:
        if not isinstance(duration_str, str):
            return 0
            
        parts = duration_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return 0
    except Exception:
        return 0 