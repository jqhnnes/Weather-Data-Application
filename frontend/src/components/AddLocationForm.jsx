import React, { useState } from 'react'
import { getAuthHeaders } from '../utils/auth'
import './AddLocationForm.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function AddLocationForm({ onLocationAdded }) {
  const [name, setName] = useState('')
  const [lat, setLat] = useState('')
  const [lon, setLon] = useState('')
  const [pollInterval, setPollInterval] = useState('30')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [resolvedName, setResolvedName] = useState(null)
  const [resolvingName, setResolvingName] = useState(false)
  const [existingLocation, setExistingLocation] = useState(null)
  const [checkingExisting, setCheckingExisting] = useState(false)

  // Resolve name from coordinates and check if location already exists
  React.useEffect(() => {
    const resolveNameFromCoordinates = async () => {
      // Case 1: Only coordinates provided - resolve name and check
      if (lat.trim() && lon.trim() && !name.trim()) {
        const latNum = parseFloat(lat)
        const lonNum = parseFloat(lon)
        
        if (!isNaN(latNum) && !isNaN(lonNum) && latNum >= -90 && latNum <= 90 && lonNum >= -180 && lonNum <= 180) {
          setResolvingName(true)
          setCheckingExisting(true)
          
          try {
            // First, resolve the name from coordinates
            const response = await fetch(
              `${API_BASE_URL}/weather/current?lat=${latNum}&lon=${lonNum}`,
              { headers: getAuthHeaders() }
            )
            if (response.ok) {
              const data = await response.json()
              if (data.data?.location) {
                const resolvedLocationName = data.data.location
                setResolvedName(resolvedLocationName)
                
                // Check if a location with this name already exists (independent of coordinates)
                const checkNameResponse = await fetch(
                  `${API_BASE_URL}/locations/check-name?name=${encodeURIComponent(resolvedLocationName)}`,
                  { headers: getAuthHeaders() }
                )
                if (checkNameResponse.ok) {
                  const checkData = await checkNameResponse.json()
                  if (checkData.exists) {
                    setExistingLocation(checkData.location)
                  } else {
                    setExistingLocation(null)
                  }
                }
              }
            }
          } catch (err) {
            // Silently fail - will be resolved on submit
            setExistingLocation(null)
          } finally {
            setResolvingName(false)
            setCheckingExisting(false)
          }
        }
      } 
      // Case 2: Name provided - check if it already exists
      else if (name.trim() && name.trim().length > 0) {
        setCheckingExisting(true)
        try {
          const checkNameResponse = await fetch(
            `${API_BASE_URL}/locations/check-name?name=${encodeURIComponent(name.trim())}`,
            { headers: getAuthHeaders() }
          )
          if (checkNameResponse.ok) {
            const checkData = await checkNameResponse.json()
            if (checkData.exists) {
              setExistingLocation(checkData.location)
            } else {
              setExistingLocation(null)
            }
          }
        } catch (err) {
          setExistingLocation(null)
        } finally {
          setCheckingExisting(false)
        }
      } 
      // Case 3: Nothing provided - reset
      else {
        setResolvedName(null)
        setExistingLocation(null)
      }
    }

    const timeoutId = setTimeout(resolveNameFromCoordinates, 500) // Debounce
    return () => clearTimeout(timeoutId)
  }, [lat, lon, name])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      // Validierung: Entweder Name oder beide Koordinaten müssen vorhanden sein
      const hasName = name.trim().length > 0
      const hasLat = lat.trim().length > 0
      const hasLon = lon.trim().length > 0
      
      if (!hasName && (!hasLat || !hasLon)) {
        throw new Error('Bitte geben Sie entweder einen Ortsnamen oder beide Koordinaten (lat und lon) ein')
      }

      const intervalValue = parseInt(pollInterval)
      if (isNaN(intervalValue) || intervalValue < 1 || intervalValue > 1440) {
        throw new Error('Abfrage-Intervall muss zwischen 1 und 1440 Minuten liegen')
      }

      const body = { 
        poll_interval_minutes: intervalValue
      }
      
      // Name hinzufügen, wenn vorhanden
      if (hasName) {
        body.name = name.trim()
      }
      
      // Koordinaten hinzufügen, wenn vorhanden
      if (hasLat && hasLon) {
        body.lat = parseFloat(lat)
        body.lon = parseFloat(lon)
      }

      const response = await fetch(`${API_BASE_URL}/locations?fetch_weather=true`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Fehler beim Erstellen des Ortes')
      }

      setSuccess(true)
      setName('')
      setLat('')
      setLon('')
      setPollInterval('30')
      setShowAdvanced(false)
      onLocationAdded()

      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="add-location-form">
      <h2>Neuen Ort hinzufügen</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="location-name">Ortsname</label>
          <input
            id="location-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="z.B. Bremen,DE"
            required={!lat || !lon}
            disabled={loading}
          />
        </div>

        <button
          type="button"
          className="toggle-advanced"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '▼' : '▶'} Erweiterte Optionen
        </button>

        {showAdvanced && (
          <div className="advanced-options">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="location-lat">Breitengrad (lat)</label>
                <input
                  id="location-lat"
                  type="number"
                  step="0.0001"
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  placeholder="z.B. 53.08"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="location-lon">Längengrad (lon)</label>
                <input
                  id="location-lon"
                  type="number"
                  step="0.0001"
                  value={lon}
                  onChange={(e) => setLon(e.target.value)}
                  placeholder="z.B. 8.80"
                  disabled={loading}
                />
              </div>
            </div>
            
            {lat && lon && !name && (
              <div className="coordinate-preview">
                {checkingExisting || resolvingName ? (
                  <div className="resolving-name">
                    <span className="spinner">⏳</span> Prüfe Koordinaten und ermittle Ortsname...
                  </div>
                ) : existingLocation ? (
                  <div className="existing-location-warning">
                    <span className="warning-icon">⚠️</span> 
                    <div>
                      <strong>Ort bereits vorhanden:</strong> {existingLocation.name}
                      <br />
                      <small>Koordinaten: {existingLocation.lat.toFixed(4)}, {existingLocation.lon.toFixed(4)}</small>
                    </div>
                  </div>
                ) : resolvedName ? (
                  <div className="resolved-name">
                    <span className="check-icon">✓</span> Ermittelter Ort: <strong>{resolvedName}</strong>
                  </div>
                ) : (
                  <div className="coordinate-info">
                    <span className="info-icon">ℹ️</span> Der Ortsname wird automatisch aus den Koordinaten ermittelt
                  </div>
                )}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="location-interval">
                Abfrage-Intervall (Minuten)
              </label>
              <input
                id="location-interval"
                type="number"
                min="1"
                max="1440"
                value={pollInterval}
                onChange={(e) => setPollInterval(e.target.value)}
                required
                disabled={loading}
              />
              <div className="interval-hint">
                {(() => {
                  const interval = parseInt(pollInterval)
                  if (isNaN(interval) || interval < 1) {
                    return 'Bitte geben Sie eine Zahl zwischen 1 und 1440 ein'
                  }
                  if (interval === 1) return 'Wird jede Minute abgerufen'
                  if (interval < 60) return `Wird alle ${interval} Minuten abgerufen`
                  if (interval === 60) return 'Wird stündlich abgerufen'
                  if (interval < 1440) return `Wird alle ${Math.round(interval / 60)} Stunden abgerufen`
                  if (interval === 1440) return 'Wird täglich abgerufen'
                  return 'Maximal 1440 Minuten (24 Stunden)'
                })()}
              </div>
            </div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">Ort erfolgreich hinzugefügt!</div>}

        <button 
          type="submit" 
          disabled={loading || (!name.trim() && (!lat.trim() || !lon.trim())) || existingLocation !== null}
        >
          {loading ? 'Wird hinzugefügt...' : existingLocation ? 'Ort bereits vorhanden' : 'Ort hinzufügen'}
        </button>
      </form>
    </div>
  )
}

export default AddLocationForm

