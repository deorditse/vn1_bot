FROM python:3.11-slim AS base

# Устанавливаем uv
RUN pip install uv

WORKDIR /app

# Копируем pyproject.toml
COPY pyproject.toml ./

# Устанавливаем зависимости
RUN uv sync --no-dev

# Копируем исходники
COPY src ./src

# Чтобы Python видел пакеты из src/
ENV PYTHONPATH=/app/src

# Точка входа
CMD ["uv", "run", "python3", "src/app/run.py"]
