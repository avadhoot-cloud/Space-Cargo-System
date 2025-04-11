# Use Python slim image for faster startup
FROM python:3.9-slim

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the backend application code
COPY backend/ .

# Create a directory for persistent data
RUN mkdir -p /data

# Pre-compile Python files to bytecode for faster startup
RUN python -m compileall .

# Expose port 8000
EXPOSE 8000

# Set up a minimal health check endpoint for faster response
RUN echo 'from django.http import HttpResponse; def health(request): return HttpResponse("OK")' > healthcheck.py

# Use Gunicorn with minimal configuration for fastest startup
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "2", "--preload", "--timeout", "5", "spacecargo.wsgi:application"]
