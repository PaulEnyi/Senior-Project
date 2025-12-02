import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { FiToggleLeft, FiToggleRight, FiSave } from 'react-icons/fi'
import toast from 'react-hot-toast'

const SettingsPanel = ({ settings, onUpdate }) => {
  const [localSettings, setLocalSettings] = useState(settings)
  const [hasChanges, setHasChanges] = useState(false)

  const handleChange = (key, value) => {
    setLocalSettings(prev => ({
      ...prev,
      [key]: value
    }))
    setHasChanges(true)
  }

  const handleSave = () => {
    onUpdate(localSettings)
    setHasChanges(false)
  }

  const voiceOptions = [
    { value: 'alloy', label: 'Alloy' },
    { value: 'echo', label: 'Echo' },
    { value: 'fable', label: 'Fable' },
    { value: 'onyx', label: 'Onyx' },
    { value: 'nova', label: 'Nova' },
    { value: 'shimmer', label: 'Shimmer' }
  ]

  return (
    <motion.div
      className="settings-panel"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <h2>System Settings</h2>

      <div className="settings-section">
        <h3>Voice Settings</h3>
        
        <div className="setting-item">
          <div className="setting-info">
            <label>Enable Voice Features</label>
            <p>Allow text-to-speech and speech-to-text functionality</p>
          </div>
          <button
            className="toggle-button"
            onClick={() => handleChange('enable_voice', !localSettings.enable_voice)}
          >
            {localSettings.enable_voice ? (
              <FiToggleRight className="toggle-on" />
            ) : (
              <FiToggleLeft className="toggle-off" />
            )}
          </button>
        </div>

        <div className="setting-item">
          <div className="setting-info">
            <label>TTS Voice</label>
            <p>Voice model for text-to-speech</p>
          </div>
          <select
            value={localSettings.tts_voice}
            onChange={(e) => handleChange('tts_voice', e.target.value)}
            disabled={!localSettings.enable_voice}
          >
            {voiceOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="setting-item">
          <div className="setting-info">
            <label>Speech Speed</label>
            <p>TTS playback speed (0.25 - 4.0)</p>
          </div>
          <input
            type="number"
            min="0.25"
            max="4"
            step="0.25"
            value={localSettings.tts_speed}
            onChange={(e) => handleChange('tts_speed', parseFloat(e.target.value))}
            disabled={!localSettings.enable_voice}
          />
        </div>
      </div>

      <div className="settings-section">
        <h3>AI Settings</h3>
        
        <div className="setting-item">
          <div className="setting-info">
            <label>Max Tokens</label>
            <p>Maximum response length (100 - 4000)</p>
          </div>
          <input
            type="number"
            min="100"
            max="4000"
            step="100"
            value={localSettings.max_tokens}
            onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
          />
        </div>

        <div className="setting-item">
          <div className="setting-info">
            <label>Temperature</label>
            <p>Response creativity (0 - 2)</p>
          </div>
          <input
            type="number"
            min="0"
            max="2"
            step="0.1"
            value={localSettings.temperature}
            onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          />
        </div>

        <div className="setting-item">
          <div className="setting-info">
            <label>Top K Results</label>
            <p>Knowledge base search results (1 - 20)</p>
          </div>
          <input
            type="number"
            min="1"
            max="20"
            value={localSettings.top_k_results}
            onChange={(e) => handleChange('top_k_results', parseInt(e.target.value))}
          />
        </div>
      </div>

      {hasChanges && (
        <motion.div
          className="settings-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <button
            className="save-button"
            onClick={handleSave}
          >
            <FiSave />
            Save Changes
          </button>
        </motion.div>
      )}
    </motion.div>
  )
}

export default SettingsPanel