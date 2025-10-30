import React, { createContext, useEffect, useMemo, useRef, useState } from 'react';

export const VoiceContext = createContext();

export const VoiceProvider = ({ children }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoiceURI, setSelectedVoiceURI] = useState(() => localStorage.getItem('tts_selected_voice_uri') || '');
  const [rate, setRate] = useState(() => parseFloat(localStorage.getItem('tts_rate') || '1.0'));
  const [pitch, setPitch] = useState(() => parseFloat(localStorage.getItem('tts_pitch') || '1.0'));
  const [volume, setVolume] = useState(() => parseFloat(localStorage.getItem('tts_volume') || '1.0'));
  const [isPaused, setIsPaused] = useState(() => {
    const stored = localStorage.getItem('tts_is_paused');
    return stored === 'true';
  });

  const synthRef = useRef(null);
  const currentUtterRef = useRef(null);

  // Initialize speechSynthesis reference
  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }
  }, []);

  // Load available voices (browsers may load them asynchronously)
  const loadVoices = () => {
    if (!synthRef.current) return;
    const list = synthRef.current.getVoices();
    if (list && list.length) {
      setVoices(list);
      // If no selected voice, try to choose a sensible default (prefer en-US female if available)
      if (!selectedVoiceURI) {
        const preferred =
          list.find(v => /female/i.test(v.name) && /en[-_]US/i.test(v.lang)) ||
          list.find(v => /en[-_]US/i.test(v.lang)) ||
          list[0];
        if (preferred) {
          setSelectedVoiceURI(preferred.voiceURI || preferred.name);
        }
      }
    }
  };

  useEffect(() => {
    if (!synthRef.current) return;
    loadVoices();
    // Some browsers fire voiceschanged when voices become available
    const handler = () => loadVoices();
    window.speechSynthesis.addEventListener('voiceschanged', handler);
    return () => window.speechSynthesis.removeEventListener('voiceschanged', handler);
  }, [synthRef.current]);

  // Optional server-side save
  const savePreferences = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      await fetch('/api/user/preferences/voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ voice: selectedVoiceURI, rate, pitch, volume })
      });
    } catch (e) {
      // Endpoint may not exist; ignore silently to avoid UX noise
      // console.warn('Voice preferences save skipped:', e?.message || e);
    }
  };

  // Persist settings
  useEffect(() => {
    localStorage.setItem('tts_selected_voice_uri', selectedVoiceURI || '');
    savePreferences();
  }, [selectedVoiceURI]);
  useEffect(() => {
    localStorage.setItem('tts_rate', String(rate));
    savePreferences();
  }, [rate]);
  useEffect(() => {
    localStorage.setItem('tts_pitch', String(pitch));
    savePreferences();
  }, [pitch]);
  useEffect(() => {
    localStorage.setItem('tts_volume', String(volume));
    savePreferences();
  }, [volume]);

  const selectedVoice = useMemo(() => {
    if (!voices || voices.length === 0) return null;
    return (
      voices.find(v => v.voiceURI === selectedVoiceURI) ||
      voices.find(v => v.name === selectedVoiceURI) ||
      null
    );
  }, [voices, selectedVoiceURI]);

  const speak = (text) => {
    if (!text || !synthRef.current) return;
    try {
      const utter = new window.SpeechSynthesisUtterance(text);
      if (selectedVoice) utter.voice = selectedVoice;
      utter.rate = rate;
      utter.pitch = pitch;
      utter.volume = volume;

      utter.onstart = () => setIsSpeaking(true);
      utter.onend = () => { setIsSpeaking(false); setIsPaused(false); currentUtterRef.current = null; };
      utter.onerror = () => { setIsSpeaking(false); setIsPaused(false); currentUtterRef.current = null; };
      utter.onpause = () => setIsPaused(true);
      utter.onresume = () => setIsPaused(false);

      // Stop any current speech and speak new
      synthRef.current.cancel();
      setIsPaused(false);
      currentUtterRef.current = utter;
      synthRef.current.speak(utter);
    } catch (e) {
      console.error('TTS speak error:', e);
      setIsSpeaking(false);
    }
  };

  const stop = () => {
    try {
      if (synthRef.current && synthRef.current.speaking) {
        synthRef.current.cancel();
      }
    } catch (e) {
      // ignore
    } finally {
      setIsSpeaking(false);
      setIsPaused(false);
      localStorage.setItem('tts_is_paused', 'false');
      currentUtterRef.current = null;
    }
  };

  const pause = () => {
    try {
      if (synthRef.current && synthRef.current.speaking && !synthRef.current.paused) {
        synthRef.current.pause();
        setIsPaused(true);
        localStorage.setItem('tts_is_paused', 'true');
      }
    } catch (e) {
      // ignore
    }
  };

  const resume = () => {
    try {
      if (synthRef.current && synthRef.current.paused) {
        synthRef.current.resume();
        setIsPaused(false);
        localStorage.setItem('tts_is_paused', 'false');
      }
    } catch (e) {
      // ignore
    }
  };

  const togglePause = () => {
    if (isPaused) {
      resume();
    } else {
      pause();
    }
  };

  const value = {
    // STT state
    isListening,
    setIsListening,

    // TTS state
    isSpeaking,
    setIsSpeaking,
    isPaused,
    voices,
    selectedVoiceURI,
    setSelectedVoiceURI,
    rate,
    setRate,
    pitch,
    setPitch,
    volume,
    setVolume,

    // actions
    speak,
    stop,
    pause,
    resume,
    togglePause,
  };

  return (
    <VoiceContext.Provider value={value}>
      {children}
    </VoiceContext.Provider>
  );
};
