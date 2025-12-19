.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser init test clean

help:
	@echo "HRM Application - Available Commands"
	@echo "===================================="
	@echo "make build          - Build Docker images"
	@echo "make up             - Start all services"
	@echo "make down           - Stop all services"
	@echo "make restart        - Restart all services"
	@echo "make logs           - View logs (all services)"
	@echo "make logs-web       - View web service logs"
	@echo "make logs-celery    - View celery worker logs"
	@echo "make shell          - Open Django shell"
	@echo "make bash           - Open bash in web container"
	@echo "make migrate        - Run database migrations"
	@echo "make makemigrations - Create new migrations"
	@echo "make createsuperuser - Create Django superuser"
	@echo "make init           - Initialize HRM system with default data"
	@echo "make collectstatic  - Collect static files"
	@echo "make test           - Run tests"
	@echo "make clean          - Clean up containers and volumes"
	@echo "make ps             - Show running containers"
	@echo "make backup-db      - Backup database"
	@echo "make restore-db     - Restore database from backup"

build:
	docker compose build

up:
	docker compose up -d
	@echo "Services started! Access the app at http://localhost:8000"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-celery:
	docker compose logs -f celery

logs-beat:
	docker compose logs -f celery-beat

shell:
	docker compose exec web python manage.py shell

bash:
	docker compose exec web bash

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

createsuperuser:
	docker compose exec web python manage.py createsuperuser

init:
	docker compose exec web python manage.py init_hrm
	@echo "HRM system initialized with default data!"

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

test:
	docker compose exec web python manage.py test

clean:
	docker compose down -v
	@echo "Cleaned up containers and volumes"

ps:
	docker compose ps

backup-db:
	@echo "Creating database backup..."
	docker compose exec -T db pg_dump -U hrm_user hrm_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created successfully!"

restore-db:
	@echo "Enter backup file name:"
	@read backup_file; \
	docker compose exec -T db psql -U hrm_user hrm_db < $$backup_file
	@echo "Database restored successfully!"

# Development helpers
dev-setup: build up migrate init createsuperuser
	@echo "Development environment setup complete!"

# Production helpers
prod-deploy: build up migrate collectstatic
	@echo "Production deployment complete!"
