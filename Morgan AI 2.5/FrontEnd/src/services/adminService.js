import api from './api'

export const adminService = {
  async getDashboardStats() {
    try {
      const response = await api.get('/api/admin/dashboard')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch dashboard stats')
    }
  },

  async getSettings() {
    try {
      const response = await api.get('/api/admin/settings')
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch settings')
    }
  },

  async updateSettings(settings) {
    try {
      const response = await api.put('/api/admin/settings', settings)
      return response.data
    } catch (error) {
      throw new Error('Failed to update settings')
    }
  },

  async getUsers(limit = 50, offset = 0) {
    try {
      const response = await api.get('/api/admin/users', {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch users')
    }
  },

  async createUser(userData) {
    try {
      const response = await api.post('/api/admin/users', userData)
      return response.data
    } catch (error) {
      throw new Error('Failed to create user')
    }
  },

  async updateUser(userId, userData) {
    try {
      const response = await api.put(`/api/admin/users/${userId}`, userData)
      return response.data
    } catch (error) {
      throw new Error('Failed to update user')
    }
  },

  async deleteUser(userId) {
    try {
      const response = await api.delete(`/api/admin/users/${userId}`)
      return response.data
    } catch (error) {
      throw new Error('Failed to delete user')
    }
  },

  async refreshKnowledgeBase() {
    try {
      const response = await api.post('/api/admin/knowledge-base/update', {
        operation: 'refresh'
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to refresh knowledge base')
    }
  },

  async addDocument(content, metadata) {
    try {
      const response = await api.post('/api/admin/knowledge-base/update', {
        operation: 'add',
        content,
        metadata
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to add document')
    }
  },

  async updateDocument(documentId, content, metadata) {
    try {
      const response = await api.post('/api/admin/knowledge-base/update', {
        operation: 'update',
        document_id: documentId,
        content,
        metadata
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to update document')
    }
  },

  async deleteDocument(documentId) {
    try {
      const response = await api.post('/api/admin/knowledge-base/update', {
        operation: 'delete',
        document_id: documentId
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to delete document')
    }
  },

  async getKnowledgeBaseStatus() {
    try {
      const response = await api.get('/api/admin/knowledge-base/status')
      return response.data
    } catch (error) {
      throw new Error('Failed to get knowledge base status')
    }
  },

  async terminateSession(userId) {
    try {
      const response = await api.post('/api/admin/sessions/terminate', {
        user_id: userId
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to terminate session')
    }
  },

  async getLogs(level = 'INFO', limit = 100) {
    try {
      const response = await api.get('/api/admin/logs', {
        params: { level, limit }
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch logs')
    }
  }
}