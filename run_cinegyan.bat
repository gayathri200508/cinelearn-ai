@echo off
echo ============================================
echo   CineGyan - Setup and Run
echo ============================================
echo.

REM Go to the folder this script is in
cd /d "%~dp0"

echo Step 1: Installing required packages...
pip install streamlit google-genai
echo.

REM Create .streamlit folder if it doesn't exist
if not exist ".streamlit" (
    mkdir ".streamlit"
)

REM Ask for API key only if secrets.toml doesn't already exist
if not exist ".streamlit\secrets.toml" (
    echo Step 2: Setting up your Gemini API key
    echo Get a free key from: https://aistudio.google.com/apikey
    echo.
    set /p APIKEY="Paste your Gemini API key here and press Enter: "
    echo GEMINI_API_KEY = "%APIKEY%" > ".streamlit\secrets.toml"
    echo.
    echo Key saved.
) else (
    echo Step 2: secrets.toml already exists, skipping key setup.
)

echo.
echo Step 3: Launching CineGyan...
echo (Your browser will open automatically at http://localhost:8501)
echo.
streamlit run app.py

pause
