@echo off
title InstaSafe UZ - Server
cd /d "%~dp0"
echo ==================================================
echo    InstaSafe UZ - Instagram Safety Scanner
echo ==================================================
echo Starting local web server...
echo Open your browser at: http://localhost:8000
echo.
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
