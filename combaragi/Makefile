all: makeExecutable usage

makeExecutable:
	chmod a+x manage.py
	@echo "\r\nmanage.py파일이 실행가능하게 변경되었습니다."

server: makeExecutable
	./manage.py runserver

db: makeExecutable
	./manage.py syncdb

admin: makeExecutable
	./manage.py createsuperuser --username=admin --email=admin@example.com

plinit: makeExecutable
	./manage.py plinit

testuser: makeExecutable
	./manage.py testuser

test: makeExecutable
	./manage.py test

deletedb:
	rm -f ./combaragi_db

deletePhoto:
	rm -rf ./media/photologue/

deleteUpload:
	rm -rf ./media/uploaded/

deletePortrait:
	rm -rf ./media/portrait/

init: makeExecutable deletedb deletePhoto deleteUpload deletePortrait db plinit testuser test server

usage:
	@echo "---------------make 사용 설명-----------------\r\n\
	# make server: server를 실행합니다.\r\n\
	# make db: db를 모델과 동기화 시킵니다.\r\n\
	# make admin: admin계정을 만듭니다.\r\n\
	# make testuser: 테스트 유저를 만듭니다.\r\n\
	# make plinit: photologue를 초기화합니다.\r\n\
	# make test: 모듈들을 테스트합니다.\r\n\
	# make init: 초기 셋팅을 진행합니다..\r\n\
	----------------------------------------------\r\n\
	"


