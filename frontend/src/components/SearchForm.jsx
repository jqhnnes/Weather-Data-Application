import React, { useState } from 'react'
import { format } from 'date-fns'
import { getAuthHeaders } from '../utils/auth'
import './SearchForm.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function SearchForm({ locations, onSearch, onSearchHistoryClick }) {
  const [selectedLocationId, setSelectedLocationId] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Validate dates
      if (startDate && endDate) {
        const start = new Date(startDate)
        const end = new Date(endDate)
        if (start > end) {
          throw new Error('Startdatum muss vor dem Enddatum liegen')
        }
      }

      if (!selectedLocationId) {
        throw new Error('Bitte wählen Sie einen Ort aus')
      }

      const selectedLocation = locations.find(loc => loc.id === parseInt(selectedLocationId))
      if (!selectedLocation) {
        throw new Error('Ort nicht gefunden')
      }

      // Build query parameters
      const params = new URLSearchParams()
      if (startDate) {
        params.append('start_date', new Date(startDate).toISOString())
      }
      if (endDate) {
        params.append('end_date', new Date(endDate).toISOString())
      }

      // Fetch weather data
      const response = await fetch(
        `${API_BASE_URL}/weather/location/${selectedLocationId}?${params.toString()}`,
        { headers: getAuthHeaders() }
      )
      
      if (!response.ok) {
        throw new Error('Fehler beim Laden der Wetterdaten')
      }

      const data = await response.json()
      
      // Save search to history
      try {
        await fetch(`${API_BASE_URL}/search-history`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            location_id: selectedLocation.id,
            location_name: selectedLocation.name,
            start_date: startDate ? new Date(startDate).toISOString() : null,
            end_date: endDate ? new Date(endDate).toISOString() : null,
          }),
        })
      } catch (err) {
        console.error('Error saving search history:', err)
        // Don't fail the search if history save fails
      }

      // Call parent callback with results
      onSearch({
        location: selectedLocation,
        weatherData: data.readings || [],
        startDate: startDate ? new Date(startDate) : null,
        endDate: endDate ? new Date(endDate) : null,
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setSelectedLocationId('')
    setStartDate('')
    setEndDate('')
    setError(null)
  }

  // Set default date range (last 7 days)
  const setDefaultDateRange = () => {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 7)
    
    setStartDate(format(start, 'yyyy-MM-dd'))
    setEndDate(format(end, 'yyyy-MM-dd'))
  }

  return (
    <div className="search-form">
      <div className="search-form-header">
        <h3>Suche</h3>
        <button
          type="button"
          className="search-history-btn"
          onClick={onSearchHistoryClick}
          title="Suchverlauf anzeigen"
        >
          📋
        </button>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="search-location">Ort</label>
          <select
            id="search-location"
            value={selectedLocationId}
            onChange={(e) => setSelectedLocationId(e.target.value)}
            required
            disabled={loading}
          >
            <option value="">-- Ort wählen --</option>
            {locations.map(location => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="search-start-date">Von (Datum)</label>
            <input
              id="search-start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="search-end-date">Bis (Datum)</label>
            <input
              id="search-end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={setDefaultDateRange}
            disabled={loading}
          >
            Letzte 7 Tage
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Zurücksetzen
          </button>
          <button type="submit" className="btn-primary" disabled={loading || !selectedLocationId}>
            {loading ? 'Suche...' : 'Suchen'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
      </form>
    </div>
  )
}

export default SearchForm

