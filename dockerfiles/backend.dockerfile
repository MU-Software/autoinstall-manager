FROM python:3.13-slim-bookworm AS builder
SHELL [ "/bin/bash", "-euxvc"]

# Set up environment variables
ENV TZ=Asia/Seoul \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=UTF-8 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

FROM python:3.13-slim-bookworm AS runtime
SHELL [ "/bin/bash", "-euxvc"]

ARG GIT_HASH
ENV TZ=Asia/Seoul \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=UTF-8 \
    DEPLOYMENT_GIT_HASH=$GIT_HASH

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone;

WORKDIR /app

# Make docker to always copy app directory so that source code can be refreshed.
ARG IMAGE_BUILD_DATETIME=unknown
ENV DEPLOYMENT_IMAGE_BUILD_DATETIME=$IMAGE_BUILD_DATETIME

# Copy the environment, but not the source code
COPY --chown=app:app --from=builder /backend/.venv ./.venv
COPY --chown=app:app svc/ /backend/svc/
COPY --chown=app:app alembic.ini ./alembic.ini
COPY --chown=app:app pyproject.toml ./pyproject.toml
