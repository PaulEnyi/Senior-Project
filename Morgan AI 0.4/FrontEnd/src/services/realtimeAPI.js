import { EventEmitter } from 'events'

class RealtimeAPIService extends EventEmitter {
  constructor() {
    super()
    this.ws = null
    this.sessionId = null
    this.isConnected = false
    this.isConnecting = false
    this.config = {
      model: 'gpt-4-1106-realtime-preview',
      voice: 'alloy',
      instructions: 'You are Morgan AI, a helpful assistant for Morgan State University Computer Science students.',
      temperature: 0.8,
      maxResponseOutputTokens: 4096,
      turnDetection: {
        type: 'server_vad',
        threshold: 0.5,
        prefixPaddingMs: 300,
        silenceDurationMs: 200
      }
    }
    this.audioQueue = []
    this.mediaRecorder = null
    this.audioContext = null
  }

  async connect(apiKey) {
    if (this.isConnected || this.isConnecting) {
      console.warn('Already connected or connecting to Realtime API')
      return
    }

    this.isConnecting = true

    try {
      // Create WebSocket connection to OpenAI Realtime API
      const url = 'wss://api.openai.com/v1/realtime?model=gpt-4-1106-realtime-preview'
      
      this.ws = new WebSocket(url, {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'OpenAI-Beta': 'realtime=v1'
        }
      })

      this.ws.onopen = () => {
        console.log('Connected to OpenAI Realtime API')
        this.isConnected = true
        this.isConnecting = false
        this.emit('connected')
        
        // Send initial session configuration
        this.sendSessionUpdate()
      }

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', error)
      }

      this.ws.onclose = () => {
        console.log('Disconnected from OpenAI Realtime API')
        this.isConnected = false
        this.isConnecting = false
        this.emit('disconnected')
        this.cleanup()
      }
    } catch (error) {
      console.error('Failed to connect to Realtime API:', error)
      this.isConnecting = false
      this.emit('error', error)
      throw error
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.cleanup()
    }
  }

  cleanup() {
    this.ws = null
    this.sessionId = null
    this.isConnected = false
    this.audioQueue = []
    
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop()
    }
    
    if (this.audioContext) {
      this.audioContext.close()
    }
  }

  sendSessionUpdate() {
    this.sendEvent({
      type: 'session.update',
      session: {
        modalities: ['text', 'audio'],
        instructions: this.config.instructions,
        voice: this.config.voice,
        input_audio_format: 'webm-opus',
        output_audio_format: 'pcm16',
        input_audio_transcription: {
          model: 'whisper-1'
        },
        turn_detection: this.config.turnDetection,
        temperature: this.config.temperature,
        max_response_output_tokens: this.config.maxResponseOutputTokens
      }
    })
  }

  sendEvent(event) {
    if (!this.isConnected || !this.ws) {
      console.error('Not connected to Realtime API')
      return false
    }

    try {
      this.ws.send(JSON.stringify(event))
      return true
    } catch (error) {
      console.error('Failed to send event:', error)
      this.emit('error', error)
      return false
    }
  }

  handleMessage(message) {
    const { type, ...data } = message

    switch (type) {
      case 'session.created':
        this.sessionId = data.session.id
        this.emit('session.created', data.session)
        break

      case 'session.updated':
        this.emit('session.updated', data.session)
        break

      case 'conversation.item.created':
        this.emit('conversation.item.created', data.item)
        this.handleConversationItem(data.item)
        break

      case 'response.created':
        this.emit('response.created', data.response)
        break

      case 'response.done':
        this.emit('response.done', data.response)
        break

      case 'response.output_item.added':
        this.emit('response.output_item.added', data.item)
        break

      case 'response.output_item.done':
        this.emit('response.output_item.done', data.item)
        break

      case 'response.text.delta':
        this.emit('response.text.delta', data)
        break

      case 'response.text.done':
        this.emit('response.text.done', data)
        break

      case 'response.audio.delta':
        this.handleAudioDelta(data)
        break

      case 'response.audio.done':
        this.emit('response.audio.done', data)
        break

      case 'response.audio_transcript.delta':
        this.emit('response.audio_transcript.delta', data)
        break

      case 'response.audio_transcript.done':
        this.emit('response.audio_transcript.done', data)
        break

      case 'input_audio_buffer.speech_started':
        this.emit('speech.started')
        break

      case 'input_audio_buffer.speech_stopped':
        this.emit('speech.stopped')
        break

      case 'input_audio_buffer.committed':
        this.emit('input_audio_buffer.committed')
        break

      case 'error':
        console.error('Realtime API error:', data.error)
        this.emit('error', data.error)
        break

      default:
        console.log('Unhandled message type:', type, data)
    }
  }

  handleConversationItem(item) {
    if (item.type === 'message') {
      if (item.role === 'assistant' && item.content) {
        item.content.forEach(content => {
          if (content.type === 'text') {
            this.emit('assistant.message', content.text)
          } else if (content.type === 'audio') {
            this.emit('assistant.audio', content.audio)
          }
        })
      }
    }
  }

  handleAudioDelta(data) {
    // Queue audio chunks for playback
    if (data.delta) {
      this.audioQueue.push(data.delta)
      this.emit('response.audio.delta', data)
    }
  }

  // Text input methods
  sendTextMessage(text) {
    return this.sendEvent({
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{
          type: 'input_text',
          text: text
        }]
      }
    })
  }

  // Audio input methods
  async startAudioRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && this.isConnected) {
          this.sendAudioChunk(event.data)
        }
      }

      this.mediaRecorder.start(100) // Send chunks every 100ms
      this.emit('recording.started')
      
      return true
    } catch (error) {
      console.error('Failed to start audio recording:', error)
      this.emit('error', error)
      return false
    }
  }

  stopAudioRecording() {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop()
      this.mediaRecorder.stream.getTracks().forEach(track => track.stop())
      this.emit('recording.stopped')
    }
  }

  async sendAudioChunk(audioData) {
    // Convert audio data to base64
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64Audio = reader.result.split(',')[1]
      this.sendEvent({
        type: 'input_audio_buffer.append',
        audio: base64Audio
      })
    }
    reader.readAsDataURL(audioData)
  }

  commitAudioBuffer() {
    return this.sendEvent({
      type: 'input_audio_buffer.commit'
    })
  }

  clearAudioBuffer() {
    return this.sendEvent({
      type: 'input_audio_buffer.clear'
    })
  }

  // Audio playback methods
  async playAudioQueue() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
    }

    for (const audioData of this.audioQueue) {
      await this.playAudioChunk(audioData)
    }

    this.audioQueue = []
  }

  async playAudioChunk(base64Audio) {
    try {
      // Decode base64 to ArrayBuffer
      const binaryString = atob(base64Audio)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }

      // Decode audio data
      const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer)
      
      // Create and play audio source
      const source = this.audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(this.audioContext.destination)
      source.start()

      // Wait for playback to complete
      return new Promise(resolve => {
        source.onended = resolve
      })
    } catch (error) {
      console.error('Failed to play audio:', error)
      this.emit('error', error)
    }
  }

  // Response generation control
  generateResponse() {
    return this.sendEvent({
      type: 'response.create',
      response: {
        modalities: ['text', 'audio']
      }
    })
  }

  cancelResponse() {
    return this.sendEvent({
      type: 'response.cancel'
    })
  }

  // Configuration methods
  updateVoice(voice) {
    this.config.voice = voice
    return this.sendSessionUpdate()
  }

  updateInstructions(instructions) {
    this.config.instructions = instructions
    return this.sendSessionUpdate()
  }

  updateTemperature(temperature) {
    this.config.temperature = temperature
    return this.sendSessionUpdate()
  }

  updateTurnDetection(settings) {
    this.config.turnDetection = { ...this.config.turnDetection, ...settings }
    return this.sendSessionUpdate()
  }

  // Utility methods
  getSessionId() {
    return this.sessionId
  }

  isReady() {
    return this.isConnected && this.sessionId !== null
  }

  getConnectionStatus() {
    if (this.isConnecting) return 'connecting'
    if (this.isConnected) return 'connected'
    return 'disconnected'
  }
}

// Create singleton instance
const realtimeAPI = new RealtimeAPIService()

export default realtimeAPI
export { RealtimeAPIService }
