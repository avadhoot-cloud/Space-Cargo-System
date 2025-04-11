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

# Expose port 8000
EXPOSE 8000

# Use our minimal health_app.py for extremely fast startup
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "health_app:application"]
