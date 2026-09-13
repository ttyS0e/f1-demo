FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--reload"]
