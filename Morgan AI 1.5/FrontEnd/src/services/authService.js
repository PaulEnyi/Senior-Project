import api from './api'

export const authService = {
  async adminLogin(username, password) {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await api.post('/api/admin/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      return response.data
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || 
        'Invalid credentials. Please check your username and password.'
      )
    }
  },

  async verifyToken(token) {
    try {
      // In a real app, you'd verify with the backend
      // For now, check if token exists and hasn't expired
      if (!token) return false
      
      const payload = this.decodeToken(token)
      if (!payload) return false
      
      // Check expiration
      const now = Date.now() / 1000
      if (payload.exp && payload.exp < now) {
        return false
      }
      
      return true
    } catch (error) {
      console.error('Token verification error:', error)
      return false
    }
  },

  decodeToken(token) {
    try {
      // Decode JWT token (simple base64 decode for payload)
      const parts = token.split('.')
      if (parts.length !== 3) return null
      
      const payload = JSON.parse(atob(parts[1]))
      return payload
    } catch (error) {
      console.error('Token decode error:', error)
      return null
    }
  },

  logout() {
    localStorage.removeItem('auth_token')
    window.location.href = '/'
  },

  isAuthenticated() {
    const token = localStorage.getItem('auth_token')
    return this.verifyToken(token)
  },

  getToken() {
    return localStorage.getItem('auth_token')
  },

  getCurrentUser() {
    const token = this.getToken()
    if (!token) return null
    
    const payload = this.decodeToken(token)
    if (!payload) return null
    
    return {
      username: payload.sub,
      role: payload.role,
      user_id: payload.user_id
    }
  }
}