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
  const currentTextRef = useRef(null);

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

      utter.onstart = () => {
        console.log('Speech started');
        setIsSpeaking(true);
      };
      utter.onend = () => { 
        console.log('Speech ended');
        setIsSpeaking(false); 
        setIsPaused(false); 
        currentUtterRef.current = null;
        currentTextRef.current = null;
      };
      utter.onerror = (e) => { 
        console.error('Speech error:', e);
        setIsSpeaking(false); 
        setIsPaused(false); 
        currentUtterRef.current = null;
        currentTextRef.current = null;
      };
      utter.onpause = () => {
        console.log('Speech paused event');
        setIsPaused(true);
      };
      utter.onresume = () => {
        console.log('Speech resume event');
        setIsPaused(false);
      };

      // Stop any current speech and speak new
      synthRef.current.cancel();
      setIsPaused(false);
      currentUtterRef.current = utter;
      currentTextRef.current = text;
      synthRef.current.speak(utter);
      console.log('Speak called for new text');
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
      currentTextRef.current = null;
    }
  };

  const pause = () => {
    console.log('PAUSE called', {
      speaking: synthRef.current?.speaking,
      paused: synthRef.current?.paused
    });
    
    try {
      if (synthRef.current && synthRef.current.speaking && !synthRef.current.paused) {
        synthRef.current.pause();
        setIsPaused(true);
        localStorage.setItem('tts_is_paused', 'true');
        console.log('Pause command executed');
        
        // Verify pause worked after a delay
        setTimeout(() => {
          console.log('After pause - speaking:', synthRef.current?.speaking, 'paused:', synthRef.current?.paused);
        }, 100);
      }
    } catch (e) {
      console.error('Pause error:', e);
    }
  };

  const resume = () => {
    console.log('RESUME called', { 
      hasSynth: !!synthRef.current, 
      isPaused, 
      speaking: synthRef.current?.speaking,
      paused: synthRef.current?.paused
    });
    
    try {
      if (!synthRef.current) {
        console.log('No synthRef');
        return;
      }

      // Try native resume first - it works in most modern browsers when done correctly
      if (synthRef.current.paused || isPaused) {
        console.log('Calling native resume()');
        synthRef.current.resume();
        setIsPaused(false);
        localStorage.setItem('tts_is_paused', 'false');
        
        // Verify resume worked
        setTimeout(() => {
          console.log('After resume - speaking:', synthRef.current?.speaking, 'paused:', synthRef.current?.paused);
          
          // If still paused after resume attempt, force restart
          if (synthRef.current && synthRef.current.paused && currentTextRef.current) {
            console.log('Native resume failed, forcing restart');
            const textToRestart = currentTextRef.current;
            const voiceToUse = selectedVoice;
            
            synthRef.current.cancel();
            
            setTimeout(() => {
              if (!synthRef.current) return;
              
              const utter = new window.SpeechSynthesisUtterance(textToRestart);
              if (voiceToUse) utter.voice = voiceToUse;
              utter.rate = rate;
              utter.pitch = pitch;
              utter.volume = volume;

              utter.onstart = () => {
                console.log('Forced restart - speech playing');
                setIsSpeaking(true);
              };
              utter.onend = () => {
                setIsSpeaking(false);
                setIsPaused(false);
                currentUtterRef.current = null;
                currentTextRef.current = null;
              };
              utter.onerror = () => {
                setIsSpeaking(false);
                setIsPaused(false);
                currentUtterRef.current = null;
                currentTextRef.current = null;
              };
              utter.onpause = () => setIsPaused(true);
              utter.onresume = () => setIsPaused(false);

              currentUtterRef.current = utter;
              synthRef.current.speak(utter);
              console.log('Restart speak() called');
            }, 50);
          }
        }, 100);
      } else {
        console.log('Not in paused state - cannot resume');
      }
    } catch (e) {
      console.error('TTS resume error:', e);
      setIsPaused(false);
      localStorage.setItem('tts_is_paused', 'false');
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
