# Service Analytics Troubleshooting Guide

## Common Error Messages and Fixes

### TypeError: '<' not supported between instances of 'str' and 'float'

This error occurs when trying to sort or compare a mixture of string and numeric values.

**Cause**: The `TechCode` or `Technician` column contains both string and numeric values.

**Solution**:
1. Convert all values to strings before sorting:
   ```python
   df['TechCode'] = df['TechCode'].astype(str)
   tech_list = sorted(df['TechCode'].unique().tolist())
   ```

2. Or use a try/except to handle sorting errors:
   ```python
   try:
       tech_list = sorted(techs)
   except TypeError:
       tech_list = techs  # unsorted
   ```

### ValueError: Missing required columns: ['TotalMaterialInSale']

This error occurs when the metrics calculation functions can't find expected columns.

**Cause**: The data format doesn't match what the functions expect.

**Solution**:
1. Update the `calculate_tech_revenue_metrics` function to detect and support both formats:
   ```python
   if 'TotalMaterialInSale' not in df.columns and 'PartsSold' in df.columns:
       df['TotalMaterialInSale'] = df['PartsSold']
   ```

2. Or create separate functions for different data formats:
   ```python
   if all(col in df.columns for col in ['PartsSold', 'LaborSold']):
       return calculate_tech_revenue_metrics_real(df)
   else:
       return calculate_tech_revenue_metrics_demo(df)
   ```

### KeyError: 'TechCode'

This error occurs during merging operations when the joining column doesn't exist.

**Cause**: Trying to merge dataframes using columns that don't exist in one or both frames.

**Solution**:
1. Ensure both dataframes have the joining column:
   ```python
   if 'Technician' in df.columns and 'TechCode' not in df.columns:
       df['TechCode'] = df['Technician']
   ```

2. Check for column existence before merging:
   ```python
   if 'TechCode' in df1.columns and 'TechCode' in df2.columns:
       merged = pd.merge(df1, df2, on='TechCode')
   else:
       print("Cannot merge - missing TechCode column")
   ```

### 'utf-8' codec can't decode byte 0x92

This error occurs when trying to read a file with an incompatible encoding.

**Cause**: The Type6 report uses latin1 encoding, not utf-8.

**Solution**:
1. Try multiple encodings when reading files:
   ```python
   encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
   for encoding in encodings:
       try:
           df = pd.read_csv(filepath, encoding=encoding)
           break
       except:
           continue
   ```

### FutureWarning: Parsed string with unrecognized timezone

This warning appears when parsing dates with non-standard timezone abbreviations.

**Cause**: GPS data uses "PST" timezone abbreviation which isn't in the standard set.

**Solution**:
1. Strip timezone info before parsing:
   ```python
   # Remove timezone abbreviations
   df['datetime'] = df['datetime'].str.replace(' PST', '').str.replace(' PDT', '')
   # Then parse
   df['datetime'] = pd.to_datetime(df['datetime'])
   ```

2. Or keep but ignore the warning:
   ```python
   import warnings
   warnings.filterwarnings('ignore', message='Parsed string .* included an un-recognized timezone')
   ```

## Data Loading Issues

### No data loaded or empty dataframes

**Cause 1**: File paths are incorrect.

**Solution**: Check that all required files exist in the data directory:
```python
import os
data_dir = 'data'
required_files = ['Type6report2025.csv', 'SlsJrnl.csv']
for file in required_files:
    if not os.path.exists(os.path.join(data_dir, file)):
        print(f"Missing file: {file}")
```

**Cause 2**: File format is incorrect.

**Solution**: Verify file formats and convert if needed:
```
python prepare_data.py verify data/Type6report2025.csv --type type6
python prepare_data.py convert data/SlsJrnl.4P6.Dat.str --output data/SlsJrnl.csv
```

## Dashboard Display Issues

### No data shows up in dashboard

**Cause 1**: Date range filter doesn't include any data.

**Solution**: Check the date ranges in your data and adjust the default filter:
```python
# Determine min/max dates in data
min_date = pd.to_datetime(df['DateRecorded']).min().date()
max_date = pd.to_datetime(df['DateRecorded']).max().date()

# Use as defaults in filter
start_date = st.sidebar.date_input("Start Date", value=min_date)
end_date = st.sidebar.date_input("End Date", value=max_date)
```

**Cause 2**: Technician selection is empty.

**Solution**: Ensure at least one technician is selected:
```python
if not selected_techs:
    st.warning("Please select at least one technician")
```

### Incorrect metrics or weird values

**Cause**: Data type conversion issues.

**Solution**: Ensure proper data type conversion for numeric columns:
```python
for col in ['LaborSold', 'PartsSold', 'SCallSold', 'TotalSale']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
```

## Last Resort

If all else fails, you can reset the environment:

1. Delete the virtual environment (.venv folder)
2. Recreate it with: `python -m venv .venv`
3. Reinstall requirements: `pip install -r requirements.txt`
4. Run the test_imports.py script to check the environment is working
5. Start Streamlit with: `streamlit run app.py` 