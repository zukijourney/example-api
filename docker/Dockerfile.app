FROM python:3.11-slim as build

ENV PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install "poetry" \
    && poetry install --no-root --no-ansi --no-interaction \
    && poetry export -f requirements.txt -o requirements.txt

### Final stage
FROM python:3.11-slim as final

WORKDIR /app

COPY --from=build /app/requirements.txt .

COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "-c", "python3 -B -m litestar run --port 80 --host 0.0.0.0"]