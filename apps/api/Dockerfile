# Build from the repository root:  docker build -f apps/api/Dockerfile -t builder-api .
FROM python:3.11-slim
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/sitegen packages/sitegen
COPY apps/api apps/api
RUN uv sync --frozen --no-dev --package builder-api
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app/apps/api
EXPOSE 8000
# apply migrations, then serve
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
