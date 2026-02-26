@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found in PATH. Attempting to install Python 3 via winget...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo winget is not available on this system.
    echo Please install Python 3 manually from https://www.python.org/downloads/ and try again.
    pause
    exit /b 1
  )

  winget install -e --id Python.Python.3 --source winget

  where python >nul 2>nul
  if errorlevel 1 (
    echo Python installation did not complete or PATH was not updated.
    echo Please reopen this window or install Python manually and try again.
    pause
    exit /b 1
  )
)

python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"

python "%~dp0code.py"

endlocal
