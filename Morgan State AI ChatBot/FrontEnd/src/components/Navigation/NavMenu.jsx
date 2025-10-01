import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMenu, 
  FiX, 
  FiMessageSquare, 
  FiMic, 
  FiSettings, 
  FiLogOut,
  FiExternalLink,
  FiBook,
  FiUsers,
  FiCalendar,
  FiClipboard,
  FiGlobe,
  FiHelpCircle,
  FiSun,
  FiMoon,
  FiAward
} from 'react-icons/fi';
import './NavMenu.css';

const NavMenu = ({
  onNewThread,
  onShowAdmin,
  onToggleVoice,
  isVoiceEnabled = false,
  currentThread,
  onLoadThread,
  onToggleTheme,
  isDarkMode = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeSection, setActiveSection] = useState(null);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
        setActiveSection(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        setActiveSection(null);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
    setActiveSection(null);
  };

  const handleSectionClick = (section) => {
    setActiveSection(activeSection === section ? null : section);
  };

  const handleActionClick = (action) => {
    if (action) action();
    setIsOpen(false);
    setActiveSection(null);
  };

  const menuVariants = {
    closed: {
      opacity: 0,
      x: -300,
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    },
    open: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.3,
        ease: "easeInOut",
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    closed: { opacity: 0, x: -20 },
    open: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.2 }
    }
  };

  const overlayVariants = {
    closed: { opacity: 0 },
    open: { opacity: 1 }
  };

  const morganLinks = [
    {
      title: "CS Department",
      url: "https://www.morgan.edu/scmns/computerscience",
      description: "Main department page"
    },
    {
      title: "Faculty & Staff",
      url: "https://www.morgan.edu/computer-science/faculty-and-staff",
      description: "Meet our faculty"
    },
    {
      title: "Registration",
      url: "https://www.morgan.edu/office-of-the-registrar/records-and-registration-services/registration",
      description: "Course registration"
    },
    {
      title: "Academic Calendar",
      url: "https://www.morgan.edu/academic-calendar",
      description: "Important dates"
    },
    {
      title: "Canvas LMS",
      url: "https://morganstate.instructure.com/login/ldap",
      description: "Learning management system"
    },
    {
      title: "WebSIS",
      url: "https://lbpsso.morgan.edu/authenticationendpoint/login.do",
      description: "Student information system"
    }
  ];

  return (
    <>
      <motion.button
        className={`nav-menu-button ${isOpen ? 'open' : ''}`}
        onClick={toggleMenu}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label={isOpen ? "Close menu" : "Open menu"}
      >
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </motion.div>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="nav-menu-overlay"
            variants={overlayVariants}
            initial="closed"
            animate="open"
            exit="closed"
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={menuRef}
            className="nav-menu-panel"
            variants={menuVariants}
            initial="closed"
            animate="open"
            exit="closed"
          >
            <motion.div className="nav-menu-header" variants={itemVariants}>
              <div className="header-content">
                <div className="morgan-branding">
                  <div className="university-logo">
                    <FiAward />
                  </div>
                  <div className="brand-text">
                    <h2>Morgan AI</h2>
                    <p>CS Department Assistant</p>
                  </div>
                </div>
                {currentThread && (
                  <div className="thread-info">
                    <span className="thread-indicator">ACTIVE</span>
                    <span className="thread-text">
                      {currentThread.slice(-8)}
                    </span>
                  </div>
                )}
              </div>
            </motion.div>

            <motion.div className="nav-menu-section" variants={itemVariants}>
              <h3 className="section-title">Chat Actions</h3>
              <div className="menu-items">
                <motion.button
                  className="menu-item primary"
                  onClick={() => handleActionClick(onNewThread)}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FiMessageSquare className="item-icon" />
                  <span className="item-text">New Conversation</span>
                  <span className="item-shortcut">Ctrl+N</span>
                </motion.button>

                <motion.button
                  className={`menu-item ${isVoiceEnabled ? 'active' : ''}`}
                  onClick={() => handleActionClick(onToggleVoice)}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FiMic className="item-icon" />
                  <span className="item-text">
                    {isVoiceEnabled ? 'Disable Voice' : 'Enable Voice'}
                  </span>
                  <span className={`voice-status ${isVoiceEnabled ? 'on' : 'off'}`}>
                    {isVoiceEnabled ? 'ON' : 'OFF'}
                  </span>
                </motion.button>
              </div>
            </motion.div>

            <motion.div className="nav-menu-section" variants={itemVariants}>
              <div 
                className="section-header clickable"
                onClick={() => handleSectionClick('resources')}
              >
                <h3 className="section-title">
                  <FiBook className="section-icon" />
                  Quick Resources
                </h3>
                <motion.div
                  className="expand-icon"
                  animate={{ rotate: activeSection === 'resources' ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  ▼
                </motion.div>
              </div>
              
              <AnimatePresence>
                {activeSection === 'resources' && (
                  <motion.div
                    className="expandable-content"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="quick-questions">
                      <motion.button
                        className="quick-question-item"
                        onClick={() => handleActionClick(() => onLoadThread?.("course-info"))}
                        whileHover={{ scale: 1.02, x: 5 }}
                      >
                        <FiClipboard className="question-icon" />
                        <span>Course Information</span>
                      </motion.button>
                      
                      <motion.button
                        className="quick-question-item"
                        onClick={() => handleActionClick(() => onLoadThread?.("faculty-info"))}
                        whileHover={{ scale: 1.02, x: 5 }}
                      >
                        <FiUsers className="question-icon" />
                        <span>Faculty Directory</span>
                      </motion.button>
                      
                      <motion.button
                        className="quick-question-item"
                        onClick={() => handleActionClick(() => onLoadThread?.("calendar-info"))}
                        whileHover={{ scale: 1.02, x: 5 }}
                      >
                        <FiCalendar className="question-icon" />
                        <span>Academic Calendar</span>
                      </motion.button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            <motion.div className="nav-menu-section" variants={itemVariants}>
              <div 
                className="section-header clickable"
                onClick={() => handleSectionClick('morgan-links')}
              >
                <h3 className="section-title">
                  <FiGlobe className="section-icon" />
                  Morgan State Links
                </h3>
                <motion.div
                  className="expand-icon"
                  animate={{ rotate: activeSection === 'morgan-links' ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  ▼
                </motion.div>
              </div>
              
              <AnimatePresence>
                {activeSection === 'morgan-links' && (
                  <motion.div
                    className="expandable-content"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="morgan-links">
                      {morganLinks.map((link, index) => (
                        <motion.a
                          key={index}
                          className="morgan-link"
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          whileHover={{ scale: 1.02, x: 5 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="link-content">
                            <span className="link-title">{link.title}</span>
                            <span className="link-description">{link.description}</span>
                          </div>
                          <FiExternalLink className="external-icon" />
                        </motion.a>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            <motion.div className="nav-menu-section" variants={itemVariants}>
              <h3 className="section-title">Settings</h3>
              <div className="menu-items">
                <motion.button
                  className="menu-item"
                  onClick={() => handleActionClick(onToggleTheme)}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isDarkMode ? <FiSun className="item-icon" /> : <FiMoon className="item-icon" />}
                  <span className="item-text">
                    {isDarkMode ? 'Light Mode' : 'Dark Mode'}
                  </span>
                </motion.button>

                <motion.button
                  className="menu-item"
                  onClick={() => handleActionClick(onShowAdmin)}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FiSettings className="item-icon" />
                  <span className="item-text">Admin Panel</span>
                </motion.button>
              </div>
            </motion.div>

            <motion.div className="nav-menu-section" variants={itemVariants}>
              <h3 className="section-title">Help</h3>
              <div className="menu-items">
                <motion.button
                  className="menu-item"
                  onClick={() => handleActionClick(() => {
                    window.dispatchEvent(new CustomEvent('sendMessage', {
                      detail: { message: 'How do I use Morgan AI?' }
                    }));
                  })}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FiHelpCircle className="item-icon" />
                  <span className="item-text">How to Use</span>
                </motion.button>
              </div>
            </motion.div>

            <motion.div className="nav-menu-footer" variants={itemVariants}>
              <div className="footer-content">
                <p className="footer-text">
                  Morgan State University<br />
                  Computer Science Department
                </p>
                <div className="footer-version">
                  Version 1.0.0
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default NavMenu;