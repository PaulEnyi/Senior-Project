import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiEye, FiEyeOff, FiLock, FiUser, FiShield } from 'react-icons/fi';
import { apiService } from '../../services/api';
import './AdminLogin.css';

const AdminLogin = ({ onLogin, onClose, isOpen = true }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState({});

  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation errors when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    // Clear general error
    if (error) {
      setError('');
    }
  };

  // Validate form
  const validateForm = () => {
    const errors = {};
    
    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await apiService.adminLogin({
        username: formData.username.trim(),
        password: formData.password
      });
      
      // Call parent's onLogin callback with success
      onLogin({
        success: true,
        token: response.access_token,
        user: {
          username: formData.username,
          role: 'admin'
        }
      });
      
    } catch (err) {
      const errorMessage = err.message || 'Login failed. Please check your credentials.';
      setError(errorMessage);
      
      // Call parent's onLogin callback with failure
      onLogin({
        success: false,
        error: errorMessage
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'Enter' && !isLoading) {
      handleSubmit(e);
    }
  };

  // Animation variants
  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  };

  const modalVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8, 
      y: -50 
    },
    visible: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 25
      }
    },
    exit: {
      opacity: 0,
      scale: 0.8,
      y: -50,
      transition: {
        duration: 0.2
      }
    }
  };

  const inputVariants = {
    focus: {
      scale: 1.02,
      transition: { duration: 0.2 }
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="admin-login-backdrop"
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
          onClick={(e) => e.target === e.currentTarget && onClose()}
          onKeyDown={handleKeyDown}
          tabIndex={-1}
        >
          <motion.div
            className="admin-login-modal"
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            {/* Modal Header */}
            <div className="modal-header">
              <div className="header-content">
                <div className="admin-icon">
                  <FiShield />
                </div>
                <div className="header-text">
                  <h2>Admin Login</h2>
                  <p>Morgan AI Administration Portal</p>
                </div>
              </div>
              <button
                className="close-button"
                onClick={onClose}
                aria-label="Close admin login"
              >
                <FiX />
              </button>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="login-form">
              {/* General Error Message */}
              {error && (
                <motion.div
                  className="error-message"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <span className="error-icon">⚠️</span>
                  {error}
                </motion.div>
              )}

              {/* Username Field */}
              <div className="form-group">
                <label htmlFor="username" className="form-label">
                  <FiUser />
                  Username
                </label>
                <motion.div
                  className="input-wrapper"
                  variants={inputVariants}
                  whileFocus="focus"
                >
                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={formData.username}
                    onChange={handleInputChange}
                    className={`form-input ${validationErrors.username ? 'error' : ''}`}
                    placeholder="Enter admin username"
                    disabled={isLoading}
                    autoFocus
                    autoComplete="username"
                  />
                </motion.div>
                {validationErrors.username && (
                  <span className="field-error">{validationErrors.username}</span>
                )}
              </div>

              {/* Password Field */}
              <div className="form-group">
                <label htmlFor="password" className="form-label">
                  <FiLock />
                  Password
                </label>
                <motion.div
                  className="input-wrapper password-wrapper"
                  variants={inputVariants}
                  whileFocus="focus"
                >
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={handleInputChange}
                    className={`form-input ${validationErrors.password ? 'error' : ''}`}
                    placeholder="Enter admin password"
                    disabled={isLoading}
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    disabled={isLoading}
                  >
                    {showPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </motion.div>
                {validationErrors.password && (
                  <span className="field-error">{validationErrors.password}</span>
                )}
              </div>

              {/* Submit Button */}
              <motion.button
                type="submit"
                className="login-button"
                disabled={isLoading || !formData.username.trim() || !formData.password}
                whileHover={{ scale: isLoading ? 1 : 1.02 }}
                whileTap={{ scale: isLoading ? 1 : 0.98 }}
              >
                {isLoading ? (
                  <div className="loading-content">
                    <div className="spinner"></div>
                    Authenticating...
                  </div>
                ) : (
                  <>
                    <FiShield />
                    Access Admin Portal
                  </>
                )}
              </motion.button>
            </form>

            {/* Footer */}
            <div className="modal-footer">
              <p className="security-notice">
                <FiLock />
                Secure admin access for Morgan State University Computer Science Department
              </p>
              <div className="keyboard-hints">
                <kbd>Enter</kbd> to login • <kbd>Esc</kbd> to close
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AdminLogin;