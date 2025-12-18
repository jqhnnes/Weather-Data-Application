"""Weather reading model for storing weather data."""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WeatherReading(Base):
    """Model for weather data readings."""
    
    __tablename__ = "weather_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    
    # Weather data
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False, default=0.0)
    pressure = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to location
    location = relationship("Location", back_populates="weather_readings")
    
    def __repr__(self):
        return f"<WeatherReading(id={self.id}, location_id={self.location_id}, temp={self.temperature}°C, time={self.timestamp})>"
