// frontend/src/services/audioService.js
import { apiService } from './api.js';

class AudioService {
  constructor() {
    this.currentAudio = null;
    this.isPlaying = false;
    this.audioQueue = [];
    this.defaultVoice = 'alloy';
    this.volume = 1.0;
    this.playbackRate = 1.0;
    
    // Available voices from OpenAI TTS
    this.availableVoices = [
      { id: 'alloy', name: 'Alloy', description: 'Neutral and versatile' },
      { id: 'echo', name: 'Echo', description: 'Male, warm tone' },
      { id: 'fable', name: 'Fable', description: 'British accent, storytelling' },
      { id: 'onyx', name: 'Onyx', description: 'Deep male, authoritative' },
      { id: 'nova', name: 'Nova', description: 'Female, energetic' },
      { id: 'shimmer', name: 'Shimmer', description: 'Soft female, gentle' }
    ];
    
    // Load saved preferences
    this.loadPreferences();
  }

  /**
   * Convert text to speech using OpenAI TTS API
   * @param {string} text - Text to convert to speech
   * @param {Object} options - TTS options
   * @returns {Promise<boolean>} - Success status
   */
  async textToSpeech(text, options = {}) {
    try {
      if (!text || typeof text !== 'string') {
        throw new Error('Text must be a non-empty string');
      }

      // Clean and prepare text
      const cleanText = this.prepareTextForTTS(text);
      if (!cleanText) {
        console.warn('Text is empty after cleaning, skipping TTS');
        return false;
      }

      const voice = options.voice || this.defaultVoice;
      
      // Stop current audio if playing
      if (this.isPlaying) {
        this.stop();
      }

      console.log(`Generating TTS for: "${cleanText.substring(0, 50)}..." with voice: ${voice}`);

      // Get audio blob from API
      const audioBlob = await apiService.textToSpeech(cleanText, voice);
      
      if (!audioBlob || audioBlob.size === 0) {
        throw new Error('Received empty audio response');
      }

      // Create audio URL and play
      const audioUrl = URL.createObjectURL(audioBlob);
      const success = await this.playAudio(audioUrl, options);
      
      return success;

    } catch (error) {
      console.error('TTS Error:', error);
      this.handleTTSError(error);
      return false;
    }
  }

  /**
   * Play audio from URL
   * @param {string} audioUrl - Audio blob URL
   * @param {Object} options - Playback options
   * @returns {Promise<boolean>} - Success status
   */
  async playAudio(audioUrl, options = {}) {
    return new Promise((resolve, reject) => {
      try {
        // Create audio element
        const audio = new Audio(audioUrl);
        this.currentAudio = audio;
        
        // Configure audio
        audio.volume = options.volume || this.volume;
        audio.playbackRate = options.playbackRate || this.playbackRate;
        
        // Event handlers
        audio.onloadstart = () => {
          console.log('Audio loading started');
        };

        audio.oncanplay = () => {
          console.log('Audio can start playing');
        };

        audio.onplay = () => {
          this.isPlaying = true;
          this.dispatchEvent('tts-started', { text: options.text });
          console.log('Audio playback started');
        };

        audio.onended = () => {
          this.isPlaying = false;
          this.currentAudio = null;
          URL.revokeObjectURL(audioUrl);
          this.dispatchEvent('tts-ended', { text: options.text });
          console.log('Audio playback ended');
          resolve(true);
        };

        audio.onpause = () => {
          this.isPlaying = false;
          this.dispatchEvent('tts-paused', { text: options.text });
          console.log('Audio playback paused');
        };

        audio.onerror = (error) => {
          this.isPlaying = false;
          this.currentAudio = null;
          URL.revokeObjectURL(audioUrl);
          this.dispatchEvent('tts-error', { error: error.message });
          console.error('Audio playback error:', error);
          reject(new Error(`Audio playback failed: ${error.message}`));
        };

        // Start playback
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log('Audio play promise resolved');
            })
            .catch((error) => {
              console.error('Audio play promise rejected:', error);
              this.handlePlaybackError(error);
              reject(error);
            });
        }

      } catch (error) {
        console.error('Audio setup error:', error);
        reject(error);
      }
    });
  }

  /**
   * Stop current audio playback
   */
  stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    this.isPlaying = false;
    this.dispatchEvent('tts-stopped');
    console.log('Audio playback stopped');
  }

  /**
   * Pause current audio playback
   */
  pause() {
    if (this.currentAudio && this.isPlaying) {
      this.currentAudio.pause();
      this.dispatchEvent('tts-paused');
    }
  }

  /**
   * Resume audio playback
   */
  resume() {
    if (this.currentAudio && !this.isPlaying) {
      this.currentAudio.play()
        .then(() => {
          this.dispatchEvent('tts-resumed');
        })
        .catch((error) => {
          console.error('Resume playback error:', error);
          this.handlePlaybackError(error);
        });
    }
  }

  /**
   * Set volume (0.0 to 1.0)
   * @param {number} volume - Volume level
   */
  setVolume(volume) {
    if (volume >= 0 && volume <= 1) {
      this.volume = volume;
      if (this.currentAudio) {
        this.currentAudio.volume = volume;
      }
      this.savePreferences();
    }
  }

  /**
   * Set playback rate (0.5 to 2.0)
   * @param {number} rate - Playback rate
   */
  setPlaybackRate(rate) {
    if (rate >= 0.5 && rate <= 2.0) {
      this.playbackRate = rate;
      if (this.currentAudio) {
        this.currentAudio.playbackRate = rate;
      }
      this.savePreferences();
    }
  }

  /**
   * Set default voice
   * @param {string} voiceId - Voice ID
   */
  setDefaultVoice(voiceId) {
    if (this.availableVoices.find(v => v.id === voiceId)) {
      this.defaultVoice = voiceId;
      this.savePreferences();
    }
  }

  /**
   * Get available voices
   * @returns {Array} - Available voices
   */
  getAvailableVoices() {
    return this.availableVoices;
  }

  /**
   * Check if currently playing
   * @returns {boolean} - Playing status
   */
  getIsPlaying() {
    return this.isPlaying;
  }

  /**
   * Get current settings
   * @returns {Object} - Current settings
   */
  getSettings() {
    return {
      defaultVoice: this.defaultVoice,
      volume: this.volume,
      playbackRate: this.playbackRate,
      isPlaying: this.isPlaying
    };
  }

  /**
   * Prepare text for TTS by cleaning and formatting
   * @param {string} text - Raw text
   * @returns {string} - Cleaned text
   */
  prepareTextForTTS(text) {
    if (!text) return '';

    let cleanText = text
      // Remove markdown formatting
      .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
      .replace(/\*(.*?)\*/g, '$1')     // Italic
      .replace(/`(.*?)`/g, '$1')       // Code
      .replace(/#{1,6}\s*/g, '')       // Headers
      .replace(/>\s*/g, '')            // Blockquotes
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Links
      
      // Clean up special characters
      .replace(/[""]/g, '"')           // Smart quotes
      .replace(/['']/g, "'")           // Smart apostrophes
      .replace(/…/g, '...')            // Ellipsis
      .replace(/–/g, '-')              // En dash
      .replace(/—/g, ' - ')            // Em dash
      
      // Fix spacing
      .replace(/\s+/g, ' ')            // Multiple spaces
      .replace(/\n+/g, '. ')           // Line breaks
      .trim();

    // Limit length for TTS API (OpenAI has a 4000 character limit)
    if (cleanText.length > 4000) {
      cleanText = cleanText.substring(0, 3950) + '...';
      console.warn('Text truncated for TTS due to length limit');
    }

    return cleanText;
  }

  /**
   * Handle TTS errors
   * @param {Error} error - Error object
   */
  handleTTSError(error) {
    const errorMessage = error.message || 'Unknown TTS error';
    
    this.dispatchEvent('tts-error', { 
      error: errorMessage,
      type: 'tts-generation'
    });

    // Show user-friendly error messages
    if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
      console.error('TTS Network Error: Check your internet connection');
    } else if (errorMessage.includes('rate limit')) {
      console.error('TTS Rate Limited: Please wait before trying again');
    } else if (errorMessage.includes('empty')) {
      console.error('TTS Error: No text to speak');
    } else {
      console.error('TTS Error:', errorMessage);
    }
  }

  /**
   * Handle audio playback errors
   * @param {Error} error - Error object
   */
  handlePlaybackError(error) {
    const errorMessage = error.message || 'Audio playback error';
    
    this.dispatchEvent('tts-error', { 
      error: errorMessage,
      type: 'audio-playback'
    });

    if (errorMessage.includes('NotAllowedError')) {
      console.error('Audio Blocked: User interaction required to play audio');
    } else if (errorMessage.includes('NotSupportedError')) {
      console.error('Audio Format: Unsupported audio format');
    } else {
      console.error('Audio Playback Error:', errorMessage);
    }
  }

  /**
   * Dispatch custom events
   * @param {string} eventName - Event name
   * @param {Object} detail - Event detail
   */
  dispatchEvent(eventName, detail = {}) {
    const event = new CustomEvent(eventName, { detail });
    window.dispatchEvent(event);
  }

  /**
   * Save preferences to localStorage
   */
  savePreferences() {
    try {
      const preferences = {
        defaultVoice: this.defaultVoice,
        volume: this.volume,
        playbackRate: this.playbackRate
      };
      
      localStorage.setItem('morgan-ai-audio-preferences', JSON.stringify(preferences));
    } catch (error) {
      console.warn('Failed to save audio preferences:', error);
    }
  }

  /**
   * Load preferences from localStorage
   */
  loadPreferences() {
    try {
      const saved = localStorage.getItem('morgan-ai-audio-preferences');
      if (saved) {
        const preferences = JSON.parse(saved);
        
        if (preferences.defaultVoice && 
            this.availableVoices.find(v => v.id === preferences.defaultVoice)) {
          this.defaultVoice = preferences.defaultVoice;
        }
        
        if (typeof preferences.volume === 'number' && 
            preferences.volume >= 0 && preferences.volume <= 1) {
          this.volume = preferences.volume;
        }
        
        if (typeof preferences.playbackRate === 'number' && 
            preferences.playbackRate >= 0.5 && preferences.playbackRate <= 2.0) {
          this.playbackRate = preferences.playbackRate;
        }
      }
    } catch (error) {
      console.warn('Failed to load audio preferences:', error);
    }
  }

  /**
   * Test TTS functionality
   * @returns {Promise<boolean>} - Test success
   */
  async testTTS() {
    try {
      console.log('Testing TTS functionality...');
      const success = await this.textToSpeech('Morgan AI text to speech test.', {
        voice: this.defaultVoice
      });
      
      if (success) {
        console.log('TTS test successful');
      } else {
        console.warn('TTS test failed');
      }
      
      return success;
    } catch (error) {
      console.error('TTS test error:', error);
      return false;
    }
  }
}

// Create and export singleton instance
export const audioService = new AudioService();

// Export the class for direct instantiation if needed
export default AudioService;