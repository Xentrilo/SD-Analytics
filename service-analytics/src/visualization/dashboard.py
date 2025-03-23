"""
Visualization functions for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def create_date_filters():
    """
    Create date range filters for the dashboard.
    
    Returns:
        Tuple of (start_date, end_date)
    """
    # Get default date range (current month)
    today = datetime.date.today()
    start_of_month = datetime.date(today.year, today.month, 1)
    
    # Create date inputs in sidebar
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
    
    # Ensure end date is not before start date
    if start_date > end_date:
        st.sidebar.error('Error: End date must be after start date')
        end_date = start_date
    
    return start_date, end_date

def create_technician_filters(tech_list):
    """
    Create technician selection filters.
    
    Args:
        tech_list: List of available technicians
        
    Returns:
        List of selected technicians
    """
    st.sidebar.header('Technicians')
    
    # Select all by default
    select_all = st.sidebar.checkbox('Select All', value=True)
    
    if select_all:
        selected_techs = tech_list
    else:
        selected_techs = st.sidebar.multiselect(
            'Select Technicians',
            options=tech_list,
            default=[]
        )
    
    return selected_techs

def create_dashboard_header():
    """
    Create the main dashboard header.
    """
    st.title('Service Technician Performance Dashboard')
    st.subheader('Key Performance Indicators')
    
    # Add date information
    st.text(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

def format_tech_performance_table(df):
    """
    Format technician performance table for display.
    
    Args:
        df: DataFrame with technician metrics
        
    Returns:
        Formatted DataFrame
    """
    # Create a copy for display
    display_df = df.copy()
    
    # Format numeric columns
    if 'TotalRevenue' in display_df.columns:
        display_df['TotalRevenue'] = display_df['TotalRevenue'].map('${:,.2f}'.format)
    
    if 'AvgRevenuePerJob' in display_df.columns:
        display_df['AvgRevenuePerJob'] = display_df['AvgRevenuePerJob'].map('${:,.2f}'.format)
    
    # Format percentage columns
    for col in ['FTC_Rate', 'DiagnosticOnly_Rate', 'CancellationRate']:
        if col in display_df.columns:
            display_df[col] = display_df[col].map('{:.1%}'.format)
    
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
        'CancellationRate': 'Cancel Rate'
    }
    
    # Select and rename columns
    display_cols = [col for col in column_map.keys() if col in display_df.columns]
    display_df = display_df[display_cols].rename(columns=column_map)
    
    return display_df

def create_kpi_table(df):
    """
    Create a KPI table for display.
    
    Args:
        df: DataFrame with metrics
    """
    # Format the table
    display_df = format_tech_performance_table(df)
    
    # Display the table
    st.dataframe(display_df, use_container_width=True)

def create_goal_tracking_chart(tech_metrics):
    """
    Create a chart showing goal tracking.
    
    Args:
        tech_metrics: DataFrame with technician metrics
    """
    # Import business rules
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from config.settings import (
        FIRST_CALL_COMPLETE_GOAL, DIAGNOSTIC_ONLY_MIN_GOAL, DIAGNOSTIC_ONLY_IDEAL_GOAL
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

def create_kpi_section(tech_metrics):
    """
    Create the main KPI section.
    
    Args:
        tech_metrics: DataFrame with technician metrics
    """
    st.header('Technician Performance')
    
    # KPI metrics
    cols = st.columns(4)
    
    with cols[0]:
        ftc_rate = tech_metrics['FTC_Rate'].mean() if 'FTC_Rate' in tech_metrics.columns else 0
        st.metric("Avg FTC Rate", f"{ftc_rate:.1%}")
    
    with cols[1]:
        diag_rate = tech_metrics['DiagnosticOnly_Rate'].mean() if 'DiagnosticOnly_Rate' in tech_metrics.columns else 0
        st.metric("Avg Diagnostic Rate", f"{diag_rate:.1%}")
    
    with cols[2]:
        total_jobs = tech_metrics['TotalJobs'].sum() if 'TotalJobs' in tech_metrics.columns else 0
        st.metric("Total Jobs", f"{total_jobs}")
    
    with cols[3]:
        cancel_rate = tech_metrics['CancellationRate'].mean() if 'CancellationRate' in tech_metrics.columns else 0
        st.metric("Avg Cancellation Rate", f"{cancel_rate:.1%}")
    
    # Create KPI table
    create_kpi_table(tech_metrics)
    
    # Show KPI charts in expander
    st.subheader('Goal Tracking')
    create_goal_tracking_chart(tech_metrics)

def create_revenue_section(tech_metrics):
    """
    Create the revenue analysis section.
    
    Args:
        tech_metrics: DataFrame with revenue data
    """
    st.header('Revenue Analysis')
    
    # Revenue metrics
    cols = st.columns(3)
    
    with cols[0]:
        total_revenue = tech_metrics['TotalRevenue'].sum() if 'TotalRevenue' in tech_metrics.columns else 0
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with cols[1]:
        completed_jobs = tech_metrics['CompletedJobs'].sum() if 'CompletedJobs' in tech_metrics.columns else tech_metrics['TotalJobs'].sum()
        avg_per_job = total_revenue / completed_jobs if completed_jobs > 0 else 0
        st.metric("Average $ per Job", f"${avg_per_job:,.2f}")
    
    with cols[2]:
        parts_to_labor = tech_metrics['TotalParts'].sum() / tech_metrics['TotalLabor'].sum() if 'TotalParts' in tech_metrics.columns and 'TotalLabor' in tech_metrics.columns and tech_metrics['TotalLabor'].sum() > 0 else 0
        st.metric("Parts to Labor Ratio", f"{parts_to_labor:.2f}")
    
    # Revenue breakdown
    st.subheader('Revenue Breakdown')
    
    # Check if we have the data
    if all(col in tech_metrics.columns for col in ['TotalLabor', 'TotalParts', 'TotalServiceCalls']):
        # Calculate totals
        total_labor = tech_metrics['TotalLabor'].sum()
        total_parts = tech_metrics['TotalParts'].sum()
        total_service_calls = tech_metrics['TotalServiceCalls'].sum()
        
        # Create data for pie chart
        pie_data = pd.DataFrame({
            'Category': ['Labor', 'Parts', 'Service Calls'],
            'Amount': [total_labor, total_parts, total_service_calls]
        })
        
        # Display as a table
        st.dataframe(
            pd.DataFrame({
                'Category': ['Labor', 'Parts', 'Service Calls', 'Total'],
                'Amount': [
                    f"${total_labor:,.2f}",
                    f"${total_parts:,.2f}",
                    f"${total_service_calls:,.2f}",
                    f"${(total_labor + total_parts + total_service_calls):,.2f}"
                ],
                'Percentage': [
                    f"{total_labor/total_revenue*100:.1f}%" if total_revenue > 0 else "0.0%",
                    f"{total_parts/total_revenue*100:.1f}%" if total_revenue > 0 else "0.0%",
                    f"{total_service_calls/total_revenue*100:.1f}%" if total_revenue > 0 else "0.0%",
                    "100.0%"
                ]
            }),
            use_container_width=True
        )

def create_cancellation_section(cancellation_data):
    """
    Create the cancellation analysis section.
    
    Args:
        cancellation_data: DataFrame with cancellation metrics
    """
    st.header('Cancellation Analysis')
    
    # Skip if no data
    if cancellation_data.empty:
        st.info("No cancellation data available for the selected period.")
        return
    
    # Cancellation metrics
    total_cancellations = cancellation_data['Count'].sum() if 'Count' in cancellation_data.columns else 0
    st.metric("Total Cancellations", f"{total_cancellations}")
    
    # Cancellation table
    st.subheader('Cancellation Reasons')
    
    # Format percentages
    display_df = cancellation_data.copy()
    if 'Percentage' in display_df.columns:
        display_df['Percentage'] = display_df['Percentage'].map('{:.1f}%'.format)
    
    # Display the table
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def create_driving_section(driving_metrics):
    """
    Create the driving behavior section.
    
    Args:
        driving_metrics: DataFrame with driving data
    """
    st.header('Driving Behavior Analysis')
    
    # Skip if no data
    if driving_metrics.empty:
        st.info("No driving data available for the selected period.")
        return
    
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
            id_col = next((col for col in ['TechCode', 'DeviceId', 'DriverId'] if col in driving_metrics.columns), None)
            worst_driver = driving_metrics.iloc[worst_idx][id_col] if id_col else "Unknown"
            st.metric("Highest Risk Driver", f"{worst_driver}")
    
    # Driving table
    st.subheader('Driving Metrics by Technician')
    
    # Format for display
    display_df = driving_metrics.copy()
    
    if 'DrivingScore' in display_df.columns:
        display_df['DrivingScore'] = display_df['DrivingScore'].map('{:.1f}'.format)
    
    # Display table
    st.dataframe(display_df, use_container_width=True) 