.PHONY: api-test api-migrate api-bootstrap-admin web-typecheck verify docker-up docker-down

api-test:
	cd services/api && pytest

api-migrate:
	cd services/api && alembic upgrade head

api-bootstrap-admin:
	cd services/api && bootstrap-admin

web-typecheck:
	cd apps/web && npm run typecheck

verify: api-test web-typecheck

docker-up:
	docker compose up --build

docker-down:
	docker compose down
