SHELL := /bin/bash

.PHONY: run check-ports clean-artifacts hooks

run:
	python start.py
	@echo "Open: http://localhost/scraper"

check-ports:
	./scripts/check-no-ports.sh

clean-artifacts:
	./scripts/cleanup-artifacts.sh --apply

hooks:
	git config core.hooksPath .githooks
	@echo "Git hooks path set to .githooks"

.PHONY: lint format install-dev

install-dev:
	pip install -r requirements-dev.txt || true

lint:
	@if command -v ruff >/dev/null 2>&1; then ruff check .; else echo "ruff not found, run 'make install-dev'"; fi
	@if command -v black >/dev/null 2>&1; then black --check . || true; else echo "black not found, run 'make install-dev'"; fi

format:
	@if command -v ruff >/dev/null 2>&1; then ruff check --fix .; else echo "ruff not found, run 'make install-dev'"; fi
	@if command -v black >/dev/null 2>&1; then black .; else echo "black not found, run 'make install-dev'"; fi
