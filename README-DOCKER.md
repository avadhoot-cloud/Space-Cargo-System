# Space Cargo System - Docker Setup

This document provides instructions for running the Space Cargo System using Docker containers.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd space-cargo-system
   ```

2. Set up environment variables (optional):
   ```bash
   # Create a .env file in the project root
   cp .env.example .env
   
   # Edit the .env file to set your database credentials
   # Default values are provided in docker-compose.yml
   ```

## Running in Development Mode

For development with hot-reload:

```bash
# Start all services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000
- Nginx reverse proxy on port 80

## Running in Production Mode

For production deployment:

1. Modify the environment variables in docker-compose.yml:
   - Set `NODE_ENV=production` for the frontend

2. Build the images:
   ```bash
   docker-compose build
   ```

3. Run the services:
   ```bash
   docker-compose up -d
   ```

## Accessing the Application

- Frontend: http://localhost:3000 or http://localhost (via Nginx)
- Backend API: http://localhost:8000/api or http://localhost/api (via Nginx)
- API Documentation: http://localhost:8000/docs

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check if the database container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`

2. **Frontend/Backend Connectivity Issues**:
   - Ensure the REACT_APP_API_URL in frontend/.env.local is set correctly
   - Verify CORS settings in backend/src/main.py
   - Check Nginx configuration if using the proxy

3. **Container not starting**:
   - Check container logs: `docker-compose logs <service-name>`
   - Verify port availability on your host machine

## Container Management

```bash
# Stop all containers
docker-compose down

# Remove volumes (will delete database data)
docker-compose down -v

# Restart a specific service
docker-compose restart <service-name>

# View container logs
docker-compose logs -f <service-name>
```

## Data Persistence

Database data is stored in a Docker volume named `postgres_data`. This ensures data persists across container restarts. 