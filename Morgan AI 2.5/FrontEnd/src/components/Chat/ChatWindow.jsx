import React, { useState, useRef, useEffect, useContext } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiSend, FiMic, FiMicOff, FiUser, FiCpu, FiHelpCircle, FiX, FiTrash2, FiRefreshCw, FiVolume2, FiPause, FiPlay, FiStopCircle, FiSearch, FiLoader, FiFileText, FiUpload, FiMessageSquare } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import '../../styles/chat.css';
import { VoiceContext } from '../../context/VoiceContext';
import { DegreeWorksContext } from '../../context/DegreeWorksContext';
import { useChat } from '../../hooks/useChat';
import toast from 'react-hot-toast';

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
  const location = useLocation();
  const navigate = useNavigate();
  const { messages, sendMessage, loadThread, currentThread, isLoading: storeLoading, addSystemMessage, createThread, saveThreadTitle } = useChat();
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showQuickQuestions, setShowQuickQuestions] = useState(false);
  const [quickQuestionsData, setQuickQuestionsData] = useState(null);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [speechError, setSpeechError] = useState(null);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSavingChat, setIsSavingChat] = useState(false);
  const [loadingThread, setLoadingThread] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const hasUnsavedChangesRef = useRef(false);
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

  const { hasTranscript, summary, refresh: refreshDegreeWorks } = useContext(DegreeWorksContext);
  const [showDWUpload, setShowDWUpload] = useState(false);
  const [dwUploading, setDwUploading] = useState(false);
  const [dwUploadError, setDwUploadError] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Save chat on component unmount (logout, navigation away, etc.)
  useEffect(() => {
    return () => {
      if (messages.length > 0 && hasUnsavedChangesRef.current) {
        saveThreadTitle();
      }
    };
  }, [messages, saveThreadTitle]);

  // Load thread if coming from chat history
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const qpThreadId = params.get('threadId');
    const openThreadId = location.state?.threadId || qpThreadId;
    const newChatFlag = location.state?.newChat;

    console.log('🔄 ChatWindow navigation effect triggered:', {
      threadId: openThreadId,
      newChat: newChatFlag,
      queryParam: qpThreadId,
      isLoading: storeLoading,
      currentThreadId: currentThread?.thread_id
    });

    if (openThreadId && !storeLoading) {
      console.log(`🚀 Initiating loadThread for: ${openThreadId}`);
      loadThread(openThreadId).then(() => {
        console.log(`✅ Thread ${openThreadId} loaded successfully, cleaning navigation state`);
        // Clean URL & state after load
        if (qpThreadId) {
          navigate(location.pathname, { replace: true });
        } else {
          navigate(location.pathname, { replace: true, state: {} });
        }
      }).catch((err) => {
        console.error(`❌ Failed to load thread ${openThreadId}:`, err);
      });
    } else if (newChatFlag) {
      console.log('✨ Creating new chat thread');
      createThread();
      hasUnsavedChangesRef.current = false;
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, location.search, loadThread, createThread, navigate]);

  // Auto-save (title only) when messages change (debounced)
  useEffect(() => {
    if (messages.length > 0 && hasUnsavedChangesRef.current && !isSavingChat) {
      const timer = setTimeout(() => {
        saveThreadTitle();
        hasUnsavedChangesRef.current = false;
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [messages, saveThreadTitle]);

  // Mark as having unsaved changes when messages are added
  useEffect(() => {
    if (messages.length > 0) {
      hasUnsavedChangesRef.current = true;
    }
  }, [messages]);

  // Legacy local loadThread removed; using store.loadThread

  // Generate chat title from first user message
  const generateChatTitle = (msgs) => {
    const firstUserMsg = msgs.find(m => m.role === 'user');
    if (!firstUserMsg) return 'New Conversation';
    let t = firstUserMsg.content.substring(0, 50);
    if (firstUserMsg.content.length > 50) t += '...';
    return t;
  };

  // New chat handled by createThread() from store

  const handleSearchChat = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/chat/search?query=${encodeURIComponent(query)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (err) {
      console.error('Error searching chats:', err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleOpenSearchResult = (resultThreadId) => {
    setShowSearchModal(false);
    setSearchQuery('');
    setSearchResults([]);
    loadThread(resultThreadId);
  };

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

  const handleDegreeWorksUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setDwUploadError('Please upload a PDF file');
      return;
    }

    setDwUploading(true);
    setDwUploadError(null);

    try {
      const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/degree-works/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        await refreshDegreeWorks();
        setShowDWUpload(false);
        
        // Add confirmation message to chat
        addSystemMessage(`✅ Degree Works uploaded successfully! I can now answer personalized questions about your academic progress. Try asking: "What classes have I completed?" or "What do I still need to take?"`);
        saveThreadTitle();
      } else {
        setDwUploadError(data.detail || 'Failed to upload Degree Works');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setDwUploadError('Network error. Please try again.');
    } finally {
      setDwUploading(false);
      event.target.value = ''; // Reset file input
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || storeLoading) return;
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    if (!token) { navigate('/login'); return; }
    const activeId = currentThread?.thread_id;
    try {
      await sendMessage(inputMessage, activeId);
      // Mark unsaved and attempt title update (non-blocking)
      hasUnsavedChangesRef.current = true;
      saveThreadTitle();
    } catch (err) {
      console.error('Send message error:', err);
    } finally {
      setInputMessage('');
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

  // Clear chat and start new conversation ("New Chat" button)
  const handleClearChat = async () => {
    // Show confirmation dialog
    const confirmClear = window.confirm(
      '🆕 Start New Chat?\n\n' +
      (messages.length > 0 
        ? 'Current conversation will be saved to Chat History.\n\n'
        : '') +
      'Are you sure you want to start a new conversation?'
    );
    
    if (confirmClear) {
      createThread();
      hasUnsavedChangesRef.current = false;
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
      {/* Thread Title & Retry */}
      {messages.length > 0 && currentThread && (
        <div className="chat-thread-header">
          <div className="thread-title"><FiFileText /> {currentThread.title || generateChatTitle(messages)}</div>
          <div style={{display:'flex', gap:'0.5rem'}}>
            <button className="new-chat-btn" onClick={() => { createThread(); toast.success('Started new chat'); hasUnsavedChangesRef.current=false; }} title="Start new chat">
              <FiRefreshCw /> New Chat
            </button>
            {loadError && (
              <button className="retry-load-btn" onClick={() => loadThread(currentThread.thread_id)} title="Retry loading conversation">
                <FiRefreshCw /> Retry
              </button>
            )}
          </div>
        </div>
      )}

      {/* Loading Skeleton */}
      {storeLoading && messages.length === 0 && (
        <div className="chat-messages-area">
          <div className="messages-container">
            <div className="loading-skeleton">
              <div className="skeleton-message bot">
                <div className="skeleton-avatar"></div>
                <div className="skeleton-bubble"></div>
              </div>
              <div className="skeleton-message user">
                <div className="skeleton-bubble"></div>
                <div className="skeleton-avatar"></div>
              </div>
              <div className="skeleton-message bot">
                <div className="skeleton-avatar"></div>
                <div className="skeleton-bubble"></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State - No Messages */}
      {!storeLoading && messages.length === 0 && currentThread && (
        <div className="chat-messages-area">
          <div className="messages-container">
            <div className="empty-thread-state">
              <div className="empty-thread-icon">
                <FiMessageSquare />
              </div>
              <h3 className="empty-thread-title">No messages in this conversation</h3>
              <p className="empty-thread-text">
                This thread exists but contains no messages yet. Start chatting to add messages.
              </p>
              <button className="start-messaging-btn" onClick={() => { createThread(); toast.success('Started new chat'); }}>
                <FiRefreshCw /> Start New Chat
              </button>
            </div>
          </div>
        </div>
      )}

      {messages.length > 0 && (
        <div className="chat-messages-area">
          <div className="messages-container">
            {loadingThread && (
              <div className="chat-message system-message">
                <div className="message-bubble">
                  <div className="message-text">Loading conversation...</div>
                </div>
              </div>
            )}
            {loadError && (
              <div className="chat-message system-message error">
                <div className="message-bubble">
                  <div className="message-text">{loadError}</div>
                </div>
              </div>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`chat-message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? (
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
                    <FormattedMessage text={msg.content} />
                  </div>
                  <div className="message-time">
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  {/* TTS Play Button for bot messages */}
                  {msg.role === 'assistant' && (
                    <button
                      className="tts-play-btn"
                      title="Play message aloud"
                      onClick={() => playTTS(msg.content)}
                    >
                      <FiVolume2 />
                    </button>
                  )}
                </div>
              </div>
            ))}
            {storeLoading && (
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
              disabled={storeLoading}
            />
            <div className="input-actions">
              <button
                className="search-chat-icon-btn"
                onClick={() => setShowSearchModal(true)}
                title="Search Chat History"
              >
                <FiSearch />
              </button>
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
                onClick={() => {
                  console.log('TTS Button clicked:', { isPaused, isSpeaking });
                  if (isPaused) {
                    console.log('Calling resume()');
                    resume();
                  } else {
                    console.log('Calling pause()');
                    pause();
                  }
                }}
                disabled={!isSpeaking && !isPaused}
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
                className="dw-upload-icon-btn"
                onClick={() => document.getElementById('dw-file-input').click()}
                title="Upload Degree Works for personalized academic guidance"
              >
                <FiFileText />
                {hasTranscript && <span className="dw-transcript-badge" />}
              </button>
              <input
                id="dw-file-input"
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={handleDegreeWorksUpload}
              />
              <button
                className="send-btn"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || storeLoading}
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

      {/* Search Modal */}
      <AnimatePresence>
        {showSearchModal && (
          <motion.div 
            className="search-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowSearchModal(false)}
          >
            <motion.div 
              className="search-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="search-modal-header">
                <h2 className="search-modal-title">
                  <FiSearch /> Search Chat History
                </h2>
                <button 
                  className="search-modal-close"
                  onClick={() => setShowSearchModal(false)}
                >
                  <FiX />
                </button>
              </div>

              <div className="search-modal-body">
                <div className="search-filters">
                  <div className="search-filter-group">
                    <label className="search-filter-label">Search by title or content</label>
                    <div className="search-input-wrapper">
                      <FiSearch className="search-icon" />
                      <input
                        type="text"
                        className="search-filter-input"
                        placeholder="Type to search..."
                        value={searchQuery}
                        onChange={(e) => {
                          setSearchQuery(e.target.value);
                          handleSearchChat(e.target.value);
                        }}
                        autoFocus
                      />
                      {isSearching && <FiLoader className="search-loader spinning" />}
                    </div>
                  </div>
                </div>

                {searchQuery.trim() && (
                  <div className="search-results-container">
                    {isSearching ? (
                      <div className="empty-state">
                        <FiLoader className="spinning" />
                        <p>Searching...</p>
                      </div>
                    ) : searchResults.length === 0 ? (
                      <div className="empty-state">
                        <FiSearch />
                        <p>No results found</p>
                      </div>
                    ) : (
                      searchResults.map((result, index) => (
                        <div
                          key={index}
                          className="search-result-item"
                          onClick={() => handleOpenSearchResult(result.thread_id)}
                        >
                          <div className="search-result-header">
                            <div className="search-result-thread">
                              {result.thread_title || 'Untitled Chat'}
                            </div>
                            <div className="search-result-badge">
                              {result.matched_in === 'title' ? 'Title match' : 
                               result.matched_in === 'content' ? 'Content match' : 
                               'Title & Content'}
                            </div>
                          </div>
                          {result.matches && result.matches.length > 0 ? (
                            <div className="search-result-content">
                              <strong>{result.matches[0].role === 'user' ? 'You' : 'Morgan AI'}:</strong> {result.matches[0].snippet || result.matches[0].content.substring(0, 150)}
                              {result.matches[0].content.length > 150 && !result.matches[0].snippet && '...'}
                            </div>
                          ) : (
                            <div className="search-result-meta">
                              {result.message_count || 0} messages
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
