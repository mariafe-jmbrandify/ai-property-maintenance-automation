.PHONY: install test lint demo

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src tests

demo:
	python -m maintenance_ops.cli demo
