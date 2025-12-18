"""Location schemas for API requests and responses."""
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional


class LocationBase(BaseModel):
    """Base schema for location."""
    name: Optional[str] = Field(None, example="Bremen,DE")
    lat: Optional[float] = Field(None, example=53.08)
    lon: Optional[float] = Field(None, example=8.80)
    poll_interval_minutes: Optional[int] = Field(30, ge=1, le=1440, description="Polling interval in minutes (1-1440)")
    
    @model_validator(mode='after')
    def validate_location_data(self):
        """Validate that either name or coordinates are provided."""
        if not self.name and not (self.lat is not None and self.lon is not None):
            raise ValueError("Either 'name' or both 'lat' and 'lon' must be provided")
        return self


class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    fetch_weather_now: bool = Field(True, description="Fetch current weather immediately after creating location")


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    poll_interval_minutes: Optional[int] = Field(None, ge=1, le=1440)


class LocationResponse(LocationBase):
    """Schema for location response."""
    id: int
    name: str  # Name is mandatory after creation (either provided or reverse-geocoded)
    lat: float  # Coordinates are mandatory after creation
    lon: float
    poll_interval_minutes: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LocationListResponse(BaseModel):
    """Schema for list of locations."""
    locations: list[LocationResponse]
