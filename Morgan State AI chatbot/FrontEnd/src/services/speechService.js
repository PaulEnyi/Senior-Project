import { apiService } from './api';

class SpeechService {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.onResult = null;
    this.onError = null;
    this.onStart = null;
    this.onEnd = null;
    
    this.initializeSpeechRecognition();
  }

  /**
   * Initialize browser speech recognition
   */
  initializeSpeechRecognition() {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }

    this.recognition = new SpeechRecognition();
    
    // Configure recognition settings
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
    this.recognition.maxAlternatives = 1;

    // Set up event handlers
    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('Speech recognition started');
      if (this.onStart) this.onStart();
    };

    this.recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      if (this.onResult) {
        this.onResult({
          final: finalTranscript,
          interim: interimTranscript,
          isFinal: finalTranscript.length > 0
        });
      }

      // Auto-stop after getting final result
      if (finalTranscript) {
        this.stopListening();
      }
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      this.isListening = false;
      
      if (this.onError) {
        this.onError({
          error: event.error,
          message: this.getErrorMessage(event.error)
        });
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      console.log('Speech recognition ended');
      if (this.onEnd) this.onEnd();
    };
  }

  /**
   * Start listening for speech
   */
  startListening() {
    if (!this.recognition) {
      throw new Error('Speech recognition not supported');
    }

    if (this.isListening) {
      console.log('Already listening');
      return;
    }

    try {
      this.recognition.start();
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      throw error;
    }
  }

  /**
   * Stop listening for speech
   */
  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  /**
   * Check if speech recognition is supported
   */
  isSupported() {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }

  /**
   * Check if currently listening
   */
  getIsListening() {
    return this.isListening;
  }

  /**
   * Set event handlers
   */
  setEventHandlers({ onResult, onError, onStart, onEnd }) {
    this.onResult = onResult;
    this.onError = onError;
    this.onStart = onStart;
    this.onEnd = onEnd;
  }

  /**
   * Process audio file using backend STT service
   */
  async processAudioFile(audioFile) {
    try {
      if (!audioFile) {
        throw new Error('No audio file provided');
      }

      // Validate file size (25MB limit)
      const maxSize = 25 * 1024 * 1024;
      if (audioFile.size > maxSize) {
        throw new Error('Audio file too large. Maximum size is 25MB.');
      }

      // Validate file type
      const supportedTypes = [
        'audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/webm',
        'audio/m4a', 'audio/mp4', 'video/mp4'
      ];
      
      if (!supportedTypes.includes(audioFile.type)) {
        throw new Error(`Unsupported file type: ${audioFile.type}`);
      }

      console.log('Processing audio file:', audioFile.name, audioFile.type, audioFile.size);

      // Send to backend for processing
      const result = await apiService.speechToText(audioFile);
      
      return {
        text: result.text,
        success: true
      };

    } catch (error) {
      console.error('Audio processing failed:', error);
      throw error;
    }
  }

  /**
   * Record audio from microphone
   */
  async recordAudio(duration = 10000) {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      return new Promise((resolve, reject) => {
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          
          // Stop all tracks to release microphone
          stream.getTracks().forEach(track => track.stop());
          
          resolve(audioBlob);
        };

        mediaRecorder.onerror = (event) => {
          console.error('MediaRecorder error:', event.error);
          stream.getTracks().forEach(track => track.stop());
          reject(event.error);
        };

        // Start recording
        mediaRecorder.start();

        // Auto-stop after duration
        setTimeout(() => {
          if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
          }
        }, duration);
      });

    } catch (error) {
      console.error('Failed to record audio:', error);
      throw new Error(`Microphone access failed: ${error.message}`);
    }
  }

  /**
   * Convert recorded audio to text
   */
  async recordAndTranscribe(duration = 10000) {
    try {
      console.log('Starting audio recording...');
      
      const audioBlob = await this.recordAudio(duration);
      console.log('Recording complete, processing...');
      
      // Convert blob to file
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      
      const result = await this.processAudioFile(audioFile);
      console.log('Transcription complete:', result.text);
      
      return result;

    } catch (error) {
      console.error('Record and transcribe failed:', error);
      throw error;
    }
  }

  /**
   * Get user-friendly error messages
   */
  getErrorMessage(error) {
    const errorMessages = {
      'no-speech': 'No speech was detected. Please try again.',
      'audio-capture': 'Audio capture failed. Please check your microphone.',
      'not-allowed': 'Microphone access denied. Please allow microphone access.',
      'network': 'Network error occurred. Please check your connection.',
      'aborted': 'Speech recognition was aborted.',
      'language-not-supported': 'Language not supported.',
      'service-not-allowed': 'Speech recognition service not allowed.'
    };

    return errorMessages[error] || `Speech recognition error: ${error}`;
  }

  /**
   * Get available languages for speech recognition
   */
  getSupportedLanguages() {
    return [
      { code: 'en-US', name: 'English (US)' },
      { code: 'en-GB', name: 'English (UK)' },
      { code: 'es-ES', name: 'Spanish (Spain)' },
      { code: 'es-MX', name: 'Spanish (Mexico)' },
      { code: 'fr-FR', name: 'French (France)' },
      { code: 'de-DE', name: 'German (Germany)' },
      { code: 'it-IT', name: 'Italian (Italy)' },
      { code: 'pt-BR', name: 'Portuguese (Brazil)' },
      { code: 'ru-RU', name: 'Russian (Russia)' },
      { code: 'ja-JP', name: 'Japanese (Japan)' },
      { code: 'ko-KR', name: 'Korean (South Korea)' },
      { code: 'zh-CN', name: 'Chinese (Simplified)' }
    ];
  }

  /**
   * Set recognition language
   */
  setLanguage(languageCode) {
    if (this.recognition) {
      this.recognition.lang = languageCode;
      console.log('Speech recognition language set to:', languageCode);
    }
  }

  /**
   * Configure recognition settings
   */
  configure(options = {}) {
    if (!this.recognition) return;

    const {
      continuous = false,
      interimResults = true,
      maxAlternatives = 1,
      language = 'en-US'
    } = options;

    this.recognition.continuous = continuous;
    this.recognition.interimResults = interimResults;
    this.recognition.maxAlternatives = maxAlternatives;
    this.recognition.lang = language;

    console.log('Speech recognition configured:', options);
  }

  /**
   * Cleanup resources
   */
  destroy() {
    if (this.recognition) {
      this.stopListening();
      this.recognition = null;
    }
    
    this.onResult = null;
    this.onError = null;
    this.onStart = null;
    this.onEnd = null;
  }
}

// Create singleton instance
const speechService = new SpeechService();

export default speechService;