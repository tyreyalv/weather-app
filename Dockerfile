# First stage: perform system update & upgrade
FROM python:3.11-slim-bookworm as build
WORKDIR /app
ADD . /app

# Upgrade all packages and clean up
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Second stage: build the final image
FROM python:3.11-slim-bookworm
WORKDIR /app

# Copy only the necessary files from the first stage
COPY --from=build /app /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run weather_notifier.py when the container launches
CMD ["python", "/app/temp_check.py"]
