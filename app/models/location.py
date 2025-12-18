"""Location model for storing weather monitoring locations."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Location(Base):
    """Model for weather monitoring locations."""
    
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    poll_interval_minutes = Column(Integer, nullable=False, default=30, server_default="30")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="locations")
    weather_readings = relationship("WeatherReading", back_populates="location", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Location(id={self.id}, user_id={self.user_id}, name='{self.name}', lat={self.lat}, lon={self.lon})>"
