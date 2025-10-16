import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { FiAward } from 'react-icons/fi';
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
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  const [currentView, setCurrentView] = useState('chat');
  const [menuOpen, setMenuOpen] = useState(false);
  
  const { isAdmin, login, logout } = useAdmin();
  const {
    messages,
    isLoading,
    sendMessage,
    clearChat,
    currentThreadId,
  } = useChat();
  
  const {
    isListening,
    isSupported: voiceSupported,
    startListening,
    stopListening,
  } = useVoice();

  useEffect(() => {
    if (window.hideLoadingScreen) {
      window.hideLoadingScreen();
    }
  }, []);

  const handleAdminLogin = async (credentials) => {
    const success = await login(credentials);
    if (success) {
      setCurrentView('admin');
    }
    return success;
  };

  const handleLogout = () => {
    logout();
    setCurrentView('chat');
  };

  const handleNewChat = () => {
    if (clearChat && typeof clearChat === 'function') {
      clearChat();
    }
  };

  const handleVoiceToggle = (enabled) => {
    if (!voiceSupported) {
      alert('Voice is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (enabled) {
      startListening();
    } else {
      stopListening();
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <NavMenu
          isOpen={menuOpen}
          onToggle={() => setMenuOpen(!menuOpen)}
          currentView={currentView}
          onViewChange={setCurrentView}
          isAdmin={isAdmin}
          onLogout={handleLogout}
          onNewChat={handleNewChat}
          onVoiceToggle={handleVoiceToggle}
          onDarkModeToggle={(enabled) => {
            // Dark mode handled in NavMenu
          }}
        />

        <header className="app-header-top">
          <div className="header-logo-section">
            <div className="bookmark-icon">
              <FiAward size={40} color="#FF9100" />
            </div>
            <div className="header-text">
              <h1 className="header-title">Morgan AI</h1>
              <p className="header-subtitle">Computer Science Department Assistant</p>
            </div>
          </div>
        </header>

        <main className="app-main-content">
          {currentView === 'chat' && (
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              onSendMessage={sendMessage}
              onClearChat={clearChat}
              threadId={currentThreadId}
            />
          )}

          {currentView === 'admin-login' && !isAdmin && (
            <AdminLogin
              onLogin={handleAdminLogin}
              onBack={() => setCurrentView('chat')}
            />
          )}

          {currentView === 'admin' && isAdmin && (
            <AdminDashboard onBack={() => setCurrentView('chat')} />
          )}
        </main>

        <footer className="app-footer-bottom">
          <p className="footer-branding">
            Morgan State University - Computer Science Department
          </p>
          <div className="footer-links">
            <a href="https://www.morgan.edu" target="_blank" rel="noopener noreferrer">
              Morgan.edu
            </a>
            <span className="footer-separator">|</span>
            <a href="https://www.morgan.edu/computer-science" target="_blank" rel="noopener noreferrer">
              CS Department
            </a>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
}

export default App;