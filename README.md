# Weather Data Application

FastAPI-based application for storing and managing weather data for configurable locations. The application uses the Open-Meteo API (no API key required) and supports multi-user authentication.

## Features

- **Multi-User Support**: Each user manages their own locations and weather data
- **JWT Authentication**: Secure user login and authorization
- **Automatic Data Collection**: Background scheduler fetches weather data at configurable intervals
- **React Frontend**: Modern, responsive user interface with Dark/Light mode
- **Data Visualization**: Charts for temperature, humidity, and precipitation
- **Search Functionality**: Search by location and time range with search history

## Quickstart

### 1. Create Environment

**With Conda (recommended):**
```bash
conda env create -f environment.yml
conda activate weather-env
```

**Alternatively with venv:**
```bash
python -m venv .venv
.\.venv\Scripts\activate  # PowerShell
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project directory:
```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:55432/weather
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Start Database (PostgreSQL with Docker)

```bash
docker run --name weather-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=weather -p 55432:5432 -d postgres:16
```

**Note:** Tables are created automatically on first startup.

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

The backend will run on `http://127.0.0.1:8000`

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

## Database GUI (Adminer)

To view database tables in a web interface:

```bash
docker run --name adminer -p 8080:8080 -d adminer
```

Then open in your browser: `http://localhost:8080`

**Login credentials:**
- Login: `admin@admin.com` / `admin`

**Connection settings:**
- System: `PostgreSQL`
- Server: `host.docker.internal:55432`
- Username: `postgres`
- Password: `postgres`
- Database: `weather`

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user (returns JWT token)
- `GET /auth/me` - Get current user information

**Note:** All other endpoints require authentication (JWT token in Authorization header).

### Locations

- `POST /locations` - Create a new location
- `GET /locations` - Get all locations for the current user
- `GET /locations/{location_id}` - Get a specific location
- `GET /locations/{location_id}/with-weather` - Get location with latest weather data
- `PUT /locations/{location_id}` - Update a location
- `DELETE /locations/{location_id}` - Delete a location
- `GET /locations/check-name` - Check if location name already exists

### Weather Data

- `GET /weather/current` - Get current weather data (without saving)
- `GET /weather/location/{location_id}` - Get stored weather data for a location
- `POST /weather/location/{location_id}/fetch` - Manually fetch and save weather data

### Search History

- `POST /search-history` - Save a search to history
- `GET /search-history` - Get search history
- `DELETE /search-history/{search_id}` - Delete a search history entry

## Data Model

### Users (users)
- `id` - Unique user ID
- `username` - Username (unique)
- `email` - Email address (unique)
- `hashed_password` - Hashed password (bcrypt)
- `is_active` - Status (active/inactive)
- `created_at` - Creation timestamp

### Locations (locations)
- `id` - Unique location ID
- `user_id` - Associated user
- `name` - Location name (e.g., "Bremen,DE")
- `lat` - Latitude
- `lon` - Longitude
- `poll_interval_minutes` - Polling interval in minutes (default: 30)
- `created_at` - Creation timestamp

### Weather Data (weather_readings)
- `id` - Unique reading ID
- `location_id` - Associated location
- `temperature` - Temperature in °C
- `humidity` - Humidity in %
- `precipitation` - Precipitation in mm
- `pressure` - Air pressure in hPa
- `description` - Weather description
- `timestamp` - Measurement timestamp
- `created_at` - Creation timestamp

### Search History (search_history)
- `id` - Unique search ID
- `user_id` - Associated user
- `location_id` - Searched location (optional)
- `location_name` - Location name
- `start_date` - Start date (optional)
- `end_date` - End date (optional)
- `search_params` - Additional search parameters (JSON)
- `created_at` - Search timestamp

## How It Works

1. **Startup**: On startup, all database tables are created and the background scheduler is started
2. **Automatic Data Collection**: The scheduler regularly fetches weather data for all saved locations (configurable interval per location)
3. **Multi-User Separation**: Each user only sees their own locations and data
4. **Authentication**: All API endpoints (except Register/Login) require a valid JWT token

## Frontend (React)

The frontend is a React application with Vite.

**Features:**
- User registration and login
- Add and manage locations
- Display weather data as charts (temperature, humidity, precipitation)
- Visualize historical data (daily and hourly view)
- Search functionality by location and time range
- View and manage search history
- Dark/Light mode toggle
- Responsive design

## Insert Test Data

To test the application with test data, you can use the `insert_test_data.py` script:

```bash
# Default: Creates/uses "testuser" for "Bremen,DE" with 7 days
python insert_test_data.py

# For a different location
python insert_test_data.py "Frankfurt,DE"

# For more days
python insert_test_data.py "Bremen,DE" 14

# For a specific user
python insert_test_data.py "Bremen,DE" 7 "myusername"
```

The script automatically creates:
- Weather data for the last N days
- 6 readings per day (every 4 hours: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
- Realistic values with variations (temperature, humidity, precipitation)
- Daily variations (cooler at night, warmer during day)

**Note:** 
- If no username is provided, a `testuser` is automatically created/used
- The location must already exist in the database (e.g., created via frontend or API)
- The location must belong to the specified user

## Technology Stack

**Backend:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database (via Docker)
- APScheduler - Background scheduler
- JWT (python-jose) - Authentication
- bcrypt - Password hashing
- Open-Meteo API - Weather data (free, no API key)

**Frontend:**
- React - UI framework
- Vite - Build tool
- Chart.js - Data visualization
- date-fns - Date formatting

## Notes

- Uses Open-Meteo API (no API key required)
- Defaults to SQLite file `weather.db` in project root; switch to PostgreSQL via `DATABASE_URL`
- All API endpoints (except `/auth/register` and `/auth/login`) require authentication
- JWT tokens are sent in the `Authorization: Bearer <token>` header
