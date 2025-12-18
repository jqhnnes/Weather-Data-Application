"""Background task for periodically fetching weather data."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import weather_service
from app.crud import location as location_crud

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def fetch_weather_for_location(location_id: int):
    """Fetch and save weather for a specific location."""
    db: Session = SessionLocal()
    try:
        # Get location directly by ID (without user_id check for scheduler)
        # We need to query the database directly to get the location and its user_id
        from app.models.location import Location
        location = db.query(Location).filter(Location.id == location_id).first()
        
        if not location:
            logger.warning(f"Location with id {location_id} not found, skipping fetch")
            return
        
        logger.debug(f"Fetching weather for location {location.name} (id: {location_id}, user_id: {location.user_id})")
        reading = weather_service.fetch_and_save_weather(db, location_id, location.user_id)
        logger.debug(f"Successfully fetched weather for location {location.name} (reading id: {reading.id})")
    except Exception as e:
        logger.error(
            f"Error fetching weather for location id {location_id}: {e}",
            exc_info=True
        )
    finally:
        db.close()


def add_location_job(location_id: int, poll_interval_minutes: int):
    """Add or update a scheduled job for a location."""
    if not scheduler.running:
        logger.warning(f"Scheduler not running, cannot add job for location {location_id}")
        return
    
    job_id = f"location_{location_id}"
    
    # Remove existing job if it exists
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.debug(f"Removed existing job for location {location_id}")
    
    # Add new job with the specified interval
    scheduler.add_job(
        fetch_weather_for_location,
        args=[location_id],
        trigger=IntervalTrigger(minutes=poll_interval_minutes),
        id=job_id,
        name=f"Fetch weather for location {location_id}",
        replace_existing=True
    )
    logger.info(
        f"Added scheduled job for location {location_id} "
        f"(interval: {poll_interval_minutes} minutes)"
    )


def remove_location_job(location_id: int):
    """Remove the scheduled job for a location."""
    if not scheduler.running:
        logger.debug(f"Scheduler not running, skipping job removal for location {location_id}")
        return
    
    job_id = f"location_{location_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed scheduled job for location {location_id}")
    else:
        logger.debug(f"No job found for location {location_id}")


def refresh_all_location_jobs():
    """Load all locations from database and create/update their scheduled jobs."""
    db: Session = SessionLocal()
    try:
        # Get all locations for all users (scheduler needs to handle all locations)
        # Query directly from database to get all locations regardless of user
        from app.models.location import Location
        locations = db.query(Location).all()
        
        logger.info(f"Refreshing scheduled jobs for {len(locations)} locations across all users")
        
        for location in locations:
            add_location_job(location.id, location.poll_interval_minutes)
        
        logger.info(f"Successfully refreshed {len(locations)} location jobs")
    except Exception as e:
        logger.error(f"Error refreshing location jobs: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler and load all location jobs."""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return
    
    scheduler.start()
    logger.info("Weather poller scheduler started")
    
    # Load all locations and create jobs for them
    refresh_all_location_jobs()


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Weather poller stopped")
    else:
        logger.warning("Scheduler is not running")
