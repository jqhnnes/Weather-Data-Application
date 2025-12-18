"""Script to insert test weather data for multiple days."""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import location as location_crud
from app.crud import weather_reading as weather_crud
from app.crud import user as user_crud
from app.schemas.weather import WeatherReadingCreate
from app.schemas.user import UserCreate
import random

def insert_test_data(location_name: str = "Bremen,DE", days_back: int = 7, readings_per_day: int = 6, username: str = None):
    """
    Insert test weather data for the specified location.
    
    Args:
        location_name: Name of the location (e.g., "Bremen,DE")
        days_back: Number of days to generate data for
        readings_per_day: Number of readings per day (currently fixed at 6)
        username: Username to use (if None, creates/uses a default test user)
    """
    db: Session = SessionLocal()
    
    try:
        # Get or create user
        if username:
            user = user_crud.get_user_by_username(db, username)
            if not user:
                print(f"User '{username}' not found!")
                print("Please create the user first via the frontend or API.")
                return
        else:
            # Use or create default test user
            username = "testuser"
            user = user_crud.get_user_by_username(db, username)
            if not user:
                print(f"Creating default test user '{username}'...")
                user_create = UserCreate(
                    username=username,
                    email="test@example.com",
                    password="testpassword123"
                )
                user = user_crud.create_user(db, user_create)
                print(f"✓ Created test user '{username}' (ID: {user.id})")
            else:
                print(f"Using existing user '{username}' (ID: {user.id})")
        
        # Get location for this user
        location = location_crud.get_location_by_name(db, location_name, user.id, case_sensitive=False)
        if not location:
            print(f"Location '{location_name}' not found for user '{username}'!")
            print(f"Available locations for this user:")
            locations = location_crud.get_all_locations(db, user.id)
            if locations:
                for loc in locations:
                    print(f"  - {loc.name} (ID: {loc.id})")
            else:
                print("  (No locations found)")
            return
        
        print(f"Inserting test data for {location.name} (ID: {location.id})...")
        
        # Generate data for the last N days
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        inserted_count = 0
        for day_offset in range(days_back):
            current_date = base_date - timedelta(days=day_offset)
            
            # Generate readings throughout the day (every 4 hours)
            for hour in range(0, 24, 4):
                timestamp = current_date + timedelta(hours=hour)
                
                # Generate realistic weather data with some variation
                base_temp = 8.0 + random.uniform(-5, 10)  # Temperature between 3-18°C
                temp_variation = 2 * (12 - hour) / 12  # Cooler at night, warmer during day
                temperature = base_temp + temp_variation + random.uniform(-2, 2)
                
                humidity = 60 + random.uniform(-20, 20)  # Humidity 40-80%
                humidity = max(30, min(90, humidity))  # Clamp to reasonable range
                
                # Precipitation: sometimes rain, mostly none
                precipitation = random.choices(
                    [0.0, random.uniform(0.1, 5.0)],
                    weights=[0.7, 0.3]
                )[0]
                
                pressure = 1013 + random.uniform(-20, 20)  # Pressure around 1013 hPa
                
                descriptions = [
                    "Klarer Himmel", "Überwiegend klar", "Teilweise bewölkt",
                    "Bedeckt", "Leichter Regen", "Mäßiger Regen"
                ]
                description = random.choice(descriptions)
                
                # Create weather reading
                reading = WeatherReadingCreate(
                    location_id=location.id,
                    temperature=round(temperature, 1),
                    humidity=round(humidity, 1),
                    precipitation=round(precipitation, 2),
                    pressure=round(pressure, 1),
                    description=description,
                    timestamp=timestamp
                )
                
                weather_crud.create_weather_reading(db, reading)
                inserted_count += 1
        
        print(f"✓ Successfully inserted {inserted_count} weather readings!")
        print(f"  Data spans {days_back} days with {readings_per_day} readings per day")
        print(f"  User: {username} (ID: {user.id})")
        print(f"  Location: {location.name} (ID: {location.id})")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Usage: python insert_test_data.py [location_name] [days_back] [username]
    # Example: python insert_test_data.py "Bremen,DE" 7 "myuser"
    location_name = sys.argv[1] if len(sys.argv) > 1 else "Bremen,DE"
    days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    username = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("=" * 60)
    print("Weather Data Test Data Generator")
    print("=" * 60)
    print(f"Location: {location_name}")
    print(f"Days: {days_back}")
    print(f"Username: {username if username else 'testuser (default)'}")
    print("=" * 60)
    print()
    
    insert_test_data(location_name, days_back, username=username)

