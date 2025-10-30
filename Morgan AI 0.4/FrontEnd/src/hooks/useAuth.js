import { useState, useEffect, useCallback } from 'react'
import { authService } from '../services/authService'

export const useAuth = () => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing auth on mount
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      
      if (token) {
        // Verify token with backend
        const isValid = await authService.verifyToken(token)
        
        if (isValid) {
          // Get user info from token
          const userData = authService.decodeToken(token)
          setUser(userData)
          setIsAuthenticated(true)
        } else {
          // Clear invalid token
          localStorage.removeItem('auth_token')
          setUser(null)
          setIsAuthenticated(false)
        }
      }
    } catch (error) {
      console.error('Auth check error:', error)
      setUser(null)
      setIsAuthenticated(false)
    } finally {
      setIsLoading(false)
    }
  }

  const login = useCallback(async (credentials) => {
    try {
      setIsLoading(true)
      
      const response = await authService.adminLogin(
        credentials.username,
        credentials.password
      )
      
      if (response.access_token) {
        // Store token
        localStorage.setItem('auth_token', response.access_token)
        
        // Set user data
        const userData = {
          username: credentials.username,
          role: response.role,
          user_id: response.user_id || 'admin'
        }
        
        setUser(userData)
        setIsAuthenticated(true)
        
        return { success: true, user: userData }
      }
      
      throw new Error('Invalid response from server')
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error.message || 'Login failed' 
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    // Clear auth data
    localStorage.removeItem('auth_token')
    setUser(null)
    setIsAuthenticated(false)
    
    // Redirect to home
    window.location.href = '/'
  }, [])

  const updateUser = useCallback((userData) => {
    setUser(prev => ({ ...prev, ...userData }))
  }, [])

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    updateUser
  }
}