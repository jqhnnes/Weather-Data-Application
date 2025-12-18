from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.routers import weather, locations, search_history, auth
from app.database import engine, init_db
from app.models import User, Location, WeatherReading, SearchHistory  # Import models so they're registered
from app.tasks.weather_poller import start_scheduler, stop_scheduler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Weather Data Application")

# Enable CORS for frontend
# Allow all localhost and 127.0.0.1 origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(locations.router)
app.include_router(weather.router)
app.include_router(search_history.router)


@app.on_event("startup")
def startup_event():
    """Initialize database and start scheduler on startup."""
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    """Stop scheduler on shutdown."""
    stop_scheduler()