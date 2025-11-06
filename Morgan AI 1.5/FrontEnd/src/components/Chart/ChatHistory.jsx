import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FiX, FiPlus, FiSearch, FiClock, FiTrash2 } from 'react-icons/fi'
import { format, isToday, isYesterday } from 'date-fns'

const ChatHistory = ({ 
  threads, 
  currentThread, 
  onSelectThread, 
  onNewChat, 
  onClose 
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filteredThreads, setFilteredThreads] = useState(threads)

  useEffect(() => {
    if (searchQuery) {
      const filtered = threads.filter(thread => 
        thread.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        thread.preview?.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredThreads(filtered)
    } else {
      setFilteredThreads(threads)
    }
  }, [searchQuery, threads])

  const formatThreadDate = (date) => {
    if (!date) return ''
    const threadDate = new Date(date)
    
    if (isToday(threadDate)) {
      return `Today, ${format(threadDate, 'h:mm a')}`
    } else if (isYesterday(threadDate)) {
      return `Yesterday, ${format(threadDate, 'h:mm a')}`
    } else {
      return format(threadDate, 'MMM d, h:mm a')
    }
  }

  const groupThreadsByDate = () => {
    const groups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      older: []
    }

    filteredThreads.forEach(thread => {
      const date = new Date(thread.updated_at)
      if (isToday(date)) {
        groups.today.push(thread)
      } else if (isYesterday(date)) {
        groups.yesterday.push(thread)
      } else if ((new Date() - date) / (1000 * 60 * 60 * 24) < 7) {
        groups.thisWeek.push(thread)
      } else {
        groups.older.push(thread)
      }
    })

    return groups
  }

  const threadGroups = groupThreadsByDate()

  return (
    <motion.div
      className="chat-history-sidebar"
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      exit={{ x: -300 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <div className="history-header">
        <h2>Chat History</h2>
        <button onClick={onClose} className="close-button">
          <FiX />
        </button>
      </div>

      <div className="history-actions">
        <button onClick={onNewChat} className="new-chat-button">
          <FiPlus />
          New Chat
        </button>
      </div>

      <div className="history-search">
        <FiSearch />
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="history-list">
        {Object.entries(threadGroups).map(([group, groupThreads]) => {
          if (groupThreads.length === 0) return null

          const groupTitle = {
            today: 'Today',
            yesterday: 'Yesterday',
            thisWeek: 'This Week',
            older: 'Older'
          }[group]

          return (
            <div key={group} className="thread-group">
              <h3 className="group-title">{groupTitle}</h3>
              {groupThreads.map(thread => (
                <motion.div
                  key={thread.id}
                  className={`thread-item ${thread.id === currentThread ? 'active' : ''}`}
                  onClick={() => onSelectThread(thread.id)}
                  whileHover={{ x: 4 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="thread-content">
                    <h4 className="thread-title">
                      {thread.title || 'Untitled Conversation'}
                    </h4>
                    <p className="thread-preview">
                      {thread.preview || 'No preview available'}
                    </p>
                    <div className="thread-meta">
                      <FiClock />
                      <span>{formatThreadDate(thread.updated_at)}</span>
                    </div>
                  </div>
                  <button 
                    className="delete-thread"
                    onClick={(e) => {
                      e.stopPropagation()
                      // Handle delete
                    }}
                  >
                    <FiTrash2 />
                  </button>
                </motion.div>
              ))}
            </div>
          )
        })}

        {filteredThreads.length === 0 && (
          <div className="no-threads">
            <p>No conversations found</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default ChatHistory