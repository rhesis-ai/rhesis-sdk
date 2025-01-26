.PHONY: all format lint type-check test requirements docs

all: format lint type-check test requirements docs

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

docs:
	cd docs && make clean && make html