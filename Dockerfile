FROM python:3.11-slim AS base

# Устанавливаем pandoc (обязательно)
RUN apt-get update && apt-get install -y pandoc && apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN pip install uv

WORKDIR /app

# Сначала копируем pyproject.toml
COPY pyproject.toml ./

# Устанавливаем зависимости через uv
RUN uv sync --no-dev

# Копируем исходники
COPY src ./src

# Чтобы Python видел пакеты из src/
ENV PYTHONPATH=/app/src

# Точка входа
CMD ["uv", "run", "python3", "src/app/run.py"]