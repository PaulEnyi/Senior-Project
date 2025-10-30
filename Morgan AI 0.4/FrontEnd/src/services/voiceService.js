import api from './api'

export const voiceService = {
  async textToSpeech(text, voice = 'alloy', speed = 1.0) {
    try {
      const response = await api.post('/api/voice/text-to-speech', {
        text,
        voice,
        speed,
        format: 'mp3'
      }, {
        responseType: 'blob'
      })
      
      // Create URL for audio blob
      const audioBlob = response.data
      const audioUrl = URL.createObjectURL(audioBlob)
      
      return audioUrl
    } catch (error) {
      throw new Error('Failed to convert text to speech')
    }
  },

  async speechToText(audioBlob, language = 'en') {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      formData.append('language', language)

      const response = await api.post('/api/voice/speech-to-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      return response.data
    } catch (error) {
      throw new Error('Failed to convert speech to text')
    }
  },

  async connectRealtime() {
    try {
      const response = await api.post('/api/voice/realtime/connect')
      return response.data
    } catch (error) {
      throw new Error('Failed to connect to realtime API')
    }
  },

  async disconnectRealtime(sessionId) {
    try {
      const response = await api.post('/api/voice/realtime/disconnect', {
        session_id: sessionId
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to disconnect from realtime API')
    }
  },

  async getAvailableVoices() {
    try {
      const response = await api.get('/api/voice/voices')
      return response.data.voices
    } catch (error) {
      throw new Error('Failed to fetch available voices')
    }
  },

  async getVoiceStatus() {
    try {
      const response = await api.get('/api/voice/status')
      return response.data
    } catch (error) {
      throw new Error('Failed to get voice status')
    }
  },

  async generateGreeting(username, voice = 'alloy') {
    try {
      const response = await api.post('/api/voice/greeting', {
        username,
        voice
      }, {
        responseType: 'blob'
      })
      
      const audioBlob = response.data
      const audioUrl = URL.createObjectURL(audioBlob)
      
      return audioUrl
    } catch (error) {
      throw new Error('Failed to generate greeting')
    }
  }
}