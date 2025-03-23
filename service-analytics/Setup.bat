@echo off
echo =================================================
echo Service Analytics Dashboard - Automated Setup
echo =================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo NOTICE: This script is not running with administrator privileges.
    echo.
    echo If you are installing in a protected location like Program Files,
    echo you will need to run this script as Administrator.
    echo.
    echo Alternatively, you can install in a user-writable location.
    echo.
    echo Current directory: %CD%
    echo.
    echo Options:
    echo 1) Continue anyway (may fail if write permissions are needed)
    echo 2) Exit and restart as Administrator
    echo 3) Change installation directory to Documents folder
    echo.
    choice /c 123 /n /m "Choose an option (1-3): "
    if %errorlevel% equ 2 goto :EOF
    if %errorlevel% equ 3 (
        set USER_DOCS=%USERPROFILE%\Documents\service-analytics
        echo Creating directory: %USER_DOCS%...
        mkdir "%USER_DOCS%" 2>nul
        echo Copying files to %USER_DOCS%...
        xcopy /E /I /Y "%~dp0*.*" "%USER_DOCS%\"
        echo.
        echo Files copied. Please run Setup.bat from the new location:
        echo %USER_DOCS%\Setup.bat
        echo.
        echo Press any key to exit...
        pause >nul
        goto :EOF
    )
)

REM Set Python command variable
SET PYTHON_CMD=python

REM Check for Python installation (try 'py' first, then 'python')
py --version > nul 2>&1
if %errorlevel% equ 0 (
    SET PYTHON_CMD=py
    goto PYTHON_FOUND
)

python --version > nul 2>&1
if %errorlevel% equ 0 (
    SET PYTHON_CMD=python
    goto PYTHON_FOUND
)

echo ERROR: Python is not installed or not in PATH
echo Please install Python from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo.
echo Press any key to exit...
pause > nul
exit /b 1

:PYTHON_FOUND
echo Python is installed. Checking version...
for /f "tokens=2" %%a in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%a
echo Found Python %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo.
        echo Failed to create virtual environment.
        echo This may be due to permission issues.
        echo.
        echo Please try one of the following:
        echo 1) Run this script as administrator
        echo 2) Move this folder to a location where you have write permissions
        echo    (e.g., your Documents folder)
        echo.
        echo Press any key to exit...
        pause > nul
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    echo Attempting to continue anyway...
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install required packages.
    echo.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
call Create_Desktop_Shortcut.bat

echo.
echo =================================================
echo Setup completed successfully!
echo =================================================
echo.
echo You can now run the Service Analytics Dashboard by:
echo 1. Using the desktop shortcut
echo 2. Double-clicking Launch_Dashboard.bat or Launch_Dashboard_Hidden.vbs
echo.
echo Would you like to launch the dashboard now? (Y/N)
choice /c YN /n
if %errorlevel% equ 1 (
    echo Starting dashboard...
    echo NOTE: If you see "connection refused" in your browser, please wait 
    echo       30 seconds for Streamlit to start up, then refresh the page.
    start "" Launch_Dashboard.bat
)

echo.
echo Press any key to exit...
pause > nul 