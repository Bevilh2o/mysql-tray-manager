
# MySQL Tray Manager

## Description

This project provides a simple **system tray icon manager** for MySQL on Windows. It allows you to **start**, **stop**, and monitor the MySQL service status through a tray icon.  
The script controls the MySQL daemon (`mysqld.exe`) startup and shutdown via `mysqladmin`, either without a password or using a login file (`mylogin.cnf`).

The tray icon color indicates the service status:  
- **Gray**: MySQL is not running  
- **Green**: MySQL is running  
- **Red**: MySQL has been stopped  

If the shutdown process fails, an error message will be displayed.

---

## How to Use

1. Place the compiled executable `mysql_systray.exe` in the **same folder** as the MySQL binaries (`mysqld.exe`, `mysqladmin.exe`) and optionally the `mylogin.cnf` file containing login credentials.

2. Run `mysql_systray.exe`. The tray icon will appear, allowing you to manage the MySQL server.

---

## Building the Executable (.exe)

To simplify deployment, a batch file `build.bat` is included. This script:

- Installs the required Python packages (`pyinstaller`, `pystray`, `pillow`, `psutil`, `cryptography`)
- Compiles the Python script `mysql_systray.py` into a single console-less executable `.exe`

### Contents of `build.bat`

```@echo off
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
```

### Usage

- Place `build.bat` and `mysql_systray.py` in the same folder.
- Run `build.bat`.
- The executable `mysql_systray.exe` will be created inside the `dist` subfolder.
- Copy the executable to your MySQL binaries folder to use it.

---

## Requirements

- Python 3.x installed on your system  
- MySQL binaries (`mysqld.exe`, `mysqladmin.exe`)  
- (Optional) `mylogin.cnf` file with your MySQL login credentials for secure shutdown

---

## Notes

This program works only on Windows and expects MySQL executables to be in the same directory as the tray manager executable.  
If MySQL requires a password for shutdown, ensure you have a properly configured `mylogin.cnf` file to avoid errors.

---
