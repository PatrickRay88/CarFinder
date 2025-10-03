@echo off
REM CarFinder Startup Script

echo 🚗 Starting CarFinder...
echo ========================

REM Activate virtual environment
call venv\Scripts\activate

REM Check if Streamlit is available
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ Streamlit not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Start the application
echo 🌟 Launching CarFinder in your browser...
echo 📍 URL: http://localhost:8501
echo 🛑 Press Ctrl+C to stop the server
echo.

start "" "http://localhost:8501"
venv\Scripts\python.exe -m streamlit run app/main.py --server.address=localhost --server.port=8501

pause