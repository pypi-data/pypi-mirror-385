FROM quay.io/unstructured-io/base-images:wolfi-py3.12-slim-82e1186 AS base

ARG PYTHON=python3.12

# Set up environment
USER root
ENV HOME=/home/
WORKDIR ${HOME}
ENV PATH="/home/usr/.local/bin:${PATH}"

# Install uv
RUN pip install uv

FROM base AS python_deps_slim

# Copy and configure uv
COPY pyproject.toml uv.lock src ./
RUN uv sync

CMD uv run etl-uvicorn plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:Plugin --method-name run --plugin-id plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:Plugin --plugin-id-method id --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000} --log-level ${LOG_LEVEL:-"info"}