.PHONY: api-test web-typecheck docker-up docker-down

api-test:
	cd services/api && pytest

web-typecheck:
	cd apps/web && npm run typecheck

docker-up:
	docker compose up --build

docker-down:
	docker compose down

