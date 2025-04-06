import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import engine
from . import models
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
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Space Cargo System API")

# Configure CORS with explicitly allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(placement.router, prefix="/api/placement", tags=["placement"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Space Cargo System API"} 