# Service Analytics Data Mapping Guide

## Quick Reference: Technician Identifiers Across Files

| Data Source | Technician Column | Format | Example |
|-------------|-------------------|--------|---------|
| Sales Journal (SlsJrnl.csv) | `Technician` | Initials (2-letter code) | "BB", "JD" |
| Type6 Report (Type6report.csv) | `TechCode` | Initials (2-letter code) | "BB", "JD" |
| GPS Tracking - Various files | `Device`, `Driver_Name` | Full Name | "John Smith" |

## Data File Structure Overview

### Sales Journal (SlsJrnl.csv)

**Primary purpose**: Revenue tracking for service calls

**Key columns:**
- `DateRecorded`: Date of the service call (datetime format)
- `Technician`: Technician initials who performed the service
- `CustomerName`: Name of the customer
- `InvoiceNumber`: Unique identifier for the transaction
- `MerchandiseSold`: Dollar amount of merchandise sold
- `PartsSold`: Dollar amount of parts sold
- `LaborSold`: Dollar amount of labor charged
- `SCallSold`: Dollar amount of service call fee
- `TotalSale`: Total dollar amount of the transaction

**Notes:**
- This file tracks the financial aspects of service calls
- Imported from SlsJrnl.4P6.Dat.str using the conversion utility

### Type6 Report (Type6report2025.csv)

**Primary purpose**: Job tracking and technical details

**Key columns:**
- `OriginDate`: Date the job was created (datetime format)
- `TechCode`: Technician initials assigned to the job
- `JobNumber`: Unique identifier for the job
- `Status`: Current status of the job (Completed, Canceled, etc.)
- `WorkDescription`: Text description of the work performed
- `CompletedOnFirstTrip`: Whether the job was completed on first visit (boolean)
- `JobCanceled`: Whether the job was canceled (boolean)

**Notes:**
- This file contains operational data about each service job
- Uses latin1 encoding rather than utf-8
- Date formats may vary and require standardization

### GPS Tracking Data (Multiple files)

#### day_start_end_breakdown_*.csv
- Contains daily start/end times for technicians
- `Device`: Technician's full name
- `Date`: Date of the records
- `Start Time`, `End Time`: When the technician started/ended their day

#### drives_and_stops_*.csv
- Contains driving segments and stops
- `Device`: Technician's full name
- `Status`: "Driving" or "Stopped"
- `Start Time`, `End Time`: Start/end of driving segment or stop
- `Address`: Location of the stop (when available)

#### alert_summary_*.csv
- Contains driving alerts (speeding, hard braking, etc.)
- `Device`: Technician's full name
- `AlertType`: Type of driving alert
- `Date & Time`: When the alert occurred

## Key Relationships and Mapping

### Technician Mapping
The relationship between different technician identifiers is:
- `Technician` (Sales Journal) = `TechCode` (Type6 Report)
- Both of the above are typically 2-letter initials (e.g., "BB", "JD")
- These must be mapped to `Device` in GPS files which contains full names

### Job/Invoice Mapping
To link revenue data with job data:
- `InvoiceNumber` (Sales Journal) often correlates with `JobNumber` (Type6 Report)
- Multiple invoices may reference the same job number

### DateTime Handling
- Sales Journal: `DateRecorded` field typically in MM/DD/YYYY format
- Type6 Report: `OriginDate`, `FirstAppmnt`, `CmpltnDate` fields in various formats
- GPS data: Timezone issues with PST/PDT that should be handled properly

## Common Issues and Solutions

1. **Technician Name Inconsistency**:
   - Ensure consistent casing (uppercase both `Technician` and `TechCode`)
   - Create a mapping table for GPS data to match full names to initials

2. **Date Format Variations**:
   - Always convert dates to pandas datetime using `pd.to_datetime(field, errors='coerce')`
   - Handle missing dates gracefully

3. **Column Name Differences**:
   - Revenue data calculations should merge using:
     - `TotalLabor` = `LaborSold` (Sales Journal)
     - `TotalParts` = `PartsSold` (Sales Journal)
     - `TotalServiceCalls` = `SCallSold` (Sales Journal)

4. **Data Type Issues**:
   - `TechCode` can sometimes be numeric or float in imported data - convert to string
   - Missing values in certain fields can be NaN or empty strings - standardize handling

## Implementation Notes for Developers

When writing code to process these files:

1. Always convert technician identifiers to strings: 
   ```python
   df['TechCode'] = df['TechCode'].astype(str)
   ```

2. Handle technician data mapping early in the pipeline:
   ```python
   # If working with GPS data that needs to link to Tech Codes
   gps_to_tech_map = {
       "John Smith": "JS",
       "Bob Johnson": "BJ",
       # etc.
   }
   ```

3. Ensure proper merging between dataframes by normalizing join columns:
   ```python
   # When joining Sales Journal with Type6 Report
   sales_data['Technician'] = sales_data['Technician'].str.upper().str.strip()
   type6_data['TechCode'] = type6_data['TechCode'].str.upper().str.strip()
   merged_data = pd.merge(
       sales_data, 
       type6_data, 
       left_on='Technician', 
       right_on='TechCode',
       how='inner'
   )
   ``` 