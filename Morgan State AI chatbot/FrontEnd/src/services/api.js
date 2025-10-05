import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('adminToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`🔄 ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    
    return response;
  },
  (error) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data || error.message);
    }
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('adminToken');
      
      // Only redirect to login if we're not already on a public route
      if (window.location.pathname.includes('/admin')) {
        window.location.href = '/';
      }
    }
    
    // Enhance error message
    const enhancedError = new Error(
      error.response?.data?.message || 
      error.response?.data?.detail || 
      error.message || 
      'An unexpected error occurred'
    );
    
    enhancedError.status = error.response?.status;
    enhancedError.data = error.response?.data;
    
    return Promise.reject(enhancedError);
  }
);

// API Service class
class APIService {
  // Chat endpoints
  async sendMessage(messageData, options = {}) {
    const response = await api.post('/api/chat/send', messageData, options);
    return response.data;
  }

  async getThreadList(params = {}) {
    const response = await api.get('/api/chat/threads', { params });
    return response.data.data;
  }

  async getThreadMessages(threadId, params = {}) {
    const response = await api.get(`/api/chat/threads/${threadId}`, { params });
    return response.data.data;
  }

  async deleteThread(threadId) {
    const response = await api.delete(`/api/chat/threads/${threadId}`);
    return response.data;
  }

  async clearThread(threadId) {
    const response = await api.post(`/api/chat/threads/${threadId}/clear`);
    return response.data;
  }

  async getKnowledgeCategories() {
    const response = await api.get('/api/chat/categories');
    return response.data.data;
  }

  async getQuickQuestions() {
    const response = await api.get('/api/chat/quick-questions');
    return response.data.data;
  }

  // Voice endpoints
  async textToSpeech(text, voice = 'alloy') {
    const response = await api.post('/api/voice/text-to-speech', {
      text,
      voice
    }, {
      responseType: 'blob'
    });
    return response.data;
  }

  async speechToText(audioFile) {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    
    const response = await api.post('/api/voice/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  async getAvailableVoices() {
    const response = await api.get('/api/voice/voices');
    return response.data.data;
  }

  async getSupportedFormats() {
    const response = await api.get('/api/voice/supported-formats');
    return response.data.data;
  }

  // Admin endpoints
  async adminLogin(credentials) {
    const response = await api.post('/api/admin/login', credentials);
    
    if (response.data.access_token) {
      localStorage.setItem('adminToken', response.data.access_token);
    }
    
    return response.data;
  }

  async adminLogout() {
    localStorage.removeItem('adminToken');
    const response = await api.post('/api/admin/logout');
    return response.data;
  }

  async refreshKnowledgeBase() {
    const response = await api.post('/api/admin/refresh-knowledge');
    return response.data;
  }

  async clearVectorDatabase() {
    const response = await api.post('/api/admin/clear-database');
    return response.data;
  }

  async getSystemHealth() {
    const response = await api.get('/api/admin/system-health');
    return response.data;
  }

  async getUsageAnalytics(params = {}) {
    const response = await api.get('/api/admin/analytics', { params });
    return response.data;
  }

  async updateKnowledgeBase(data) {
    const response = await api.post('/api/admin/knowledge-base', data);
    return response.data;
  }

  // Health check endpoints
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }

  async chatHealthCheck() {
    const response = await api.get('/api/chat/health');
    return response.data;
  }

  async voiceHealthCheck() {
    const response = await api.get('/api/voice/health');
    return response.data;
  }

  // Utility methods
  isAuthenticated() {
    const token = localStorage.getItem('adminToken');
    if (!token) return false;
    
    try {
      // Basic JWT token validation (check if it's expired)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  }

  getAuthToken() {
    return localStorage.getItem('adminToken');
  }

  clearAuthToken() {
    localStorage.removeItem('adminToken');
  }

  // Error handling helpers
  handleError(error, fallbackMessage = 'An error occurred') {
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return fallbackMessage;
  }

  // Rate limiting helper
  async withRetry(apiCall, maxRetries = 3, delayMs = 1000) {
    let lastError;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiCall();
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx) except 429 (rate limit)
        if (error.status >= 400 && error.status < 500 && error.status !== 429) {
          throw error;
        }
        
        // Wait before retrying
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delayMs * (i + 1)));
        }
      }
    }
    
    throw lastError;
  }

  // Batch operations
  async batchSendMessages(messages) {
    const promises = messages.map(message => 
      this.withRetry(() => this.sendMessage(message))
    );
    
    return await Promise.allSettled(promises);
  }

  // Upload file helper
  async uploadFile(file, endpoint, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional data to form
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });
    
    const response = await api.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          console.log(`Upload progress: ${Math.round(progress)}%`);
        }
      }
    });
    
    return response.data;
  }

  // Stream support for long responses (future enhancement)
  async streamResponse(endpoint, data, onChunk) {
    try {
      const response = await fetch(`${api.defaults.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Streaming not supported');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in buffer
        buffer = lines.pop() || '';
        
        // Process complete lines
        for (const line of lines) {
          if (line.trim()) {
            try {
              const chunk = JSON.parse(line);
              onChunk(chunk);
            } catch (e) {
              console.warn('Failed to parse streaming chunk:', line);
            }
          }
        }
      }
      
    } catch (error) {
      console.error('Streaming error:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
export const apiService = new APIService();

// Export the axios instance for direct use if needed
export { api };

// Default export
export default apiService;