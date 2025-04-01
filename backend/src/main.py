from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import placement, search

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Space Cargo System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(placement.router, prefix="/api/placement", tags=["placement"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Space Cargo System API"} 