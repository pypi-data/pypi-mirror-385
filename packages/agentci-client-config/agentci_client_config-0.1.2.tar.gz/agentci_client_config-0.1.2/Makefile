.PHONY: test
test:
	uv run pytest tests/ -v --cov=src/agentci/client_config --cov-report=term-missing

.PHONY: docs-serve
docs-serve:
	uv run --extra docs mkdocs serve

.PHONY: docs-build
docs-build:
	uv run --extra docs mkdocs build
