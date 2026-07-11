FROM python:3.13.5-slim

ARG PANDOC_VERSION=3.8
ARG TARGETARCH

RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    build-essential \
    clang \
    pkg-config \
 && case "${TARGETARCH}" in \
      amd64) PANDOC_ARCH=amd64 ;; \
      arm64) PANDOC_ARCH=arm64 ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac \
 && wget https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-${PANDOC_ARCH}.deb \
 && dpkg -i pandoc-${PANDOC_VERSION}-1-${PANDOC_ARCH}.deb \
 && rm pandoc-${PANDOC_VERSION}-1-${PANDOC_ARCH}.deb \
 && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY src ./src
ENV PYTHONPATH=/app/src

CMD [".venv/bin/uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8010"]
