/**
 * Utility functions for authentication
 */

export const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

export const getAuthHeadersFormData = () => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`
    // Note: Don't set Content-Type for FormData, browser will set it with boundary
  }
}

export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token')
}

export const logout = () => {
  localStorage.removeItem('access_token')
  window.location.reload()
}

