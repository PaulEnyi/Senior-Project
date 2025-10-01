import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { motion } from 'framer-motion';
import { FiAward, FiMessageCircle, FiMic, FiMicOff } from 'react-icons/fi';
import ChatWindow from './components/Chat/ChatWindow';
import NavMenu from './components/Navigation/NavMenu';
import VoiceControls from './components/Chat/VoiceControls';
import AdminLogin from './components/Admin/AdminLogin';
import AdminDashboard from './components/Admin/AdminDashboard';
import { useChat } from './hooks/useChat';
import { useVoice } from './hooks/useVoice';
import { useAdmin } from './hooks/useAdmin';
import './styles/morgan-theme.css';
import './styles/globals.css';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [currentView, setCurrentView] = useState('chat');
  
  const { 
    messages, 
    isLoading, 
    currentThread, 
    sendMessage, 
    createNewThread,
    loadThreadHistory,
    clearCurrentThread 
  } = useChat();
  
  const { 
    isVoiceEnabled, 
    isSpeaking, 
    isListening,
    toggleVoiceFeatures,
    speakText,
    startListening,
    stopListening 
  } = useVoice();
  
  const { 
    isAuthenticated, 
    isAdmin, 
    login, 
    logout 
  } = useAdmin();

  useEffect(() => {
    const handleKeyPress = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const chatInput = document.getElementById('chat-input');
        if (chatInput) chatInput.focus();
      }
      
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createNewThread();
      }
      
      if (e.key === 'Escape') {
        if (isSpeaking) speakText('');
        if (isListening) stopListening();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [createNewThread, isSpeaking, isListening, speakText, stopListening]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.2
      }
    }
  };

  const headerVariants = {
    hidden: { y: -50, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15
      }
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <motion.div 
          className="app-container"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <NavMenu 
            onNewThread={createNewThread}
            onShowAdmin={() => setShowAdminLogin(true)}
            onToggleVoice={toggleVoiceFeatures}
            isVoiceEnabled={isVoiceEnabled}
            currentThread={currentThread}
            onLoadThread={loadThreadHistory}
          />

          <motion.div 
            className="app-header"
            variants={headerVariants}
          >
            <div className="header-content">
              <div className="logo-section">
                <motion.div 
                  className="morgan-logo"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <img 
                    src="/assets/morgan-logo.png" 
                    alt="Morgan State University" 
                    className="university-logo"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </motion.div>
                <div className="title-section">
                  <h1 className="app-title">Morgan AI</h1>
                  <p className="app-subtitle">
                    Your Computer Science Department Assistant
                  </p>
                </div>
              </div>

              {isVoiceEnabled && (
                <VoiceControls
                  isSpeaking={isSpeaking}
                  isListening={isListening}
                  onStartListening={startListening}
                  onStopListening={stopListening}
                  onToggleVoice={toggleVoiceFeatures}
                />
              )}
            </div>
          </motion.div>

          <main className="main-content">
            {currentView === 'chat' ? (
              <ChatWindow
                messages={messages}
                isLoading={isLoading}
                onSendMessage={sendMessage}
                onClearThread={clearCurrentThread}
                currentThread={currentThread}
                isVoiceEnabled={isVoiceEnabled}
                onSpeakMessage={speakText}
                onVoiceInput={startListening}
                isListening={isListening}
              />
            ) : (
              <AdminDashboard onBack={() => setCurrentView('chat')} />
            )}
          </main>

          {messages.length === 0 && !isLoading && (
            <motion.div 
              className="welcome-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.6 }}
            >
              <div className="welcome-content">
                <div className="welcome-icon">
                  <FiAward size={64} />
                </div>
                <h2>Welcome to Morgan AI!</h2>
                <p>I'm here to help you with everything related to the Morgan State University Computer Science Department.</p>
                
                <div className="quick-actions">
                  <h3>Try asking me about:</h3>
                  <div className="quick-questions-grid">
                    <QuickQuestionButton 
                      question="Where is the CS department located?"
                      onClick={sendMessage}
                    />
                    <QuickQuestionButton 
                      question="Who are the CS faculty members?"
                      onClick={sendMessage}
                    />
                    <QuickQuestionButton 
                      question="How do I join WiCS or GDSC?"
                      onClick={sendMessage}
                    />
                    <QuickQuestionButton 
                      question="What courses do I need for my CS degree?"
                      onClick={sendMessage}
                    />
                    <QuickQuestionButton 
                      question="How do I get tutoring help?"
                      onClick={sendMessage}
                    />
                    <QuickQuestionButton 
                      question="What internship programs do you recommend?"
                      onClick={sendMessage}
                    />
                  </div>
                </div>

                <div className="features-highlight">
                  <div className="feature-item">
                    <FiMic className="feature-icon" />
                    <span>Voice enabled - speak your questions!</span>
                  </div>
                  <div className="feature-item">
                    <FiMessageCircle className="feature-icon" />
                    <span>Remembers our conversation</span>
                  </div>
                  <div className="feature-item">
                    <FiAward className="feature-icon" />
                    <span>Up-to-date department information</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {showAdminLogin && (
            <AdminLogin
              onLogin={(credentials) => {
                login(credentials);
                setShowAdminLogin(false);
                if (credentials.success) {
                  setCurrentView('admin');
                }
              }}
              onClose={() => setShowAdminLogin(false)}
            />
          )}

          <motion.div 
            className="floating-actions"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 1, type: "spring", stiffness: 200 }}
          >
            <button
              className="fab new-chat"
              onClick={createNewThread}
              title="New Conversation (Ctrl+N)"
              aria-label="Start new conversation"
            >
              <FiMessageCircle className="fab-icon" />
            </button>
            
            {isVoiceEnabled && (
              <button
                className={`fab voice-toggle ${isListening ? 'listening' : ''}`}
                onClick={isListening ? stopListening : startListening}
                title={isListening ? "Stop Listening" : "Start Voice Input"}
                aria-label={isListening ? "Stop voice input" : "Start voice input"}
              >
                {isListening ? <FiMicOff className="fab-icon" /> : <FiMic className="fab-icon" />}
              </button>
            )}
          </motion.div>

          <div className="status-bar">
            <div className="status-item">
              <span className={`status-indicator ${currentThread ? 'connected' : 'disconnected'}`}></span>
              <span className="status-text">
                {currentThread ? `Thread: ${currentThread.slice(-8)}` : 'Ready to chat'}
              </span>
            </div>
            
            {isVoiceEnabled && (
              <div className="status-item">
                <span className="status-indicator voice-enabled"></span>
                <span className="status-text">Voice enabled</span>
              </div>
            )}
            
            <div className="status-item">
              <span className="status-text">
                Morgan State CS Department - AI Assistant
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </QueryClientProvider>
  );
}

const QuickQuestionButton = ({ question, onClick }) => (
  <motion.button
    className="quick-question-btn"
    onClick={() => onClick(question)}
    whileHover={{ scale: 1.02, backgroundColor: '#ffa733' }}
    whileTap={{ scale: 0.98 }}
    transition={{ type: "spring", stiffness: 400, damping: 25 }}
  >
    {question}
  </motion.button>
);

const AdminDashboard = ({ onBack }) => (
  <div className="admin-dashboard">
    <button onClick={onBack} className="back-button">
      Back to Chat
    </button>
    <h2>Admin Dashboard</h2>
    <p>Knowledge base management and system controls will be implemented here.</p>
  </div>
);

export default App;