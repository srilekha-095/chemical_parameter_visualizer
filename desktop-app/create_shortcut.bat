@echo off
REM Create a shortcut to run_app.bat on the Desktop
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\Chemical Equipment Visualizer.lnk'); $Shortcut.TargetPath = '%cd%\run_app.bat'; $Shortcut.IconLocation = '%cd%\chem-visualizer-logo.ico'; $Shortcut.Save()"
echo Shortcut created successfully on your Desktop!
pause
