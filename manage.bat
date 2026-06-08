@echo off
setlocal

:: ============================================================
:: Self-elevate to Administrator if not already running as one
:: ============================================================
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: ============================================================
:: Change to the directory where this .bat file lives
:: ============================================================
cd /d "%~dp0"

:: ============================================================
:: Check PC name and launch scripts in the appropriate order
:: ============================================================
if /i "%COMPUTERNAME%"=="PXITC006778" (
    echo [%COMPUTERNAME%] Detected target machine. Running SERVER first, then CLIENT.
    echo.

    echo Starting server.py...
    python server.py
    echo server.py finished.
    echo.

    echo Starting client.py...
    python client.py
    echo client.py finished.

) else (
    echo [%COMPUTERNAME%] Not the target machine. Running CLIENT first, then SERVER.
    echo.

    echo Starting client.py...
    python client.py
    echo client.py finished.
    echo.

    echo Starting server.py...
    python server.py
    echo server.py finished.
)

echo.
echo All done.
pause
endlocal