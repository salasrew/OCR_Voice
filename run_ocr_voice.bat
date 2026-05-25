@echo off
setlocal

cd /d "%~dp0"

set "VENV_DIR=.venv-win"
set "PYTHON_CMD=py -3"
where py >nul 2>nul
if errorlevel 1 (
    set "PYTHON_CMD=C:\Users\Salasrew\AppData\Local\Programs\Python\Python312\python.exe"
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 goto error
)

if exist "%VENV_DIR%\Scripts\python.exe" (
    set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
) else (
    echo Could not find the virtual environment Python executable.
    goto error
)

echo Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto error

echo Installing dependencies...
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto error

if not exist "config.json" (
    echo Creating config.json from config.example.json...
    copy "config.example.json" "config.json" >nul
    if errorlevel 1 goto error
)

echo Starting OCR Voice...
set PYTHONPATH=src
"%VENV_PYTHON%" -m ocr_voice --config config.json
if errorlevel 1 goto error

goto end

:error
echo.
echo OCR Voice failed to start. Check the error message above.
pause
exit /b 1

:end
endlocal
