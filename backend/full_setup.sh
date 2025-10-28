#!/bin/bash

echo "========================================="
echo "Linguana Backend - Complete Setup"
echo "========================================="
echo ""

echo "Step 1: Creating virtual environment..."
python3 -m venv venv

echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo "Step 3: Upgrading pip..."
pip install --upgrade pip

echo "Step 4: Installing Python dependencies..."
pip install -r requirements.txt

echo "Step 5: Creating .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created from template"
else
    echo ".env file already exists"
fi

echo "Step 6: Running database migrations..."
python manage.py migrate

echo "Step 7: Creating initial badges..."
python manage.py create_badges

echo "Step 8: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Start Redis: sudo service redis-server start"
echo "3. Start Celery worker: celery -A linguana worker -l info"
echo "4. Start Django server: python manage.py runserver"
echo ""
echo "To activate virtual environment in future:"
echo "source venv/bin/activate"
echo ""
