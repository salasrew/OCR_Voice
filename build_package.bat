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

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

echo Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto error

echo Installing runtime and packaging dependencies...
"%VENV_PYTHON%" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto error

echo Building executable...
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --windowed --name OCRVoice --paths src ^
    --hidden-import winrt.windows.foundation ^
    --hidden-import winrt.windows.foundation.collections ^
    --hidden-import winrt.windows.globalization ^
    --hidden-import winrt.windows.graphics.directx ^
    --hidden-import winrt.windows.graphics.imaging ^
    --hidden-import winrt.windows.media.ocr ^
    --hidden-import winrt.windows.storage ^
    --hidden-import winrt.windows.storage.fileproperties ^
    --hidden-import winrt.windows.storage.provider ^
    --hidden-import winrt.windows.storage.search ^
    --hidden-import winrt.windows.storage.streams ^
    --hidden-import winrt.windows.system ^
    src\ocr_voice_cli.py
if errorlevel 1 goto error

if not exist "dist\OCRVoice\config.json" (
    copy "config.example.json" "dist\OCRVoice\config.json" >nul
)

echo.
echo Package created at dist\OCRVoice\OCRVoice.exe
goto end

:error
echo.
echo Package build failed. Check the error message above.
exit /b 1

:end
endlocal
