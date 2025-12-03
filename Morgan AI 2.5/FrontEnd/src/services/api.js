import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('auth_token')
      localStorage.removeItem('role')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Chat Service
export const chatService = {
  async sendMessage({ message, thread_id, user_id, context }) {
    try {
      const response = await api.post('/api/chat/message', {
        message,
        thread_id,
        user_id,
        context
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message')
    }
  },

  async streamMessage({ message, thread_id, user_id }) {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('auth_token')
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message, thread_id, user_id, stream: true })
      })
      
      return response.body.getReader()
    } catch (error) {
      throw new Error('Failed to stream message')
    }
  },

  async getThreads(limit = 20, offset = 0) {
    try {
      const response = await api.get('/api/chat/threads', {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch threads')
    }
  },

  async getThreadMessages(threadId, limit = 50) {
    try {
      const response = await api.get(`/api/chat/threads/${threadId}`, {
        params: { limit }
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch messages')
    }
  },

  async deleteThread(threadId) {
    try {
      const response = await api.delete(`/api/chat/threads/${threadId}`)
      return response.data
    } catch (error) {
      throw new Error('Failed to delete thread')
    }
  },

  async submitFeedback(threadId, messageId, rating, feedback) {
    try {
      const response = await api.post('/api/chat/feedback', {
        thread_id: threadId,
        message_id: messageId,
        rating,
        feedback
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to submit feedback')
    }
  },

  async searchHistory(query, limit = 20) {
    try {
      const response = await api.get('/api/chat/search', {
        params: { query, limit }
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to search history')
    }
  }
}

export default api