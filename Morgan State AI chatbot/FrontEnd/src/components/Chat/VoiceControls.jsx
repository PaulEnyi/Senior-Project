import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMic, 
  FiMicOff, 
  FiVolume2, 
  FiVolumeX, 
  FiSettings,
  FiPlay,
  FiPause
} from 'react-icons/fi';
import './VoiceControls.css';

const VoiceControls = ({
  isSpeaking = false,
  isListening = false,
  onStartListening,
  onStopListening,
  onToggleVoice,
  voiceSettings = {}
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState(voiceSettings.voice || 'alloy');

  // Available TTS voices
  const availableVoices = [
    { id: 'alloy', name: 'Alloy', description: 'Neutral and versatile' },
    { id: 'echo', name: 'Echo', description: 'Male, warm tone' },
    { id: 'fable', name: 'Fable', description: 'British accent, storytelling' },
    { id: 'onyx', name: 'Onyx', description: 'Deep male, authoritative' },
    { id: 'nova', name: 'Nova', description: 'Female, energetic' },
    { id: 'shimmer', name: 'Shimmer', description: 'Soft female, gentle' }
  ];

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 25,
        staggerChildren: 0.1
      }
    }
  };

  const buttonVariants = {
    hidden: { opacity: 0, y: -10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 500,
        damping: 30
      }
    }
  };

  const pulseVariants = {
    pulse: {
      scale: [1, 1.2, 1],
      opacity: [1, 0.7, 1],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <motion.div
      className="voice-controls"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Main Voice Controls */}
      <div className="voice-buttons">
        {/* Microphone Button */}
        <motion.button
          className={`voice-btn microphone-btn ${isListening ? 'listening active' : ''}`}
          onClick={isListening ? onStopListening : onStartListening}
          variants={buttonVariants}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          animate={isListening ? "pulse" : "visible"}
          title={isListening ? "Stop listening" : "Start voice input"}
        >
          <motion.div
            className="btn-icon"
            variants={pulseVariants}
            animate={isListening ? "pulse" : ""}
          >
            {isListening ? <FiMicOff /> : <FiMic />}
          </motion.div>
          
          {/* Listening indicator */}
          {isListening && (
            <div className="listening-indicator">
              <div className="sound-wave">
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
                <div className="wave-bar"></div>
              </div>
            </div>
          )}
        </motion.button>

        {/* Speaker Status */}
        <motion.div
          className={`voice-status speaker-status ${isSpeaking ? 'speaking' : ''}`}
          variants={buttonVariants}
        >
          <div className="status-icon">
            {isSpeaking ? <FiVolume2 /> : <FiVolumeX />}
          </div>
          <span className="status-text">
            {isSpeaking ? 'Speaking...' : 'Ready'}
          </span>
          
          {/* Speaking indicator */}
          {isSpeaking && (
            <div className="speaking-indicator">
              <div className="audio-bars">
                <div className="bar"></div>
                <div className="bar"></div>
                <div className="bar"></div>
              </div>
            </div>
          )}
        </motion.div>

        {/* Settings Button */}
        <motion.button
          className="voice-btn settings-btn"
          onClick={() => setShowSettings(!showSettings)}
          variants={buttonVariants}
          whileHover={{ scale: 1.1, rotate: 10 }}
          whileTap={{ scale: 0.95 }}
          title="Voice settings"
        >
          <FiSettings />
        </motion.button>
      </div>

      {/* Voice Status Panel */}
      <motion.div
        className="voice-status-panel"
        initial={{ opacity: 0, height: 0 }}
        animate={{ 
          opacity: (isListening || isSpeaking) ? 1 : 0.7,
          height: 'auto'
        }}
      >
        <div className="status-content">
          <div className="status-item">
            <span className={`indicator ${isListening ? 'active listening' : ''}`}></span>
            <span className="label">
              {isListening ? 'Listening for your voice...' : 'Voice input ready'}
            </span>
          </div>
          
          <div className="status-item">
            <span className={`indicator ${isSpeaking ? 'active speaking' : ''}`}></span>
            <span className="label">
              {isSpeaking ? 'Playing response...' : 'Text-to-speech ready'}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Voice Settings Modal */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            className="voice-settings-modal"
            initial={{ opacity: 0, scale: 0.9, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <div className="modal-header">
              <h3>Voice Settings</h3>
              <button
                className="close-btn"
                onClick={() => setShowSettings(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-content">
              {/* Voice Selection */}
              <div className="setting-group">
                <label className="setting-label">Text-to-Speech Voice</label>
                <div className="voice-options">
                  {availableVoices.map((voice) => (
                    <motion.div
                      key={voice.id}
                      className={`voice-option ${selectedVoice === voice.id ? 'selected' : ''}`}
                      onClick={() => setSelectedVoice(voice.id)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="voice-info">
                        <span className="voice-name">{voice.name}</span>
                        <span className="voice-description">{voice.description}</span>
                      </div>
                      <button
                        className="test-voice-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Test voice functionality would go here
                          console.log(`Testing voice: ${voice.id}`);
                        }}
                      >
                        <FiPlay />
                      </button>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Voice Sensitivity */}
              <div className="setting-group">
                <label className="setting-label">
                  Microphone Sensitivity
                  <span className="setting-description">
                    Adjust how sensitive the microphone is to your voice
                  </span>
                </label>
                <div className="sensitivity-control">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    defaultValue="5"
                    className="sensitivity-slider"
                  />
                  <div className="slider-labels">
                    <span>Low</span>
                    <span>High</span>
                  </div>
                </div>
              </div>

              {/* Auto-stop listening */}
              <div className="setting-group">
                <label className="setting-checkbox">
                  <input
                    type="checkbox"
                    defaultChecked={true}
                  />
                  <span className="checkmark"></span>
                  <span className="checkbox-label">
                    Auto-stop listening after silence
                    <span className="setting-description">
                      Automatically stop voice input after 3 seconds of silence
                    </span>
                  </span>
                </label>
              </div>

              {/* Push to talk */}
              <div className="setting-group">
                <label className="setting-checkbox">
                  <input
                    type="checkbox"
                    defaultChecked={false}
                  />
                  <span className="checkmark"></span>
                  <span className="checkbox-label">
                    Push-to-talk mode
                    <span className="setting-description">
                      Hold spacebar to activate voice input
                    </span>
                  </span>
                </label>
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="btn secondary"
                onClick={() => setShowSettings(false)}
              >
                Cancel
              </button>
              <button
                className="btn primary"
                onClick={() => {
                  // Save settings logic would go here
                  setShowSettings(false);
                }}
              >
                Save Settings
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Keyboard Shortcuts Hint */}
      <div className="voice-hints">
        <div className="hint-item">
          <kbd>Space</kbd> Hold for voice input
        </div>
        <div className="hint-item">
          <kbd>Esc</kbd> Stop voice features
        </div>
      </div>
    </motion.div>
  );
};

export default VoiceControls;