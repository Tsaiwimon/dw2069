@echo off
REM Quick start script for Tsaiwimon development (Windows)

echo 🚀 Tsaiwimon Development Setup
echo ================================

REM Check Python
echo ✓ Checking Python...
python --version

REM Check uv
echo ✓ Checking uv...
uv --version
if errorlevel 1 (
    echo ⚠ uv not found, installing...
)

REM Create virtual environment
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    uv venv
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo 📚 Installing dependencies...
uv pip install -r requirements.txt

REM Create .env file if not exists
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠ Please edit .env with your settings
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Run migrations
echo 🗄️ Running migrations...
python manage.py makemigrations
python manage.py migrate

REM Create superuser
echo 👤 Creating superuser...
python manage.py createsuperuser

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --no-input

echo.
echo ✅ Setup complete!
echo.
echo To start development server:
echo   .venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Access at: http://localhost:8000
echo Admin at: http://localhost:8000/admin
echo API Docs at: http://localhost:8000/api/docs/
