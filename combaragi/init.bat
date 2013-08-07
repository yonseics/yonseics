@echo off
del combaragi_db
del /s /q media\photologue
del /s /q media\uploaded
del /s /q media\portrait
python manage.py syncdb
python manage.py plinit
python manage.py testuser
python manage.py test
python manage.py runserver
