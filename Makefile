.PHONY: install run test coverage seed

install:
	python -m pip install -r requirements.txt

run:
	python -m uvicorn app.main:app --reload

test:
	python -m pytest -v

coverage:
	python -m coverage run -m pytest
	python -m coverage report -m

seed:
	python -m scripts.seed_demo
