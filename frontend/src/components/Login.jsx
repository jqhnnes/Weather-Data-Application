import React, { useState } from 'react'
import './Login.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function Login({ onLoginSuccess, onSwitchToRegister }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login fehlgeschlagen')
      }

      const data = await response.json()
      
      // Store token in localStorage
      localStorage.setItem('access_token', data.access_token)
      
      // Call success callback
      onLoginSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Anmelden</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Benutzername</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Passwort</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Wird angemeldet...' : 'Anmelden'}
          </button>
          <button
            type="button"
            className="switch-btn"
            onClick={onSwitchToRegister}
          >
            Noch kein Konto? Registrieren
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login

