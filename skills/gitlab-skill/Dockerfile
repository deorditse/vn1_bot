FROM python:3.13.5-slim

RUN pip install --no-cache-dir uv

WORKDIR /repo/skills/gitlab-skill

COPY shared/python /repo/shared/python
COPY skills/gitlab-skill/pyproject.toml skills/gitlab-skill/uv.lock ./
RUN uv sync --no-dev

COPY skills/gitlab-skill/src ./src
ENV PYTHONPATH=/repo/skills/gitlab-skill/src:/repo/shared/python

CMD [".venv/bin/uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8022"]
