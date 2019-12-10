test:
	python -m pytest tests

lint:
	pylint ml_ids_api

lint-errors:
	pylint ml_ids_api -E

typecheck:
	mypy ml_ids_api