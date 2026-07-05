@echo off
echo ============================================
echo   CineGyan - Push to GitHub
echo ============================================
echo.
echo BEFORE running this:
echo 1. Create an empty repo on github.com (do NOT add README/license there)
echo 2. Copy that repo's URL, e.g. https://github.com/yourusername/cinegyan.git
echo.
cd /d "%~dp0"

set /p REPOURL="Paste your GitHub repo URL and press Enter: "

git init
git add app.py requirements.txt README.md .gitignore .streamlit\config.toml
git commit -m "CineGyan - GDG hackathon MVP"
git branch -M main
git remote add origin %REPOURL%
git push -u origin main

echo.
echo ============================================
echo   Done. Check your GitHub repo in the browser.
echo   NOTE: secrets.toml was NOT pushed (correct, by design).
echo ============================================
pause
