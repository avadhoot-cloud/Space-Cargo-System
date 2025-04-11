# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, pip, and git (if needed)
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install them
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install django gunicorn

# Copy the backend application code into the container
COPY backend/ .

# Create a directory for persistent data
RUN mkdir -p /data

# Expose port 8000 so that the backend can be reached
EXPOSE 8000

# Pre-apply migrations during build
RUN python3 manage.py migrate --noinput || true

# Use Gunicorn instead of Django's development server for faster startup
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "30", "--workers", "2", "spacecargo.wsgi:application"]
