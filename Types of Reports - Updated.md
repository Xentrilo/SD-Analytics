# Types of Reports

## Service Data System (SD) Reports

### Sales Journal (SlsJrnl.4P6.Dat.str)
- **Description**: Contains detailed transaction records with fields for date, technician, customer, invoice number, sales amounts, and payment codes
- **Key Fields**: DateRecorded, Technician, CustomerName, InvoiceNumber, MerchandiseSold, PartsSold, SCallSold, LaborSold, ImpliedTax, TotalSale, PayCode, Department, ZipCode
- **Size**: 581KB, 7603 lines
- **Note**: Primary source for accounting reconciliation with detailed payment information
- **Common PayCodes**: 129 (1496 occurrences), 149 (680 occurrences), 151.5 (445 occurrences)
- **Uses**: Financial reconciliation, technician sales performance, payment tracking

### Type6report.csv
- **Description**: Comprehensive service records with extensive customer and service details
- **Key Fields**: InvNmbr, Status, CustomerInfo (NmLst, NmFrst, Address), JobDetails (Type, Make, Model), AppointmentTracking (OriginDate, CompletionDate), PartsInfo, FinancialInfo (TotalMaterialInSale, TotalLaborInSale)
- **Size**: 1.1MB
- **Note**: Contains detailed workflow information including timestamps for job creation and completion
- **Uses**: Job tracking, workflow analysis, parts management, recall identification

### Type7report.csv
- **Description**: Focused on completed jobs with payment information
- **Key Fields**: InvNmbr, Status, ServiceDetails, MerchSold, PartsSold, SCallSold, AddedLaborSold, TotalSale
- **Size**: 189KB, 796 lines
- **Note**: Useful for reconciling completed job payments and service metrics
- **Uses**: Financial tracking, job completion analysis, sales performance

### Type3report.csv
- **Description**: Service job details with parts information
- **Key Fields**: InvNmbr, ShopJob?, CustomerInfo, EquipmentDetails, AppointmentInfo, PartDetails, TotalMaterialInSale, TotalLaborInSale
- **Size**: 391KB, 841 lines
- **Uses**: Parts inventory management, job costing analysis

### Type4report.csv
- **Description**: Service report with different formatting
- **Size**: 144KB, 796 lines
- **Uses**: Alternative view of service data

### FebDepoSummary.pdf
- **Description**: PDF report specifically about deposits for February
- **Size**: 92KB, 453 lines
- **Note**: May contain formatted summary of deposit information
- **Uses**: Monthly financial reconciliation, deposit tracking

### Additional SD Reports
- **InventoryDiscrepancies_CheckDataFeb.csv**: 9.4KB, 285 lines - Inventory reconciliation data
- **FebDataOneStep2.csv** and **febdataOneStep.csv**: 300KB, 2466 lines each - Consolidated data views
- **FullSummaryFeb.pdf**: 156KB, 993 lines - Comprehensive monthly summary
- **TechsReveDataaFeb.csv**: 30KB, 546 lines - Technician revenue data
- **PERCENtageofcompletedataFEB.csv**: 35KB, 652 lines - Completion rate metrics
- **DispatchesPerformanceReportDATATEST.xls**: 80KB, 287 lines - Dispatch performance metrics

## GPS & Technician Tracking Reports

### day_start_end_breakdown_*.csv
- **Description**: Detailed records of technicians' day start and end times, including status changes throughout the day
- **Key Fields**: Technician, Date, Status, StartTime, EndTime, Duration, Address, Coordinates
- **Size**: ~750KB, 6000+ lines for 3 months of data
- **Accuracy**: 99% reliable for time tracking
- **Uses**: Technician time management, day structure analysis, idle time tracking

### drive_detail_breakdown_*.csv
- **Description**: Granular driving data including speeds, distances, and locations
- **Key Fields**: Technician, Date, StartTime, EndTime, Distance, MaxSpeed, AvgSpeed, StartAddress, EndAddress
- **Size**: ~3.5MB per quarter
- **Accuracy**: 90-95% when GPS devices are functioning correctly
- **Uses**: Driving behavior analysis, route efficiency, safety monitoring

### drives_and_stops_*.csv
- **Description**: Comprehensive record of all driving segments and stops made by technicians
- **Key Fields**: Technician, StartTime, EndTime, StopType, Duration, Distance, Location, Address
- **Size**: ~850KB, 7000+ lines for 3 months
- **Accuracy**: 95% for time, lower for distance with problematic GPS devices
- **Uses**: Job matching, route efficiency, work pattern analysis

### day_engine_hours_*.csv
- **Description**: Daily record of total engine running time per technician
- **Key Fields**: Technician, Date, TotalEngineHours, VehicleID
- **Size**: ~20KB, 500+ lines for 3 months
- **Accuracy**: 98% reliable metric
- **Uses**: Vehicle utilization, idle time calculation, mileage validation

### idle_time_*.csv
- **Description**: Records of extended vehicle idling periods
- **Key Fields**: Technician, Date, StartTime, EndTime, Duration, Location
- **Size**: ~70KB, 480+ lines for 3 months
- **Uses**: Fuel efficiency monitoring, environmental compliance, behavior coaching

### alert_summary_*.csv
- **Description**: Summary of driving behavior alerts (speeding, harsh braking, etc.)
- **Key Fields**: Technician, Date, AlertType, Count, Details
- **Size**: Varies based on alert frequency
- **Uses**: Safety monitoring, driver coaching, risk management

### RecallDataKeyword*.csv
- **Description**: Extracted data about recall jobs with associated keywords
- **Key Fields**: InvNmbr, CustomerName, RecallReason, ApplianceType, Technician
- **Size**: ~7KB, ~100 lines for recent data
- **Uses**: Recall pattern analysis, quality control, technician performance with recalls

## Combined & Analysis Files

### Combined_Job_ReferenceTech.csv
- **Description**: Joined dataset combining job information with technician reference data
- **Size**: ~2.4MB
- **Uses**: Cross-referencing jobs with technician performance metrics

### PERCENtageofcompletedata2025.csv
- **Description**: Analysis file showing completion percentages for various metrics
- **Size**: ~92KB, 1700 lines
- **Uses**: Performance monitoring, goal tracking, benchmark comparison 