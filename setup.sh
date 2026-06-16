#!/bin/bash
# Quick start script for Tsaiwimon development

set -e

echo "🚀 Tsaiwimon Development Setup"
echo "================================"

# Check Python
echo "✓ Checking Python..."
python --version

# Check uv
echo "✓ Checking uv..."
uv --version || echo "⚠ uv not found, installing..."

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate || .venv\Scripts\activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -r requirements.txt

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠ Please edit .env with your settings"
fi

# Create logs directory
mkdir -p logs

# Run migrations
echo "🗄️ Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development server:"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Access at: http://localhost:8000"
echo "Admin at: http://localhost:8000/admin"
echo "API Docs at: http://localhost:8000/api/docs/"
