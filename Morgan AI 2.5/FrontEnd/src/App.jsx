import React, { useState, useEffect, useRef } from 'react';
import LogoModal from './components/UI/LogoModal';
import { Routes, Route, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { FiPlus, FiClock, FiAward, FiUser, FiChevronDown, FiAlertCircle, FiLoader, FiSettings, FiLogOut, FiSearch } from 'react-icons/fi';
import './styles/globals.css';
import './styles/theme.css';
import ChatWindow from './components/Chat/ChatWindow';
import ChatHistory from './components/Chat/ChatHistory';
import NavMenu from './components/Navigation/NavMenu';
import AdminDashboard from './components/Admin/AdminDashboard';
import LoginPage from './components/Auth/LoginPage';
import OAuthCallback from './components/Auth/OAuthCallback';
import CalendarView from './components/Calendar/CalendarView';
import InternshipsPage from './components/Career/InternshipsPage';
import DegreeWorksPage from './components/DegreeWorks/DegreeWorksPage';
import { useAuth } from './hooks/useAuth';
import { useTheme } from './hooks/useTheme';
import { ChatProvider } from './context/ChatContext';
import { VoiceProvider } from './context/VoiceContext';
import { DegreeWorksProvider } from './context/DegreeWorksContext';

function App() {
  const { user, isAdmin, login, logout, isLoading } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [showAdmin, setShowAdmin] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [navFocusedSection, setNavFocusedSection] = useState(null);
  const [showLogoModal, setShowLogoModal] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const [navigationError, setNavigationError] = useState(null);
  const [searchActive, setSearchActive] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const userMenuRef = useRef(null);

  const RequireAdmin = ({ children }) => {
    if (!user || !isAdmin) {
      return <Navigate to="/login" replace state={{ from: location.pathname }} />;
    }
    return children;
  };

  const isAuthRoute = location.pathname.startsWith('/login') || location.pathname.startsWith('/auth');

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        console.log('🔘 Closing user menu - clicked outside');
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      console.log('👤 User menu opened');
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  // Clear navigation errors after 5 seconds
  useEffect(() => {
    if (navigationError) {
      console.log('⚠️ Navigation error:', navigationError);
      const timer = setTimeout(() => {
        console.log('✅ Clearing navigation error');
        setNavigationError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [navigationError]);

  useEffect(() => {
    // Apply theme class to body
    document.body.className = theme;
    console.log('🎨 Theme applied:', theme);
    
    // Play welcome message if user just logged in
    if (user && !isLoading) {
      console.log('👋 Playing welcome message for:', user.name);
      playWelcomeMessage(user.name);
    }
  }, [theme, user, isLoading]);

  const handleNavigation = async (path, options = {}) => {
    try {
      console.log('🧭 Navigating to:', path, options);
      setIsNavigating(true);
      setNavigationError(null);
      
      // Simulate brief loading for smooth UX
      await new Promise(resolve => setTimeout(resolve, 200));
      
      navigate(path, options);
      console.log('✅ Navigation successful to:', path);
    } catch (error) {
      console.error('❌ Navigation error:', error);
      setNavigationError(`Failed to navigate to ${path}`);
    } finally {
      setIsNavigating(false);
    }
  };

  const handleNewChat = () => {
    console.log('➕ Starting new chat...');
    handleNavigation('/', { state: { newChat: true } });
  };

  const handleChatHistory = () => {
    console.log('🕐 Opening Chat History...');
    handleNavigation('/chat-history');
  };

  const handleDegreeWorks = () => {
    console.log('🎓 Opening Degree Works...');
    handleNavigation('/degree-works');
  };

  const handleUserMenuToggle = () => {
    console.log('👤 Toggling user menu, current state:', showUserMenu);
    setShowUserMenu(!showUserMenu);
  };

  const handleLogout = () => {
    console.log('🔐 User initiating logout from header menu...');
    setShowUserMenu(false);
    logout();
  };

  const toggleSearch = () => {
    setSearchActive(prev => !prev);
    setSearchQuery('');
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    console.log('🔍 Submitting search query:', searchQuery);
    // Placeholder: integrate backend knowledge search endpoint when available
    // fetch('/api/search', { method:'POST', body: JSON.stringify({ q: searchQuery }) })
    //   .then(r => r.json())
    //   .then(data => console.log('Search results', data))
    //   .catch(err => console.error('Search error', err));
  };

  const playWelcomeMessage = async (userName) => {
    try {
      console.log('🔊 Fetching welcome message for:', userName);
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
          console.log('✅ Playing welcome audio');
          const audio = new Audio(`data:audio/mp3;base64,${data.audio}`);
          audio.play();
        }
      } else {
        console.warn('⚠️ Welcome message API returned:', response.status);
      }
    } catch (error) {
      console.error('❌ Error playing welcome message:', error);
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
    <DegreeWorksProvider>
      <ChatProvider>
        <VoiceProvider>
          <div className={`app ${theme}`}>
          {!isAuthRoute && (
          <header className="app-header">
            <div className="header-content">
              <div className="header-top-row">
                <button 
                  className="menu-toggle"
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setSidebarOpen(!sidebarOpen)
                  }}
                  onTouchEnd={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setSidebarOpen(!sidebarOpen)
                  }}
                  aria-label="Toggle navigation menu"
                  aria-expanded={sidebarOpen}
                  aria-controls="navigation-menu"
                  type="button"
                >
                  <span className="hamburger" aria-hidden="true"></span>
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
                <nav className="header-center" aria-label="Primary">
                  {navigationError && (
                    <div className="navigation-error-toast">
                      <FiAlertCircle />
                      <span>{navigationError}</span>
                    </div>
                  )}
                  <div className="primary-nav-cluster">
                    {!isAuthRoute && location.pathname === '/' && (
                      <button 
                        className="new-chat-header-btn header-icon-btn"
                        onClick={handleNewChat}
                        disabled={isNavigating}
                        title="Start New Chat"
                        aria-label="Start new chat conversation"
                      >
                        {isNavigating ? <FiLoader className="spinning" /> : <FiPlus />}
                        <span className="btn-label">New Chat</span>
                      </button>
                    )}
                    {!isAuthRoute && (
                      <button 
                        className="chat-history-header-btn header-icon-btn"
                        onClick={handleChatHistory}
                        disabled={isNavigating}
                        title="View Chat History"
                        aria-label="View your chat history"
                      >
                        {isNavigating && location.pathname !== '/chat-history' ? (
                          <FiLoader className="spinning" />
                        ) : (
                          <FiClock />
                        )}
                        <span className="btn-label">History</span>
                      </button>
                    )}
                    {!isAuthRoute && user && (
                      <button 
                        className="degree-works-header-btn header-icon-btn"
                        onClick={handleDegreeWorks}
                        disabled={isNavigating}
                        title="View Degree Works"
                        aria-label="View your degree progress"
                      >
                        {isNavigating && location.pathname !== '/degree-works' ? (
                          <FiLoader className="spinning" />
                        ) : (
                          <FiAward />
                        )}
                        <span className="btn-label">Degree</span>
                      </button>
                    )}
                    {!isAuthRoute && (
                      <button
                        className="voice-settings-toggle header-icon-btn"
                        onClick={() => { 
                          console.log('🔊 Opening voice settings...'); 
                          setSidebarOpen(true); 
                          setNavFocusedSection('settings'); 
                        }}
                        title="Open Voice Settings"
                        aria-label="Configure voice settings"
                      >
                        <span className="btn-label">Voice</span>
                      </button>
                    )}
                    <button 
                      className="theme-toggle header-icon-btn theme-toggle--cluster"
                      onClick={() => {
                        console.log('🎨 Toggling theme from', theme, 'to', theme === 'dark' ? 'light' : 'dark');
                        toggleTheme();
                      }}
                      aria-label="Toggle theme"
                      title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                    >
                      {theme === 'light' ? '🌙' : '🌞'}
                    </button>
                    {!user && (
                      <button 
                        className="login-button header-icon-btn login-button--accent"
                        onClick={() => {
                          console.log('🔐 Navigating to login...');
                          handleNavigation('/login');
                        }}
                        disabled={isNavigating}
                        title="Sign in to your account"
                      >
                        {isNavigating ? <FiLoader className="spinning" /> : 'Sign in'}
                      </button>
                    )}
                  </div>
                </nav>
                {user && (
                  <div className="user-menu-container" ref={userMenuRef}>
                    <button 
                      className="user-menu-trigger header-icon-btn"
                      onClick={handleUserMenuToggle}
                      aria-expanded={showUserMenu}
                      aria-haspopup="true"
                      title="User menu"
                    >
                      <FiUser className="user-icon" />
                      <span className="user-name-short">{user.name?.split(' ')[0] || 'User'}</span>
                      <FiChevronDown className={`chevron ${showUserMenu ? 'rotated' : ''}`} />
                    </button>
                    {showUserMenu && (
                      <div className="user-dropdown-menu">
                        <div className="user-dropdown-header">
                          <FiUser className="profile-icon" />
                          <div className="user-info">
                            <span className="user-full-name">{user.name}</span>
                            <span className="user-email">{user.email || user.username}</span>
                          </div>
                        </div>
                        <div className="dropdown-divider"></div>
                        {isAdmin && (
                          <button 
                            className="dropdown-item admin-item"
                            onClick={() => {
                              console.log('👨‍💼 Opening admin panel...');
                              setShowAdmin(!showAdmin);
                              setShowUserMenu(false);
                            }}
                          >
                            <FiSettings />
                            <span>Admin Panel</span>
                          </button>
                        )}
                        <button 
                          className="dropdown-item logout-item"
                          onClick={handleLogout}
                        >
                          <FiLogOut />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </header>
          )}

          <div className={`app-body ${isAuthRoute ? 'app-body--auth' : ''}`}>
            <main className={`app-main ${isAuthRoute ? 'app-main--auth' : ''}`}>
              <Routes>
                <Route path="/" element={<ChatWindow user={user} />} />
                <Route path="/chat-history" element={<ChatHistory user={user} />} />
                <Route path="/degree-works" element={<DegreeWorksPage user={user} />} />
                <Route path="/courses" element={<ChatWindow user={user} />} />
                <Route path="/courses/:courseId" element={<ChatWindow user={user} />} />
                <Route path="/calendar" element={<CalendarView user={user} />} />
                <Route path="/organizations" element={<ChatWindow user={user} />} />
                <Route path="/career" element={<ChatWindow user={user} />} />
                <Route path="/career/internships" element={<InternshipsPage user={user} />} />
                <Route path="/study" element={<ChatWindow user={user} />} />
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
  
        {/* Navigation Menu - Rendered OUTSIDE main app container for proper layering */}
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
        
  <LogoModal show={showLogoModal} onClose={() => setShowLogoModal(false)} />
        </VoiceProvider>
      </ChatProvider>
    </DegreeWorksProvider>
  );
}

export default App;