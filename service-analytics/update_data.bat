@echo off
echo Updating service analytics data...

REM Set paths
set DOWNLOAD_DIR=C:\Path\To\Downloads
set APP_DATA_DIR=C:\Projects and Programs\Analytic Reports\service-analytics\data

REM Create archive directory if it doesn't exist
set ARCHIVE_DIR=%APP_DATA_DIR%\archive\%date:~10,4%-%date:~4,2%
if not exist "%ARCHIVE_DIR%" mkdir "%ARCHIVE_DIR%"

REM Archive current files if they exist
if exist "%APP_DATA_DIR%\Type6report*.csv" copy "%APP_DATA_DIR%\Type6report*.csv" "%ARCHIVE_DIR%\"
if exist "%APP_DATA_DIR%\SlsJrnl*.csv" copy "%APP_DATA_DIR%\SlsJrnl*.csv" "%ARCHIVE_DIR%\"
if exist "%APP_DATA_DIR%\*_breakdown_*.csv" copy "%APP_DATA_DIR%\*_breakdown_*.csv" "%ARCHIVE_DIR%\"
if exist "%APP_DATA_DIR%\drives_and_stops_*.csv" copy "%APP_DATA_DIR%\drives_and_stops_*.csv" "%ARCHIVE_DIR%\"
if exist "%APP_DATA_DIR%\day_engine_*.csv" copy "%APP_DATA_DIR%\day_engine_*.csv" "%ARCHIVE_DIR%\"
if exist "%APP_DATA_DIR%\idle_time_*.csv" copy "%APP_DATA_DIR%\idle_time_*.csv" "%ARCHIVE_DIR%\"
if exist "%APP_DATA_DIR%\alert_summary_*.csv" copy "%APP_DATA_DIR%\alert_summary_*.csv" "%ARCHIVE_DIR%\"

REM Copy newest files
copy "%DOWNLOAD_DIR%\Type6report*.csv" "%APP_DATA_DIR%\"
copy "%DOWNLOAD_DIR%\SlsJrnl*.csv" "%APP_DATA_DIR%\"
copy "%DOWNLOAD_DIR%\*_breakdown_*.csv" "%APP_DATA_DIR%\"
copy "%DOWNLOAD_DIR%\drives_and_stops_*.csv" "%APP_DATA_DIR%\"
copy "%DOWNLOAD_DIR%\day_engine_*.csv" "%APP_DATA_DIR%\"
copy "%DOWNLOAD_DIR%\idle_time_*.csv" "%APP_DATA_DIR%\"
copy "%DOWNLOAD_DIR%\alert_summary_*.csv" "%APP_DATA_DIR%\"

echo Data update complete.
echo Files archived to: %ARCHIVE_DIR%
echo.
echo Remember to modify DOWNLOAD_DIR in this script to match your download folder.
pause 