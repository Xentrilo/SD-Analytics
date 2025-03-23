# Service Analytics Dashboard - Installation Guide

This guide will help you set up the Service Analytics Dashboard on a new computer.

## Important Prerequisites

Before installing, please note:
- **Admin Rights**: If installing in a protected folder (like Program Files), you'll need administrator rights
- **Installation Location**: Choose a location where you have write permissions
- **Connectivity**: The dashboard runs a local web server that should not be blocked by firewalls

## Option 1: Simple Installation (Recommended)

### Step 1: Install Python
1. Download and install Python from [python.org](https://www.python.org/downloads/)
   - **Important**: During installation, check "Add Python to PATH"
   - Choose Python 3.9 or newer

### Step 2: Choose an Installation Location
1. **User Documents (Recommended)**:
   - Copy the `service-analytics` folder to `C:\Users\[username]\Documents\`
   - This location avoids permission issues

2. **Program Files (Requires Admin)**:
   - Only choose this if you have administrator rights
   - Copy to `C:\Program Files\service-analytics`

### Step 3: Run Setup
1. Double-click on `Setup.bat` in the service-analytics folder
2. Follow the prompts:
   - If you get permission errors, choose option 3 to move files to Documents
   - The setup will create a virtual environment and install required packages
   - A desktop shortcut will be created automatically

## Troubleshooting Installation Issues

### "Access Denied" Error
- **Cause**: Trying to write to a protected folder without admin rights
- **Solution**: 
  1. Run Setup.bat as Administrator (right-click → Run as Administrator), OR
  2. Choose option 3 when prompted to move to Documents folder

### "Python not found" Error
- **Cause**: Python isn't installed or not in the PATH
- **Solution**: Install Python and make sure to check "Add Python to PATH"

### "Connection Refused" in Browser
- **Cause**: Streamlit server hasn't fully started yet
- **Solution**: 
  1. Wait 30 seconds for the server to start
  2. Refresh the browser page
  3. Check that the console window is still running

### Black Console Window with No Output
- **Cause**: Virtual environment path issue
- **Solution**: Use the `Launch_Dashboard.bat` file instead of the hidden launcher

## Using the Dashboard

1. Double-click the desktop shortcut created during installation
2. The dashboard will start and open automatically in your default web browser
3. If the dashboard doesn't open automatically, open a browser and go to: http://localhost:8503
4. **Important**: The first startup may take 15-30 seconds - be patient and refresh if needed

## Data Updates

To update data in the dashboard:

1. Place new data files in the `data` folder
2. Restart the dashboard by closing and reopening it

For automated updates, see the README.md file. 