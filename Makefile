.PHONY: help install run test seed

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

run:  ## Start the development server
	uv run uvicorn app.main:app --reload --port 8000

test:  ## Run tests
	uv run pytest

seed:  ## Seed malicious URLs from CSV (default: data/urls.csv)
	PYTHONPATH=. uv run python scripts/seed.py $(or $(CSV),data/urls.csv)
