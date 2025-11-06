import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiPhone, FiX, FiEye, FiEyeOff, FiUser, FiLock, FiShield, FiMail } from 'react-icons/fi';
import { FaGoogle, FaApple, FaMicrosoft } from 'react-icons/fa';
import '../../styles/login.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [showCredentialsPanel, setShowCredentialsPanel] = useState(false);
  const [authProvider, setAuthProvider] = useState(null); // 'email' | 'google' | 'apple' | 'microsoft' | 'phone'
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const validateForm = () => {
    if (mode === 'signup' && !formData.fullName) {
      setError('Full name is required');
      return false;
    }
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
    if (mode === 'signup') {
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

  const openCredentials = (provider) => {
    setAuthProvider(provider);
    setShowCredentialsPanel(true);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      setLoading(true);
      const endpoint = mode === 'signup' ? '/api/auth/signup' : '/api/auth/login';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          username: mode === 'signup' ? formData.username : undefined,
          full_name: mode === 'signup' ? formData.fullName : undefined,
          password: formData.password,
          role: isAdmin ? 'admin' : 'user'
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || data.message || 'Authentication failed');

      // Store token robustly for all API requests
      const token = data.token || data.access_token;
      if (token) {
        localStorage.setItem('token', token);
        localStorage.setItem('auth_token', token);
      } else {
        throw new Error('No token received from server');
      }
      localStorage.setItem('role', isAdmin ? 'admin' : 'user');
      localStorage.setItem('user', JSON.stringify(data.user || { email: formData.email }));

      // Optionally, clear any old session data
      sessionStorage.clear();

      const redirectTo = (location.state && location.state.from) || '/';
      navigate(redirectTo);
    } catch (err) {
      console.error('Auth error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSocial = async (provider) => {
    // Start OAuth on backend if available; otherwise, open credentials panel as fallback
    try {
      setLoading(true);
      setError('');
      const oauthUrl = `http://localhost:8000/api/auth/oauth/${provider}/start`;
      
      // Attempt OAuth endpoint
      const response = await fetch(oauthUrl, { method: 'GET' });
      
      if (response.ok) {
        // OAuth is configured, redirect to provider
        window.location.href = oauthUrl;
        return;
      } else if (response.status === 501) {
        // OAuth not implemented, fall back to email/password
        const data = await response.json();
        setError(data.detail || `${provider.charAt(0).toUpperCase() + provider.slice(1)} OAuth is not configured. Please use email/password login.`);
        openCredentials('email');
        return;
      }
    } catch (err) {
      console.log(`OAuth not available for ${provider}, falling back to email auth`);
      setError(`Social login is not currently available. Please use email/password instead.`);
      openCredentials('email');
    } finally {
      setLoading(false);
    }
  };

  const closePanel = () => {
    setShowCredentialsPanel(false);
    setAuthProvider(null);
  };

  return (
    <div className="login-page-root">
      {/* Header */}
      <header className="login-header">
        <div className="login-header-content">
          <div className="brand-left" onClick={() => navigate('/')}> 
            <div className="brand-logo-pop">
              <img src="/assets/morgan-logo/morgan-logo.png" alt="Morgan State University" />
            </div>
            <div className="brand-titles">
              <h1>Morgan AI Assistant</h1>
              <p>Computer Science Department</p>
            </div>
          </div>

          <div className="header-actions">
            <button className="stay-signed-out" onClick={() => navigate('/')}>Stay signed out</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="login-container">
        <div className="column-separator" aria-hidden></div>
        {/* Left Branding Panel */}
        <aside className="branding-panel">
          <div className="branding-inner">
            <div className="crest-badge">
              <img src="/assets/morgan-logo/morgan-logo.png" alt="Morgan State" />
            </div>
            <h2 className="branding-title">Morgan AI Assistant</h2>
            <p className="branding-subtitle">Smart help for courses, advising, internships, and more.</p>
          </div>
        </aside>

        {/* Right Auth Panel */}
        <section className="auth-panel">
          <div className="auth-card">
            <div className="auth-card-inner">
              <div className="auth-header-area">
                <div className="big-icon">
                  <div className="big-icon-inner">➡️</div>
                </div>
                <h2 className="welcome-heading">Welcome Back</h2>
                <p className="welcome-desc">Log in or sign up to get smarter responses, upload files and images, and more.</p>
              </div>

              {/* Social Buttons */}
              <div className="social-buttons">
                <button className="social-btn google" onClick={() => handleSocial('google')}>
                  <FaGoogle className="social-ico" />
                  <span>Continue with Google</span>
                </button>
                <button className="social-btn apple" onClick={() => handleSocial('apple')}>
                  <FaApple className="social-ico" />
                  <span>Continue with Apple</span>
                </button>
                <button className="social-btn microsoft" onClick={() => handleSocial('microsoft')}>
                  <FaMicrosoft className="social-ico" />
                  <span>Continue with Microsoft</span>
                </button>
                <button className="social-btn phone" onClick={() => handleSocial('phone')}>
                  <FiPhone className="social-ico" />
                  <span>Continue with phone</span>
                </button>
              </div>

              {/* Divider with requested copy */}
              <div className="divider-row">
                <div className="line"></div>
                <div className="divider-text">Sign up or stay signed out.</div>
                <div className="line"></div>
              </div>

              {/* Email prompt */}
              <form className="email-shortcut" onSubmit={(e) => { e.preventDefault(); openCredentials('email'); }}>
                <div className="input-chip">
                  <div className="input-chip-wrap">
                    <FiMail className="chip-ico" />
                    <input 
                      type="email" 
                      name="email" 
                      placeholder="Email address" 
                      value={formData.email}
                      onChange={handleInputChange}
                      aria-label="Email address"
                    />
                  </div>
                </div>
                <button type="submit" className="continue-btn">Continue</button>
              </form>

              {/* Footer link row */}
              <div className="below-or-row">
                {mode === 'login' ? (
                  <>
                    <button className="linklike" onClick={() => setMode('signup')}>Sign up</button>
                    <span className="dot-sep">•</span>
                    <button className="linklike" onClick={() => navigate('/')}>Stay signed out</button>
                  </>
                ) : (
                  <>
                    <button className="linklike" onClick={() => setMode('login')}>Back to sign in</button>
                    <span className="dot-sep">•</span>
                    <button className="linklike" onClick={() => navigate('/')}>Stay signed out</button>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Sliding Credentials Panel */}
        {showCredentialsPanel && (
          <div 
            className={`credentials-overlay ${showCredentialsPanel ? 'visible' : ''}`}
            onClick={closePanel}
            aria-hidden
          />
        )}
        <section className={`credentials-slide ${showCredentialsPanel ? 'open' : ''}`}>
          <div className="credentials-header">
            <div className="provider-label">
              <span className="pill">{authProvider ? authProvider.toUpperCase() : ''}</span>
              <span className="mode-pill">{mode.toUpperCase()}</span>
            </div>
            <button className="close-cred" onClick={closePanel}><FiX /></button>
          </div>

          <div className="role-toggle">
            <button 
              className={`role-btn ${!isAdmin ? 'active' : ''}`} 
              onClick={() => setIsAdmin(false)}
              type="button"
            >
              <FiUser /> User
            </button>
            <button 
              className={`role-btn ${isAdmin ? 'active' : ''}`} 
              onClick={() => setIsAdmin(true)}
              type="button"
            >
              <FiShield /> Admin
            </button>
          </div>

          <form className="credentials-form" onSubmit={handleSubmit}>
            {mode === 'signup' && (
              <div className="form-row">
                <label>Full Name</label>
                <div className="input-wrap"><FiUser className="in-ico" /><input type="text" name="fullName" value={formData.fullName} onChange={handleInputChange} placeholder="Enter your full name" required /></div>
              </div>
            )}

            {mode === 'signup' && (
              <div className="form-row">
                <label>Username</label>
                <div className="input-wrap"><FiUser className="in-ico" /><input type="text" name="username" value={formData.username} onChange={handleInputChange} placeholder="Choose a username" required /></div>
              </div>
            )}

            <div className="form-row">
              <label>Email Address</label>
              <div className="input-wrap"><FiUser className="in-ico" /><input type="email" name="email" value={formData.email} onChange={handleInputChange} placeholder="Enter your email" required /></div>
            </div>

            <div className="form-row">
              <label>Password</label>
              <div className="input-wrap">
                <FiLock className="in-ico" />
                <input type={showPassword ? 'text' : 'password'} name="password" value={formData.password} onChange={handleInputChange} placeholder="Enter your password" required />
                <button className="peek" type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? <FiEyeOff /> : <FiEye />}</button>
              </div>
            </div>

            {mode === 'signup' && (
              <div className="form-row">
                <label>Confirm Password</label>
                <div className="input-wrap">
                  <FiLock className="in-ico" />
                  <input type={showPassword ? 'text' : 'password'} name="confirmPassword" value={formData.confirmPassword} onChange={handleInputChange} placeholder="Re-enter your password" required />
                </div>
              </div>
            )}

            {error && (
              <div className="form-error"><span>⚠️</span><p>{error}</p></div>
            )}

            <div className="form-actions">
              <button type="submit" className="primary-act" disabled={loading}>{mode === 'signup' ? 'Create Account' : 'Sign In'}</button>
              <button type="button" className="ghost-act" onClick={() => setMode(mode === 'signup' ? 'login' : 'signup')}>
                {mode === 'signup' ? 'Have an account? Sign In' : "Don't have an account? Sign Up"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
