.PHONY: api-test api-migrate web-typecheck docker-up docker-down

api-test:
	cd services/api && pytest

api-migrate:
	cd services/api && alembic upgrade head

web-typecheck:
	cd apps/web && npm run typecheck

docker-up:
	docker compose up --build

docker-down:
	docker compose down
