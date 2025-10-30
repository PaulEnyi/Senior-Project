import React, { useState, useEffect } from 'react';
import LogoModal from './components/UI/LogoModal';
import { Routes, Route, useNavigate, Navigate, useLocation } from 'react-router-dom';
import './styles/globals.css';
import './styles/theme.css';
import ChatWindow from './components/Chat/ChatWindow';
import NavMenu from './components/Navigation/NavMenu';
import AdminDashboard from './components/Admin/AdminDashboard';
import LoginPage from './components/Auth/LoginPage';
import OAuthCallback from './components/Auth/OAuthCallback';
import { useAuth } from './hooks/useAuth';
import { useTheme } from './hooks/useTheme';
import { ChatProvider } from './context/ChatContext';
import { VoiceProvider } from './context/VoiceContext';

function App() {
  const { user, isAdmin, login, logout, isLoading } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [showAdmin, setShowAdmin] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [navFocusedSection, setNavFocusedSection] = useState(null);
  const [showLogoModal, setShowLogoModal] = useState(false);

  const RequireAdmin = ({ children }) => {
    if (!user || !isAdmin) {
      return <Navigate to="/login" replace state={{ from: location.pathname }} />;
    }
    return children;
  };

  const isAuthRoute = location.pathname.startsWith('/login') || location.pathname.startsWith('/auth');

  useEffect(() => {
    // Apply theme class to body
    document.body.className = theme;
    
    // Play welcome message if user just logged in
    if (user && !isLoading) {
      playWelcomeMessage(user.name);
    }
  }, [theme, user, isLoading]);

  const playWelcomeMessage = async (userName) => {
    try {
      const response = await fetch('/api/voice/welcome', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ userName })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.audio) {
          const audio = new Audio(`data:audio/mp3;base64,${data.audio}`);
          audio.play();
        }
      }
    } catch (error) {
      console.error('Error playing welcome message:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loader">
          <img src="/assets/morgan-logo/morgan-logo.png" alt="Morgan State University" />
          <div className="spinner"></div>
          <p>Loading Morgan AI Assistant...</p>
        </div>
      </div>
    );
  }

  return (
    <ChatProvider>
      <VoiceProvider>
        <div className={`app ${theme}`}>
          {!isAuthRoute && (
          <header className="app-header">
            <div className="header-content">
              <button 
                className="menu-toggle"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                aria-label="Toggle menu"
              >
                <span className="hamburger"></span>
              </button>
              
              <div className="header-brand">
                <img 
                  src="/assets/morgan-logo/morgan-logo.png" 
                  alt="Morgan State University" 
                  className="logo"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setShowLogoModal(true)}
                />
                <div className="brand-text">
                  <h1>Morgan AI Assistant</h1>
                  <p>Computer Science Department</p>
                </div>
              </div>

              <div className="header-actions">
                <button 
                  className="theme-toggle"
                  onClick={toggleTheme}
                  aria-label="Toggle theme"
                >
                  {theme === 'dark' ? '🌞' : '🌙'}
                </button>

                {/* Voice settings quick access */}
                {!isAuthRoute && (
                  <button
                    className="voice-settings-toggle"
                    onClick={() => { setSidebarOpen(true); setNavFocusedSection('settings'); }}
                    title="Open Voice Settings"
                  >
                    Voice
                  </button>
                )}

                {user ? (
                  <div className="user-menu">
                    <span className="user-name">Welcome, {user.name}</span>
                    {isAdmin && (
                      <button 
                        className="admin-button"
                        onClick={() => setShowAdmin(!showAdmin)}
                      >
                        Admin Panel
                      </button>
                    )}
                    <button className="logout-button" onClick={logout}>
                      Sign out
                    </button>
                  </div>
                ) : (
                  <button 
                    className="login-button"
                    onClick={() => navigate('/login')}
                  >
                    Sign in
                  </button>
                )}
              </div>
            </div>
          </header>
          )}

          <div className={`app-body ${isAuthRoute ? 'app-body--auth' : ''}`}>
            {!isAuthRoute && (
              <NavMenu 
                isOpen={sidebarOpen} 
                onToggle={() => setSidebarOpen(!sidebarOpen)}
                theme={theme}
                onThemeToggle={toggleTheme}
                user={user}
                onLogout={logout}
                focusedSection={navFocusedSection}
              />
            )}

            <main className={`app-main ${isAuthRoute ? 'app-main--auth' : ''}`}>
              <Routes>
                <Route path="/" element={<ChatWindow user={user} />} />
                <Route path="/courses" element={<ChatWindow user={user} />} />
                <Route path="/calendar" element={<ChatWindow user={user} />} />
                <Route path="/organizations" element={<ChatWindow user={user} />} />
                <Route path="/career" element={<ChatWindow user={user} />} />
                <Route path="/help" element={<ChatWindow user={user} />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/auth/callback" element={<OAuthCallback />} />
                <Route path="/admin" element={
                  <RequireAdmin>
                    <AdminDashboard onClose={() => setShowAdmin(false)} />
                  </RequireAdmin>
                } />
              </Routes>
            </main>
          </div>

          {!isAuthRoute && (
          <footer className="app-footer">
            <div className="footer-content">
              <p>© 2024 Morgan State University - Computer Science Department</p>
              <div className="footer-links">
                <a href="https://www.morgan.edu/computer-science" target="_blank" rel="noopener noreferrer">
                  Department Website
                </a>
                <span className="separator">|</span>
                <a href="mailto:cs@morgan.edu">Contact Us</a>
                <span className="separator">|</span>
                <a href="/privacy">Privacy Policy</a>
              </div>
            </div>
          </footer>
          )}
  </div>
  <LogoModal show={showLogoModal} onClose={() => setShowLogoModal(false)} />
      </VoiceProvider>
    </ChatProvider>
  );
}

export default App;