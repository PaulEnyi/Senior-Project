import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { FiLock, FiUser, FiEye, FiEyeOff } from 'react-icons/fi'
import toast from 'react-hot-toast'
import { authService } from '../../services/authService'

const AdminLogin = ({ onLogin }) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!username || !password) {
      toast.error('Please enter username and password')
      return
    }

    setIsLoading(true)

    try {
      const response = await authService.adminLogin(username, password)
      
      if (response.access_token) {
        // Store token
        localStorage.setItem('auth_token', response.access_token)
        
        // Call parent login handler
        onLogin({
          username,
          role: response.role,
          token: response.access_token
        })

        toast.success('Welcome to Admin Dashboard!')
        navigate('/admin')
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (error) {
      console.error('Login error:', error)
      toast.error(error.message || 'Invalid credentials')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="admin-login-page">
      <motion.div
        className="login-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-header">
          <img 
            src="/assets/morgan-logo/morgan-logo.png" 
            alt="Morgan State" 
            className="login-logo"
          />
          <h1>Admin Login</h1>
          <p>Morgan AI Chatbot Administration</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">
              <FiUser />
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              disabled={isLoading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              <FiLock />
              Password
            </label>
            <div className="password-input">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="password-toggle"
              >
                {showPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </div>

          <motion.button
            type="submit"
            className="login-button"
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <span className="loading-spinner">Logging in...</span>
            ) : (
              'Login'
            )}
          </motion.button>
        </form>

        <div className="login-footer">
          <p>Authorized personnel only</p>
          <a href="/" className="back-link">
            Back to Chat
          </a>
        </div>
      </motion.div>
    </div>
  )
}

export default AdminLogin