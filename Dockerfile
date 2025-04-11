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

# Copy the backend application code into the container
COPY backend/ .

# Create a directory for persistent data
RUN mkdir -p /data

# Expose port 8000 so that the backend can be reached
EXPOSE 8000

# Run the backend application using Uvicorn.
# (Assumes your ASGI entry point is at placement.wsgi:application)
CMD ["uvicorn", "placement.wsgi:application", "--host", "0.0.0.0", "--port", "8000"]
