@echo off
title Safe Media Downloader - Pro Edition
echo =======================================================
echo          Safe Media Downloader Launcher
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
