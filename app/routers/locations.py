"""Locations API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.location import LocationCreate, LocationResponse, LocationListResponse, LocationUpdate
from app.schemas.weather import WeatherReadingResponse
from app.services import location_service
from app.tasks.weather_poller import add_location_job, remove_location_job
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("", response_model=LocationResponse, status_code=201)
def create_location(
    location: LocationCreate,
    fetch_weather: bool = Query(True, description="Fetch current weather immediately"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new location for the current user.
    
    If fetch_weather is True, current weather will be fetched and saved immediately.
    """
    try:
        location_response, weather_data = location_service.create_location_with_weather(
            db, location, user_id=current_user.id, fetch_weather=fetch_weather
        )
        
        # Add scheduled job for this location
        poll_interval = location.poll_interval_minutes or 30
        add_location_job(location_response.id, poll_interval)
        
        return location_response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating location: {str(e)}")


@router.get("", response_model=LocationListResponse)
def get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all locations for the current user with pagination."""
    locations = location_service.get_all_locations(db, current_user.id, skip=skip, limit=limit)
    return LocationListResponse(locations=locations)


@router.get("/check-name")
def check_name(
    name: str = Query(..., description="Location name to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if a location with given name already exists for the current user (case-insensitive).
    
    Returns:
        {"exists": bool, "location": LocationResponse or None}
    """
    return location_service.check_location_name(db, name, current_user.id)


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific location by ID, ensuring it belongs to the current user."""
    try:
        return location_service.get_location(db, location_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{location_id}/with-weather")
def get_location_with_weather(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get location with its latest weather reading, ensuring it belongs to the current user."""
    try:
        return location_service.get_location_with_latest_weather(db, location_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_update: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a location (name, coordinates, or polling interval), ensuring it belongs to the current user."""
    try:
        updated_location = location_service.update_location(db, location_id, location_update, current_user.id)
        
        # Update scheduled job if polling interval changed
        if location_update.poll_interval_minutes is not None:
            add_location_job(location_id, updated_location.poll_interval_minutes)
        
        return updated_location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{location_id}", status_code=204)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a location and all its weather readings, ensuring it belongs to the current user.
    
    Uses a database transaction to ensure atomicity:
    - If deletion succeeds: both location and weather readings are deleted
    - If deletion fails: nothing is deleted (automatic rollback)
    """
    try:
        location_service.delete_location(db, location_id, current_user.id)
        
        # Only remove scheduled job if database deletion was successful
        remove_location_job(location_id)
        
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Handle any other database errors
        db.rollback()  # Ensure rollback (though CRUD already does this)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting location: {str(e)}"
        )
