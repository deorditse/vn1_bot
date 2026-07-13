FROM python:3.13.5-slim

RUN pip install --no-cache-dir uv

WORKDIR /repo/skills/orchestrator-skill

COPY shared/python /repo/shared/python
COPY skills/orchestrator-skill/pyproject.toml skills/orchestrator-skill/uv.lock ./
RUN uv sync --no-dev

COPY skills/orchestrator-skill/src ./src
ENV PYTHONPATH=/repo/skills/orchestrator-skill/src:/repo/shared/python

CMD [".venv/bin/uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8020"]
