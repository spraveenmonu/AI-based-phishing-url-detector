@echo off
echo Adding AI Phishing Detector to Windows Startup...
set "VBS_PATH=%~dp0run_hidden.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\AI_Phishing_Detector_Background.lnk"

rem Create a shortcut via PowerShell
powershell -Command "$wshell = New-Object -ComObject WScript.Shell; $shortcut = $wshell.CreateShortcut('%SHORTCUT_PATH%'); $shortcut.TargetPath = 'wscript.exe'; $shortcut.Arguments = '\"%VBS_PATH%\"'; $shortcut.WorkingDirectory = '%~dp0'; $shortcut.WindowStyle = 1; $shortcut.Save()"

echo Done! The backend will now automatically start hidden in the background every time you turn on your computer.
echo You can now just open the website normally without running python run.py!
pause
