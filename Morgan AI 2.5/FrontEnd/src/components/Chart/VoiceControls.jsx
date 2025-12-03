import React from 'react';
import { motion } from 'framer-motion';
import { FaVolumeUp, FaVolumeMute, FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa';

const VoiceControls = ({ isEnabled, onToggle, isSpeaking, isListening }) => {
  return (
    <div className="voice-controls">
      <motion.button
        className={`voice-control-btn ${isEnabled ? 'active' : ''}`}
        onClick={onToggle}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title={isEnabled ? 'Disable voice' : 'Enable voice'}
      >
        {isEnabled ? (
          <>
            <FaVolumeUp className="control-icon" />
            <span className="control-label">Voice On</span>
          </>
        ) : (
          <>
            <FaVolumeMute className="control-icon" />
            <span className="control-label">Voice Off</span>
          </>
        )}
      </motion.button>

      {isEnabled && (
        <div className="voice-status">
          {isSpeaking && (
            <motion.div
              className="status-indicator speaking"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <FaVolumeUp className="status-icon" />
              <span>Speaking...</span>
            </motion.div>
          )}
          
          {isListening && (
            <motion.div
              className="status-indicator listening"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 1 }}
            >
              <FaMicrophone className="status-icon" />
              <span>Listening...</span>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

export default VoiceControls;