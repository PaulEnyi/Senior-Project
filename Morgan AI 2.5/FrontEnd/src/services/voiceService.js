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
  },

  // --- WebSocket Streaming (Low-latency voice) ---
  createStreamingClient({ onTranscript, onResponse, onError, onReset, onMetrics } = {}) {
    let ws
    let mediaRecorder
    let sessionId = `ws_${Math.random().toString(16).slice(2)}`
    let audioChunks = []
    const handlers = { onTranscript, onResponse, onError, onReset, onMetrics }

    function connect(token) {
      const base = window.location.origin.replace(/^http/, 'ws')
      const url = new URL(`${base}/ws/voice/${sessionId}`)
      if (token) url.searchParams.set('token', `Bearer ${token}`)
      ws = new WebSocket(url.toString())
      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data)
          if (msg.type === 'transcript' && handlers.onTranscript) handlers.onTranscript(msg)
          else if (msg.type === 'response' && handlers.onResponse) handlers.onResponse(msg)
          else if (msg.type === 'reset' && handlers.onReset) handlers.onReset()
          else if (msg.type === 'error' && handlers.onError) handlers.onError(msg.error)
          else if (msg.type === 'response' && handlers.onMetrics && msg.metrics) handlers.onMetrics(msg.metrics)
          else if (msg.type === 'audio_start') { audioChunks = [] }
          else if (msg.type === 'audio_chunk' && msg.b64) { audioChunks.push(msg.b64) }
          else if (msg.type === 'audio_end') {
            const b64 = audioChunks.join('')
            const binary = atob(b64)
            const len = binary.length
            const bytes = new Uint8Array(len)
            for (let i = 0; i < len; i++) bytes[i] = binary.charCodeAt(i)
            const blob = new Blob([bytes], { type: 'audio/mpeg' })
            const url = URL.createObjectURL(blob)
            if (handlers.onResponse) handlers.onResponse({ audioUrl: url })
          }
        } catch {
          // ignore non JSON acknowledgements
        }
      }
      return new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject })
    }

    async function startRecording(intervalMs = 250) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
          const fr = new FileReader()
          fr.onload = () => ws.send(fr.result)
          fr.readAsArrayBuffer(e.data)
        }
      }
      mediaRecorder.start(intervalMs)
    }

    function commit() { if (ws && ws.readyState === WebSocket.OPEN) ws.send('commit') }
    function reset() { if (ws && ws.readyState === WebSocket.OPEN) ws.send('reset') }
    function stop() { if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop() }
    function close() { if (ws) ws.close() }

    return { connect, startRecording, commit, reset, stop, close, sessionId }
  }
}