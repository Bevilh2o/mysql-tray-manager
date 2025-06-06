@echo off
setlocal enabledelayedexpansion

:: List of required packages
set packages=pyinstaller pystray pillow psutil cryptography

echo Checking required Python packages...

for %%p in (%packages%) do (
    pip show %%p >nul 2>&1
    if !errorlevel! neq 0 (
        echo Installing %%p...
        pip install %%p
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to install %%p
            pause
            exit /b 1
        )
    ) else (
        echo %%p is already installed.
    )
)

echo.
echo Compiling the Python script to EXE...
if not exist mysql_systray.py (
    echo [ERROR] File "mysql_systray.py" not found!
    pause
    exit /b 1
)

pyinstaller --onefile --noconsole mysql_systray.py
if errorlevel 1 (
    echo [ERROR] Compilation failed.
    pause
    exit /b 1
)

echo.
echo Build complete! You can find the EXE in the "dist" folder.
pause
