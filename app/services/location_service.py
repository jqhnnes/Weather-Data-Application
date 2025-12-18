"""Location service - Business logic for locations."""
from sqlalchemy.orm import Session
from typing import Optional
from app.crud import location as location_crud
from app.crud import weather_reading as weather_crud
from app.schemas.location import LocationCreate, LocationResponse
from app.schemas.weather import WeatherReadingCreate
from app.clients.openweather import get_current_weather, OpenMeteoClient
from datetime import datetime


def create_location_with_weather(
    db: Session, 
    location_data: LocationCreate,
    user_id: int,
    fetch_weather: bool = True
) -> tuple[LocationResponse, Optional[dict]]:
    """
    Create a new location and optionally fetch current weather.
    
    Args:
        db: Database session
        location_data: Location data to create
        user_id: ID of the user creating the location
        fetch_weather: Whether to fetch and save current weather
    
    Returns:
        Tuple of (LocationResponse, weather_data_dict or None)
    """
    # Determine name and coordinates
    location_name = location_data.name
    location_lat = location_data.lat
    location_lon = location_data.lon
    
    # If only coordinates provided, reverse geocode to get name FIRST
    # This allows us to check by name instead of coordinates (more accurate)
    if not location_name and location_lat is not None and location_lon is not None:
        try:
            client = OpenMeteoClient()
            location_name = client._reverse_geocode(location_lat, location_lon)
            # Name is already in format "City,CountryCode" (no space) from _reverse_geocode
        except Exception as e:
            # Fallback: use coordinates as name
            location_name = f"{location_lat:.4f},{location_lon:.4f}"
    
    # If only name provided, geocode to get coordinates
    if location_name and (location_lat is None or location_lon is None):
        try:
            weather_data = get_current_weather(city=location_name)
            location_lat = weather_data["lat"]
            location_lon = weather_data["lon"]
        except Exception:
            raise ValueError(f"Could not find coordinates for location '{location_name}'")
    
    # Check if location already exists by NAME for this user (independent of coordinates)
    # This is the main check: if coordinates are provided, we first resolve the name,
    # then check if that name already exists for this user, regardless of the coordinates
    if location_name:
        existing_by_name = location_crud.get_location_by_name(db, location_name, user_id, case_sensitive=False)
        if existing_by_name:
            raise ValueError(
                f"Location '{location_name}' already exists "
                f"(coordinates: {existing_by_name.lat:.4f}, {existing_by_name.lon:.4f})"
            )
    
    # Create location with determined values
    location_data.name = location_name
    location_data.lat = location_lat
    location_data.lon = location_lon
    db_location = location_crud.create_location(db, location_data, user_id)
    
    weather_result = None
    
    # Fetch and save current weather if requested
    if fetch_weather:
        try:
            weather_data = get_current_weather(
                city=location_data.name,
                lat=db_location.lat,
                lon=db_location.lon
            )
            
            # Save weather reading
            reading = WeatherReadingCreate(
                location_id=db_location.id,
                temperature=weather_data["temperature"],
                humidity=weather_data["humidity"],
                precipitation=weather_data["precipitation"],
                pressure=weather_data.get("pressure"),
                description=weather_data.get("description"),
                timestamp=datetime.fromtimestamp(weather_data.get("timestamp", datetime.now().timestamp()))
            )
            weather_crud.create_weather_reading(db, reading)
            weather_result = weather_data
        except Exception as e:
            # Log error but don't fail location creation
            print(f"Warning: Could not fetch weather for {location_data.name}: {e}")
    
    return LocationResponse.model_validate(db_location), weather_result


def get_location_with_latest_weather(
    db: Session,
    location_id: int,
    user_id: int
) -> dict:
    """Get location with its latest weather reading, ensuring it belongs to the user."""
    db_location = location_crud.get_location(db, location_id, user_id)
    if not db_location:
        raise ValueError(f"Location with id {location_id} not found")
    
    latest_weather = weather_crud.get_latest_weather_reading(db, location_id, user_id)
    
    result = {
        "location": LocationResponse.model_validate(db_location),
        "latest_weather": None
    }
    
    if latest_weather:
        from app.schemas.weather import WeatherReadingResponse
        result["latest_weather"] = WeatherReadingResponse.model_validate(latest_weather)
    
    return result
