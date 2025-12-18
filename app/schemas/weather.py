"""Weather schemas for API requests and responses."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WeatherReadingResponse(BaseModel):
    """Schema for weather reading response."""
    id: int
    location_id: int
    temperature: float
    humidity: float
    precipitation: float
    pressure: Optional[float]
    description: Optional[str]
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class WeatherReadingListResponse(BaseModel):
    """Schema for list of weather readings."""
    readings: list[WeatherReadingResponse]
    total: int


class WeatherReadingCreate(BaseModel):
    """Schema for creating a new weather reading."""
    location_id: int
    temperature: float
    humidity: float
    precipitation: float
    pressure: Optional[float] = None
    description: Optional[str] = None
    timestamp: datetime
