FROM python:3.11-slim-bookworm as build
WORKDIR /app
ADD . /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

FROM python:3.11-slim-bookworm
WORKDIR /app

COPY --from=build /app /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/app/temp_check.py"]
