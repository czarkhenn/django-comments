.PHONY: help start stop build test restart makemigrations migrate superuser shell logs clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make start         - Start the application with hot reload"
	@echo "  make stop          - Stop all containers"
	@echo "  make build         - Build Docker images"
	@echo "  make test          - Run test suite"
	@echo "  make restart       - Restart the application"
	@echo "  make makemigrations - Create database migrations"
	@echo "  make migrate       - Apply database migrations"
	@echo "  make superuser     - Create Django superuser"
	@echo "  make shell         - Open Django shell"
	@echo "  make logs          - Show application logs"
	@echo "  make clean         - Clean up containers and volumes"

# Start the application with hot reload
start:
	@echo "Starting Django application with hot reload..."
	@cp .env.example .env 2>/dev/null || true
	@docker-compose up -d --build
	@echo "Application started at http://localhost:8000"

# Stop all containers
stop:
	@echo "Stopping all containers..."
	@docker-compose down

# Build Docker images
build:
	@echo "Building Docker images..."
	@docker-compose build --no-cache

# Run test suite
test:
	@echo "Running test suite..."
	@docker exec django-comments-backend-1 python manage.py test

# Restart the application
restart:
	@echo "Restarting application..."
	@docker-compose restart backend

# Create database migrations
makemigrations:
	@echo "Creating database migrations..."
	@docker exec django-comments-backend-1 python manage.py makemigrations

# Apply database migrations
migrate:
	@echo "Applying database migrations..."
	@docker exec django-comments-backend-1 python manage.py migrate

# Create Django superuser
superuser:
	@echo "Creating Django superuser..."
	@docker exec -it django-comments-backend-1 python manage.py createsuperuser

# Open Django shell
shell:
	@echo "Opening Django shell..."
	@docker exec -it django-comments-backend-1 python manage.py shell

# Show application logs
logs:
	@docker-compose logs -f backend

# Clean up containers and volumes
clean:
	@echo "Cleaning up containers and volumes..."
	@docker-compose down -v
	@docker system prune -f
