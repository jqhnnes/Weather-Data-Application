import React, { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { getAuthHeaders } from '../utils/auth'
import './SearchHistory.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function SearchHistory({ onSelectSearch, onClose }) {
  const [searches, setSearches] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    fetchSearchHistory()
  }, [])

  const fetchSearchHistory = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/search-history?limit=50`, {
        headers: getAuthHeaders()
      })
      if (response.ok) {
        const data = await response.json()
        setSearches(data.searches || [])
      }
    } catch (error) {
      console.error('Error fetching search history:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectSearch = (search) => {
    if (onSelectSearch) {
      onSelectSearch({
        locationId: search.location_id,
        locationName: search.location_name,
        startDate: search.start_date ? new Date(search.start_date) : null,
        endDate: search.end_date ? new Date(search.end_date) : null,
      })
    }
    if (onClose) {
      onClose()
    }
  }

  const handleDelete = async (e, searchId) => {
    e.stopPropagation() // Prevent triggering the select search
    if (!window.confirm('Möchten Sie diesen Eintrag wirklich löschen?')) {
      return
    }

    setDeleting(searchId)
    try {
      const response = await fetch(`${API_BASE_URL}/search-history/${searchId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      
      if (response.ok) {
        // Remove from list
        setSearches(searches.filter(s => s.id !== searchId))
      } else {
        alert('Fehler beim Löschen des Eintrags')
      }
    } catch (error) {
      console.error('Error deleting search history:', error)
      alert('Fehler beim Löschen des Eintrags')
    } finally {
      setDeleting(null)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    try {
      return format(new Date(dateString), 'dd.MM.yyyy HH:mm')
    } catch {
      return dateString
    }
  }

  const formatDateRange = (start, end) => {
    if (!start && !end) return 'Kein Zeitraum'
    if (start && end) {
      return `${format(new Date(start), 'dd.MM.yyyy')} - ${format(new Date(end), 'dd.MM.yyyy')}`
    }
    if (start) {
      return `Ab ${format(new Date(start), 'dd.MM.yyyy')}`
    }
    if (end) {
      return `Bis ${format(new Date(end), 'dd.MM.yyyy')}`
    }
    return '-'
  }

  return (
    <div className="search-history-modal">
      <div className="search-history-content">
        <div className="search-history-header">
          <h2>Suchverlauf</h2>
          <button className="close-btn" onClick={onClose} title="Schließen">
            ×
          </button>
        </div>

        {loading ? (
          <div className="loading">Lade Suchverlauf...</div>
        ) : searches.length === 0 ? (
          <div className="no-searches">
            <p>Noch keine Suchen gespeichert</p>
          </div>
        ) : (
          <div className="searches-list">
            {searches.map(search => (
              <div
                key={search.id}
                className="search-item"
                onClick={() => handleSelectSearch(search)}
              >
                <div className="search-item-main">
                  <div className="search-location">
                    <strong>{search.location_name || 'Unbekannter Ort'}</strong>
                  </div>
                  <div className="search-date-range">
                    {formatDateRange(search.start_date, search.end_date)}
                  </div>
                </div>
                <div className="search-item-meta">
                  <span className="search-time">{formatDate(search.created_at)}</span>
                  <button
                    className="delete-search-btn"
                    onClick={(e) => handleDelete(e, search.id)}
                    disabled={deleting === search.id}
                    title="Löschen"
                  >
                    {deleting === search.id ? '...' : '×'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchHistory

