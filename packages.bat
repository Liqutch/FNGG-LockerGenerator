@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo Python is not installed. Installing Python...
  REM Download and install Python from official website
  powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe' -OutFile 'python-installer.exe'}"
  python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
)

echo Installing Python packages...
py -3 -m pip install -U -r requirements.txt
echo.
echo Python packages installation complete.
pause