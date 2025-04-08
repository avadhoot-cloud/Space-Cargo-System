import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import JSONResponse

from .database import engine, Base
from .routers import placement, search, upload, simulation
import pathlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Ensure data directory exists
data_dir = pathlib.Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Space Cargo System API",
    default_response_class=JSONResponse  # Ensure JSON responses
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add middleware to ensure JSON content type in responses
@app.middleware("http")
async def add_content_type_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json"
    return response

# Include routers
app.include_router(placement.router, prefix="/api/placement", tags=["placement"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])

@app.get("/")
async def root():
    return {"message": "Welcome to Space Cargo System API", "status": "online"} 