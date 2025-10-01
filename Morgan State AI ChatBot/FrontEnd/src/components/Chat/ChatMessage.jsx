import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiCopy, FiVolume2, FiCheck, FiUser, FiAward, FiThumbsUp, FiThumbsDown, FiAlertTriangle } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import { formatDistanceToNow } from 'date-fns';
import './ChatMessage.css';

const ChatMessage = ({ message, onSpeak, onCopy }) => {
  const [copied, setCopied] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  const isUser = message.role === 'user';
  const isAI = message.role === 'assistant';

  const handleCopy = async () => {
    if (onCopy) {
      await onCopy(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSpeak = () => {
    if (onSpeak && !speaking) {
      setSpeaking(true);
      onSpeak(message.content)
        .then(() => setSpeaking(false))
        .catch(() => setSpeaking(false));
    }
  };

  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch {
      return '';
    }
  };

  const messageVariants = {
    hidden: { opacity: 0, x: isUser ? 20 : -20, y: 10 },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 500,
        damping: 30
      }
    }
  };

  const avatarVariants = {
    hidden: { scale: 0, rotate: -180 },
    visible: {
      scale: 1,
      rotate: 0,
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 25,
        delay: 0.1
      }
    }
  };

  return (
    <motion.div
      className={`message ${isUser ? 'user-message' : 'ai-message'}`}
      variants={messageVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="message-container">
        <motion.div 
          className="message-avatar"
          variants={avatarVariants}
        >
          {isUser ? (
            <div className="user-avatar">
              <FiUser />
            </div>
          ) : (
            <div className="ai-avatar">
              <FiAward />
            </div>
          )}
        </motion.div>

        <div className="message-content">
          <div className="message-header">
            <span className="message-sender">
              {isUser ? 'You' : 'Morgan AI'}
            </span>
            {message.timestamp && (
              <span className="message-time">
                {formatTime(message.timestamp)}
              </span>
            )}
          </div>

          <div className="message-body">
            {isAI ? (
              <div className="ai-response">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="markdown-paragraph">{children}</p>,
                    strong: ({ children }) => <strong className="markdown-bold">{children}</strong>,
                    em: ({ children }) => <em className="markdown-italic">{children}</em>,
                    ul: ({ children }) => <ul className="markdown-list">{children}</ul>,
                    ol: ({ children }) => <ol className="markdown-ordered-list">{children}</ol>,
                    li: ({ children }) => <li className="markdown-list-item">{children}</li>,
                    code: ({ children, inline }) => 
                      inline ? (
                        <code className="markdown-inline-code">{children}</code>
                      ) : (
                        <pre className="markdown-code-block">
                          <code>{children}</code>
                        </pre>
                      ),
                    blockquote: ({ children }) => (
                      <blockquote className="markdown-blockquote">{children}</blockquote>
                    ),
                    h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
                    h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
                    h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
                    a: ({ children, href }) => (
                      <a 
                        className="markdown-link" 
                        href={href} 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    )
                  }}
                >
                  {message.content}
                </ReactMarkdown>
                
                {message.sources_used && message.sources_used.length > 0 && (
                  <div className="message-sources">
                    <h4 className="sources-title">Sources:</h4>
                    <ul className="sources-list">
                      {message.sources_used.map((source, index) => (
                        <li key={index} className="source-item">
                          {source}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {message.related_questions && message.related_questions.length > 0 && (
                  <div className="related-questions">
                    <h4 className="related-title">Related Questions:</h4>
                    <div className="related-list">
                      {message.related_questions.map((question, index) => (
                        <motion.button
                          key={index}
                          className="related-question-btn"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            const event = new CustomEvent('sendMessage', {
                              detail: { message: question }
                            });
                            window.dispatchEvent(event);
                          }}
                        >
                          {question}
                        </motion.button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="user-text">
                {message.content}
              </div>
            )}
          </div>

          <div className="message-actions">
            <motion.button
              className="action-btn copy-btn"
              onClick={handleCopy}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Copy message"
              aria-label="Copy message to clipboard"
            >
              {copied ? <FiCheck className="success-icon" /> : <FiCopy />}
            </motion.button>

            {isAI && onSpeak && (
              <motion.button
                className={`action-btn speak-btn ${speaking ? 'speaking' : ''}`}
                onClick={handleSpeak}
                disabled={speaking}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Read aloud"
                aria-label="Read message aloud"
              >
                <FiVolume2 />
                {speaking && (
                  <div className="speaking-indicator">
                    <div className="wave"></div>
                    <div className="wave"></div>
                    <div className="wave"></div>
                  </div>
                )}
              </motion.button>
            )}

            {isAI && (
              <div className="feedback-buttons">
                <motion.button
                  className="feedback-btn thumbs-up"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="This was helpful"
                  aria-label="Mark as helpful"
                >
                  <FiThumbsUp />
                </motion.button>
                <motion.button
                  className="feedback-btn thumbs-down"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="This wasn't helpful"
                  aria-label="Mark as not helpful"
                >
                  <FiThumbsDown />
                </motion.button>
              </div>
            )}
          </div>
        </div>
      </div>

      {message.error && (
        <motion.div
          className="message-error"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
        >
          <div className="error-content">
            <FiAlertTriangle className="error-icon" />
            <span className="error-text">
              Failed to send message. Please try again.
            </span>
            <button className="retry-btn">Retry</button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ChatMessage;