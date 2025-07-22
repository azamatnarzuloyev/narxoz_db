.PHONY: help setup up down build logs shell migrate createsuperuser test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup the project (build, migrate, create superuser, seed data)
	@echo "Setting up the project..."
	docker-compose build
	docker-compose up -d db redis
	@echo "Waiting for database to be ready..."
	sleep 10
	docker-compose run --rm web python manage.py migrate
	docker-compose run --rm web python scripts/create_superuser.py
	@echo "Setup complete! You can now run 'make up' to start the services."

up: ## Start all services
	docker-compose up -d
	@echo "Services started! Access the application at:"
	@echo "  - API: http://localhost/api/v1/"
	@echo "  - Admin: http://localhost/admin/"
	@echo "  - API Docs: http://localhost/api/docs/"

down: ## Stop all services
	docker-compose down

build: ## Build the Docker images
	docker-compose build

logs: ## Show logs from all services
	docker-compose logs -f

logs-web: ## Show logs from web service only
	docker-compose logs -f web

logs-db: ## Show logs from database service only
	docker-compose logs -f db

shell: ## Access Django shell
	docker-compose exec web python manage.py shell

bash: ## Access container bash
	docker-compose exec web bash

migrate: ## Run database migrations
	docker-compose exec web python manage.py migrate

makemigrations: ## Create new migrations
	docker-compose exec web python manage.py makemigrations

createsuperuser: ## Create a superuser
	docker-compose exec web python manage.py createsuperuser

collectstatic: ## Collect static files
	docker-compose exec web python manage.py collectstatic --noinput

test: ## Run tests
	docker-compose exec web python manage.py test

seed: ## Seed the database with sample data
	docker-compose exec db psql -U postgres -d attendance_db -f /app/scripts/seed_data.sql

backup-db: ## Backup database
	docker-compose exec db pg_dump -U postgres attendance_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database (usage: make restore-db FILE=backup.sql)
	docker-compose exec -T db psql -U postgres attendance_db < $(FILE)

clean: ## Clean up containers, volumes, and images
	docker-compose down -v
	docker system prune -f

restart: ## Restart all services
	docker-compose restart

restart-web: ## Restart web service only
	docker-compose restart web

status: ## Show status of all services
	docker-compose ps

dev-setup: ## Setup for development (without Docker)
	python -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	python manage.py migrate
	python scripts/create_superuser.py

dev-run: ## Run development server (without Docker)
	python manage.py runserver 0.0.0.0:8000

install-deps: ## Install Python dependencies
	pip install -r requirements.txt

update-deps: ## Update requirements.txt
	pip freeze > requirements.txt

check: ## Run Django system checks
	docker-compose exec web python manage.py check

format: ## Format code with black
	black .

lint: ## Lint code with flake8
	flake8 .

security-check: ## Run security checks
	docker-compose exec web python manage.py check --deploy

performance-test: ## Run performance tests
	docker-compose exec web python manage.py test --keepdb --parallel

coverage: ## Run tests with coverage
	docker-compose exec web coverage run --source='.' manage.py test
	docker-compose exec web coverage report
	docker-compose exec web coverage html
