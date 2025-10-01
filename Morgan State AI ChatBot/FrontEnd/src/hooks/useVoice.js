// frontend/src/hooks/useVoice.js
import { useState, useCallback, useRef, useEffect } from 'react';
import { voiceService } from '../services/voiceService';

export const useVoice = () => {
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceSettings, setVoiceSettings] = useState({
    voice: 'alloy',
    autoStop: true,
    pushToTalk: false,
    sensitivity: 5
  });
  const [error, setError] = useState(null);
  
  const recognitionRef = useRef(null);
  const speechSynthesisRef = useRef(null);
  const listeningTimeoutRef = useRef(null);

  // Check if voice features are supported
  const checkVoiceSupport = useCallback(() => {
    const hasWebSpeech = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    const hasSpeechSynthesis = 'speechSynthesis' in window;
    return { hasWebSpeech, hasSpeechSynthesis };
  }, []);

  // Initialize voice recognition
  const initializeSpeechRecognition = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) return null;

    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log('Speech recognition started');
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event) => {
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

      if (finalTranscript) {
        // Dispatch event with the recognized text
        window.dispatchEvent(new CustomEvent('speechRecognized', {
          detail: { text: finalTranscript.trim() }
        }));
      }

      // Auto-stop after silence if enabled
      if (voiceSettings.autoStop && interimTranscript === '') {
        if (listeningTimeoutRef.current) {
          clearTimeout(listeningTimeoutRef.current);
        }
        
        listeningTimeoutRef.current = setTimeout(() => {
          if (recognition && isListening) {
            recognition.stop();
          }
        }, 3000);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setError(`Speech recognition error: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      console.log('Speech recognition ended');
      setIsListening(false);
      if (listeningTimeoutRef.current) {
        clearTimeout(listeningTimeoutRef.current);
      }
    };

    return recognition;
  }, [isListening, voiceSettings.autoStop]);

  // Toggle voice features on/off
  const toggleVoiceFeatures = useCallback(() => {
    const { hasWebSpeech, hasSpeechSynthesis } = checkVoiceSupport();
    
    if (!hasWebSpeech || !hasSpeechSynthesis) {
      setError('Voice features are not supported in this browser');
      return;
    }

    setIsVoiceEnabled(!isVoiceEnabled);
    
    if (!isVoiceEnabled) {
      // Initialize speech recognition when enabling
      recognitionRef.current = initializeSpeechRecognition();
    } else {
      // Clean up when disabling
      stopListening();
      stopSpeaking();
    }
  }, [isVoiceEnabled, initializeSpeechRecognition]);

  // Start listening for speech input
  const startListening = useCallback(() => {
    if (!isVoiceEnabled || !recognitionRef.current) return;

    try {
      recognitionRef.current.start();
    } catch (err) {
      console.error('Error starting speech recognition:', err);
      setError('Could not start voice input');
    }
  }, [isVoiceEnabled]);

  // Stop listening for speech input
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
    
    if (listeningTimeoutRef.current) {
      clearTimeout(listeningTimeoutRef.current);
    }
    
    setIsListening(false);
  }, [isListening]);

  // Speak text using TTS
  const speakText = useCallback(async (text, voice = null) => {
    if (!text || isSpeaking) return;

    setIsSpeaking(true);
    setError(null);

    try {
      const selectedVoice = voice || voiceSettings.voice;
      const audioBlob = await voiceService.textToSpeech(text, selectedVoice);
      
      // Create audio element and play
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };
      
      audio.onerror = () => {
        setError('Failed to play audio');
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };

      speechSynthesisRef.current = audio;
      await audio.play();

    } catch (err) {
      console.error('Text-to-speech error:', err);
      setError('Failed to generate speech');
      setIsSpeaking(false);
    }
  }, [isSpeaking, voiceSettings.voice]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (speechSynthesisRef.current) {
      speechSynthesisRef.current.pause();
      speechSynthesisRef.current = null;
    }
    setIsSpeaking(false);
  }, []);

  // Process audio file for speech-to-text
  const processAudioFile = useCallback(async (file) => {
    if (!file) return null;

    try {
      setError(null);
      const text = await voiceService.speechToText(file);
      return text;
    } catch (err) {
      console.error('Audio processing error:', err);
          setError('Failed to process audio file');
          return null;
        }
      }, []);
    
      return {
        isVoiceEnabled,
        isSpeaking,
        isListening,
        voiceSettings,
        error,
        toggleVoiceFeatures,
        startListening,
        stopListening,
        speakText,
        stopSpeaking,
        processAudioFile,
        setVoiceSettings
      };
    };