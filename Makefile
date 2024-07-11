run:
	docker-compose up -d

build:
	docker-compose up -d --build

linters:
	black server
	isort --profile black server
	mypy server

build-tests:
	docker-compose -f docker-compose-test.yml up

male tests:
	pytest server/tests/test_flask.py