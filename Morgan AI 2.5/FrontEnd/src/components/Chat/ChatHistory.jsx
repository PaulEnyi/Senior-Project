import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiClock, 
  FiMessageSquare, 
  FiTrash2, 
  FiSearch,
  FiCalendar,
  FiLoader,
  FiAlertCircle,
  FiPlus,
  FiEdit2,
  FiCheck,
  FiX,
  FiStar,
  FiFilter,
  FiChevronDown
} from 'react-icons/fi';
import '../../styles/chat.css';

export default function ChatHistory() {
  const navigate = useNavigate();
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [deletingThreadId, setDeletingThreadId] = useState(null);
  const [editingThreadId, setEditingThreadId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('updated'); // 'updated', 'created', 'title', 'messages'
  const [favorites, setFavorites] = useState(() => {
    const saved = localStorage.getItem('chat_favorites');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    fetchThreads();
    
    // Auto-refresh every 10 seconds to catch new chats
    const interval = setInterval(() => {
      fetchThreads();
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchThreads = async () => {
    setLoading(true);
    setError(null);
    try {
          const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
          if (!token) {
        setError('Please log in to view chat history');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/chat/threads', {
        headers: {
              'Authorization': `Bearer ${token}`,
        }
      });

      if (response.status === 401) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }

      const data = await response.json();
      setThreads(data.threads || []);
    } catch (err) {
      console.error('Error fetching chat history:', err);
      setError('Failed to load chat history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChat = async (query) => {
    if (!query.trim() && !dateFrom && !dateTo) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
          const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
      
      // Build query parameters
      const params = new URLSearchParams();
      if (query.trim()) {
        params.append('query', query);
      }
      if (dateFrom) {
        params.append('date_from', new Date(dateFrom).toISOString());
      }
      if (dateTo) {
        params.append('date_to', new Date(dateTo).toISOString());
      }
      
      const response = await fetch(
        `http://localhost:8000/api/chat/search?${params.toString()}`,
        {
          headers: {
                'Authorization': `Bearer ${token}`,
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

  const handleDeleteThread = async (threadId, e) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      return;
    }

    setDeletingThreadId(threadId);
    try {
          const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/chat/threads/${threadId}`, {
        method: 'DELETE',
        headers: {
              'Authorization': `Bearer ${token}`,
        }
      });

      if (response.ok) {
        setThreads(threads.filter(t => t.thread_id !== threadId));
        setSearchResults(searchResults.filter(r => r.thread_id !== threadId));
        
        // Remove from favorites if present
        const newFavorites = favorites.filter(id => id !== threadId);
        setFavorites(newFavorites);
        localStorage.setItem('chat_favorites', JSON.stringify(newFavorites));
      } else {
        setError('Failed to delete chat. Please try again.');
      }
    } catch (err) {
      console.error('Error deleting thread:', err);
      setError('Failed to delete chat. Please try again.');
    } finally {
      setDeletingThreadId(null);
    }
  };

  const handleStartEditTitle = (threadId, currentTitle, e) => {
    e.stopPropagation();
    setEditingThreadId(threadId);
    setEditTitle(currentTitle || 'Untitled Chat');
  };

  const handleCancelEditTitle = (e) => {
    if (e) e.stopPropagation();
    setEditingThreadId(null);
    setEditTitle('');
  };

  const handleSaveTitle = async (threadId, e) => {
    e.stopPropagation();
    
    if (!editTitle.trim()) {
      setError('Title cannot be empty');
      return;
    }

    try {
      const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/chat/threads/${threadId}/title`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: editTitle.trim() })
      });

      if (response.ok) {
        // Update local state
        setThreads(threads.map(t => 
          t.thread_id === threadId ? { ...t, title: editTitle.trim() } : t
        ));
        setSearchResults(searchResults.map(r => 
          r.thread_id === threadId ? { ...r, thread_title: editTitle.trim() } : r
        ));
        setEditingThreadId(null);
        setEditTitle('');
      } else {
        setError('Failed to update title. Please try again.');
      }
    } catch (err) {
      console.error('Error updating title:', err);
      setError('Failed to update title. Please try again.');
    }
  };

  const toggleFavorite = (threadId, e) => {
    e.stopPropagation();
    const newFavorites = favorites.includes(threadId)
      ? favorites.filter(id => id !== threadId)
      : [...favorites, threadId];
    setFavorites(newFavorites);
    localStorage.setItem('chat_favorites', JSON.stringify(newFavorites));
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setDateFrom('');
    setDateTo('');
    setSearchResults([]);
  };

  const handleOpenThread = (threadId) => {
    // Navigate to chat with thread_id as state
    navigate('/', { state: { threadId } });
  };

  const handleNewChat = () => {
    // Navigate to chat with newChat flag
    navigate('/', { state: { newChat: true } });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const displayThreads = searchQuery.trim() || dateFrom || dateTo ? searchResults : threads;
  
  // Sort threads based on selected sort option
  const sortedThreads = [...displayThreads].sort((a, b) => {
    // Always show favorites first
    const aFav = favorites.includes(a.thread_id);
    const bFav = favorites.includes(b.thread_id);
    if (aFav && !bFav) return -1;
    if (!aFav && bFav) return 1;
    
    // Then sort by selected criteria
    switch (sortBy) {
      case 'created':
        return new Date(b.created_at || 0) - new Date(a.created_at || 0);
      case 'title':
        return (a.title || a.thread_title || '').localeCompare(b.title || b.thread_title || '');
      case 'messages':
        return (b.message_count || 0) - (a.message_count || 0);
      case 'updated':
      default:
        return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
    }
  });
  
  const groupedByThread = {};
  
  // Group search results by thread
  if ((searchQuery.trim() || dateFrom || dateTo) && searchResults.length > 0) {
    searchResults.forEach(result => {
      if (!groupedByThread[result.thread_id]) {
        groupedByThread[result.thread_id] = {
          thread_id: result.thread_id,
          title: result.thread_title || 'Untitled Chat',
          created_at: result.created_at,
          updated_at: result.updated_at,
          message_count: result.message_count,
          matches: []
        };
      }
      if (result.matches && result.matches.length > 0) {
        groupedByThread[result.thread_id].matches.push(...result.matches);
      }
    });
  }

  return (
    <div className="chat-history-page">
      <div className="chat-history-header">
        <div className="header-title-section">
          <FiClock className="header-icon" />
          <div>
            <h1 className="page-title">Chat History</h1>
            <p className="page-subtitle">View, search, and manage your previous conversations</p>
          </div>
        </div>

        <div className="header-actions">
          <button className="new-chat-btn" onClick={handleNewChat}>
            <FiPlus /> New Chat
          </button>
          <button 
            className={`filter-toggle-btn ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <FiFilter /> Filters
          </button>
        </div>

        <div className="search-bar-container">
          <div className="search-input-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search messages, titles..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                handleSearchChat(e.target.value);
              }}
            />
            {isSearching && <FiLoader className="search-loader spinning" />}
          </div>
        </div>

        {/* Advanced Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              className="filters-panel"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="filters-content">
                <div className="filter-group">
                  <label className="filter-label">
                    <FiCalendar /> Date Range
                  </label>
                  <div className="date-range-inputs">
                    <input
                      type="date"
                      className="date-input"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                      placeholder="From date"
                    />
                    <span className="date-separator">to</span>
                    <input
                      type="date"
                      className="date-input"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                      placeholder="To date"
                    />
                  </div>
                </div>

                <div className="filter-group">
                  <label className="filter-label">
                    Sort By
                  </label>
                  <select 
                    className="sort-select"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="updated">Recently Updated</option>
                    <option value="created">Recently Created</option>
                    <option value="title">Title (A-Z)</option>
                    <option value="messages">Message Count</option>
                  </select>
                </div>

                <div className="filter-actions">
                  <button 
                    className="apply-filters-btn"
                    onClick={() => handleSearchChat(searchQuery)}
                  >
                    Apply Filters
                  </button>
                  <button 
                    className="clear-filters-btn"
                    onClick={handleClearFilters}
                  >
                    Clear All
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="chat-history-content">
        {loading ? (
          <div className="loading-state">
            <FiLoader className="spinning" />
            <p>Loading chat history...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <FiAlertCircle />
            <p>{error}</p>
          </div>
        ) : (searchQuery.trim() || dateFrom || dateTo) && searchResults.length === 0 ? (
          <div className="empty-state">
            <FiSearch />
            <p>No results found{searchQuery.trim() ? ` for "${searchQuery}"` : ''}</p>
            <button className="clear-search-btn" onClick={handleClearFilters}>
              Clear filters
            </button>
          </div>
        ) : threads.length === 0 ? (
          <div className="empty-state">
            <FiMessageSquare />
            <p>No chat history yet</p>
            <p className="empty-subtitle">Start a conversation to see it here</p>
            <button className="start-chat-btn" onClick={() => navigate('/')}>
              Start chatting
            </button>
          </div>
        ) : (searchQuery.trim() || dateFrom || dateTo) ? (
          // Display search results grouped by thread
          <div className="search-results-list">
            {Object.values(groupedByThread).sort((a, b) => {
              const aFav = favorites.includes(a.thread_id);
              const bFav = favorites.includes(b.thread_id);
              if (aFav && !bFav) return -1;
              if (!aFav && bFav) return 1;
              return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
            }).map(({ thread_id, title, matches, created_at, updated_at, message_count }) => (
              <motion.div
                key={thread_id}
                className="search-result-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                onClick={() => handleOpenThread(thread_id)}
              >
                <div className="result-header">
                  <div className="result-title-section">
                    {favorites.includes(thread_id) && (
                      <FiStar className="favorite-star filled" />
                    )}
                    <h3 className="result-title">{title}</h3>
                  </div>
                  <div className="result-actions">
                    <button
                      className="favorite-btn"
                      onClick={(e) => toggleFavorite(thread_id, e)}
                      title={favorites.includes(thread_id) ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      <FiStar className={favorites.includes(thread_id) ? 'filled' : ''} />
                    </button>
                    <button
                      className="delete-thread-btn"
                      onClick={(e) => handleDeleteThread(thread_id, e)}
                      disabled={deletingThreadId === thread_id}
                    >
                      {deletingThreadId === thread_id ? (
                        <FiLoader className="spinning" />
                      ) : (
                        <FiTrash2 />
                      )}
                    </button>
                  </div>
                </div>
                <div className="result-meta">
                  <span className="result-date">
                    <FiCalendar />
                    {formatDate(updated_at || created_at)}
                  </span>
                  <span className="result-message-count">
                    {message_count || 0} messages
                  </span>
                </div>
                <div className="result-matches">
                  {matches && matches.slice(0, 3).map((match, idx) => (
                    <div key={idx} className="match-preview">
                      <span className="match-role">{match.role === 'user' ? 'You' : 'Morgan AI'}:</span>
                      <span className="match-content">{match.content.substring(0, 100)}...</span>
                    </div>
                  ))}
                  {matches && matches.length > 3 && (
                    <p className="more-matches">+{matches.length - 3} more matches</p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          // Display all threads
          <div className="threads-list">
            <AnimatePresence>
              {sortedThreads.map((thread, index) => (
                <motion.div
                  key={thread.thread_id}
                  className={`thread-card ${favorites.includes(thread.thread_id) ? 'favorited' : ''}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => handleOpenThread(thread.thread_id)}
                >
                  <div className="thread-header">
                    <div className="thread-icon-wrapper">
                      <div className="thread-icon">
                        <FiMessageSquare />
                      </div>
                      {favorites.includes(thread.thread_id) && (
                        <FiStar className="favorite-indicator" />
                      )}
                    </div>
                    <div className="thread-info">
                      {editingThreadId === thread.thread_id ? (
                        <div className="title-edit-container" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="text"
                            className="title-edit-input"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') handleSaveTitle(thread.thread_id, e);
                              if (e.key === 'Escape') handleCancelEditTitle(e);
                            }}
                            autoFocus
                          />
                          <div className="title-edit-actions">
                            <button
                              className="title-save-btn"
                              onClick={(e) => handleSaveTitle(thread.thread_id, e)}
                              title="Save title"
                            >
                              <FiCheck />
                            </button>
                            <button
                              className="title-cancel-btn"
                              onClick={handleCancelEditTitle}
                              title="Cancel"
                            >
                              <FiX />
                            </button>
                          </div>
                        </div>
                      ) : (
                        <h3 className="thread-title">
                          {thread.title || 'Untitled Chat'}
                        </h3>
                      )}
                      <div className="thread-meta">
                        <span className="thread-date">
                          <FiCalendar />
                          {formatDate(thread.updated_at || thread.created_at)}
                        </span>
                        <span className="thread-messages">
                          {thread.message_count || 0} messages
                        </span>
                      </div>
                    </div>
                    <div className="thread-actions">
                      {editingThreadId !== thread.thread_id && (
                        <button
                          className="edit-title-btn"
                          onClick={(e) => handleStartEditTitle(thread.thread_id, thread.title, e)}
                          title="Edit title"
                        >
                          <FiEdit2 />
                        </button>
                      )}
                      <button
                        className="favorite-btn"
                        onClick={(e) => toggleFavorite(thread.thread_id, e)}
                        title={favorites.includes(thread.thread_id) ? 'Remove from favorites' : 'Add to favorites'}
                      >
                        <FiStar className={favorites.includes(thread.thread_id) ? 'filled' : ''} />
                      </button>
                      <button
                        className="delete-thread-btn"
                        onClick={(e) => handleDeleteThread(thread.thread_id, e)}
                        disabled={deletingThreadId === thread.thread_id}
                      >
                        {deletingThreadId === thread.thread_id ? (
                          <FiLoader className="spinning" />
                        ) : (
                          <FiTrash2 />
                        )}
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
