import React, { useState, useRef, useEffect, useContext } from 'react';
import { FiSend, FiMic, FiMicOff, FiUser, FiCpu, FiHelpCircle, FiX, FiTrash2, FiRefreshCw, FiVolume2, FiPause, FiPlay, FiStopCircle } from 'react-icons/fi';
import '../../styles/chat.css';
import { VoiceContext } from '../../context/VoiceContext';

// Component to format message text with proper line breaks, lists, and paragraphs
function FormattedMessage({ text }) {
  if (!text) return null;

  // Function to format the text with proper HTML structure
  const formatText = (content) => {
    let formattedContent = content;

    // Replace numbered lists (e.g., "1. Item", "2. Item")
    formattedContent = formattedContent.replace(/(\d+)\.\s+([^\n]+)/g, '<li class="numbered-item"><span class="list-number">$1.</span> <span class="list-content">$2</span></li>');
    
    // Replace bullet points (-, *, •)
    formattedContent = formattedContent.replace(/^[\-\*\•]\s+(.+)$/gm, '<li class="bullet-item">$1</li>');
    
    // Wrap consecutive list items in ul/ol tags
    formattedContent = formattedContent.replace(/(<li class="numbered-item">.*?<\/li>\s*)+/gs, '<ol class="formatted-list">$&</ol>');
    formattedContent = formattedContent.replace(/(<li class="bullet-item">.*?<\/li>\s*)+/gs, '<ul class="formatted-list">$&</ul>');
    
    // Replace **bold** text
    formattedContent = formattedContent.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Replace ### headers
    formattedContent = formattedContent.replace(/^###\s+(.+)$/gm, '<h3 class="message-heading">$1</h3>');
    formattedContent = formattedContent.replace(/^##\s+(.+)$/gm, '<h2 class="message-heading">$1</h2>');
    
    // Replace inline code `code`
    formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
    
    // Split by double newlines to create paragraphs
    const paragraphs = formattedContent.split(/\n\n+/);
    formattedContent = paragraphs
      .map(para => {
        // Skip if it's already wrapped in a tag
        if (para.trim().startsWith('<')) {
          return para;
        }
        // Replace single newlines with <br> within paragraphs
        const withBreaks = para.trim().replace(/\n/g, '<br>');
        return withBreaks ? `<p class="message-paragraph">${withBreaks}</p>` : '';
      })
      .filter(Boolean)
      .join('\n');

    return formattedContent;
  };

  const formattedHTML = formatText(text);

  return (
    <div 
      className="formatted-message-content"
      dangerouslySetInnerHTML={{ __html: formattedHTML }}
    />
  );
}

export default function ChatWindow({ user }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showQuickQuestions, setShowQuickQuestions] = useState(false);
  const [quickQuestionsData, setQuickQuestionsData] = useState(null);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [speechError, setSpeechError] = useState(null);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const {
    isSpeaking,
  speak,
  isPaused,
  pause,
  resume,
    stop,
    voices,
    selectedVoiceURI,
    setSelectedVoiceURI,
    rate,
    setRate,
    pitch,
    setPitch,
    volume,
    setVolume,
  } = useContext(VoiceContext);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch quick questions from backend
  const fetchQuickQuestions = async () => {
    if (quickQuestionsData) {
      setShowQuickQuestions(true);
      return;
    }

    setLoadingQuestions(true);
    try {
      const response = await fetch('http://localhost:8000/api/chat/quick-questions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'guest'}`
        }
      });
      const data = await response.json();
      setQuickQuestionsData(data);
      setShowQuickQuestions(true);
    } catch (error) {
      console.error('Error fetching quick questions:', error);
      // Fallback to default questions if API fails
      setQuickQuestionsData({
        categories: {
          "Department Information": [
            "Where is the Computer Science department located?",
            "Who are the faculty members in Computer Science?",
            "What are the department's office hours?",
            "How do I contact the CS department?"
          ],
          "Academic Support": [
            "What tutoring services are available for CS students?",
            "How do I get help with programming assignments?",
            "How do I join student organizations like WiCS or GDSC?",
            "What study spaces are available for CS students?"
          ],
          "Career Resources": [
            "What internship programs are recommended?",
            "How do I prepare for technical interviews?",
            "What career resources are available through the department?",
            "How do I access NeetCode, LeetCode, and other prep resources?"
          ],
          "Advising & Registration": [
            "Who is my academic advisor and how do I contact them?",
            "How do I get an enrollment PIN for registration?",
            "What are the prerequisites for advanced CS courses?",
            "How do I submit an override request for a full class?"
          ]
        }
      });
      setShowQuickQuestions(true);
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleSelectQuickQuestion = (question) => {
    setInputMessage(question);
    setShowQuickQuestions(false);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const token = localStorage.getItem('token');
    if (!token || token === 'guest') {
      alert('You must be logged in to use chat. Please log in.');
      window.location.reload();
      return;
    }

    const newMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages([...messages, newMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          message: inputMessage,
          user_id: user?.id || 'guest'
        })
      });

      let data = {};
      try {
        data = await response.json();
      } catch (jsonErr) {
        data = { detail: 'No response from server.' };
      }

      if (response.status === 401) {
        localStorage.removeItem('token');
        alert('Session expired or unauthorized. Please log in again.');
        window.location.reload();
        return;
      }

      const botMessage = {
        id: Date.now() + 1,
        text: data.message || data.response || data.detail || 'I apologize, but I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: error.message || 'Sorry, I\'m having trouble connecting right now. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Toggle voice input using Web Speech API
  const toggleVoice = async () => {
    if (isListening) {
      setIsListening(false);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    } else {
      if (!SpeechRecognition) {
        setSpeechError('Speech recognition not supported in this browser.');
        return;
      }
      setIsListening(true);
      setSpeechError(null);
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      let finalTranscript = '';
      recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        setInputMessage(finalTranscript + interimTranscript);
      };
      recognition.onerror = (event) => {
        setSpeechError('Mic error: ' + event.error);
        setIsListening(false);
      };
      recognition.onend = () => {
        setIsListening(false);
      };
      recognition.start();
    }
  };

  // Text-to-Speech: Play bot message aloud using VoiceContext
  const playTTS = (text) => {
    if (!text) return;
    speak(text);
  };

  const quickQuestions = [
    { icon: '📚', text: 'What courses are offered?', query: 'What computer science courses does Morgan State offer?' },
    { icon: '📅', text: 'When is registration?', query: 'When is the registration period?' },
    { icon: '💼', text: 'Internship opportunities', query: 'How can I find internship opportunities?' },
    { icon: '🎓', text: 'Degree requirements', query: 'What are the CS degree requirements?' }
  ];

  const handleQuickQuestion = (query) => {
    setInputMessage(query);
  };

  // Clear chat and start new conversation
  const handleClearChat = () => {
    // Show confirmation dialog
    const confirmClear = window.confirm(
      '🗑️ Clear Chat History?\n\n' +
      'This will permanently delete all messages in the current conversation and start fresh.\n\n' +
      'Are you sure you want to continue?'
    );
    
    if (confirmClear) {
      // Clear all messages
      setMessages([]);
      // Clear input
      setInputMessage('');
      // Reset states
      setIsLoading(false);
      setIsListening(false);
      setShowQuickQuestions(false);
      
      // Optional: Show success feedback
      console.log('✨ Chat cleared successfully - Starting new conversation');
    }
  };

  return (
    <div className="chat-window-container">
      {/* Welcome Section - Professional Business Layout */}
      {messages.length === 0 && (
        <div className="chat-welcome-professional">
          <div className="welcome-hero-section">
            <div className="hero-branding">
              <div className="hero-logo-container">
                <img 
                  src="/assets/morgan-logo/morgan-bear-shield.png" 
                  alt="Morgan State Computer Science" 
                  className="hero-logo-image" 
                />
              </div>
              <div className="hero-text-content">
                <h1 className="hero-university-name">Morgan State University</h1>
                <h2 className="hero-department-name">Computer Science Department</h2>
                <div className="hero-ai-badge">
                  <FiCpu className="ai-badge-icon" />
                  <span className="ai-badge-text">AI-Powered Assistant</span>
                </div>
              </div>
            </div>
            
            <div className="hero-description-card">
              <p className="hero-description-text">
                Welcome to your intelligent academic companion. Get instant answers about courses, faculty, 
                degree requirements, registration, internships, and all aspects of the Computer Science program 
                at Morgan State University.
              </p>
            </div>
          </div>

          <div className="welcome-features-section">
            <div className="features-header">
              <h3 className="features-title">How Can I Help You Today?</h3>
              <p className="features-subtitle">Select a topic below or ask your own question</p>
            </div>
            
            <div className="features-grid-professional">
              <div className="feature-category-card">
                <div className="category-header">
                  <span className="category-icon">📚</span>
                  <h4 className="category-title">Academics</h4>
                </div>
                <div className="category-questions">
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('What computer science courses does Morgan State offer?')}
                  >
                    What courses are offered?
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('What are the CS degree requirements?')}
                  >
                    Degree requirements
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('What are the prerequisites for advanced CS courses?')}
                  >
                    Course prerequisites
                  </button>
                </div>
              </div>

              <div className="feature-category-card">
                <div className="category-header">
                  <span className="category-icon">📅</span>
                  <h4 className="category-title">Registration</h4>
                </div>
                <div className="category-questions">
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('When is the registration period?')}
                  >
                    Registration dates
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('How do I get an enrollment PIN for registration?')}
                  >
                    Get enrollment PIN
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('How do I submit an override request for a full class?')}
                  >
                    Course overrides
                  </button>
                </div>
              </div>

              <div className="feature-category-card">
                <div className="category-header">
                  <span className="category-icon">💼</span>
                  <h4 className="category-title">Career & Internships</h4>
                </div>
                <div className="category-questions">
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('How can I find internship opportunities?')}
                  >
                    Internship programs
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('How do I prepare for technical interviews?')}
                  >
                    Interview preparation
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('What career resources are available through the department?')}
                  >
                    Career resources
                  </button>
                </div>
              </div>

              <div className="feature-category-card">
                <div className="category-header">
                  <span className="category-icon">🎓</span>
                  <h4 className="category-title">Student Resources</h4>
                </div>
                <div className="category-questions">
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('What tutoring services are available for CS students?')}
                  >
                    Tutoring services
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('How do I join student organizations like WiCS or GDSC?')}
                  >
                    Student organizations
                  </button>
                  <button 
                    className="category-question-btn"
                    onClick={() => handleQuickQuestion('Who are the faculty members in Computer Science?')}
                  >
                    Faculty directory
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      {messages.length > 0 && (
        <div className="chat-messages-area">
          <div className="messages-container">
            {messages.map((msg) => (
              <div key={msg.id} className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                <div className="message-avatar">
                  {msg.sender === 'user' ? (
                    <div className="avatar user-avatar">
                      <FiUser />
                    </div>
                  ) : (
                    <div className="avatar bot-avatar">
                      <FiCpu />
                    </div>
                  )}
                </div>
                <div className="message-bubble">
                  <div className="message-text">
                    <FormattedMessage text={msg.text} />
                  </div>
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  {/* TTS Play Button for bot messages */}
                  {msg.sender === 'bot' && (
                    <button
                      className="tts-play-btn"
                      title="Play message aloud"
                      onClick={() => playTTS(msg.text)}
                    >
                      <FiVolume2 />
                    </button>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chat-message bot-message">
                <div className="message-avatar">
                  <div className="avatar bot-avatar">
                    <FiCpu />
                  </div>
                </div>
                <div className="message-bubble typing-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Chat Input - Fixed at Bottom */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <div className="input-box">
            <textarea
              className="chat-textarea"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about Morgan State CS..."
              rows="1"
              disabled={isLoading}
            />
            <div className="input-actions">
              <button
                className="quick-questions-icon-btn"
                onClick={fetchQuickQuestions}
                disabled={loadingQuestions}
                title="Quick Questions"
              >
                <FiHelpCircle />
              </button>
              <button
                className={`voice-btn ${isListening ? 'listening' : ''}`}
                onClick={toggleVoice}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening ? <FiMicOff /> : <FiMic />}
              </button>
              {/* TTS Controls */}
              <button
                className="tts-pause-btn"
                onClick={() => (isPaused ? resume() : pause())}
                disabled={!isSpeaking}
                title={isPaused ? 'Resume speech' : 'Pause speech'}
                aria-label={isPaused ? 'Resume speech' : 'Pause speech'}
                tabIndex={0}
              >
                {isPaused ? <><FiPlay /><span className="tts-resume-label">Resume</span></> : <FiPause />}
              </button>
              <button
                className="tts-stop-btn"
                onClick={stop}
                disabled={!isSpeaking}
                title="Stop speech"
                aria-label="Stop speech"
                tabIndex={0}
              >
                <FiStopCircle />
              </button>
              <button
                className="clear-chat-input-btn"
                onClick={handleClearChat}
                disabled={messages.length === 0}
                title="Clear chat and start new conversation"
              >
                <FiTrash2 />
              </button>
              <button
                className="send-btn"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                title="Send message"
              >
                <FiSend />
              </button>
            </div>
          </div>
        </div>
      </div>
      {/* Show speech error if any */}
      {speechError && (
        <div className="speech-error-banner">
          <span>{speechError}</span>
        </div>
      )}

      {/* Quick Questions Modal */}
      {showQuickQuestions && quickQuestionsData && (
        <div className="quick-questions-modal-overlay" onClick={() => setShowQuickQuestions(false)}>
          <div className="quick-questions-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">
                <FiHelpCircle className="modal-icon" />
                Quick Questions
              </h2>
              <button 
                className="modal-close-btn" 
                onClick={() => setShowQuickQuestions(false)}
                title="Close"
              >
                <FiX />
              </button>
            </div>
            
            <div className="modal-content">
              {Object.entries(quickQuestionsData.categories).map(([category, questions]) => (
                <div key={category} className="question-category">
                  <h3 className="category-title">{category}</h3>
                  <div className="category-questions">
                    {questions.map((question, index) => (
                      <button
                        key={index}
                        className="modal-question-btn"
                        onClick={() => handleSelectQuickQuestion(question)}
                      >
                        <span className="question-number">{index + 1}</span>
                        <span className="question-text">{question}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="modal-footer">
              <p className="modal-footer-text">
                Click a question to add it to your message box
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
