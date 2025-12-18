"""CRUD operations for Location model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


def create_location(db: Session, location: LocationCreate, user_id: int) -> Location:
    """Create a new location for a specific user."""
    # Name should already be in format "City,CountryCode" (no space) from reverse geocoding
    # If user entered name manually, normalize it
    location_name = location.name
    if location_name:
        # Remove space after comma if present (e.g., "Bremen, DE" -> "Bremen,DE")
        location_name = location_name.replace(", ", ",").replace(" ,", ",")
    
    db_location = Location(
        user_id=user_id,
        name=location_name,
        lat=location.lat,
        lon=location.lon,
        poll_interval_minutes=location.poll_interval_minutes or 30
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location(db: Session, location_id: int, user_id: int) -> Optional[Location]:
    """Get a location by ID, ensuring it belongs to the user."""
    return db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == user_id
    ).first()


def get_location_by_name(db: Session, name: str, user_id: int, case_sensitive: bool = False) -> Optional[Location]:
    """
    Get a location by name for a specific user.
    
    Args:
        db: Database session
        name: Location name (will be normalized: "Bremen, DE" -> "Bremen,DE")
        user_id: User ID to filter by
        case_sensitive: Whether to perform case-sensitive search (default: False)
    
    Returns:
        Location if found, None otherwise
    """
    # Normalize input: remove space after comma
    normalized_name = name.replace(", ", ",").replace(" ,", ",").strip()
    
    if case_sensitive:
        # Compare normalized names
        locations = db.query(Location).filter(Location.user_id == user_id).all()
        for loc in locations:
            normalized_db_name = loc.name.replace(", ", ",").replace(" ,", ",").strip() if loc.name else ""
            if normalized_db_name == normalized_name:
                return loc
        return None
    else:
        # Case-insensitive: normalize and compare lowercase
        normalized_lower = normalized_name.lower()
        locations = db.query(Location).filter(Location.user_id == user_id).all()
        for loc in locations:
            normalized_db_name = loc.name.replace(", ", ",").replace(" ,", ",").strip() if loc.name else ""
            if normalized_db_name.lower() == normalized_lower:
                return loc
        return None


def get_all_locations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Location]:
    """Get all locations for a specific user with pagination."""
    return db.query(Location).filter(
        Location.user_id == user_id
    ).offset(skip).limit(limit).all()


def update_location(
    db: Session, 
    location_id: int, 
    location_update: LocationUpdate,
    user_id: int
) -> Optional[Location]:
    """Update a location, ensuring it belongs to the user."""
    location = get_location(db, location_id, user_id)
    if not location:
        return None
    
    if location_update.name is not None:
        # Remove space after comma if present (e.g., "Bremen, DE" -> "Bremen,DE")
        location.name = location_update.name.replace(", ", ",").replace(" ,", ",")
    if location_update.lat is not None:
        location.lat = location_update.lat
    if location_update.lon is not None:
        location.lon = location_update.lon
    if location_update.poll_interval_minutes is not None:
        location.poll_interval_minutes = location_update.poll_interval_minutes
    
    db.commit()
    db.refresh(location)
    return location


def delete_location(db: Session, location_id: int, user_id: int) -> bool:
    """
    Delete a location and all its weather readings, ensuring it belongs to the user.
    
    Uses a transaction to ensure atomicity: if deletion of weather readings fails,
    the location deletion is rolled back.
    
    Returns:
        True if deletion was successful, False if location not found
    """
    location = get_location(db, location_id, user_id)
    if not location:
        return False
    
    try:
        # Delete location (cascade will automatically delete all weather_readings)
        # This happens in a transaction - if anything fails, everything is rolled back
        db.delete(location)
        db.commit()
        return True
    except Exception as e:
        # Rollback transaction on any error
        db.rollback()
        # Re-raise the exception so the caller can handle it
        raise e
