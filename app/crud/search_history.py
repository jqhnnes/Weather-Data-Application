"""CRUD operations for SearchHistory model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.search_history import SearchHistory


def create_search_history(
    db: Session,
    user_id: int,
    location_id: Optional[int] = None,
    location_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search_params: Optional[dict] = None
) -> SearchHistory:
    """Create a new search history entry for a specific user."""
    search = SearchHistory(
        user_id=user_id,
        location_id=location_id,
        location_name=location_name,
        start_date=start_date,
        end_date=end_date,
        search_params=search_params
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


def get_search_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[SearchHistory]:
    """Get search history for a specific user with pagination, ordered by most recent first."""
    return db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(SearchHistory.created_at.desc()).offset(skip).limit(limit).all()


def get_search_history_by_location(
    db: Session,
    location_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[SearchHistory]:
    """Get search history for a specific location, ensuring it belongs to the user."""
    return (
        db.query(SearchHistory)
        .filter(
            SearchHistory.location_id == location_id,
            SearchHistory.user_id == user_id
        )
        .order_by(SearchHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_search_history(db: Session, search_id: int, user_id: int) -> bool:
    """Delete a search history entry by ID, ensuring it belongs to the user."""
    search = db.query(SearchHistory).filter(
        SearchHistory.id == search_id,
        SearchHistory.user_id == user_id
    ).first()
    if not search:
        return False
    db.delete(search)
    db.commit()
    return True

