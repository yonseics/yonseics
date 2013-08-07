@echo off
setlocal
set /p str=생성하려고 하는 모듈 이름을 입력하세요:
python manage.py startapp %str%
echo 모듈 %str% 이 생성되었습니다.
pause