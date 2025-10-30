import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import VoiceControls from './VoiceControls';
import QuickQuestions from './QuickQuestions';
import ChatHistory from './ChatHistory';
import { useChat } from '../../hooks/useChat';
import { useVoice } from '../../hooks/useVoice';
import { useWebSocket } from '../../hooks/useWebSocket';
import '../../styles/chat.css';

const ChatWindow = ({ user }) => {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const {
    messages,
    sendMessage,
    loadingMessage,
    error,
    clearError,
    sessionId
  } = useChat();
  
  const {
    isListening,
    isSpeaking,
    voiceEnabled,
    startListening,
    stopListening,
    toggleVoice,
    speakText
  } = useVoice();

  // WebSocket for real-time communication
  const { sendMessage: wsSendMessage, isConnected } = useWebSocket(
    sessionId,
    (message) => {
      // Handle incoming WebSocket messages
      if (message.type === 'assistant_message') {
        handleIncomingMessage(message.data);
      }
    }
  );

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleIncomingMessage = (messageData) => {
    // If voice is enabled, speak the message
    if (voiceEnabled && messageData.audio) {
      const audio = new Audio(`data:audio/mp3;base64,${messageData.audio}`);
      audio.play();
    } else if (voiceEnabled && messageData.text) {
      speakText(messageData.text);
    }
  };

  const handleSendMessage = async (text = input) => {
    if (!text.trim()) return;

    const messageText = text.trim();
    setInput('');
    setIsTyping(true);

    try {
      // Send via WebSocket if connected, otherwise use HTTP
      if (isConnected) {
        wsSendMessage({
          type: 'user_message',
          message: messageText,
          voice_enabled: voiceEnabled
        });
      } else {
        await sendMessage(messageText, voiceEnabled);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickQuestion = (question) => {
    setInput(question);
    handleSendMessage(question);
  };

  const handleVoiceInput = (transcript) => {
    setInput(transcript);
    handleSendMessage(transcript);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-content">
          <h2>Morgan AI Assistant</h2>
          <div className="chat-status">
            {isConnected ? (
              <span className="status-indicator connected">● Connected</span>
            ) : (
              <span className="status-indicator">● Offline Mode</span>
            )}
          </div>
        </div>
        
        <div className="chat-header-actions">
          <button 
            className="history-toggle"
            onClick={() => setShowHistory(!showHistory)}
            title="Chat History"
          >
            📜
          </button>
          <VoiceControls
            isListening={isListening}
            isSpeaking={isSpeaking}
            voiceEnabled={voiceEnabled}
            onStartListening={startListening}
            onStopListening={stopListening}
            onToggleVoice={toggleVoice}
            onTranscript={handleVoiceInput}
          />
        </div>
      </div>

      <QuickQuestions onSelectQuestion={handleQuickQuestion} />

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <img 
              src="/assets/morgan-logo/morgan-logo.png" 
              alt="Morgan State" 
              className="welcome-logo"
            />
            <h3>Welcome to Morgan AI Assistant!</h3>
            <p>
              I'm here to help you with information about the Computer Science 
              Department at Morgan State University. Ask me about:
            </p>
            <ul>
              <li>Course information and prerequisites</li>
              <li>Faculty and office hours</li>
              <li>Registration and advising</li>
              <li>Internships and career opportunities</li>
              <li>Department events and deadlines</li>
            </ul>
            <p>How can I assist you today?</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id || index}
                message={message}
                isUser={message.role === 'user'}
                timestamp={message.timestamp}
              />
            ))}
            {loadingMessage && (
              <div className="message-wrapper assistant">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={clearError}>✕</button>
        </div>
      )}

      <div className="chat-input-container">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isListening ? "Listening..." : "Type your message here..."}
            disabled={isListening || isTyping}
            className="chat-input"
            rows="1"
          />
          
          <div className="input-actions">
            <button
              className={`voice-button ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopListening : startListening}
              disabled={isTyping}
              title={isListening ? "Stop listening" : "Start voice input"}
            >
              🎤
            </button>
            
            <button
              className="send-button"
              onClick={() => handleSendMessage()}
              disabled={!input.trim() || isTyping || isListening}
              title="Send message"
            >
              {isTyping ? '⏳' : '➤'}
            </button>
          </div>
        </div>
        
        <div className="input-info">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {voiceEnabled && (
            <span className="voice-status">🔊 Voice enabled</span>
          )}
        </div>
      </div>

      {showHistory && (
        <ChatHistory
          onClose={() => setShowHistory(false)}
          onSelectConversation={(conversation) => {
            // Load selected conversation
            console.log('Loading conversation:', conversation);
          }}
        />
      )}
    </div>
  );
};

export default ChatWindow;