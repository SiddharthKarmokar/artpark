.PHONY: run test build docs docs-serve clean

run:
	@echo "Starting local environment..."
	./deploy.sh localhost

stop:
	@echo "Stopping local environment..."
	docker compose -f docker-compose.local.yml down

test:
	@echo "Running tests..."
	uv pip install --system -r app/pyproject.toml[dev]
	pytest app/tests/ -v

lint:
	@echo "Running linter..."
	ruff check app/
	mypy app/

build:
	@echo "Building Docker image..."
	docker build -t tabular-analytics:latest .

docs:
	@echo "Building MkDocs documentation..."
	mkdocs build

docs-serve:
	@echo "Serving MkDocs documentation locally..."
	mkdocs serve

clean: stop
	@echo "Cleaning up..."
	docker volume rm tabular-analytics_postgres_data || true
	rm -rf site/
