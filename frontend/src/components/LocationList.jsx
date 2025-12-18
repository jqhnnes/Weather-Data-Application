import React, { useState } from 'react'
import EditLocationModal from './EditLocationModal'
import { getAuthHeaders } from '../utils/auth'
import './LocationList.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function LocationList({ locations, selectedLocation, onSelectLocation, onLocationDeleted }) {
  const [deleting, setDeleting] = useState(null)
  const [editingLocation, setEditingLocation] = useState(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  const handleDelete = async (locationId, e) => {
    e.stopPropagation()
    
    if (!confirm('Möchten Sie diesen Ort wirklich löschen? Alle Wetterdaten werden ebenfalls gelöscht.')) {
      return
    }

    setDeleting(locationId)
    try {
      const response = await fetch(`${API_BASE_URL}/locations/${locationId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })

      if (response.ok) {
        onLocationDeleted()
      } else {
        alert('Fehler beim Löschen des Ortes')
      }
    } catch (error) {
      console.error('Error deleting location:', error)
      alert('Fehler beim Löschen des Ortes')
    } finally {
      setDeleting(null)
    }
  }

  const handleEdit = (location, e) => {
    e.stopPropagation()
    setEditingLocation(location)
    setIsEditModalOpen(true)
  }

  const handleEditClose = () => {
    setIsEditModalOpen(false)
    setEditingLocation(null)
  }

  const handleEditUpdated = () => {
    onLocationDeleted() // Refresh list
  }

  return (
    <div className="location-list">
      <h2>Orte ({locations.length})</h2>
      {locations.length === 0 ? (
        <p className="empty-message">Noch keine Orte hinzugefügt</p>
      ) : (
        <ul className="location-items">
          {locations.map((location) => (
            <li
              key={location.id}
              className={`location-item ${selectedLocation?.id === location.id ? 'selected' : ''}`}
              onClick={() => onSelectLocation(location)}
            >
              <div className="location-info">
                <h3>{location.name}</h3>
                {location.lat && location.lon && (
                  <p className="coordinates">
                    {location.lat.toFixed(2)}, {location.lon.toFixed(2)}
                  </p>
                )}
              </div>
              <div className="location-actions">
                <button
                  className="edit-btn"
                  onClick={(e) => handleEdit(location, e)}
                  title="Ort bearbeiten"
                >
                  ⚙️
                </button>
                <button
                  className="delete-btn"
                  onClick={(e) => handleDelete(location.id, e)}
                  disabled={deleting === location.id}
                  title="Ort löschen"
                >
                  {deleting === location.id ? '...' : '×'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <EditLocationModal
        location={editingLocation}
        isOpen={isEditModalOpen}
        onClose={handleEditClose}
        onUpdated={handleEditUpdated}
      />
    </div>
  )
}

export default LocationList

