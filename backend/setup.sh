#!/bin/bash

echo "========================================="
echo "Linguana Backend Setup Script"
echo "========================================="

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

echo "Running migrations..."
python manage.py migrate

echo "Creating badges..."
python manage.py create_badges

echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Start server: python manage.py runserver"
echo "4. Start Celery worker: celery -A linguana worker -l info"
echo "5. Start Redis: redis-server"
echo ""
