import React from 'react';
import { 
  FiMenu, 
  FiX, 
  FiMessageSquare, 
  FiMic,
  FiBook,
  FiGlobe,
  FiMoon,
  FiShield,
  FiHelpCircle,
  FiChevronDown,
  FiChevronRight
} from 'react-icons/fi';
import './NavMenu.css';

const NavMenu = ({ isOpen, onToggle, currentView, onViewChange, isAdmin, onLogout, onNewChat, onVoiceToggle, onDarkModeToggle }) => {
  const [quickResourcesOpen, setQuickResourcesOpen] = React.useState(false);
  const [morganLinksOpen, setMorganLinksOpen] = React.useState(false);
  const [voiceEnabled, setVoiceEnabled] = React.useState(false);
  const [darkMode, setDarkMode] = React.useState(false);

  const handleNewConversation = () => {
    if (onNewChat) onNewChat();
    onViewChange('chat');
    onToggle();
  };

  const handleVoiceToggle = () => {
    const newState = !voiceEnabled;
    setVoiceEnabled(newState);
    if (onVoiceToggle) onVoiceToggle(newState);
  };

  const handleDarkMode = () => {
    const newState = !darkMode;
    setDarkMode(newState);
    if (onDarkModeToggle) onDarkModeToggle(newState);
    document.body.classList.toggle('dark-mode', newState);
  };

  return (
    <>
      {!isOpen && (
        <button className="sidebar-toggle" onClick={onToggle} aria-label="Toggle menu">
          <FiMenu size={20} />
        </button>
      )}

      <nav className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="header-content">
            <h2>Morgan AI</h2>
            <p>CS Department Assistant</p>
          </div>
          <button className="close-sidebar-btn" onClick={onToggle} aria-label="Close menu">
            <FiX size={20} />
          </button>
        </div>

        <div className="sidebar-section">
          <h3 className="section-title">CHAT ACTIONS</h3>
          
          <button className="action-button primary" onClick={handleNewConversation}>
            <FiMessageSquare size={18} />
            <span>New Conversation</span>
            <kbd>Ctrl+N</kbd>
          </button>

          <div className="voice-toggle">
            <FiMic size={18} />
            <span>Enable Voice</span>
            <button 
              className={`toggle-switch ${voiceEnabled ? 'on' : 'off'}`}
              onClick={handleVoiceToggle}
            >
              {voiceEnabled ? 'ON' : 'OFF'}
            </button>
          </div>
        </div>

        <div className="sidebar-section">
          <button 
            className="section-header" 
            onClick={() => setQuickResourcesOpen(!quickResourcesOpen)}
          >
            <FiBook size={18} />
            <span>QUICK RESOURCES</span>
            {quickResourcesOpen ? <FiChevronDown size={16} /> : <FiChevronRight size={16} />}
          </button>
          
          {quickResourcesOpen && (
            <div className="section-content">
              <a 
                href="https://catalog.morgan.edu/preview_program.php?catoid=26&poid=5968" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="sidebar-link"
              >
                Course Catalog
              </a>
              <a 
                href="https://www.morgan.edu/academic-calendar" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="sidebar-link"
              >
                Academic Calendar
              </a>
              <a 
                href="https://morgan.joinhandshake.com/login" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="sidebar-link"
              >
                Student Handbook
              </a>
            </div>
          )}
        </div>

        <div className="sidebar-section">
          <button 
            className="section-header" 
            onClick={() => setMorganLinksOpen(!morganLinksOpen)}
          >
            <FiGlobe size={18} />
            <span>MORGAN STATE LINKS</span>
            {morganLinksOpen ? <FiChevronDown size={16} /> : <FiChevronRight size={16} />}
          </button>
          
          {morganLinksOpen && (
            <div className="section-content">
              <a 
                href="https://www.morgan.edu" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="sidebar-link"
              >
                Morgan.edu
              </a>
              <a 
                href="https://www.morgan.edu/computer-science" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="sidebar-link"
              >
                CS Department
              </a>
              <a 
                href="https://portal.morgan.edu" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="sidebar-link"
              >
                Student Portal
              </a>
            </div>
          )}
        </div>

        <div className="sidebar-section">
          <h3 className="section-title">SETTINGS</h3>
          
          <button className="sidebar-item" onClick={handleDarkMode}>
            <FiMoon size={18} />
            <span>Dark Mode</span>
          </button>

          {isAdmin ? (
            <button className="sidebar-item" onClick={() => { onViewChange('admin'); onToggle(); }}>
              <FiShield size={18} />
              <span>Admin Panel</span>
            </button>
          ) : (
            <button className="sidebar-item" onClick={() => { onViewChange('admin-login'); onToggle(); }}>
              <FiShield size={18} />
              <span>Admin Panel</span>
            </button>
          )}
        </div>

        <div className="sidebar-section">
          <h3 className="section-title">HELP</h3>
          <button 
            className="sidebar-item" 
            onClick={() => window.open('https://www.morgan.edu/computer-science', '_blank')}
          >
            <FiHelpCircle size={18} />
            <span>How to Use</span>
          </button>
        </div>

        <div className="sidebar-footer">
          <p>Morgan State University</p>
          <p>Computer Science Department</p>
          <p className="version">Version 1.0.0</p>
        </div>
      </nav>

      {isOpen && <div className="sidebar-overlay" onClick={onToggle} />}
    </>
  );
};

export default NavMenu;