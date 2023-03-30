FROM python:3.10-slim-buster

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.4.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 -

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN mkdir -p /app
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ADD . /app

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --without=dev

EXPOSE 8080

CMD ["poetry", "run", "python", "jaundice_rate/server.py"]