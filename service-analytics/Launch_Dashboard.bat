@echo off
echo =================================================
echo Starting Service Analytics Dashboard...
echo =================================================
echo.

REM Change to the app directory
cd /d "%~dp0"

REM Set Python command variable (try py first, then python)
SET PYTHON_CMD=python
py --version > nul 2>&1
if %errorlevel% equ 0 (
    SET PYTHON_CMD=py
) else (
    python --version > nul 2>&1
    if %errorlevel% equ 0 (
        SET PYTHON_CMD=python
    ) else (
        echo ERROR: Python is not installed or not in PATH.
        echo Please run Setup.bat first to configure the environment.
        pause
        exit /b 1
    )
)

REM Check if a virtual environment exists in common locations
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment from .venv folder...
    call .venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo WARNING: Failed to activate virtual environment.
        echo This may be due to permissions or path issues.
        echo Attempting to continue anyway...
    )
) else if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment from venv folder...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo WARNING: Failed to activate virtual environment.
        echo Attempting to continue anyway...
    )
) else if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment from env folder...
    call env\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo WARNING: Failed to activate virtual environment.
        echo Attempting to continue anyway...
    )
) else (
    echo No virtual environment found.
    echo NOTE: This may cause issues if Streamlit is not installed globally.
    echo Attempting to run with system Python...
)

echo.
echo Checking for Streamlit installation...
%PYTHON_CMD% -m pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Streamlit is not installed.
    echo Please run Setup.bat to install required packages.
    echo.
    echo Attempting to install Streamlit now...
    %PYTHON_CMD% -m pip install streamlit
    if %errorlevel% neq 0 (
        echo Failed to install Streamlit.
        echo Please run Setup.bat to properly configure the environment.
        pause
        exit /b 1
    )
    echo Streamlit installed successfully.
) else (
    echo Streamlit is installed.
)

echo.
echo Starting Streamlit server...
echo NOTE: Server may take up to 30 seconds to start.
echo If you see "connection refused" in your browser, please wait and refresh.
echo.

REM Start browser with a delay to give Streamlit time to start
start "" cmd /c "ping 127.0.0.1 -n 6 > nul && start http://localhost:8503"

REM Run the Streamlit app
echo Running: %PYTHON_CMD% -m streamlit run app.py
%PYTHON_CMD% -m streamlit run app.py

REM This pause is only reached if Streamlit exits
echo.
echo Streamlit server has stopped.
pause 