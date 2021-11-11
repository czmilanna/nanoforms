.PHONY: deploy destroy

deploy:
	docker-compose -f docker-compose.yml --env-file docker-compose.env -p nanoforms up --build -d --remove-orphans

destroy:
	docker-compose -f docker-compose.yml --env-file docker-compose.env -p nanoforms down -v

create_super_user:
	docker-compose exec app python manage.py createsuperuser
