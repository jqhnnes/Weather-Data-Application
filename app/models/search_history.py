"""Search history model for storing user search queries."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SearchHistory(Base):
    """Model for storing search history."""
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    location_id = Column(Integer, nullable=True, index=True)  # Nullable for searches without location
    location_name = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    search_params = Column(JSON, nullable=True)  # Store additional search parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="search_history")
    
    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, location_id={self.location_id}, created_at={self.created_at})>"

