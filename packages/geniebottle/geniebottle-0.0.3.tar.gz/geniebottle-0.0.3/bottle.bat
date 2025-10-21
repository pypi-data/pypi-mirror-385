@echo off
REM Genie Bottle CLI wrapper for Windows

REM Find Python command
set PYTHON_CMD=
for %%P in (python3.exe python.exe py.exe) do (
    where %%P >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set PYTHON_CMD=%%P
        goto :found
    )
)

:found
if "%PYTHON_CMD%"=="" (
    echo Error: Python 3.7+ is required but not found.
    echo.
    echo Please install Python 3.7 or higher and try again.
    echo Run 'bottle install' after installing Python for setup instructions.
    exit /b 1
)

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Run the Python script
"%PYTHON_CMD%" "%SCRIPT_DIR%bottle.py" %*
