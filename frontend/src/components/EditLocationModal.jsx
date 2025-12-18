import React, { useState, useEffect } from 'react'
import { getAuthHeaders } from '../utils/auth'
import './EditLocationModal.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function EditLocationModal({ location, isOpen, onClose, onUpdated }) {
  const [name, setName] = useState('')
  const [pollInterval, setPollInterval] = useState('30')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (location && isOpen) {
      setName(location.name || '')
      setPollInterval(String(location.poll_interval_minutes || 30))
    }
  }, [location, isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const updateData = {}
      
      if (name !== location.name) {
        updateData.name = name
      }
      
      const intervalValue = parseInt(pollInterval)
      if (isNaN(intervalValue) || intervalValue < 1 || intervalValue > 1440) {
        throw new Error('Abfrage-Intervall muss zwischen 1 und 1440 Minuten liegen')
      }
      
      if (intervalValue !== location.poll_interval_minutes) {
        updateData.poll_interval_minutes = intervalValue
      }

      if (Object.keys(updateData).length === 0) {
        onClose()
        return
      }

      const response = await fetch(`${API_BASE_URL}/locations/${location.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updateData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Fehler beim Aktualisieren')
      }

      onUpdated()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Ort bearbeiten</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="edit-name">Ortsname</label>
            <input
              id="edit-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          {location.lat && location.lon && (
            <div className="coordinates-display">
              <label>Koordinaten (nur Anzeige)</label>
              <div className="coordinates-value">
                {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
              </div>
              <small>Koordinaten können nicht geändert werden</small>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="edit-interval">
              Abfrage-Intervall (Minuten)
              <span className="help-text">Wie oft sollen Wetterdaten abgerufen werden?</span>
            </label>
            <input
              id="edit-interval"
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

          {error && <div className="error-message">{error}</div>}

          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Abbrechen
            </button>
            <button type="submit" disabled={loading}>
              {loading ? 'Wird gespeichert...' : 'Speichern'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EditLocationModal

