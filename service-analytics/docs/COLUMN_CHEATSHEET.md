# Column Mapping Cheat Sheet

## Technician Identifiers
| Purpose | Sales Journal | Type6 Report | GPS Files |
|---------|---------------|--------------|-----------|
| Technician ID | `Technician` | `TechCode` | `Device` |
| Format | 2-letter initials | 2-letter initials | Full name |

## Job Identifiers
| Purpose | Sales Journal | Type6 Report |
|---------|---------------|--------------|
| Job/Invoice ID | `InvoiceNumber` | `JobNumber` |
| Customer Name | `CustomerName` | `NmLst`, `NmFrst` |

## Date Fields
| Purpose | Sales Journal | Type6 Report | GPS Files |
|---------|---------------|--------------|-----------|
| Job Created | N/A | `OriginDate` | N/A |
| Service Date | `DateRecorded` | `FirstAppmnt` | `Date` |
| Completion Date | N/A | `CmpltnDate` | N/A |

## Financial Data
| Purpose | Sales Journal | Internal Naming |
|---------|---------------|-----------------|
| Labor Amount | `LaborSold` | `TotalLabor` |
| Parts Amount | `PartsSold` | `TotalParts` |
| Service Call Fee | `SCallSold` | `TotalServiceCalls` |
| Merchandise | `MerchandiseSold` | N/A |
| Total Amount | `TotalSale` | `TotalRevenue` |

## Status Information
| Purpose | Sales Journal | Type6 Report |
|---------|---------------|--------------|
| Job Status | N/A | `Status` |
| Cancellation | N/A | `JobCanceled` |
| First Trip Complete | N/A | `CompletedOnFirstTrip` |

## GPS Data Types
| Data Type | File | Key Columns |
|-----------|------|-------------|
| Daily Schedule | day_start_end_*.csv | `Device`, `Date`, `Start Time`, `End Time` |
| Driving Activity | drives_stops_*.csv | `Device`, `Status`, `Start Time`, `End Time`, `Length (mi)` |
| Driver Alerts | alert_summary_*.csv | `Device`, `AlertType`, `Date & Time` |
| Idle Time | idle_time_*.csv | `Device`, `Start Time`, `End Time`, `Duration` |

## Common Gotchas
- The Type6 report uses latin1 encoding, not utf-8
- Some date fields in GPS data have timezone issues with PST/PDT
- TechCode can sometimes be a mix of strings and floats
- Always check for NaN values in key joining fields

## Recommended Preprocessing
```python
# 1. Convert tech identifiers to strings
df['TechCode'] = df['TechCode'].astype(str).str.strip()
df['Technician'] = df['Technician'].astype(str).str.strip()

# 2. Standardize case for technician IDs
df['TechCode'] = df['TechCode'].str.upper()
df['Technician'] = df['Technician'].str.upper()

# 3. Handle NaN values
df['TechCode'] = df['TechCode'].replace('nan', '')
df['TechCode'] = df['TechCode'].replace('NaN', '')

# 4. Convert date fields
df['DateRecorded'] = pd.to_datetime(df['DateRecorded'], errors='coerce')
``` 