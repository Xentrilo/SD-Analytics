# PowerShell script to run the Streamlit application
# Run this script to start the Service Analytics Dashboard

# Change to the service-analytics directory
Set-Location -Path "service-analytics"

# Run the Streamlit application
& streamlit run app.py

# Note: In PowerShell, use semicolons (;) to separate commands, not ampersands (&&)
# This script can be executed with: .\run.ps1 