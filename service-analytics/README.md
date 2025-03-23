# Service Analytics Dashboard

A Streamlit-based dashboard for analyzing service technician performance, revenue metrics, and driving data.

## Features

- Technician Performance Metrics
- Revenue Analysis
- Cancellation Tracking
- GPS and Driving Data Integration
- Customizable Date Ranges and Filtering

## Getting Started

### Prerequisites

- Python 3.6+
- Pip package manager

### Installation

1. Clone this repository:
```
git clone [repository-url]
cd service-analytics
```

2. Install required packages:
```
pip install -r requirements.txt
```

3. Run the application:
```
streamlit run app.py
```

## Data Setup

### Initial Setup with Real Data

1. Place your data files in the `data/` directory using the following file naming convention:
   - `Type6report20XX.csv` - Your service job report
   - `SlsJrnl.csv` - Your sales journal data
   - GPS data files follow the naming convention used by the GPS tracking provider

2. The application checks for these files in the data directory and will automatically load them.

### Preparing Data for Regular Updates

To set up regular data updates:

1. **Manual Updates**
   - Download fresh data exports from your service management system
   - Place them in the `data/` directory, replacing or updating existing files
   - Restart the Streamlit app to load the new data

2. **Automated Updates (Windows)**
   Create a batch script `update_data.bat` with the following:
   ```batch
   @echo off
   echo Updating service analytics data...
   
   REM Set paths
   set DOWNLOAD_DIR=C:\Path\To\Downloads
   set APP_DATA_DIR=C:\Projects and Programs\Analytic Reports\service-analytics\data
   
   REM Copy newest files
   copy "%DOWNLOAD_DIR%\Type6report*.csv" "%APP_DATA_DIR%\"
   copy "%DOWNLOAD_DIR%\SlsJrnl*.csv" "%APP_DATA_DIR%\"
   copy "%DOWNLOAD_DIR%\*_breakdown_*.csv" "%APP_DATA_DIR%\"
   copy "%DOWNLOAD_DIR%\drives_and_stops_*.csv" "%APP_DATA_DIR%\"
   copy "%DOWNLOAD_DIR%\day_engine_*.csv" "%APP_DATA_DIR%\"
   copy "%DOWNLOAD_DIR%\idle_time_*.csv" "%APP_DATA_DIR%\"
   copy "%DOWNLOAD_DIR%\alert_summary_*.csv" "%APP_DATA_DIR%\"
   
   echo Data update complete.
   ```

3. **Scheduled Updates (Windows)**
   - Open Task Scheduler
   - Create a new task to run weekly/monthly
   - Set the action to run the `update_data.bat` script
   - Configure triggers for your preferred schedule (e.g., every Friday at 5pm)

4. **Data Archiving**
   For historical analysis, create an archiving system:
   ```
   data/
   ├── current/        # Current files used by the app
   ├── archive/
   │   ├── 2025-03/    # Monthly archives
   │   ├── 2025-02/
   │   └── 2025-01/
   ```

## File Format Requirements

The application expects the following formats:

1. **Type6report.csv**
   - Contains service job information
   - Must include: TechCode, JobNumber, OriginDate, Status, WorkDescription fields

2. **SlsJrnl.csv**
   - Contains sales and revenue data 
   - Must include: DateRecorded, Technician, InvoiceNumber, JobNumber, MerchandiseSold, PartsSold, LaborSold fields

3. **GPS tracking files**
   - Format must match the sample files provided in the data directory
   - Naming conventions must be maintained for proper file type identification

## Troubleshooting

If you encounter issues:

1. Check that data files are in the correct format and location
2. Verify file permissions allow reading from the data directory 
3. Run `python test_imports.py` to check if all imports work correctly
4. Examine Streamlit console output for specific error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details. 