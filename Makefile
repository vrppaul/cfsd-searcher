.PHONY: start
start:
	docker-compose build
	docker-compose up -d

.PHONY: stop
stop:
	docker-compose stop

.PHONY: migrate
migrate:
	docker-compose exec web python manage.py migrate

.PHONY: parse-csfd
parse-csfd:
	docker-compose exec web python manage.py parse_csfd
