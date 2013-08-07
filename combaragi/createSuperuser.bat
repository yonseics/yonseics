@echo off
set /p str=Username: 
python manage.py createsuperuser --username=%str% --email=admin@example.com