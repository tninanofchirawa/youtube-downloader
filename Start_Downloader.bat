@echo off
title Downloader 1.0 - Fast ^& Safe Media Downloader
echo =======================================================
echo                 Downloader 1.0
echo =======================================================
echo.
echo Starting application in safe mode...
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred. Please ensure Python is installed.
    echo You can install requirements using: pip install -r requirements.txt
    pause
)
