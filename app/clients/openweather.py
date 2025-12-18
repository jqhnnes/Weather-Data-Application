"""Open-Meteo API client (replaces OpenWeatherMap - no API key needed)."""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime


class OpenMeteoClient:
    """Client for Open-Meteo API (free, no API key required)."""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    
    def __init__(self):
        """Initialize client (no API key needed)."""
        pass
    
    def _geocode_city(self, city: str) -> tuple[float, float]:
        """
        Convert city name to coordinates using Open-Meteo Geocoding API.
        
        Args:
            city: City name (e.g., "Bremen,DE" or "Bremen")
        
        Returns:
            Tuple of (latitude, longitude)
        
        Raises:
            ValueError: If city not found
        """
        # Split city and country if provided
        parts = city.split(",")
        city_name = parts[0].strip()
        country = parts[1].strip() if len(parts) > 1 else None
        
        params = {
            "name": city_name,
            "count": 1,
            "language": "de",
            "format": "json"
        }
        
        if country:
            params["country"] = country
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(self.GEOCODING_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        if not data.get("results") or len(data["results"]) == 0:
            raise ValueError(f"City '{city}' not found")
        
        result = data["results"][0]
        return result["latitude"], result["longitude"]
    
    def _reverse_geocode(self, lat: float, lon: float) -> str:
        """
        Convert coordinates to city name using Open-Meteo Geocoding API.
        Uses a search with coordinates to find nearby locations.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            City name string (e.g., "Bremen, DE")
        
        Raises:
            ValueError: If location not found
        """
        # Open-Meteo Geocoding API supports reverse search via coordinates
        # We search for locations near the given coordinates
        params = {
            "latitude": lat,
            "longitude": lon,
            "count": 1,
            "language": "de",
            "format": "json"
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # Try reverse geocoding endpoint (if available) or use search with coordinates
                response = client.get(self.GEOCODING_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                # Format: "City, CountryCode" - use country code for consistency
                name_parts = []
                city_name = result.get("name", "").strip()
                country_code = result.get("country_code", "").strip()
                country = result.get("country", "").strip()
                
                # Add city name
                if city_name:
                    name_parts.append(city_name)
                
                # Prefer country code (2-letter ISO code) over full country name
                if country_code and len(country_code) == 2:
                    name_parts.append(country_code.upper())
                elif country and country != city_name:
                    # Fallback to country name if code not available
                    if country not in name_parts:
                        name_parts.append(country)
                
                # Return format: "City,CountryCode" (no space after comma for consistency)
                result_name = ",".join(name_parts) if name_parts else f"{lat:.4f},{lon:.4f}"
                return result_name
        except Exception:
            pass
        
        # Fallback: Use Nominatim (OpenStreetMap) for reverse geocoding
        try:
            nominatim_url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1,
                "accept-language": "de"
            }
            headers = {
                "User-Agent": "Weather-Data-Application/1.0"
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(nominatim_url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            address = data.get("address", {})
            name_parts = []
            
            # Get city/town/village name
            city_name = (address.get("city") or address.get("town") or address.get("village") or "").strip()
            if city_name:
                name_parts.append(city_name)
            
            # Get country code (ISO 3166-1 alpha-2) - Nominatim provides this
            country_code = address.get("country_code", "").strip().upper()
            if country_code and len(country_code) == 2:
                name_parts.append(country_code)
            else:
                # Fallback to country name if code not available
                country = address.get("country", "").strip()
                if country and country.lower() != city_name.lower():
                    if not any(part.lower() == country.lower() for part in name_parts):
                        name_parts.append(country)
            
            # Return format: "City,CountryCode" (no space after comma for consistency)
            result_name = ",".join(name_parts) if name_parts else f"{lat:.4f},{lon:.4f}"
            return result_name
        except Exception:
            pass
        
        # Final fallback: return coordinates as name
        return f"{lat:.4f},{lon:.4f}"
    
    def get_current_weather(
        self, 
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get current weather data for a location.
        
        Args:
            city: City name (e.g., "Bremen,DE")
            lat: Latitude (requires lon)
            lon: Longitude (requires lat)
        
        Returns:
            Dictionary with weather data (temp, humidity, precipitation, etc.)
        
        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If no valid location provided
        """
        # Get coordinates
        if city:
            lat, lon = self._geocode_city(city)
        elif lat is not None and lon is not None:
            pass  # Use provided coordinates
        else:
            raise ValueError("Either city or lat/lon must be provided")
        
        # Build API request
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,pressure_msl,weather_code",
            "timezone": "auto"
        }
        
        # Make API request
        with httpx.Client(timeout=10.0) as client:
            response = client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        current = data["current"]
        
        # Map weather codes to descriptions (simplified)
        weather_code = current.get("weather_code", 0)
        description = self._weather_code_to_description(weather_code)
        
        # Extract relevant data
        return {
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "precipitation": current.get("precipitation", 0.0),
            "pressure": current.get("pressure_msl", None),
            "description": description,
            "city": city if city else f"{lat:.2f},{lon:.2f}",
            "country": "",  # Open-Meteo doesn't provide country in current weather
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().timestamp(),  # Current time
            "raw_data": data  # Store full response for later use
        }
    
    def _weather_code_to_description(self, code: int) -> str:
        """Convert WMO weather code to description."""
        # Simplified mapping (WMO Weather interpretation codes)
        codes = {
            0: "Klarer Himmel",
            1: "Überwiegend klar",
            2: "Teilweise bewölkt",
            3: "Bedeckt",
            45: "Nebel",
            48: "Gefrierender Nebel",
            51: "Leichter Nieselregen",
            53: "Mäßiger Nieselregen",
            55: "Starker Nieselregen",
            61: "Leichter Regen",
            63: "Mäßiger Regen",
            65: "Starker Regen",
            71: "Leichter Schneefall",
            73: "Mäßiger Schneefall",
            75: "Starker Schneefall",
            80: "Leichte Regenschauer",
            81: "Mäßige Regenschauer",
            82: "Starke Regenschauer",
            85: "Leichte Schneeschauer",
            86: "Starke Schneeschauer",
            95: "Gewitter",
            96: "Gewitter mit Hagel",
            99: "Gewitter mit starkem Hagel"
        }
        return codes.get(code, f"Unbekannt (Code: {code})")


# Convenience function
def get_current_weather(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> Dict[str, Any]:
    """Convenience function to get current weather."""
    client = OpenMeteoClient()
    return client.get_current_weather(city=city, lat=lat, lon=lon)
