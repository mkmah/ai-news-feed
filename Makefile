
db-up:
	docker compose -f deploy/compose.yml up -d

create-migration:
	uv run -m alembic revision --autogenerate -m "$(MSG)"

migrate:
	uv run -m alembic upgrade head

.PHONY: db-up create-migration migrate
