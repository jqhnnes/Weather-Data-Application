import React, { useState, useEffect } from 'react'
import LocationList from './components/LocationList'
import WeatherChart from './components/WeatherChart'
import AddLocationForm from './components/AddLocationForm'
import SearchForm from './components/SearchForm'
import SearchHistory from './components/SearchHistory'
import ThemeToggle from './components/ThemeToggle'
import Login from './components/Login'
import Register from './components/Register'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if token exists in localStorage
    return !!localStorage.getItem('access_token')
  })
  const [showRegister, setShowRegister] = useState(false)
  const [registerSuccessMessage, setRegisterSuccessMessage] = useState(null)
  
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [weatherData, setWeatherData] = useState([])
  const [loading, setLoading] = useState(false)
  const [showSearchHistory, setShowSearchHistory] = useState(false)
  const [searchDateRange, setSearchDateRange] = useState({ startDate: null, endDate: null })
  const isSearchRef = React.useRef(false) // Track if location change is from search
  const [theme, setTheme] = useState(() => {
    // Load theme from localStorage or default to 'light'
    return localStorage.getItem('theme') || 'light'
  })

  useEffect(() => {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    if (isAuthenticated) {
      fetchLocations()
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (selectedLocation) {
      // Only reset date range and fetch if location was selected directly (not via search)
      if (!isSearchRef.current) {
        setSearchDateRange({ startDate: null, endDate: null })
        fetchWeatherData(selectedLocation.id)
      }
      // Reset the flag after handling
      isSearchRef.current = false
    }
  }, [selectedLocation])

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  const fetchLocations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/locations`, {
        headers: getAuthHeaders()
      })
      
      if (response.status === 401) {
        // Token expired or invalid
        handleLogout()
        return
      }
      
      const data = await response.json()
      setLocations(data.locations || [])
    } catch (error) {
      console.error('Error fetching locations:', error)
    }
  }

  const fetchWeatherData = async (locationId, startDate = null, endDate = null) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('limit', '1000')
      if (startDate) {
        params.append('start_date', startDate.toISOString())
      }
      if (endDate) {
        params.append('end_date', endDate.toISOString())
      }
      
      const url = `${API_BASE_URL}/weather/location/${locationId}?${params.toString()}`
      const response = await fetch(url, {
        headers: getAuthHeaders()
      })
      
      if (response.status === 401) {
        handleLogout()
        return
      }
      
      const data = await response.json()
      setWeatherData(data.readings || [])
    } catch (error) {
      console.error('Error fetching weather data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async ({ location, weatherData: searchWeatherData, startDate, endDate }) => {
    // Mark that this is a search, not a direct location selection
    isSearchRef.current = true
    // Store the search date range first
    setSearchDateRange({ startDate, endDate })
    // Then set location and data
    setSelectedLocation(location)
    setWeatherData(searchWeatherData)
  }

  const handleSearchHistorySelect = async ({ locationId, locationName, startDate, endDate }) => {
    const location = locations.find(loc => loc.id === locationId)
    if (location) {
      // Mark that this is a search, not a direct location selection
      isSearchRef.current = true
      // Store the search date range first
      setSearchDateRange({ startDate, endDate })
      // Then set location and fetch data
      setSelectedLocation(location)
      await fetchWeatherData(locationId, startDate, endDate)
    }
  }

  const handleLocationAdded = () => {
    fetchLocations()
  }

  const handleLocationDeleted = () => {
    setSelectedLocation(null)
    setWeatherData([])
    fetchLocations()
  }

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light')
  }

  const handleLoginSuccess = () => {
    setIsAuthenticated(true)
    setShowRegister(false)
    setRegisterSuccessMessage(null)
  }

  const handleRegisterSuccess = (message) => {
    setRegisterSuccessMessage(message)
    setShowRegister(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsAuthenticated(false)
    setLocations([])
    setSelectedLocation(null)
    setWeatherData([])
  }

  const handleSwitchToRegister = () => {
    setShowRegister(true)
    setRegisterSuccessMessage(null)
  }

  const handleSwitchToLogin = () => {
    setShowRegister(false)
    setRegisterSuccessMessage(null)
  }

  // Show login/register if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="app">
        {showRegister ? (
          <Register
            onRegisterSuccess={handleRegisterSuccess}
            onSwitchToLogin={handleSwitchToLogin}
          />
        ) : (
          <Login
            onLoginSuccess={handleLoginSuccess}
            onSwitchToRegister={handleSwitchToRegister}
          />
        )}
        {registerSuccessMessage && (
          <div className="success-message-overlay">
            <div className="success-message">
              {registerSuccessMessage}
              <button onClick={handleSwitchToLogin}>Zur Anmeldung</button>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Weather Data Application</h1>
        <div className="header-actions">
          <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
          <button className="logout-btn" onClick={handleLogout} title="Abmelden">
            Abmelden
          </button>
        </div>
      </header>

      <main className="app-main">
        <div className="sidebar">
          <AddLocationForm onLocationAdded={handleLocationAdded} />
          <SearchForm
            locations={locations}
            onSearch={handleSearch}
            onSearchHistoryClick={() => setShowSearchHistory(true)}
          />
          <LocationList
            locations={locations}
            selectedLocation={selectedLocation}
            onSelectLocation={setSelectedLocation}
            onLocationDeleted={handleLocationDeleted}
          />
        </div>

        <div className="content">
          {selectedLocation ? (
            <WeatherChart
              location={selectedLocation}
              weatherData={weatherData}
              loading={loading}
              searchDateRange={searchDateRange}
              onRefresh={() => fetchWeatherData(selectedLocation.id, searchDateRange.startDate, searchDateRange.endDate)}
            />
          ) : (
            <div className="placeholder">
              <p>Wähle einen Ort aus, um Wetterdaten anzuzeigen</p>
            </div>
          )}
        </div>
      </main>

      {showSearchHistory && (
        <SearchHistory
          onSelectSearch={handleSearchHistorySelect}
          onClose={() => setShowSearchHistory(false)}
        />
      )}
    </div>
  )
}

export default App

