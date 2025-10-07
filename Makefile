.PHONY: dev prod down test logs

dev:
	@echo "Starting development environment..."
	docker-compose --env-file .env.development up --build

prod:
	@echo "Starting production environment..."
	docker-compose --env-file .env.production up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

test-backend:
	docker-compose run backend python manage.py test

test-frontend:
	docker-compose run frontend npm test

test: test-backend test-frontend