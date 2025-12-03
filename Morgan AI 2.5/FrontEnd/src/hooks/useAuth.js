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
      
      console.log('🔐 Starting login process...')
      
      const response = await authService.adminLogin(
        credentials.username,
        credentials.password
      )
      
      if (response.access_token) {
        console.log('✅ Login successful - initializing session...')
        
        // Store token
        localStorage.setItem('auth_token', response.access_token)
        localStorage.setItem('token', response.access_token) // Backup for compatibility
        
        // Set user data
        const userData = {
          username: credentials.username,
          name: response.name || credentials.username,
          role: response.role,
          user_id: response.user_id || 'admin'
        }
        
        // Store user profile
        localStorage.setItem('user', JSON.stringify(userData))
        localStorage.setItem('user_profile', JSON.stringify(userData))
        
        setUser(userData)
        setIsAuthenticated(true)
        
        console.log('✅ Session initialized - user data stored')
        console.log('ℹ️ User will start with fresh chat interface')
        console.log('ℹ️ Previous chats available in Chat History')
        
        return { success: true, user: userData }
      }
      
      throw new Error('Invalid response from server')
    } catch (error) {
      console.error('❌ Login error:', error)
      return { 
        success: false, 
        error: error.message || 'Login failed' 
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      setIsLoading(true)
      
      console.log('🔐 Initiating user logout...')
      
      // Call authService logout which handles:
      // 1. Save current chat to backend
      // 2. Deactivate active threads
      // 3. Clear session data
      // 4. Redirect to login
      await authService.logout()
      
      // Clear local state
      setUser(null)
      setIsAuthenticated(false)
      
      console.log('✅ User logged out successfully')
      
    } catch (error) {
      console.error('❌ Logout error:', error)
      // Force logout on error
      localStorage.removeItem('auth_token')
      localStorage.removeItem('token')
      setUser(null)
      setIsAuthenticated(false)
      window.location.href = '/login'
    } finally {
      setIsLoading(false)
    }
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