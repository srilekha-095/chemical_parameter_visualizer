# Create a shortcut to run_app.bat on the Desktop
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "Chemical Equipment Visualizer.lnk"
$IconPath = Join-Path $ScriptDir "chem-visualizer-logo.ico"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $ScriptDir "run_app.bat"
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "Chemical Parameter Visualizer"
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()

Write-Host "Shortcut created successfully at: $ShortcutPath" -ForegroundColor Green
Write-Host "Icon: $IconPath" -ForegroundColor Green
