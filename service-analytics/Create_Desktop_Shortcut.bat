@echo off
echo Creating Desktop Shortcut for Service Analytics Dashboard...

REM Get the current directory where the batch file is located
set APP_DIR=%~dp0
set APP_PATH=%APP_DIR%Launch_Dashboard_Hidden.vbs
set SHORTCUT_NAME=Service Analytics Dashboard.lnk

REM Create the desktop shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%APP_PATH%'; $Shortcut.IconLocation = 'C:\Windows\System32\imageres.dll,108'; $Shortcut.Description = 'Launch Service Analytics Dashboard'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Save()"

echo.
echo Desktop shortcut created successfully!
echo.
echo You can now launch the dashboard by double-clicking the shortcut on your desktop.
echo.
pause 