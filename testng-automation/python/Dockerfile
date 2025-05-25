FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    docker.io \
    curl \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Flask
RUN pip install flask

# Copy app code
WORKDIR /app
COPY main.py .

# Expose port
EXPOSE 8080

# Run app
CMD ["python3", "main.py"]
