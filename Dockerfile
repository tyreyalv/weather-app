# Build Stage
FROM python:3.11-slim-bookworm as build
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt --target=/app

# Final Stage
FROM python:3.11-slim-bookworm
WORKDIR /app
COPY --from=build /app /app
COPY . .
RUN useradd -m weather
USER weather
CMD ["python", "/app/main.py"]