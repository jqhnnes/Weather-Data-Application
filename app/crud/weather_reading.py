"""CRUD operations for WeatherReading model."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.models.weather_reading import WeatherReading
from app.schemas.weather import WeatherReadingCreate


def create_weather_reading(db: Session, reading: WeatherReadingCreate) -> WeatherReading:
    """Create a new weather reading."""
    db_reading = WeatherReading(
        location_id=reading.location_id,
        temperature=reading.temperature,
        humidity=reading.humidity,
        precipitation=reading.precipitation,
        pressure=reading.pressure,
        description=reading.description,
        timestamp=reading.timestamp
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


def get_weather_reading(db: Session, reading_id: int) -> Optional[WeatherReading]:
    """Get a weather reading by ID."""
    return db.query(WeatherReading).filter(WeatherReading.id == reading_id).first()


def get_weather_readings_by_location(
    db: Session, 
    location_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[WeatherReading]:
    """
    Get all weather readings for a specific location, ensuring the location belongs to the user.
    Ordered by timestamp (newest first).
    """
    from app.models.location import Location
    return (
        db.query(WeatherReading)
        .join(Location)
        .filter(
            WeatherReading.location_id == location_id,
            Location.user_id == user_id
        )
        .order_by(desc(WeatherReading.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_latest_weather_reading(
    db: Session, 
    location_id: int,
    user_id: int
) -> Optional[WeatherReading]:
    """Get the latest weather reading for a location, ensuring it belongs to the user."""
    from app.models.location import Location
    return (
        db.query(WeatherReading)
        .join(Location)
        .filter(
            WeatherReading.location_id == location_id,
            Location.user_id == user_id
        )
        .order_by(desc(WeatherReading.timestamp))
        .first()
    )


def get_weather_readings_by_date_range(
    db: Session,
    location_id: int,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> List[WeatherReading]:
    """Get weather readings for a location within a date range, ensuring the location belongs to the user."""
    from app.models.location import Location
    return (
        db.query(WeatherReading)
        .join(Location)
        .filter(
            WeatherReading.location_id == location_id,
            Location.user_id == user_id,
            WeatherReading.timestamp >= start_date,
            WeatherReading.timestamp <= end_date
        )
        .order_by(desc(WeatherReading.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_weather_reading(db: Session, reading_id: int) -> bool:
    """Delete a weather reading."""
    reading = get_weather_reading(db, reading_id)
    if not reading:
        return False
    
    db.delete(reading)
    db.commit()
    return True
