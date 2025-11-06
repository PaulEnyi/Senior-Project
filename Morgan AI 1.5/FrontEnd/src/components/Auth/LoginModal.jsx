import React, { useState } from 'react';
import { FiX, FiUser, FiLock, FiMail, FiEye, FiEyeOff, FiUserPlus, FiLogIn, FiPhone } from 'react-icons/fi';
import { FaGoogle, FaApple, FaMicrosoft } from 'react-icons/fa';
import '../../styles/auth.css';

export default function LoginModal({ onLogin, onClose }) {
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const validateForm = () => {
    if (!formData.email) {
      setError('Email address is required');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    if (!formData.password) {
      setError('Password is required');
      return false;
    }

    if (isSignup) {
      if (!formData.fullName) {
        setError('Full name is required for signup');
        return false;
      }
      if (!formData.username) {
        setError('Username is required for signup');
        return false;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return false;
      }
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const endpoint = isSignup ? '/api/auth/signup' : '/api/auth/login';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          email: isSignup ? formData.email : undefined,
          full_name: isSignup ? formData.fullName : undefined
        })
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.token || data.access_token);
        onLogin(data.user || { name: formData.username, username: formData.username });
        onClose();
      } else {
        setError(data.detail || data.message || (isSignup ? 'Signup failed' : 'Invalid credentials'));
      }
    } catch (err) {
      setError(isSignup ? 'Signup failed. Please try again.' : 'Login failed. Please try again.');
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsSignup(!isSignup);
    setError('');
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      fullName: ''
    });
  };

  const handleSocialLogin = async (provider) => {
    try {
      setError('');
      setLoading(true);
      
      // Social login would integrate with OAuth providers here
      console.log(`Initiating ${provider} login...`);
      
      // For now, show a message that this feature is coming soon
      setError(`${provider} login will be available soon. Please use email/password for now.`);
      
      // In production, you would redirect to OAuth provider:
      // window.location.href = `http://localhost:8000/api/auth/${provider}/login`;
      
    } catch (err) {
      setError(`${provider} login failed. Please try again.`);
      console.error('Social login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePhoneLogin = async () => {
    try {
      setError('');
      setLoading(true);
      
      // Phone login would integrate with SMS verification here
      console.log('Initiating phone login...');
      
      setError('Phone login will be available soon. Please use email/password for now.');
      
    } catch (err) {
      setError('Phone login failed. Please try again.');
      console.error('Phone login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-container" onClick={(e) => e.stopPropagation()}>
        <button className="auth-close-btn" onClick={onClose} title="Close">
          <FiX />
        </button>

        <div className="auth-modal-content">
          {/* Left Side - Branding */}
          <div className="auth-branding-side">
            <div className="branding-content">
              <div className="branding-logo">
                <img src="/assets/morgan-logo.png" alt="Morgan State University" />
              </div>
              <h2 className="branding-title">Morgan AI Assistant</h2>
              <p className="branding-subtitle">Computer Science Department</p>
              <div className="branding-features">
                <div className="feature-item">
                  <div className="feature-icon">✨</div>
                  <div className="feature-text">
                    <h4>Smart Assistance</h4>
                    <p>Get instant answers about courses, programs, and resources</p>
                  </div>
                </div>
                <div className="feature-item">
                  <div className="feature-icon">🎓</div>
                  <div className="feature-text">
                    <h4>Academic Support</h4>
                    <p>Access tutoring, advising, and career resources</p>
                  </div>
                </div>
                <div className="feature-item">
                  <div className="feature-icon">💼</div>
                  <div className="feature-text">
                    <h4>Career Guidance</h4>
                    <p>Explore internships and job opportunities</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Form */}
          <div className="auth-form-side">
            <div className="auth-form-container">
              <div className="auth-header">
                <div className="auth-icon-circle">
                  {isSignup ? <FiUserPlus /> : <FiLogIn />}
                </div>
                <h2 className="auth-title">{isSignup ? 'Create Account' : 'Welcome Back'}</h2>
                <p className="auth-description">
                  {isSignup 
                    ? 'Sign up to access personalized AI assistance' 
                    : 'Log in or sign up to get smarter responses, upload files and images, and more.'}
                </p>
              </div>

              {/* Social Login Buttons */}
              <div className="social-login-section">
                <button 
                  type="button" 
                  className="social-login-btn google-btn"
                  onClick={() => handleSocialLogin('Google')}
                  disabled={loading}
                >
                  <FaGoogle className="social-icon" />
                  <span>Continue with Google</span>
                </button>

                <button 
                  type="button" 
                  className="social-login-btn apple-btn"
                  onClick={() => handleSocialLogin('Apple')}
                  disabled={loading}
                >
                  <FaApple className="social-icon" />
                  <span>Continue with Apple</span>
                </button>

                <button 
                  type="button" 
                  className="social-login-btn microsoft-btn"
                  onClick={() => handleSocialLogin('Microsoft')}
                  disabled={loading}
                >
                  <FaMicrosoft className="social-icon" />
                  <span>Continue with Microsoft</span>
                </button>

                <button 
                  type="button" 
                  className="social-login-btn phone-btn"
                  onClick={handlePhoneLogin}
                  disabled={loading}
                >
                  <FiPhone className="social-icon" />
                  <span>Continue with phone</span>
                </button>
              </div>

              {/* Divider */}
              <div className="auth-divider-section">
                <div className="divider-line"></div>
                <span className="divider-text-center">OR</span>
                <div className="divider-line"></div>
              </div>

              <form className="auth-form" onSubmit={handleSubmit}>
                {isSignup && (
                  <div className="form-group">
                    <label htmlFor="fullName" className="form-label">Full Name</label>
                    <div className="input-wrapper">
                      <FiUser className="input-icon" />
                      <input
                        type="text"
                        id="fullName"
                        name="fullName"
                        className="form-input"
                        placeholder="Enter your full name"
                        value={formData.fullName}
                        onChange={handleInputChange}
                        required={isSignup}
                        disabled={loading}
                      />
                    </div>
                  </div>
                )}

                {isSignup && (
                  <div className="form-group">
                    <label htmlFor="username" className="form-label">Username</label>
                    <div className="input-wrapper">
                      <FiUser className="input-icon" />
                      <input
                        type="text"
                        id="username"
                        name="username"
                        className="form-input"
                        placeholder="Choose a username"
                        value={formData.username}
                        onChange={handleInputChange}
                        required
                        disabled={loading}
                      />
                    </div>
                  </div>
                )}

                <div className="form-group">
                  <label htmlFor="email" className="form-label">Email Address</label>
                  <div className="input-wrapper">
                    <FiMail className="input-icon" />
                    <input
                      type="email"
                      id="email"
                      name="email"
                      className="form-input"
                      placeholder="Email address"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                {!isSignup && (
                  <div className="form-group">
                    <label htmlFor="username" className="form-label">Username (Optional)</label>
                    <div className="input-wrapper">
                      <FiUser className="input-icon" />
                      <input
                        type="text"
                        id="username"
                        name="username"
                        className="form-input"
                        placeholder="Or enter username"
                        value={formData.username}
                        onChange={handleInputChange}
                        disabled={loading}
                      />
                    </div>
                  </div>
                )}

                <div className="form-group">
                  <label htmlFor="password" className="form-label">Password</label>
                  <div className="input-wrapper">
                    <FiLock className="input-icon" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      className="form-input"
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                      tabIndex={-1}
                    >
                      {showPassword ? <FiEyeOff /> : <FiEye />}
                    </button>
                  </div>
                </div>

                {isSignup && (
                  <div className="form-group">
                    <label htmlFor="confirmPassword" className="form-label">Confirm Password</label>
                    <div className="input-wrapper">
                      <FiLock className="input-icon" />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        className="form-input"
                        placeholder="Confirm your password"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        required={isSignup}
                        disabled={loading}
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        tabIndex={-1}
                      >
                        {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                      </button>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{error}</span>
                  </div>
                )}

                <button 
                  type="submit" 
                  className="submit-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="loading-spinner">
                      <span className="spinner-dot"></span>
                      <span className="spinner-dot"></span>
                      <span className="spinner-dot"></span>
                    </span>
                  ) : (
                    <>
                      {isSignup ? 'Create Account' : 'Continue'}
                    </>
                  )}
                </button>
              </form>

              <div className="auth-footer">
                <div className="auth-divider">
                  <span className="divider-text">or</span>
                </div>
                <button 
                  type="button" 
                  className="toggle-mode-btn"
                  onClick={toggleMode}
                  disabled={loading}
                >
                  {isSignup ? (
                    <>
                      Already have an account? <span className="toggle-link">Sign In</span>
                    </>
                  ) : (
                    <>
                      Don't have an account? <span className="toggle-link">Sign Up</span>
                    </>
                  )}
                </button>
                
                <div className="stay-logged-out-section">
                  <button 
                    type="button" 
                    className="stay-logged-out-btn"
                    onClick={onClose}
                  >
                    Stay logged out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
