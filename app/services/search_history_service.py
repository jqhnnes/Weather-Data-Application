"""Search history service - Business logic for search history."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.crud import search_history as search_history_crud
from app.crud import location as location_crud
from app.schemas.search_history import SearchHistoryCreate, SearchHistoryResponse


def record_search(
    db: Session,
    search_data: SearchHistoryCreate,
    user_id: int
) -> SearchHistoryResponse:
    """
    Record a search query in the history.
    
    Args:
        db: Database session
        search_data: Search history data
        user_id: ID of the user performing the search
    
    Returns:
        SearchHistoryResponse
    """
    from fastapi import HTTPException
    
    # Validate that if location_id is provided, the location exists and belongs to user
    if search_data.location_id:
        location = location_crud.get_location(db, search_data.location_id, user_id)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location with ID {search_data.location_id} not found.")
        # Use the actual location name if not provided
        if not search_data.location_name:
            search_data.location_name = location.name
    
    # Validate date range
    if search_data.start_date and search_data.end_date:
        if search_data.start_date > search_data.end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    # Create search history entry
    search_entry = search_history_crud.create_search_history(
        db,
        user_id=user_id,
        location_id=search_data.location_id,
        location_name=search_data.location_name,
        start_date=search_data.start_date,
        end_date=search_data.end_date,
        search_params=search_data.search_params
    )
    
    return SearchHistoryResponse.model_validate(search_entry)


def get_search_history_list(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    location_id: Optional[int] = None
) -> List[SearchHistoryResponse]:
    """
    Get search history for a specific user with optional filtering.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return
        location_id: Optional filter by location ID
    
    Returns:
        List of SearchHistoryResponse
    """
    from fastapi import HTTPException
    
    if location_id:
        # Validate location exists and belongs to user
        location = location_crud.get_location(db, location_id, user_id)
        if not location:
            raise HTTPException(status_code=404, detail=f"Location with id {location_id} not found")
        
        searches = search_history_crud.get_search_history_by_location(
            db, location_id, user_id, skip=skip, limit=limit
        )
    else:
        searches = search_history_crud.get_search_history(db, user_id, skip=skip, limit=limit)
    
    return [SearchHistoryResponse.model_validate(s) for s in searches]


def delete_search_entry(
    db: Session,
    search_id: int,
    user_id: int
) -> bool:
    """
    Delete a search history entry, ensuring it belongs to the user.
    
    Args:
        db: Database session
        search_id: ID of the search entry to delete
        user_id: ID of the user
    
    Returns:
        True if deleted, False if not found
    
    Raises:
        HTTPException: If search entry not found
    """
    from fastapi import HTTPException
    
    success = search_history_crud.delete_search_history(db, search_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Search history entry with id {search_id} not found")
    return True

