"""
Functions for classifying job types and outcomes.
"""

import pandas as pd
import numpy as np
import re
import sys
import os

# Add the project root to the path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def classify_ftc_jobs(df):
    """
    Identify First Trip Complete (FTC) jobs.
    
    Args:
        df: DataFrame with job data
        
    Returns:
        DataFrame with 'Is_FTC' column added
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Create Is_FTC column
    result_df['Is_FTC'] = False
    
    # Check CompletedOnFirstTrip field
    if 'CompletedOnFirstTrip' in result_df.columns:
        result_df.loc[result_df['CompletedOnFirstTrip'] == True, 'Is_FTC'] = True
    
    # If that's not available, check HowManyVisits and Status
    if 'HowManyVisits' in result_df.columns and 'Status' in result_df.columns:
        result_df.loc[
            (result_df['HowManyVisits'] == 1) & 
            (result_df['Status'].str.contains('Completed|Archived|Closed', case=False, na=False)),
            'Is_FTC'
        ] = True
    
    # Check if job was canceled
    if 'JobCanceled' in result_df.columns:
        result_df.loc[result_df['JobCanceled'] == True, 'Is_FTC'] = False
    
    return result_df

def classify_diagnostic_only(df):
    """
    Identify Diagnostic Only jobs.
    
    Args:
        df: DataFrame with job data
        
    Returns:
        DataFrame with 'Is_DiagnosticOnly' column added
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Create Is_DiagnosticOnly column
    result_df['Is_DiagnosticOnly'] = False
    
    # Check parts and labor amounts
    if 'TotalMaterialInSale' in result_df.columns and 'SCallSold' in result_df.columns:
        # If there are no parts used but there is a service call charge
        result_df.loc[
            (result_df['TotalMaterialInSale'] == 0) & 
            (result_df['SCallSold'] > 0) & 
            (pd.notna(result_df['SCallSold'])),
            'Is_DiagnosticOnly'
        ] = True
    
    # Check WorkDescription for diagnostic indicators
    diagnostic_keywords = [
        'diagnostic', 'diagnose', 'diagnosis', 
        'quote', 'quoted', 'estimate',
        'not worth', 'too expensive', 'declined repair',
        'customer declined', 'cust declined'
    ]
    
    if 'WorkDescription' in result_df.columns:
        for keyword in diagnostic_keywords:
            result_df.loc[
                result_df['WorkDescription'].str.contains(keyword, case=False, na=False),
                'Is_DiagnosticOnly'
            ] = True
    
    return result_df

def classify_recalls(df):
    """
    Identify Recall jobs.
    
    Args:
        df: DataFrame with job data
        
    Returns:
        DataFrame with 'Is_Recall' column added
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Create Is_Recall column
    result_df['Is_Recall'] = False
    
    # Check WorkDescription for recall indicators
    recall_keywords = [
        'recall', 'safety notice', 'safety alert',
        'manufacturer notice', 'service bulletin',
        'factory recall', 'warranty recall'
    ]
    
    if 'WorkDescription' in result_df.columns:
        for keyword in recall_keywords:
            result_df.loc[
                result_df['WorkDescription'].str.contains(keyword, case=False, na=False),
                'Is_Recall'
            ] = True
    
    # Check Department field if it exists
    if 'Department' in result_df.columns:
        result_df.loc[
            result_df['Department'].str.contains('recall', case=False, na=False),
            'Is_Recall'
        ] = True
    
    return result_df

def classify_all_jobs(df):
    """
    Apply all job classifications.
    
    Args:
        df: DataFrame with job data
        
    Returns:
        DataFrame with all classification columns added
    """
    # Apply classifications sequentially
    result_df = classify_ftc_jobs(df)
    result_df = classify_diagnostic_only(result_df)
    result_df = classify_recalls(result_df)
    
    # Add a summary column for job type
    result_df['JobType'] = 'Standard Repair'
    result_df.loc[result_df['Is_DiagnosticOnly'], 'JobType'] = 'Diagnostic Only'
    result_df.loc[result_df['Is_Recall'], 'JobType'] = 'Recall'
    
    # Handle canceled jobs
    if 'JobCanceled' in result_df.columns:
        result_df.loc[result_df['JobCanceled'] == True, 'JobType'] = 'Canceled'
    
    return result_df 