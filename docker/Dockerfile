FROM python:3.14-slim-trixie

# uv 0.9.22 (82a6a66b8 2026-01-06)
COPY --from=ghcr.io/astral-sh/uv@sha256:019833ee72f9635c5b3af288045e4d257ebcf86598f6ae94b34b4458aad4f1ac /uv /uvx /bin/

WORKDIR /work

# Copy the project into the image
COPY . .

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked

CMD ["uv", "run", "app/main.py"]
