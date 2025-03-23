# Service Analytics Dashboard Quick Start Guide

This guide provides step-by-step instructions to get started with your Service Analytics Dashboard using real data.

## Initial Setup

1. Make sure you have Python installed (3.6+)
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Working with Real Data

### Step 1: Prepare Your Data Files

1. **Export required data files**:
   - Export Type6 report from ServiceDesk as CSV
   - Export Sales Journal data
   - Download GPS tracking files

2. **Verify file formats match requirements**:
   ```
   python prepare_data.py verify data/Type6report2025.csv --type type6
   python prepare_data.py verify data/SlsJrnl.csv --type sales
   ```

3. **Convert DAT files to CSV if needed**:
   ```
   python prepare_data.py convert data/SlsJrnl.4P6.Dat.str --output data/SlsJrnl.csv
   ```

4. **Fix date formats if needed**:
   ```
   python prepare_data.py fix_dates data/Type6report2025.csv
   ```

### Step 2: Place Files in Data Directory

1. Make sure all files are in the `data/` directory
2. File naming should follow these conventions:
   - `Type6report20XX.csv` for service job data
   - `SlsJrnl.csv` for sales journal data
   - GPS files should keep their original naming patterns

### Step 3: Run the Dashboard

You have several options to launch the dashboard:

#### Option 1: Command Line
```
streamlit run app.py
```

#### Option 2: Use the Launcher
Double-click on `Launch_Dashboard.bat` to start the dashboard with a visible console window.

#### Option 3: Hidden Launcher
Double-click on `Launch_Dashboard_Hidden.vbs` to start the dashboard with no console window.

#### Option 4: Desktop Shortcut
1. Run `Create_Desktop_Shortcut.bat` once
2. Use the created desktop shortcut to launch the dashboard anytime

## Regular Data Updates

### Manual Data Updates

1. **Export fresh data files** from your service management system
2. Run the `update_data.bat` script:
   ```
   update_data.bat
   ```
   Note: Edit the script first to set your correct download directory path.

### Automated Updates

1. **Configure Windows Task Scheduler**:
   - Open Task Scheduler
   - Create a new task
   - Set the program/script to: `C:\Projects and Programs\Analytic Reports\service-analytics\update_data.bat`
   - Set a schedule (weekly/monthly as needed)

## Troubleshooting

If the dashboard doesn't load properly:

1. **Check for import errors**: Run `python test_imports.py`
2. **Verify your data**: Run `python prepare_data.py verify` on each file
3. **Look at the console output** when running Streamlit for detailed error messages
   - If using the hidden launcher, try the regular `Launch_Dashboard.bat` to see error messages

## Using the Dashboard

1. **Select date range** in the sidebar
2. **Filter by technicians** as needed
3. **Navigate through tabs** to see different analytics:
   - Performance Overview
   - Revenue Analysis
   - Cancellation Tracking
   - Technician Driving Analysis

## Need Help?

For detailed documentation, see the full README.md file. 