.PHONY: alembic

alembic:
	PYTHONPATH=./app alembic revision --autogenerate -m "migration run"
	PYTHONPATH=./app alembic upgrade head
up:
	sudo docker compose up --build
poetry-export:
	poetry export -f requirements.txt --without-hashes --output requirements.txt
lint:
	poetry run isort .
	poetry run black .

