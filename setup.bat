@echo off
REM CarFinder Setup Script for Windows

echo 🚗 CarFinder Setup Script
echo ========================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error creating virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error installing dependencies
    echo Try running: pip install streamlit pandas sqlalchemy python-dotenv
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️ Please edit .env file with your settings
)

REM Initialize database
echo 🗄️ Setting up database...
python scripts/setup_database.py
if errorlevel 1 (
    echo ❌ Error setting up database
    pause
    exit /b 1
)

REM Ingest sample data
echo 📊 Adding sample vehicle data...
python scripts/ingest_sample_data.py
if errorlevel 1 (
    echo ❌ Error adding sample data
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo    1. Install Ollama from https://ollama.ai
echo    2. Run: ollama pull llama3.1
echo    3. Run: ollama pull nomic-embed-text
echo    4. Start the app: streamlit run app/main.py
echo.
echo 💡 Or run start.bat to launch the app
echo.

REM Create start script
echo @echo off > start.bat
echo call venv\Scripts\activate >> start.bat
echo streamlit run app/main.py >> start.bat

pause