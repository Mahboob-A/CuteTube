
#### Docker management commands 

docker-up:
	docker compose -p cutetube -f production.yml up --build -d --remove-orphans 

docker-down:
	docker compose -p cutetube -f production.yml down

docker-down-v:
	docker compose -p cutetube -f production.yml down -v

docker-logs:
	docker compose -p cutetube -f production.yml logs 

docker-logs-cutetube-api:
	docker compose -p cutetube -f production.yml logs cutetube-api 

docker-restart-cutetube-api:
	docker compose -p cutetube -f production.yml restart cutetube-api 

docker-exec-cutetube-api:
	docker compose -p cutetube -f production.yml exec cutetube-api /bin/bash 

docker-check-deploy:
	docker compose -p cutetube -f production.yml run --rm cutetube-api python manage.py check --deploy


# ### Docker Volume and Postgres Database 

docker-exec-postgres: 
	docker compose -p cutetube -f production.yml exec postgres /bin/bash 

algocode-database: 
	docker compose -p cutetube -f production.yml exec postgres psql --username="$(POSTGRES_USER)" --dbname="$(POSTGRES_DB)" 





# ### Services logs commands 

docker-logs-celery:
	docker compose -p cutetube -f production.yml logs cutetube-celery-worker

docker-logs-redis:
	docker compose -p cutetube -f production.yml logs cutetube-redis

docker-logs-flower:
	docker compose -p cutetube -f production.yml logs flower

docker-logs-postgres: 
	docker compose -p cutetube -f production.yml logs postgres



# docker compose -p d_v -f dev.yml up --build -d --remove-orphans

# docker compose -p d_v -f dev.yml down -v

# ### Django Commands

makemigrations: 
	docker compose -p cutetube -f production.yml run --rm cutetube-api python manage.py makemigrations

migrate: 
	docker compose -p cutetube -f production.yml run --rm cutetube-api python manage.py migrate

collectstatic: 
	docker compose -p cutetube -f production.yml run --rm cutetube-api python manage.py collectstatic --no-input --clear 

superuser: 
	docker compose -p cutetube -f production.yml run --rm cutetube-api python manage.py createsuperuser 

