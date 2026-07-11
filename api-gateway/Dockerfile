FROM python:3.13.5-slim

RUN pip install --no-cache-dir uv

WORKDIR /repo/api-gateway

COPY shared/python /repo/shared/python
COPY api-gateway/pyproject.toml api-gateway/uv.lock ./
RUN uv sync --no-dev

COPY api-gateway/src ./src
ENV PYTHONPATH=/repo/api-gateway/src:/repo/shared/python

CMD [".venv/bin/uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8000"]
