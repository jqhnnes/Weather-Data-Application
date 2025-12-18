"""Search history schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SearchHistoryCreate(BaseModel):
    """Schema for creating a search history entry."""
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_params: Optional[Dict[str, Any]] = None


class SearchHistoryResponse(BaseModel):
    """Schema for search history response."""
    id: int
    location_id: Optional[int]
    location_name: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    search_params: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SearchHistoryListResponse(BaseModel):
    """Schema for list of search history entries."""
    searches: list[SearchHistoryResponse]
    total: int

