"""Weather API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.clients.openweather import get_current_weather, OpenMeteoClient
from app.schemas.weather import WeatherReadingListResponse, WeatherReadingResponse
from app.services import weather_service
from app.crud import location as location_crud
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current")
def get_current_weather_endpoint(
    city: Optional[str] = Query(None, description="City name (e.g., 'Bremen,DE')"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current weather data from Open-Meteo API (without saving to database).
    
    Either provide city name OR lat/lon coordinates.
    """
    try:
        data = get_current_weather(city=city, lat=lat, lon=lon)
        
        # If only coordinates were provided, reverse geocode to get city name
        location_name = data.get('city', '')
        if not city and lat is not None and lon is not None:
            # The API returns coordinates as city name when no city is provided
            # Use reverse geocoding to get the actual city name
            try:
                client = OpenMeteoClient()
                location_name = client._reverse_geocode(lat, lon)
            except Exception:
                # If reverse geocoding fails, use coordinates
                location_name = f"{lat:.4f},{lon:.4f}"
        
        return {
            "success": True,
            "data": {
                "location": f"{location_name}, {data['country']}" if data.get('country') and data['country'] != location_name else location_name,
                "coordinates": {
                    "lat": data['lat'],
                    "lon": data['lon']
                },
                "temperature": data['temperature'],
                "humidity": data['humidity'],
                "precipitation": data['precipitation'],
                "pressure": data.get('pressure'),
                "description": data['description']
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}")


@router.get("/location/{location_id}", response_model=WeatherReadingListResponse)
def get_weather_for_location(
    location_id: int,
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of readings"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get stored weather data for a location, ensuring it belongs to the current user.
    
    Returns weather readings from the database for the specified location.
    """
    readings = weather_service.get_weather_history(
        db, location_id, current_user.id, limit=limit, start_date=start_date, end_date=end_date
    )
    
    return WeatherReadingListResponse(readings=readings, total=len(readings))


@router.post("/location/{location_id}/fetch")
def fetch_and_save_weather(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetch current weather for a location and save it to database, ensuring it belongs to the current user.
    """
    try:
        reading = weather_service.fetch_and_save_weather(db, location_id, current_user.id)
        return {
            "success": True,
            "message": "Weather data fetched and saved",
            "reading": reading
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")
