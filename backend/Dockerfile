FROM python:3.10.12-slim

# Install system dependencies required for MCP servers
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        nodejs \
        npm \
        gcc \
        g++ \
        make \
        cmake \
        libsqlite3-dev \
        awscli \
        ffmpeg \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create media directories
RUN mkdir -p media/uploads media/splits media/frames

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
