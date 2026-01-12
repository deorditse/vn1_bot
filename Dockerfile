FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    pandoc \
    build-essential \
    clang \
    pkg-config \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# uv
RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./

# Установка зависимостей
RUN uv sync --no-dev

COPY src ./src

ENV PYTHONPATH=/app/src

CMD ["uv", "run", "python", "src/app/run.py"]