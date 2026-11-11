@echo off
TITLE FoxTrader-Pro Algorithmic Trading Platform
echo ==============================================================================
echo                      🦊 FOXTRADER-PRO TERMINAL 🦊
echo          Real-Time Market Scanning & Institutional Smart Money Concepts
echo ==============================================================================
echo.
echo [1/3] Navigating to Dhan Muhurat root directory...
cd /d "%~dp0"

echo [2/3] Launching Dhan Muhurat Server on http://127.0.0.1:8088 ...
echo Press Ctrl+C in this terminal window to stop the server at any time.
echo.
echo [3/3] Opening browser to http://127.0.0.1:8088 after server warmup...
start "" /b cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:8088"

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8088
pause
