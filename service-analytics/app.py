"""
Main Streamlit application for Service Analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import traceback
from datetime import datetime, timedelta
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Service Analytics Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the project directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    # Import local modules
    from src.data_processing.importers import (
        load_type6_report, load_sales_journal, load_gps_tracking
    )
    from src.data_processing.integrator import (
        map_tech_codes_to_devices, match_jobs_to_gps_stops, merge_sales_with_jobs, add_alert_data_to_techs
    )
    from src.analysis.classifier import classify_all_jobs
    from src.analysis.text_mining import extract_cancellation_reasons_from_df, extract_time_on_job
    from src.analysis.metrics import (
        calculate_tech_revenue_metrics, calculate_performance_metrics, 
        calculate_cancellation_metrics, calculate_alert_scores, analyze_idle_time
    )

    # Import visualization modules
    import src.visualization.dashboard as dashboard_viz
    
    # Test imports from config to make sure they work
    from config.cancel_categories import CANCEL_CATEGORIES, CATEGORY_PRIORITY
    from config.settings import SERVICE_CALL_PRICES
    from config.alert_weights import ALERT_WEIGHTS, DRIVING_SCORE_THRESHOLDS
    
    imports_success = True
except Exception as e:
    st.error(f"Error importing modules: {str(e)}")
    st.code(traceback.format_exc())
    imports_success = False

# Function to create a mock dataset for testing if real data is not available
def create_mock_data():
    """Create mock data for testing the dashboard."""
    
    # Create mock technician data
    tech_data = pd.DataFrame({
        'TechCode': ['TECH1', 'TECH2', 'TECH3', 'TECH4', 'TECH5'],
        'TechName': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
        'TotalJobs': [120, 105, 98, 115, 87],
        'CompletedJobs': [110, 95, 88, 105, 77],
        'FTC_Jobs': [85, 70, 60, 88, 50],
        'DiagnosticOnly_Jobs': [20, 15, 18, 12, 22],
        'CanceledJobs': [10, 10, 10, 10, 10],
        'TotalLabor': [12500, 11200, 9800, 13200, 8500],
        'TotalParts': [8200, 7500, 6200, 8900, 5500],
        'TotalServiceCalls': [5200, 4800, 4500, 5500, 4000],
        'TotalRevenue': [25900, 23500, 20500, 27600, 18000],
        'AvgRevenuePerJob': [215.83, 223.81, 209.18, 240.00, 206.90],
        'FTC_Rate': [0.71, 0.67, 0.61, 0.77, 0.57],
        'DiagnosticOnly_Rate': [0.17, 0.14, 0.18, 0.10, 0.25],
        'CancellationRate': [0.08, 0.10, 0.10, 0.09, 0.11],
    })
    
    # Calculate additional metrics
    tech_data['AvgLaborPerJob'] = tech_data['TotalLabor'] / tech_data['CompletedJobs']
    tech_data['AvgPartsPerJob'] = tech_data['TotalParts'] / tech_data['CompletedJobs']
    tech_data['PartsToLaborRatio'] = tech_data['TotalParts'] / tech_data['TotalLabor']
    
    # Create mock cancellation data
    cancel_data = pd.DataFrame({
        'CancellationReason': ['CUSTOMER_INITIATED', 'NO_SHOW', 'SCHEDULING_CONFLICT', 'PRICE_TOO_HIGH', 'OTHER'],
        'Count': [35, 20, 15, 10, 5],
        'Percentage': [41.2, 23.5, 17.6, 11.8, 5.9]
    })
    
    # Create mock driving data
    driving_data = pd.DataFrame({
        'TechCode': ['TECH1', 'TECH2', 'TECH3', 'TECH4', 'TECH5'],
        'DriverName': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
        'DeviceId': ['DEV001', 'DEV002', 'DEV003', 'DEV004', 'DEV005'],
        'TotalAlerts': [12, 5, 18, 3, 22],
        'Speeding': [5, 2, 8, 1, 10],
        'HardBraking': [4, 1, 6, 1, 8],
        'RapidAccel': [3, 2, 4, 1, 4],
        'DrivingScore': [85, 92, 78, 95, 72],
        'DrivingCategory': ['GOOD', 'EXCELLENT', 'AVERAGE', 'EXCELLENT', 'BELOW_AVERAGE']
    })
    
    return tech_data, cancel_data, driving_data

def load_data():
    """Load and process all data sources."""
    
    # Create data load status
    data_load_state = st.sidebar.text('Loading data...')
    
    # Define data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        st.sidebar.warning(f"Data directory not found: {data_dir}")
        st.sidebar.error("Unable to find data directory. Please check your setup.")
        type6_data, sales_data, gps_data = None, None, {}
        return type6_data, sales_data, gps_data
    
    # Load Type6 report data
    type6_path = os.path.join(data_dir, 'Type6report2025.csv')
    if os.path.exists(type6_path):
        type6_data = load_type6_report(type6_path)
        
        # Clean TechCode column - convert everything to strings
        if 'TechCode' in type6_data.columns:
            type6_data['TechCode'] = type6_data['TechCode'].astype(str)
            # Replace 'nan' strings with empty strings
            type6_data['TechCode'] = type6_data['TechCode'].replace('nan', '')
    else:
        st.sidebar.warning(f"File not found: {type6_path}")
        st.sidebar.error("Type6 report file missing. Please add file to data directory.")
        type6_data = pd.DataFrame()
    
    # Load Sales Journal data
    sales_path = os.path.join(data_dir, 'SlsJrnl.csv')
    if os.path.exists(sales_path):
        sales_data = load_sales_journal(sales_path)
        
        # Clean Technician column if it exists
        if 'Technician' in sales_data.columns:
            sales_data['Technician'] = sales_data['Technician'].astype(str)
            sales_data['Technician'] = sales_data['Technician'].replace('nan', '')
    else:
        st.sidebar.warning(f"File not found: {sales_path}")
        st.sidebar.error("Sales Journal file missing. Please add file to data directory.")
        sales_data = pd.DataFrame()
    
    # Load GPS data
    gps_files = {
        'day_start_end': 'day_start_end_breakdown_01_01_2025_12_00am_PST-03_14_2025_12_00am_PDT.csv',
        'drives_stops': 'drives_and_stops_01_01_2025_12_00am_PST-03_17_2025_12_00am_PDT.csv',
        'day_engine': 'day_engine_hours_01_01_2025_12_00am_PST-03_14_2025_12_00am_PDT.csv',
        'idle_time': 'idle_time_01_01_2025_12_00am_PST-03_18_2025_12_00am_PDT.csv',
        'alert': 'alert_summary_01_01_2025_12_00am_PST-03_14_2025_12_00am_PDT.csv'
    }
    
    gps_data = {}
    for file_type, filename in gps_files.items():
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            gps_data[file_type] = load_gps_tracking(file_path, file_type)
        else:
            st.sidebar.warning(f"GPS file not found: {filename}")
            gps_data[file_type] = pd.DataFrame()
    
    data_load_state.text('Data loaded!')
    
    return type6_data, sales_data, gps_data

def process_data(type6_data, sales_data, gps_data, start_date, end_date, selected_techs):
    """Process and integrate data sources."""
    
    process_state = st.sidebar.text('Processing data...')
    
    # DISABLED MOCK DATA: Force the app to use only real data
    # If no real data, show error instead of using mock data
    if (type6_data is None or type6_data.empty) and (sales_data is None or sales_data.empty):
        st.sidebar.error("Required data files are missing or empty. Please check your data directory.")
        process_state.text('Error: Missing required data!')
        return None, None, None
    
    # Skip if no data loaded
    if type6_data.empty or sales_data.empty:
        process_state.text('Error: Missing required data!')
        return None, None, None
    
    # Filter data by date range
    if 'OriginDate' in type6_data.columns:
        type6_filtered = type6_data[
            (type6_data['OriginDate'] >= pd.Timestamp(start_date)) &
            (type6_data['OriginDate'] <= pd.Timestamp(end_date))
        ]
    else:
        type6_filtered = type6_data
    
    if 'DateRecorded' in sales_data.columns:
        sales_filtered = sales_data[
            (sales_data['DateRecorded'] >= pd.Timestamp(start_date)) &
            (sales_data['DateRecorded'] <= pd.Timestamp(end_date))
        ]
    else:
        sales_filtered = sales_data
    
    # Map technician codes to GPS device names if needed
    type6_with_devices = map_tech_codes_to_devices(type6_filtered)
    
    # Filter by selected technicians
    if selected_techs:
        type6_with_devices = type6_with_devices[type6_with_devices['TechCode'].isin(selected_techs)]
    
    # Classify jobs
    classified_jobs = classify_all_jobs(type6_with_devices)
    
    # Extract cancellation reasons
    jobs_with_cancellations = extract_cancellation_reasons_from_df(classified_jobs)
    
    # Extract time on job when available
    if 'WorkDescription' in jobs_with_cancellations.columns:
        jobs_with_cancellations['TimeOnJob'] = jobs_with_cancellations['WorkDescription'].apply(extract_time_on_job)
    
    # Merge with sales data - Add technician mapping if needed
    if 'Technician' in sales_filtered.columns and not 'TechCode' in sales_filtered.columns:
        sales_filtered['TechCode'] = sales_filtered['Technician']
    
    if not sales_filtered.empty:
        # Make sure job/invoice numbers are strings for joining
        if 'JobNumber' in jobs_with_cancellations.columns and 'InvoiceNumber' in sales_filtered.columns:
            jobs_with_cancellations['JobNumber'] = jobs_with_cancellations['JobNumber'].astype(str).str.strip()
            sales_filtered['InvoiceNumber'] = sales_filtered['InvoiceNumber'].astype(str).str.strip()
        
        integrated_data = merge_sales_with_jobs(jobs_with_cancellations, sales_filtered)
    else:
        integrated_data = jobs_with_cancellations
    
    # Match with GPS data if available
    if 'drives_stops' in gps_data and not gps_data['drives_stops'].empty:
        stops_data = gps_data['drives_stops'][gps_data['drives_stops']['Status'] == 'Stopped']
        integrated_data = match_jobs_to_gps_stops(integrated_data, stops_data)
    
    # Calculate metrics - make sure TechCode exists
    if 'Technician' in integrated_data.columns and 'TechCode' not in integrated_data.columns:
        integrated_data['TechCode'] = integrated_data['Technician']
    
    # Calculate metrics
    tech_metrics = calculate_tech_revenue_metrics(integrated_data)
    
    # Make sure TechCode exists in all metric dataframes
    if 'Technician' in integrated_data.columns and 'TechCode' not in integrated_data.columns:
        integrated_data['TechCode'] = integrated_data['Technician']
    
    # Calculate performance metrics
    performance_metrics = calculate_performance_metrics(integrated_data)
    
    # Calculate cancellation metrics
    cancellation_metrics = calculate_cancellation_metrics(integrated_data)
    
    # Ensure tech_metrics has TechCode for merging
    if 'TechCode' not in tech_metrics.columns and 'Technician' in tech_metrics.columns:
        tech_metrics['TechCode'] = tech_metrics['Technician']
    
    # Ensure performance_metrics has TechCode for merging
    if 'TechCode' not in performance_metrics.columns and 'Technician' in performance_metrics.columns:
        performance_metrics['TechCode'] = performance_metrics['Technician']
    
    # Get the column differences while ensuring TechCode exists
    if 'TechCode' in tech_metrics.columns and 'TechCode' in performance_metrics.columns:
        # Combine metrics with safe column differencing
        performance_cols_to_use = [col for col in performance_metrics.columns 
                                  if col != 'TechCode' and col not in tech_metrics.columns]
        
        # Add TechCode to the selection
        performance_cols_to_use = ['TechCode'] + performance_cols_to_use
        
        # Merge with specific columns to avoid conflicts
        combined_metrics = pd.merge(
            tech_metrics,
            performance_metrics[performance_cols_to_use],
            on='TechCode',
            how='outer'
        )
        
        # Merge cancellation metrics too
        cancel_cols_to_use = [col for col in cancellation_metrics.columns 
                             if col != 'TechCode' and col not in combined_metrics.columns]
        
        # Only merge if there are non-TechCode columns to merge
        if cancel_cols_to_use:
            cancel_cols_to_use = ['TechCode'] + cancel_cols_to_use
            combined_metrics = pd.merge(
                combined_metrics,
                cancellation_metrics[cancel_cols_to_use],
                on='TechCode',
                how='outer'
            )
    else:
        # Fallback if we somehow don't have TechCode in both
        st.warning("Warning: Unable to merge metrics due to missing TechCode column")
        combined_metrics = tech_metrics
    
    # Process driving data if available
    driving_metrics = None
    if 'alert' in gps_data and not gps_data['alert'].empty:
        try:
            alert_data = gps_data['alert']
            
            # Check the structure of alert data
            print("Alert data columns:", alert_data.columns.tolist())
            
            # Ensure we have the required columns for alert data
            if 'AlertType' not in alert_data.columns and 'Alert' not in alert_data.columns:
                # Try to identify alert column
                for col in alert_data.columns:
                    if 'alert' in col.lower() or 'type' in col.lower():
                        alert_data['AlertType'] = alert_data[col]
                        print(f"Using {col} as alert type column")
                        break
                else:
                    # If no suitable column found, create a dummy
                    alert_data['AlertType'] = 'Unknown'
                    print("No alert type column found, using placeholder")
            
            # Make sure we have a device identifier column
            device_col = None
            for col in ['Device', 'DeviceId', 'Driver', 'DriverName']:
                if col in alert_data.columns:
                    device_col = col
                    break
            
            if device_col is None:
                # Create a mapping from tech codes to device names if available
                if 'TechCode' in integrated_data.columns and 'Device' in integrated_data.columns:
                    tech_to_device = dict(zip(
                        integrated_data['TechCode'].astype(str),
                        integrated_data['Device'].astype(str)
                    ))
                    # Use first tech code's device as placeholder
                    if tech_to_device:
                        first_device = list(tech_to_device.values())[0]
                        alert_data['Device'] = first_device
                        print(f"No device column found, using {first_device} as placeholder")
                    else:
                        alert_data['Device'] = 'Unknown'
                        print("No device mapping available, using 'Unknown' as placeholder")
                else:
                    alert_data['Device'] = 'Unknown'
                    print("No device information available, using 'Unknown' as placeholder")
            
            # Filter alerts by date
            date_col = next((col for col in alert_data.columns if 'date' in col.lower() or 'time' in col.lower()), None)
            if date_col:
                # Ensure date column is datetime
                if not pd.api.types.is_datetime64_dtype(alert_data[date_col]):
                    alert_data[date_col] = pd.to_datetime(alert_data[date_col], errors='coerce')
                
                alert_data = alert_data[
                    (alert_data[date_col] >= pd.Timestamp(start_date)) &
                    (alert_data[date_col] <= pd.Timestamp(end_date))
                ]
            
            # Use end_date as the as_of_date
            end_datetime = pd.Timestamp(end_date)
            
            # Calculate alert scores with improved error handling
            driving_metrics = calculate_alert_scores(alert_data, end_datetime)
            
            # If we still don't have a proper structure, create a fallback
            if driving_metrics is None or driving_metrics.empty:
                print("No driving metrics could be generated, creating fallback data")
                driving_metrics = pd.DataFrame({
                    'TechCode': selected_techs,
                    'TotalAlerts': 0,
                    'DrivingScore': 90  # Default good score
                })
        except Exception as e:
            st.warning(f"Error processing alert data: {str(e)}")
            print(f"Alert data processing error: {str(e)}")
            print(f"Alert data columns: {gps_data['alert'].columns.tolist() if 'alert' in gps_data else 'No alert data'}")
            
            # Create dummy driving metrics instead of failing
            driving_metrics = pd.DataFrame({
                'TechCode': selected_techs,
                'TotalAlerts': 0,
                'DrivingScore': 90  # Default good score
            })
    
    # Summarize cancellations by reason
    if 'CancellationReason' in integrated_data.columns:
        # Group by reason and count
        cancellation_summary = integrated_data[integrated_data['CancellationReason'] != 'NOT_CANCELED'].groupby(
            'CancellationReason'
        ).size().reset_index(name='Count')
        
        # Calculate percentages
        total_cancellations = cancellation_summary['Count'].sum()
        if total_cancellations > 0:
            cancellation_summary['Percentage'] = (cancellation_summary['Count'] / total_cancellations) * 100
        else:
            cancellation_summary['Percentage'] = 0
    else:
        cancellation_summary = pd.DataFrame(columns=['Reason', 'Count', 'Percentage'])
    
    process_state.text('Processing complete!')
    
    return combined_metrics, driving_metrics, cancellation_summary

def create_kpi_table(tech_metrics):
    """
    Create a formatted table for technician KPIs.
    
    Args:
        tech_metrics: DataFrame with technician metrics
    """
    # Create a copy for display
    display_df = tech_metrics.copy()
    
    # Format numeric columns
    if 'TotalRevenue' in display_df.columns:
        display_df['TotalRevenue'] = display_df['TotalRevenue'].map('${:,.2f}'.format)
    
    if 'AvgRevenuePerJob' in display_df.columns:
        display_df['AvgRevenuePerJob'] = display_df['AvgRevenuePerJob'].map('${:,.2f}'.format)
    
    if 'AvgProfitPerJob' in display_df.columns:
        display_df['AvgProfitPerJob'] = display_df['AvgProfitPerJob'].map('${:,.2f}'.format)
    
    # Format percentage columns
    for col in ['FTC_Rate', 'DiagnosticOnly_Rate']:
        if col in display_df.columns:
            display_df[col] = display_df[col].map('{:.1%}'.format)
    
    # Format profit margin as percentage
    if 'ProfitMargin' in display_df.columns:
        display_df['ProfitMargin'] = display_df['ProfitMargin'].map('{:.1f}%'.format)
    
    # Format part markup as percentage
    if 'PartMarkupPct' in display_df.columns:
        display_df['PartMarkupPct'] = display_df['PartMarkupPct'].map('{:.1f}%'.format)
    
    # Rename columns for display
    column_map = {
        'TechCode': 'Technician',
        'TotalJobs': 'Total Jobs',
        'CompletedJobs': 'Completed',
        'FTC_Jobs': 'FTC Jobs',
        'DiagnosticOnly_Jobs': 'Diag. Only',
        'FTC_Rate': 'FTC Rate',
        'DiagnosticOnly_Rate': 'Diag. Rate',
        'TotalRevenue': 'Revenue',
        'AvgRevenuePerJob': 'Avg $/Job',
        'AvgProfitPerJob': 'Avg Profit/Job',
        'ProfitMargin': 'Profit Margin',
        'PartMarkupPct': 'Parts Markup'
    }
    
    # Select and rename columns
    display_cols = [col for col in column_map.keys() if col in display_df.columns]
    display_df = display_df[display_cols].rename(columns=column_map)
    
    # Display the table
    st.dataframe(display_df, use_container_width=True)

def create_goal_tracking_chart(tech_metrics):
    """
    Create a chart showing goal tracking.
    
    Args:
        tech_metrics: DataFrame with technician metrics
    """
    # Import business rules
    from config.settings import (
        FIRST_CALL_COMPLETE_GOAL, DIAGNOSTIC_ONLY_MIN_GOAL, 
        DIAGNOSTIC_ONLY_IDEAL_GOAL
    )
    
    # Create columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("First Trip Complete Rate by Technician")
        
        # Create data for chart
        if 'TechCode' in tech_metrics.columns and 'FTC_Rate' in tech_metrics.columns:
            chart_data = tech_metrics[['TechCode', 'FTC_Rate']].copy()
            chart_data = chart_data.sort_values('FTC_Rate', ascending=False)
            
            # Create bar chart
            st.bar_chart(chart_data.set_index('TechCode'), use_container_width=True)
            
            # Show goal line
            st.markdown(f"**Goal: {FIRST_CALL_COMPLETE_GOAL:.0%}**")
            
            # Show average
            avg_ftc = tech_metrics['FTC_Rate'].mean()
            st.metric("Company Average", f"{avg_ftc:.1%}")
    
    with col2:
        st.subheader("Diagnostic Only Rate by Technician")
        
        # Create data for chart
        if 'TechCode' in tech_metrics.columns and 'DiagnosticOnly_Rate' in tech_metrics.columns:
            chart_data = tech_metrics[['TechCode', 'DiagnosticOnly_Rate']].copy()
            chart_data = chart_data.sort_values('DiagnosticOnly_Rate', ascending=False)
            
            # Create bar chart
            st.bar_chart(chart_data.set_index('TechCode'), use_container_width=True)
            
            # Show goal lines
            st.markdown(f"**Min Goal: {DIAGNOSTIC_ONLY_MIN_GOAL:.0%}, Ideal: {DIAGNOSTIC_ONLY_IDEAL_GOAL:.0%}**")
            
            # Show average
            avg_diag = tech_metrics['DiagnosticOnly_Rate'].mean()
            st.metric("Company Average", f"{avg_diag:.1%}")

def main():
    """Main Streamlit application."""
    
    # Create dashboard header
    st.title('Service Technician Performance Dashboard')
    st.subheader('Key Performance Indicators')
    
    # Add date information
    st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Create sidebar filters
    st.sidebar.title('Filters')
    
    # Create date filters
    # Get default date range (current month)
    today = datetime.now().date()
    start_of_month = datetime(today.year, today.month, 1).date()
    
    st.sidebar.header('Date Range')
    start_date = st.sidebar.date_input(
        "Start Date",
        value=start_of_month,
        key='start_date'
    )
    
    end_date = st.sidebar.date_input(
        "End Date",
        value=today,
        key='end_date'
    )
    
    # Load data
    type6_data, sales_data, gps_data = load_data()
    
    # Get available technicians
    if type6_data is not None and not type6_data.empty and 'TechCode' in type6_data.columns:
        # Convert TechCode to string, handle NaN and empty values properly
        type6_data['TechCode'] = type6_data['TechCode'].fillna('').astype(str)
        
        # Filter to only valid tech codes (non-empty, non-NaN)
        valid_techs = [tech for tech in type6_data['TechCode'].unique() 
                      if tech and tech.strip() and tech.lower() != 'nan']
        
        # Sort using a safer approach
        try:
            # Convert to strings to ensure consistent sorting
            tech_list = sorted([str(tech) for tech in valid_techs])
            print(f"Successfully sorted {len(tech_list)} technicians")
        except Exception as e:
            # Fallback if sorting fails
            print(f"Warning: Could not sort technicians: {str(e)}")
            tech_list = valid_techs
            
    elif sales_data is not None and not sales_data.empty and 'Technician' in sales_data.columns:
        # Try getting techs from sales data if available
        sales_data['Technician'] = sales_data['Technician'].astype(str)
        valid_techs = []
        for tech in sales_data['Technician'].unique():
            if tech and tech.strip() and tech.lower() != 'nan':
                valid_techs.append(tech)
        try:
            # Ensure all values are strings before sorting
            tech_list = sorted([str(tech) for tech in valid_techs])
        except TypeError:
            tech_list = valid_techs
    else:
        # Mock tech list if no data
        tech_list = ['TECH1', 'TECH2', 'TECH3', 'TECH4', 'TECH5']
    
    # Create technician filters
    st.sidebar.header('Technicians')
    select_all = st.sidebar.checkbox('Select All', value=True)
    
    if select_all:
        selected_techs = tech_list
    else:
        selected_techs = st.sidebar.multiselect(
            'Select Technicians',
            options=tech_list,
            default=[]
        )
    
    # Process data based on filters
    tech_metrics, driving_metrics, cancellation_summary = process_data(
        type6_data, sales_data, gps_data, start_date, end_date, selected_techs
    )
    
    # Display metrics if data is available
    if tech_metrics is not None and not tech_metrics.empty:
        # Create tabs for different sections
        tabs = st.tabs([
            "Technician Performance", 
            "Revenue Analysis", 
            "Cancellation Analysis", 
            "Driving Behavior"
        ])
        
        # Technician Performance tab
        with tabs[0]:
            st.header('Technician Performance Metrics')
            
            # KPI metrics
            cols = st.columns(3)
            
            with cols[0]:
                ftc_rate = tech_metrics['FTC_Rate'].mean() if 'FTC_Rate' in tech_metrics.columns else 0
                st.metric("Avg FTC Rate", f"{ftc_rate:.1%}")
            
            with cols[1]:
                diag_rate = tech_metrics['DiagnosticOnly_Rate'].mean() if 'DiagnosticOnly_Rate' in tech_metrics.columns else 0
                st.metric("Avg Diagnostic Rate", f"{diag_rate:.1%}")
            
            with cols[2]:
                total_jobs = tech_metrics['TotalJobs'].sum() if 'TotalJobs' in tech_metrics.columns else 0
                st.metric("Total Jobs", f"{total_jobs}")
            
            # Technician KPI table
            st.subheader('Technician KPI Table')
            create_kpi_table(tech_metrics)
            
            # Goal tracking charts
            st.subheader('Goal Tracking')
            create_goal_tracking_chart(tech_metrics)
        
        # Revenue Analysis tab
        with tabs[1]:
            st.header('Revenue Analysis')
            
            # Revenue metrics
            st.subheader('Revenue Metrics')
            cols = st.columns(3)
            
            with cols[0]:
                total_revenue = tech_metrics['TotalRevenue'].sum() if 'TotalRevenue' in tech_metrics.columns else 0
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            
            with cols[1]:
                completed_jobs = tech_metrics['CompletedJobs'].sum() if 'CompletedJobs' in tech_metrics.columns else tech_metrics['TotalJobs'].sum()
                avg_per_job = total_revenue / completed_jobs if completed_jobs > 0 else 0
                st.metric("Average $ per Job", f"${avg_per_job:,.2f}")
            
            with cols[2]:
                if 'TotalParts' in tech_metrics.columns and 'TotalLabor' in tech_metrics.columns:
                    total_parts = tech_metrics['TotalParts'].sum()
                    total_labor = tech_metrics['TotalLabor'].sum()
                    parts_to_labor = total_parts / total_labor if total_labor > 0 else 0
                else:
                    parts_to_labor = 0
                st.metric("Parts to Labor Ratio", f"{parts_to_labor:.2f}")
            
            # Profit metrics section (new)
            if 'TotalProfit' in tech_metrics.columns:
                st.subheader('Profit Metrics')
                profit_cols = st.columns(3)
                
                with profit_cols[0]:
                    total_profit = tech_metrics['TotalProfit'].sum()
                    st.metric("Total Profit", f"${total_profit:,.2f}")
                
                with profit_cols[1]:
                    avg_profit_per_job = total_profit / completed_jobs if completed_jobs > 0 else 0
                    st.metric("Average Profit per Job", f"${avg_profit_per_job:,.2f}")
                
                with profit_cols[2]:
                    profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
                    st.metric("Overall Profit Margin", f"{profit_margin:.1f}%")
                
                # Part cost and markup analysis
                if 'TotalPartCost' in tech_metrics.columns and 'PartMarkupPct' in tech_metrics.columns:
                    st.subheader('Parts Cost Analysis')
                    parts_cols = st.columns(3)
                    
                    with parts_cols[0]:
                        total_part_cost = tech_metrics['TotalPartCost'].sum()
                        st.metric("Total Parts Cost", f"${total_part_cost:,.2f}")
                    
                    with parts_cols[1]:
                        parts_markup = (total_parts - total_part_cost) / total_part_cost * 100 if total_part_cost > 0 else 0
                        st.metric("Parts Markup", f"{parts_markup:.1f}%")
                    
                    with parts_cols[2]:
                        avg_markup = tech_metrics['PartMarkupPct'].mean()
                        st.metric("Avg Tech Markup", f"{avg_markup:.1f}%")
                    
                    # Part markup by technician table
                    st.markdown("#### Part Markup by Technician")
                    
                    # Create a DataFrame for display
                    markup_df = tech_metrics[['TechCode', 'TotalParts', 'TotalPartCost', 'PartMarkupPct']].copy()
                    markup_df['Markup $'] = markup_df['TotalParts'] - markup_df['TotalPartCost']
                    
                    # Format for display
                    markup_df['TotalParts'] = markup_df['TotalParts'].map('${:,.2f}'.format)
                    markup_df['TotalPartCost'] = markup_df['TotalPartCost'].map('${:,.2f}'.format)
                    markup_df['Markup $'] = markup_df['Markup $'].map('${:,.2f}'.format)
                    markup_df['PartMarkupPct'] = markup_df['PartMarkupPct'].map('{:.1f}%'.format)
                    
                    # Rename columns for display
                    markup_df.columns = ['Technician', 'Parts Revenue', 'Parts Cost', 'Markup %', 'Markup $']
                    
                    # Display table
                    st.dataframe(markup_df, use_container_width=True)
                
                # Part usage analysis (if available)
                if 'SpecialOrderPartsCount' in tech_metrics.columns and 'StockPartsCount' in tech_metrics.columns:
                    st.subheader('Part Usage Analysis')
                    usage_cols = st.columns(2)
                    
                    with usage_cols[0]:
                        total_special_order = tech_metrics['SpecialOrderPartsCount'].sum()
                        st.metric("Special Order Parts", f"{total_special_order}")
                    
                    with usage_cols[1]:
                        total_stock = tech_metrics['StockPartsCount'].sum()
                        st.metric("Stock Parts", f"{total_stock}")
                    
                    # Calculate percentage
                    total_parts_count = total_special_order + total_stock
                    if total_parts_count > 0:
                        special_order_pct = total_special_order / total_parts_count * 100
                        stock_pct = total_stock / total_parts_count * 100
                        
                        # Create data for pie chart
                        usage_data = pd.DataFrame({
                            'Type': ['Special Order', 'Stock'],
                            'Count': [total_special_order, total_stock]
                        })
                        
                        # Create pie chart
                        usage_fig = px.pie(
                            usage_data,
                            values='Count',
                            names='Type',
                            title='Part Usage Breakdown',
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        usage_fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(usage_fig, use_container_width=True)
            
            # Revenue breakdown
            st.subheader('Revenue Breakdown')
            
            # Check if we have the core revenue data
            if 'TotalLabor' in tech_metrics.columns and 'TotalParts' in tech_metrics.columns and 'TotalServiceCalls' in tech_metrics.columns:
                # Get raw totals
                total_labor = tech_metrics['TotalLabor'].sum() 
                total_parts = tech_metrics['TotalParts'].sum()
                total_service = tech_metrics['TotalServiceCalls'].sum()
                
                # Recalculate total for consistency
                total_all = total_labor + total_parts + total_service
                
                # Create data for breakdown table
                if total_all > 0:
                    breakdown_data = {
                        'Category': ['Labor', 'Parts', 'Service Calls', 'Total'],
                        'Amount': [
                            f"${total_labor:,.2f}",
                            f"${total_parts:,.2f}",
                            f"${total_service:,.2f}",
                            f"${total_all:,.2f}"
                        ],
                        'Percentage': [
                            f"{(total_labor/total_all*100):.1f}%",
                            f"{(total_parts/total_all*100):.1f}%",
                            f"{(total_service/total_all*100):.1f}%",
                            "100.0%"
                        ]
                    }
                else:
                    # Handle zero revenue case
                    breakdown_data = {
                        'Category': ['Labor', 'Parts', 'Service Calls', 'Total'],
                        'Amount': ["$0.00", "$0.00", "$0.00", "$0.00"],
                        'Percentage': ["0.0%", "0.0%", "0.0%", "0.0%"]
                    }
                
                # Create and display the breakdown table
                breakdown_df = pd.DataFrame(breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
                
                # Show the breakdown as a pie chart
                if total_all > 0:
                    # Create chart data (excluding total)
                    chart_data = pd.DataFrame({
                        'Category': ['Labor', 'Parts', 'Service Calls'],
                        'Amount': [total_labor, total_parts, total_service]
                    })
                    
                    # Create and display the pie chart
                    pie_fig = px.pie(
                        chart_data, 
                        values='Amount', 
                        names='Category',
                        title='Revenue Breakdown',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(pie_fig, use_container_width=True)
                
                # Profit breakdown (if available)
                if 'TotalProfit' in tech_metrics.columns and 'TotalPartCost' in tech_metrics.columns:
                    st.subheader('Profit Breakdown')
                    
                    # Calculate profit components
                    labor_profit = total_labor  # Assuming labor is all profit
                    parts_profit = total_parts - tech_metrics['TotalPartCost'].sum()
                    service_profit = total_service  # Assuming service calls are all profit
                    
                    total_profit = labor_profit + parts_profit + service_profit
                    
                    # Create profit breakdown table
                    if total_profit > 0:
                        profit_breakdown = {
                            'Category': ['Labor', 'Parts', 'Service Calls', 'Total'],
                            'Amount': [
                                f"${labor_profit:,.2f}",
                                f"${parts_profit:,.2f}",
                                f"${service_profit:,.2f}",
                                f"${total_profit:,.2f}"
                            ],
                            'Percentage': [
                                f"{(labor_profit/total_profit*100):.1f}%",
                                f"{(parts_profit/total_profit*100):.1f}%",
                                f"{(service_profit/total_profit*100):.1f}%",
                                "100.0%"
                            ]
                        }
                        
                        # Create and display the profit breakdown table
                        profit_df = pd.DataFrame(profit_breakdown)
                        st.dataframe(profit_df, use_container_width=True, hide_index=True)
                        
                        # Show the profit breakdown as a pie chart
                        profit_chart_data = pd.DataFrame({
                            'Category': ['Labor', 'Parts', 'Service Calls'],
                            'Amount': [labor_profit, parts_profit, service_profit]
                        })
                        
                        profit_fig = px.pie(
                            profit_chart_data,
                            values='Amount',
                            names='Category',
                            title='Profit Breakdown',
                            color_discrete_sequence=px.colors.qualitative.Pastel1
                        )
                        profit_fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(profit_fig, use_container_width=True)
            else:
                st.warning("Revenue breakdown data is not available.")
        
        # Cancellation Analysis tab
        with tabs[2]:
            st.header('Cancellation Analysis')
            
            # Skip if no data
            if cancellation_summary is None or cancellation_summary.empty:
                st.info("No cancellation data available for the selected period.")
            else:
                # Cancellation metrics
                total_cancellations = cancellation_summary['Count'].sum() if 'Count' in cancellation_summary.columns else 0
                st.metric("Total Cancellations", f"{total_cancellations}")
                
                # Cancellation table
                st.subheader('Cancellation Reasons')
                
                # Format percentages
                if 'Percentage' in cancellation_summary.columns:
                    cancellation_summary['Percentage'] = cancellation_summary['Percentage'].map('{:.1f}%'.format)
                
                # Display table
                st.dataframe(
                    cancellation_summary,
                    use_container_width=True,
                    hide_index=True
                )
        
        # Driving Behavior tab
        with tabs[3]:
            st.header('Driving Behavior Analysis')
            
            # Skip if no data
            if driving_metrics is None or driving_metrics.empty:
                st.info("No driving data available for the selected period.")
            else:
                # Driving metrics
                cols = st.columns(3)
                
                with cols[0]:
                    avg_score = driving_metrics['DrivingScore'].mean() if 'DrivingScore' in driving_metrics.columns else 0
                    st.metric("Average Safety Score", f"{avg_score:.1f}")
                
                with cols[1]:
                    total_alerts = driving_metrics['TotalAlerts'].sum() if 'TotalAlerts' in driving_metrics.columns else 0
                    st.metric("Total Alerts", f"{total_alerts}")
                
                with cols[2]:
                    if 'DrivingScore' in driving_metrics.columns and not driving_metrics.empty:
                        worst_idx = driving_metrics['DrivingScore'].idxmin()
                        worst_driver = driving_metrics.iloc[worst_idx]['TechCode'] if 'TechCode' in driving_metrics.columns else "Unknown"
                        st.metric("Highest Risk Driver", f"{worst_driver}")
                
                # Driving table
                st.subheader('Driving Metrics by Technician')
                
                # Format for display
                display_df = driving_metrics.copy()
                
                if 'DrivingScore' in display_df.columns:
                    display_df['DrivingScore'] = display_df['DrivingScore'].map('{:.1f}'.format)
                
                # Display table
                st.dataframe(
                    display_df,
                    use_container_width=True
                )
    else:
        st.warning("No data available for the selected filters. Please adjust your selection or check your data files.")
    
    # Add footer
    st.markdown("---")
    st.markdown("© 2025 Service Analytics Dashboard | Developed with Streamlit")

if __name__ == "__main__":
    main() 