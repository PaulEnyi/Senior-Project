import React, { useState, useEffect, useContext, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link, useLocation } from 'react-router-dom'
import {
  FiHome,
  FiMessageSquare,
  FiBookOpen,
  FiCalendar,
  FiUsers,
  FiBriefcase,
  FiHelpCircle,
  FiSettings,
  FiLogOut,
  FiMoon,
  FiSun,
  FiMenu,
  FiX,
  FiChevronRight,
  FiExternalLink,
  FiMapPin,
  FiPhone,
  FiMail
} from 'react-icons/fi'
import '../../styles/navigation.css'
import { VoiceContext } from '../../context/VoiceContext'

const navItems = [
  { path: '/', label: 'Chat', icon: FiMessageSquare, color: '#F47B20' },
  { path: '/courses', label: 'Courses', icon: FiBookOpen, color: '#003DA5' },
  { path: '/calendar', label: 'Calendar', icon: FiCalendar, color: '#10B981' },
  { path: '/organizations', label: 'Organizations', icon: FiUsers, color: '#8B5CF6' },
  { path: '/career', label: 'Career', icon: FiBriefcase, color: '#EF4444' },
  { path: '/help', label: 'Help', icon: FiHelpCircle, color: '#F59E0B' },
]

const quickLinks = [
  { label: 'WebSIS', url: 'https://lbpsso.morgan.edu/authenticationendpoint/login.do', icon: FiExternalLink },
  { label: 'Canvas', url: 'https://morganstate.instructure.com/login/ldap', icon: FiExternalLink },
  { label: 'CS Dept', url: 'https://www.morgan.edu/scmns/computerscience', icon: FiExternalLink },
  { label: 'Library', url: 'https://www.morgan.edu/library', icon: FiExternalLink },
]

const NavMenu = ({ 
  isOpen, 
  onToggle, 
  theme, 
  onThemeToggle, 
  user, 
  onLogout,
  focusedSection,
}) => {
  const location = useLocation()
  const [expandedSection, setExpandedSection] = useState(null)
  const {
    isSpeaking,
    isPaused,
    speak,
    stop,
    pause,
    resume,
    voices,
    selectedVoiceURI,
    setSelectedVoiceURI,
    rate,
    setRate,
    pitch,
    setPitch,
    volume,
    setVolume,
  } = useContext(VoiceContext)

  const [langFilter, setLangFilter] = useState('en')
  const [genderFilter, setGenderFilter] = useState('all')

  const languages = useMemo(() => {
    const set = new Set()
    voices.forEach(v => set.add((v.lang || '').split('-')[0]))
    return Array.from(set)
  }, [voices])

  const filteredVoices = useMemo(() => {
    return voices.filter(v => {
      const langOk = langFilter ? (v.lang || '').toLowerCase().startsWith(langFilter.toLowerCase()) : true
      const isFemale = /(female|zira|aria|emma|jenny|sonia|ava|michelle|clara|molly|libby|maisie)/i.test(v.name || '')
      const isMale = /(male|david|mark|brian|andrew|ryan|roger|eric|guy|thomas|james|luke|liam|wayne)/i.test(v.name || '')
      const genderOk = genderFilter === 'all' || (genderFilter === 'female' && isFemale) || (genderFilter === 'male' && isMale)
      return langOk && genderOk
    })
  }, [voices, langFilter, genderFilter])

  // Close menu with Escape key or any typing (for chat)
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (!isOpen) return

      // Close on Escape key
      if (e.key === 'Escape') {
        onToggle()
        return
      }

      // Close when user starts typing (alphanumeric, space, or common punctuation)
      // Ignore special keys like Tab, Shift, Ctrl, Alt, etc.
      const isTyping = (
        e.key.length === 1 && // Single character keys
        !e.ctrlKey && // Not holding Ctrl
        !e.altKey && // Not holding Alt
        !e.metaKey // Not holding Command/Windows key
      )

      if (isTyping) {
        onToggle()
      }
    }

    document.addEventListener('keydown', handleKeyPress)
    return () => document.removeEventListener('keydown', handleKeyPress)
  }, [isOpen, onToggle])

  // Close menu when clicking on navigation links (mobile)
  const handleLinkClick = () => {
    if (window.innerWidth < 1024) {
      onToggle()
    }
  }

  const sidebarVariants = {
    open: { 
      x: 0,
      transition: { 
        type: "spring", 
        stiffness: 300, 
        damping: 30 
      }
    },
    closed: { 
      x: -320,
      transition: { 
        type: "spring", 
        stiffness: 300, 
        damping: 30 
      }
    }
  }

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  // Allow parent to request a section to open, e.g., focusedSection="settings"
  useEffect(() => {
    if (isOpen && focusedSection) {
      setExpandedSection(focusedSection)
    }
  }, [isOpen, focusedSection])

  return (
    <>
      {/* Overlay for mobile/tablet */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="nav-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onToggle}
            transition={{ duration: 0.2 }}
          />
        )}
      </AnimatePresence>

      {/* Sidebar Navigation */}
      <motion.nav
        className="nav-sidebar"
        initial="closed"
        animate={isOpen ? "open" : "closed"}
        variants={sidebarVariants}
      >
        <div className="nav-container">
          {/* Header Section */}
          <div className="nav-header-section">
            <div className="nav-brand">
              <div className="brand-logo-container">
                <img 
                  src="/assets/morgan-logo/morgan-logo.png" 
                  alt="Morgan State" 
                  className="brand-logo"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              </div>
              <div className="brand-info">
                <h2 className="brand-title">Morgan AI</h2>
                <p className="brand-subtitle">CS Department</p>
              </div>
            </div>
            
            <button 
              className="nav-close-btn"
              onClick={onToggle}
              aria-label="Close navigation"
            >
              <FiX />
            </button>
          </div>

          {/* User Profile Section */}
          {user && (
            <div className="nav-user-section">
              <div className="user-profile-card">
                <div className="user-avatar-circle">
                  <FiUsers />
                </div>
                <div className="user-details">
                  <p className="user-display-name">{user.username || 'Guest User'}</p>
                  <span className="user-role-badge">{user.role || 'Student'}</span>
                </div>
              </div>
            </div>
          )}

          {/* Main Navigation Links */}
          <div className="nav-content-scroll">
            <div className="nav-section">
              <h3 className="nav-section-title">Navigation</h3>
              <div className="nav-links-container">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`nav-link-item ${isActive ? 'active' : ''}`}
                      onClick={handleLinkClick}
                      style={{
                        '--item-color': item.color
                      }}
                    >
                      <div className="nav-link-icon">
                        <Icon />
                      </div>
                      <span className="nav-link-text">{item.label}</span>
                      {isActive && <div className="nav-link-indicator" />}
                    </Link>
                  )
                })}
                
                {/* Admin Link */}
                {user?.role === 'admin' && (
                  <Link
                    to="/admin"
                    className={`nav-link-item ${location.pathname.startsWith('/admin') ? 'active' : ''}`}
                    onClick={handleLinkClick}
                    style={{ '--item-color': '#6366F1' }}
                  >
                    <div className="nav-link-icon">
                      <FiSettings />
                    </div>
                    <span className="nav-link-text">Admin Panel</span>
                    {location.pathname.startsWith('/admin') && <div className="nav-link-indicator" />}
                  </Link>
                )}
              </div>
            </div>

            {/* Quick Links Section */}
            <div className="nav-section">
              <div 
                className="nav-section-header"
                onClick={() => toggleSection('quickLinks')}
              >
                <h3 className="nav-section-title">Quick Links</h3>
                <motion.div
                  animate={{ rotate: expandedSection === 'quickLinks' ? 90 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <FiChevronRight />
                </motion.div>
              </div>
              
              <AnimatePresence>
                {expandedSection === 'quickLinks' && (
                  <motion.div
                    className="quick-links-grid"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {quickLinks.map((link, index) => {
                      const Icon = link.icon
                      return (
                        <a
                          key={index}
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="quick-link-card"
                        >
                          <Icon className="quick-link-icon" />
                          <span className="quick-link-label">{link.label}</span>
                        </a>
                      )
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Settings Section */}
            <div className="nav-section">
              <div 
                className="nav-section-header"
                onClick={() => toggleSection('settings')}
              >
                <h3 className="nav-section-title">Settings</h3>
                <motion.div
                  animate={{ rotate: expandedSection === 'settings' ? 90 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <FiChevronRight />
                </motion.div>
              </div>

              <AnimatePresence>
                {expandedSection === 'settings' && (
                  <motion.div
                    className="settings-panel"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="settings-group">
                      <h4 className="settings-title">Voice Settings</h4>
                      <p className="settings-subtitle">Choose a voice and tune how the assistant sounds.</p>

                      <div className="settings-row">
                        <div className="settings-field">
                          <label>Language</label>
                          <select value={langFilter} onChange={(e) => setLangFilter(e.target.value)}>
                            <option value="">All</option>
                            {languages.map(l => <option key={l} value={l}>{l}</option>)}
                          </select>
                        </div>
                        <div className="settings-field">
                          <label>Gender</label>
                          <select value={genderFilter} onChange={(e) => setGenderFilter(e.target.value)}>
                            <option value="all">All</option>
                            <option value="female">Female</option>
                            <option value="male">Male</option>
                          </select>
                        </div>
                      </div>

                      <div className="settings-field">
                        <label>Voice</label>
                        <select
                          className="voice-select"
                          value={selectedVoiceURI || ''}
                          onChange={(e) => setSelectedVoiceURI(e.target.value)}
                        >
                          {filteredVoices.map((v, idx) => (
                            <option key={`${v.voiceURI || v.name}-${idx}`} value={v.voiceURI || v.name}>
                              {v.name} ({v.lang}) {v.default ? '— Default' : ''}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="settings-row">
                        <div className="settings-field">
                          <label>Rate: {rate.toFixed(2)}</label>
                          <input type="range" min="0.5" max="2.0" step="0.05" value={rate} onChange={(e) => setRate(parseFloat(e.target.value))} />
                        </div>
                        <div className="settings-field">
                          <label>Pitch: {pitch.toFixed(2)}</label>
                          <input type="range" min="0.5" max="2.0" step="0.05" value={pitch} onChange={(e) => setPitch(parseFloat(e.target.value))} />
                        </div>
                        <div className="settings-field">
                          <label>Volume: {volume.toFixed(2)}</label>
                          <input type="range" min="0.0" max="1.0" step="0.05" value={volume} onChange={(e) => setVolume(parseFloat(e.target.value))} />
                        </div>
                      </div>

                      <div className="settings-actions">
                        <button className="voice-test-btn" onClick={() => speak('Hello! This is your Morgan State AI assistant speaking.')}>Test Voice</button>
                        <button className="voice-pause-btn" onClick={() => isPaused ? resume() : pause()} disabled={!isSpeaking}>
                          {isPaused ? 'Resume' : 'Pause'}
                        </button>
                        <button className="voice-stop-btn" onClick={stop} disabled={!isSpeaking}>Stop</button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            {/* End Settings */}
            {/* Contact Information */}
            <div className="nav-section">
              <div 
                className="nav-section-header"
                onClick={() => toggleSection('contact')}
              >
                <h3 className="nav-section-title">Contact Info</h3>
                <motion.div
                  animate={{ rotate: expandedSection === 'contact' ? 90 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <FiChevronRight />
                </motion.div>
              </div>
              
              <AnimatePresence>
                {expandedSection === 'contact' && (
                  <motion.div
                    className="contact-info-list"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="contact-item">
                      <FiMapPin className="contact-icon" />
                      <span className="contact-text">Science Complex, Room 325</span>
                    </div>
                    <div className="contact-item">
                      <FiPhone className="contact-icon" />
                      <span className="contact-text">(443) 885-3130</span>
                    </div>
                    <div className="contact-item">
                      <FiMail className="contact-icon" />
                      <span className="contact-text">cs@morgan.edu</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Bottom Actions */}
          <div className="nav-footer-section">
            <button 
              className="theme-toggle-btn"
              onClick={onThemeToggle}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              <div className="theme-icon">
                {theme === 'dark' ? <FiSun /> : <FiMoon />}
              </div>
              <span className="theme-label">
                {theme === 'dark' ? 'Light' : 'Dark'} Mode
              </span>
            </button>

            {user && (
              <button 
                className="logout-btn"
                onClick={onLogout}
              >
                <div className="logout-icon">
                  <FiLogOut />
                </div>
                <span className="logout-label">Sign out</span>
              </button>
            )}
          </div>
        </div>
      </motion.nav>
    </>
  )
}

export default NavMenu