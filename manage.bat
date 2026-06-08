@echo off
:: Check if the script is already running with administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Reset the working directory to the folder where this batch script is located
cd /d "%~dp0"

set "TARGET_PC=PXITC006778"

:: Case-insensitive comparison of the computer name
if /i "%COMPUTERNAME%"=="%TARGET_PC%" (
    echo Local PC matches %TARGET_PC%.
    echo Launching server.py with admin privileges...
    python server.py
    
    echo server.py has finished. Launching client.py with admin privileges...
    python client.py
) else (
    echo Local PC is %COMPUTERNAME% (does not match %TARGET_PC%).
    echo Launching client.py with admin privileges...
    python client.py
    
    echo client.py has finished. Launching server.py with admin privileges...
    python server.py
)

pause