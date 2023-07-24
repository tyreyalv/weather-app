# First stage: perform system update & upgrade
FROM python:3.10-slim-buster as build
WORKDIR /app
ADD . /app

# Upgrade all packages and clean up
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: build the final image
FROM python:3.10-slim-buster
WORKDIR /app

# Copy only the necessary files from the first stage
COPY --from=build /app /app

# Run weather_notifier.py when the container launches
CMD ["python", "/app/temp_check.py"]
