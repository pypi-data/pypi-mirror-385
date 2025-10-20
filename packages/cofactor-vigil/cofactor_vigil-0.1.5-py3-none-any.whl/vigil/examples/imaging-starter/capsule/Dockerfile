# syntax=docker/dockerfile:1.6
FROM python:3.11-slim@sha256:518fcb868d8d01bfaf70bbb098a3ce8841d735d1a023d30ca272cadd5c36c0dd

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# Install system dependencies required for science stacks.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        curl \
        git \
        pkg-config \
        libssl-dev \
        libffi-dev \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv and project dependencies using the pinned lockfile.
ENV PATH="/root/.cargo/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /workspace
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the rest of the repository for runtime use.
COPY . .

# Default command runs the doctor to validate the capsule wiring.
CMD ["uv", "run", "doctor"]
