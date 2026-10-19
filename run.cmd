@echo off
setlocal
set "APP=%~dp0app.py"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys, tkinter; assert sys.version_info >= (3, 10)" >nul 2>&1
    if not errorlevel 1 (
        py -3 "%APP%"
        goto :finished
    )
)

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys, tkinter; assert sys.version_info >= (3, 10)" >nul 2>&1
    if not errorlevel 1 (
        python "%APP%"
        goto :finished
    )
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%~fD\python.exe" (
        "%%~fD\python.exe" -c "import sys, tkinter; assert sys.version_info >= (3, 10)" >nul 2>&1
        if not errorlevel 1 (
            "%%~fD\python.exe" "%APP%"
            goto :finished
        )
    )
)

echo Python 3.10 or newer with Tkinter was not found.
echo Install Python from https://www.python.org/downloads/ and try again.
pause
exit /b 1

:finished
if errorlevel 1 pause
