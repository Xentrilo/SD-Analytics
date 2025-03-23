"""
Data preparation utility for the Service Analytics Dashboard.

This script helps prepare and clean data files before they're used in the dashboard.
It can convert files from different formats, correct common issues, and verify data quality.
"""

import os
import sys
import pandas as pd
import argparse
from datetime import datetime
import re
import csv

# Add the project directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the data loading functions
from src.data_processing.importers import (
    load_type6_report, load_sales_journal, load_gps_tracking
)

def convert_salesjournal_dat_to_csv(dat_file, output_file=None):
    """
    Convert a Sales Journal DAT file to CSV format.
    
    Args:
        dat_file: Path to the .dat file
        output_file: Path to save the CSV (if None, replaces extension with .csv)
    
    Returns:
        Path to the created CSV file
    """
    if output_file is None:
        output_file = os.path.splitext(dat_file)[0] + '.csv'
    
    print(f"Converting {dat_file} to {output_file}...")
    
    try:
        # Read the DAT file
        with open(dat_file, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        # Extract column names from the first line
        first_line = lines[0].strip()
        if ',' in first_line:
            # Already comma separated
            header_line = first_line
            columns = [col.strip() for col in header_line.split(',')]
            start_idx = 1
        else:
            # Space or tab delimited
            parts = re.split(r'\t|\s{2,}', first_line)
            columns = [p.strip() for p in parts if p.strip()]
            start_idx = 1
        
        # Process data lines
        data = []
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            
            # Handle different formats
            if line.startswith('#') and '"' in line:
                # This is already CSV-like format with dates in #date# format
                # Use CSV parser to handle quoted fields correctly
                row_values = next(csv.reader([line]))
                if len(row_values) == 1 and ',' in row_values[0]:
                    # Sometimes CSV reader doesn't split it correctly
                    row_values = row_values[0].split(',')
                
                row = {}
                for j, val in enumerate(row_values):
                    if j < len(columns):
                        # Clean up values
                        val = val.strip()
                        if val.startswith('"') and val.endswith('"'):
                            val = val[1:-1]
                        if val.startswith('#') and val.endswith('#'):
                            val = val[1:-1]
                        row[columns[j]] = val
                    else:
                        # Extra values
                        row['Extra_' + str(j-len(columns)+1)] = val
                
                data.append(row)
            else:
                # Try space/tab delimited
                parts = re.split(r'\t|\s{2,}', line)
                parts = [p.strip() for p in parts if p.strip()]
                
                row = {}
                for j, val in enumerate(parts):
                    if j < len(columns):
                        row[columns[j]] = val
                    else:
                        # Extra values get merged into the last column
                        row[columns[-1]] = row.get(columns[-1], '') + ' ' + val
                
                data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Successfully converted file with {len(df)} records")
        
        # Print sample data
        print("\nSample data (first 2 rows):")
        print(df.head(2))
        print("\nColumns in the output file:")
        print(", ".join(df.columns))
        
        return output_file
    
    except Exception as e:
        print(f"Error converting file: {e}")
        return None

def fix_date_formats(file_path):
    """
    Fix common date format issues in CSV files.
    
    Args:
        file_path: Path to the CSV file to fix
    """
    try:
        df = pd.read_csv(file_path)
        modified = False
        
        # Identify and fix date columns
        for col in df.columns:
            # Check if column name suggests it's a date
            if any(date_term in col.lower() for date_term in ['date', 'time', 'day']):
                # Sample the first few non-null values
                sample_values = df[col].dropna().head(5).astype(str)
                
                # Check if values look like dates
                date_patterns = [
                    r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
                    r'\d{4}-\d{1,2}-\d{1,2}',     # YYYY-MM-DD
                    r'\d{1,2}-\d{1,2}-\d{4}',     # MM-DD-YYYY or DD-MM-YYYY
                ]
                
                is_date = any(sample_values.str.contains(pattern).any() for pattern in date_patterns)
                
                if is_date and df[col].dtype != 'datetime64[ns]':
                    print(f"Converting column '{col}' to datetime")
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    modified = True
        
        if modified:
            print(f"Saving fixed date formats to {file_path}")
            df.to_csv(file_path, index=False)
            print("Date formats fixed successfully")
        else:
            print("No date format issues found")
    
    except Exception as e:
        print(f"Error fixing date formats: {e}")

def verify_data_quality(file_path, file_type=None):
    """
    Verify the quality of a data file and report issues.
    
    Args:
        file_path: Path to the file to verify
        file_type: Type of file ('type6', 'sales', or None for auto-detect)
    """
    try:
        # Auto-detect file type if not specified
        if file_type is None:
            if 'type6' in file_path.lower():
                file_type = 'type6'
            elif 'slsjrnl' in file_path.lower() or 'journal' in file_path.lower():
                file_type = 'sales'
            elif any(term in file_path.lower() for term in ['day_start', 'drives', 'engine', 'idle', 'alert']):
                file_type = 'gps'
            else:
                print("Could not auto-detect file type. Please specify.")
                return
        
        print(f"Verifying {file_type} file: {file_path}...")
        
        # Load the file using the appropriate function
        if file_type == 'type6':
            df = load_type6_report(file_path)
        elif file_type == 'sales':
            df = load_sales_journal(file_path)
        elif file_type == 'gps':
            # Determine GPS file subtype
            if 'day_start' in file_path:
                subtype = 'day_start_end'
            elif 'drives' in file_path:
                subtype = 'drives_stops'
            elif 'engine' in file_path:
                subtype = 'day_engine'
            elif 'idle' in file_path:
                subtype = 'idle_time'
            elif 'alert' in file_path:
                subtype = 'alert'
            else:
                subtype = 'unknown'
            
            df = load_gps_tracking(file_path, subtype)
        
        # Basic data quality checks
        print(f"File has {len(df)} rows and {len(df.columns)} columns")
        
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            print("\nMissing values by column:")
            for col, count in missing_values[missing_values > 0].items():
                print(f"  {col}: {count} missing values ({count/len(df):.1%})")
        
        # Check for duplicate rows
        dupes = df.duplicated().sum()
        if dupes > 0:
            print(f"\nWarning: {dupes} duplicate rows found ({dupes/len(df):.1%} of data)")
        
        print("\nColumn data types:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
        
        print("\nData quality verification complete")
    
    except Exception as e:
        print(f"Error verifying data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Service Analytics Data Preparation Tool')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert file format')
    convert_parser.add_argument('input_file', help='Input file to convert')
    convert_parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    # Fix dates command
    fix_parser = subparsers.add_parser('fix_dates', help='Fix date formats in CSV file')
    fix_parser.add_argument('file', help='CSV file to fix')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify data quality')
    verify_parser.add_argument('file', help='File to verify')
    verify_parser.add_argument('--type', '-t', choices=['type6', 'sales', 'gps'], 
                              help='File type (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        if args.input_file.endswith('.dat') or args.input_file.endswith('.str'):
            convert_salesjournal_dat_to_csv(args.input_file, args.output)
        else:
            print(f"Unsupported file format: {args.input_file}")
    
    elif args.command == 'fix_dates':
        fix_date_formats(args.file)
    
    elif args.command == 'verify':
        verify_data_quality(args.file, args.type)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 