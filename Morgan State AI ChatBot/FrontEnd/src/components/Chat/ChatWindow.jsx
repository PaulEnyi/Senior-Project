import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSend, FiMic, FiMicOff, FiRefreshCw, FiAward } from 'react-icons/fi';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import './ChatWindow.css';

const ChatWindow = ({
  messages = [],
  isLoading = false,
  onSendMessage,
  onClearThread,
  currentThread,
  isVoiceEnabled = false,
  onSpeakMessage,
  onVoiceInput,
  isListening = false
}) => {
  const [inputText, setInputText] = useState('');
  const [showQuickQuestions, setShowQuickQuestions] = useState(false);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
      const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100;
      
      if (isNearBottom) {
        chatContainerRef.current.scrollTo({
          top: scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText.trim());
      setInputText('');
      setShowQuickQuestions(false);
    }
  };

  const handleQuickQuestion = (question) => {
    setInputText(question);
    setShowQuickQuestions(false);
    inputRef.current?.focus();
  };

  const handleVoiceInput = () => {
    if (isListening) {
      onVoiceInput(false);
    } else {
      onVoiceInput(true);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    } else if (e.key === 'Escape') {
      setShowQuickQuestions(false);
    } else if (e.key === '/' && e.ctrlKey) {
      e.preventDefault();
      setShowQuickQuestions(!showQuickQuestions);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 500,
        damping: 30
      }
    }
  };

  const quickQuestions = [
    "Where is the Computer Science department located?",
    "Who are the faculty members in CS?",
    "What courses do I need for a CS degree?",
    "How do I join WiCS or GDSC?",
    "What tutoring services are available?",
    "How do I get help with programming assignments?",
    "What internship programs are recommended?",
    "How do I prepare for technical interviews?",
    "Who is my academic advisor?",
    "How do I get an enrollment PIN?",
    "What are the prerequisites for CS courses?",
    "When are the add/drop deadlines?",
    "How do I submit an override request?",
    "What career resources are available?",
    "How do I access NeetCode and LeetCode?",
  ];

  return (
    <motion.div 
      className="chat-window"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="chat-header">
        <div className="chat-info">
          <h3 className="chat-title">
            Morgan AI Assistant
            {currentThread && (
              <span className="thread-id">
                • Thread {currentThread.slice(-8)}
              </span>
            )}
          </h3>
          <p className="chat-subtitle">
            Computer Science Department Helper
          </p>
        </div>
        
        <div className="chat-actions">
          <motion.button
            className="action-btn"
            onClick={onClearThread}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Clear conversation"
            aria-label="Clear conversation"
          >
            <FiRefreshCw />
          </motion.button>
        </div>
      </div>

      <div 
        className="messages-container" 
        ref={chatContainerRef}
      >
        <AnimatePresence>
          {messages.length === 0 ? (
            <motion.div 
              className="empty-state"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
            >
              <div className="empty-content">
                <div className="morgan-avatar">
                  <FiAward size={64} />
                </div>
                <h3>Hello! I'm Morgan AI</h3>
                <p>
                  I'm here to help you with questions about the Morgan State University 
                  Computer Science Department. Ask me anything!
                </p>
                <motion.button
                  className="quick-questions-trigger"
                  onClick={() => setShowQuickQuestions(true)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Show me some example questions
                </motion.button>
              </div>
            </motion.div>
          ) : (
            messages.map((message, index) => (
              <motion.div
                key={message.id || index}
                variants={messageVariants}
                initial="hidden"
                animate="visible"
                exit="hidden"
              >
                <ChatMessage
                  message={message}
                  onSpeak={isVoiceEnabled ? onSpeakMessage : null}
                  onCopy={(text) => navigator.clipboard.writeText(text)}
                />
              </motion.div>
            ))
          )}
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <TypingIndicator />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {showQuickQuestions && (
          <motion.div
            className="quick-questions-panel"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="panel-header">
              <h4>Quick Questions</h4>
              <button 
                className="close-btn"
                onClick={() => setShowQuickQuestions(false)}
                aria-label="Close quick questions"
              >
                ×
              </button>
            </div>
            <div className="questions-grid">
              {quickQuestions.map((question, index) => (
                <motion.button
                  key={index}
                  className="quick-question"
                  onClick={() => handleQuickQuestion(question)}
                  whileHover={{ scale: 1.02, backgroundColor: '#f0f8ff' }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ 
                    opacity: 1, 
                    x: 0,
                    transition: { delay: index * 0.05 }
                  }}
                >
                  {question}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        className="chat-input-container"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <form onSubmit={handleSubmit} className="chat-form">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              id="chat-input"
              className="chat-input"
              placeholder={
                isListening 
                  ? "Listening..." 
                  : "Ask me anything about Morgan State CS..."
              }
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading || isListening}
              rows={1}
              style={{
                minHeight: '44px',
                maxHeight: '120px',
                resize: 'none'
              }}
            />
            
            <div className="input-actions">
              {isVoiceEnabled && (
                <motion.button
                  type="button"
                  className={`voice-btn ${isListening ? 'listening' : ''}`}
                  onClick={handleVoiceInput}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title={isListening ? "Stop listening" : "Voice input"}
                  aria-label={isListening ? "Stop voice input" : "Start voice input"}
                >
                  {isListening ? <FiMicOff /> : <FiMic />}
                </motion.button>
              )}
              
              <motion.button
                type="button"
                className="quick-btn"
                onClick={() => setShowQuickQuestions(!showQuickQuestions)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Quick questions (Ctrl+/)"
                aria-label="Show quick questions"
              >
                ?
              </motion.button>
              
              <motion.button
                type="submit"
                className="send-btn"
                disabled={!inputText.trim() || isLoading}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Send message (Enter)"
                aria-label="Send message"
              >
                <FiSend />
              </motion.button>
            </div>
          </div>
        </form>
        
        <div className="input-hints">
          <span className="hint-item">
            <kbd>Enter</kbd> to send
          </span>
          <span className="hint-item">
            <kbd>Shift</kbd> + <kbd>Enter</kbd> for new line
          </span>
          {isVoiceEnabled && (
            <span className="hint-item">
              <kbd>Esc</kbd> to stop voice
            </span>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ChatWindow;