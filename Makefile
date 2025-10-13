.PHONY: help dev prod down logs clean test lint fix

help:
	@echo "Available commands:"
	@echo "  make dev              - start development environment"
	@echo "  make prod             - start production environment"
	@echo "  make down             - stop all services"
	@echo "  make logs             - show logs"
	@echo "  make clean            - remove all containers and volumes"
	@echo "  make test             - run all tests"
	@echo "  make lint             - run code linters"
	@echo "  make fix              - auto-fix code style"

dev:
	@echo "Starting development environment..."
	docker compose --env-file .env.dev --profile dev up --build

prod:
	@echo "Starting production environment..."
	docker compose --env-file .env.prod --profile prod up --build

down:
	docker compose --profile dev --profile prod --profile test --profile lint down

logs:
	docker compose logs -f

clean:
	docker compose down -v
	docker system prune -f

test:
	@echo "Running tests..."
	docker compose --env-file .env.dev --profile test up --build --abort-on-container-exit

test-backend:
	docker compose --env-file .env.dev --profile test up backend-test --build --abort-on-container-exit

test-frontend:
	docker compose --env-file .env.dev --profile test up frontend-test --build --abort-on-container-exit

lint:
	@echo "Running linters..."
	docker compose --profile lint up --build --abort-on-container-exit

lint-backend:
	docker compose --profile lint up backend-codecheck --build --abort-on-container-exit

lint-frontend:
	docker compose --profile lint up frontend-codecheck --build --abort-on-container-exit

fix:
	@echo "Auto-fixing code..."
	docker compose --profile fix up --build --abort-on-container-exit

fix-backend:
	docker compose --profile fix up backend-codefix --build --abort-on-container-exit

fix-frontend:
	docker compose --profile fix up frontend-codefix --build --abort-on-container-exit
