@echo off
TITLE FoxTrader-Pro Algorithmic Trading Platform
echo ==============================================================================
echo                      🦊 FOXTRADER-PRO TERMINAL 🦊
echo          Real-Time Market Scanning & Institutional Smart Money Concepts
echo ==============================================================================
echo.
echo [1/3] Navigating to backend directory...
cd /d "%~dp0backend"

echo [2/3] Launching FoxTrader-Pro Server on http://127.0.0.1:8088 ...
echo Press Ctrl+C in this terminal window to stop the server at any time.
echo.
echo Opening browser to http://127.0.0.1:8088 in 3 seconds...
start "" timeout /t 3 /nobreak >nul & start http://127.0.0.1:8088

python -m uvicorn main:app --host 127.0.0.1 --port 8088 --reload
pause
