FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-root

COPY . .