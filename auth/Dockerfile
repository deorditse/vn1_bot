FROM python:3.13.5-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY src ./src
ENV PYTHONPATH=/app/src

CMD ["uv", "run", "uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8030"]
