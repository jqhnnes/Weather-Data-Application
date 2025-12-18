"""Weather service - Business logic for weather data."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.crud import location as location_crud
from app.crud import weather_reading as weather_crud
from app.clients.openweather import get_current_weather
from app.schemas.weather import WeatherReadingCreate, WeatherReadingResponse


def fetch_and_save_weather(
    db: Session,
    location_id: int,
    user_id: int
) -> WeatherReadingResponse:
    """
    Fetch current weather for a location and save it to database.
    
    Args:
        db: Database session
        location_id: ID of the location
        user_id: ID of the user (to verify ownership)
    
    Returns:
        WeatherReadingResponse
    """
    # Get location, ensuring it belongs to the user
    location = location_crud.get_location(db, location_id, user_id)
    if not location:
        raise ValueError(f"Location with id {location_id} not found")
    
    # Fetch weather data
    weather_data = get_current_weather(
        city=location.name,
        lat=location.lat,
        lon=location.lon
    )
    
    # Create weather reading
    reading = WeatherReadingCreate(
        location_id=location_id,
        temperature=weather_data["temperature"],
        humidity=weather_data["humidity"],
        precipitation=weather_data["precipitation"],
        pressure=weather_data.get("pressure"),
        description=weather_data.get("description"),
        timestamp=datetime.fromtimestamp(weather_data.get("timestamp", datetime.now().timestamp()))
    )
    
    db_reading = weather_crud.create_weather_reading(db, reading)
    return WeatherReadingResponse.model_validate(db_reading)


def fetch_weather_for_all_locations(db: Session, user_id: int) -> dict:
    """
    Fetch and save current weather for all locations of a specific user.
    
    Args:
        db: Database session
        user_id: ID of the user
    
    Returns:
        Dictionary with results for each location
    """
    locations = location_crud.get_all_locations(db, user_id)
    results = {
        "success": [],
        "failed": []
    }
    
    for location in locations:
        try:
            reading = fetch_and_save_weather(db, location.id, user_id)
            results["success"].append({
                "location_id": location.id,
                "location_name": location.name,
                "reading_id": reading.id
            })
        except Exception as e:
            results["failed"].append({
                "location_id": location.id,
                "location_name": location.name,
                "error": str(e)
            })
    
    return results


def get_weather_history(
    db: Session,
    location_id: int,
    user_id: int,
    limit: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[WeatherReadingResponse]:
    """
    Get weather history for a location, ensuring it belongs to the user.
    
    Args:
        db: Database session
        location_id: ID of the location
        user_id: ID of the user (to verify ownership)
        limit: Maximum number of readings to return
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        List of WeatherReadingResponse
    """
    if start_date and end_date:
        readings = weather_crud.get_weather_readings_by_date_range(
            db, location_id, user_id, start_date, end_date, limit=limit
        )
    else:
        readings = weather_crud.get_weather_readings_by_location(
            db, location_id, user_id, limit=limit
        )
    
    return [WeatherReadingResponse.model_validate(r) for r in readings]
