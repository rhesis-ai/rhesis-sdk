.PHONY: all format lint type-check test requirements

all: format lint type-check test requirements

format:
	black src tests

lint:
	flake8 src tests

type-check:
	PYTHONPATH=src mypy --package rhesis

test:
	pytest

requirements:
	poetry export -f requirements.txt --without-hashes > requirements.txt
	poetry export -f requirements.txt --without-hashes --with dev > requirements-dev.txt