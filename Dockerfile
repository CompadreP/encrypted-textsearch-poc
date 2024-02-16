FROM python-3.11-slim

WORKDIR /app/

RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential gcc curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./app /app/app
COPY ./tests /app/tests
COPY ./scripts /app/scripts
COPY ./config.py /app/
COPY ./main.py /app/
COPY ./pyproject.toml /app/
COPY ./poetry.lock /app/
COPY ./settings.toml /app/
COPY ./whitelist.py /app/

RUN poetry install --no-root

ENV PYTHONPATH=/app
