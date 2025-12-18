"""Search history API endpoints."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.schemas.search_history import SearchHistoryCreate, SearchHistoryResponse, SearchHistoryListResponse
from app.services import search_history_service
from app.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/search-history", tags=["search-history"])


@router.post("", response_model=SearchHistoryResponse, status_code=201)
def create_search_history_entry(
    search: SearchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Save a search query to history for the current user."""
    try:
        search_entry = search_history_service.record_search(
            db, search, current_user.id
        )
        return search_entry
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording search: {str(e)}")


@router.get("", response_model=SearchHistoryListResponse)
def get_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get search history for the current user."""
    try:
        searches = search_history_service.get_search_history_list(
            db, current_user.id, skip=skip, limit=limit, location_id=location_id
        )
        return SearchHistoryListResponse(
            searches=searches,
            total=len(searches)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching search history: {str(e)}")


@router.delete("/{search_id}", status_code=204)
def delete_search_history_entry(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a search history entry, ensuring it belongs to the current user."""
    try:
        search_history_service.delete_search_entry(db, search_id, current_user.id)
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting search history: {str(e)}")

