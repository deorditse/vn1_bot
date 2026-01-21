FROM python:3.13.5-slim

ARG PANDOC_VERSION=3.8

RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    build-essential \
    clang \
    pkg-config \
 && wget https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-amd64.deb \
 && dpkg -i pandoc-${PANDOC_VERSION}-1-amd64.deb \
 && rm pandoc-${PANDOC_VERSION}-1-amd64.deb \
 && rm -rf /var/lib/apt/lists/*

# locale — критично для pandoc
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# uv
RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY src ./src
ENV PYTHONPATH=/app/src

CMD ["uv", "run", "uvicorn", "src.app.api.api:app", "--host", "0.0.0.0", "--port", "8010"]