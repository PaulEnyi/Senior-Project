import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import openaiService from '../services/openaiService';

const useVoiceStore = create(
  persist(
    (set, get) => ({
      isVoiceEnabled: true,
      isListening: false,
      isSpeaking: false,
      selectedVoice: 'alloy',
      speechRate: 1.0,
      volume: 1.0,
      recognition: null,
      synthesis: null,

      // Initialize voice services
      initVoice: () => {
        // Check if browser supports speech synthesis
        if ('speechSynthesis' in window) {
          set({ synthesis: window.speechSynthesis });
        }

        // Check if browser supports speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
          const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
          const recognition = new SpeechRecognition();
          
          recognition.continuous = false;
          recognition.interimResults = true;
          recognition.lang = 'en-US';
          
          set({ recognition });
        }
      },

      // Toggle voice on/off
      toggleVoice: () => {
        const { isVoiceEnabled, stopSpeaking, stopListening } = get();
        
        if (isVoiceEnabled) {
          stopSpeaking();
          stopListening();
        }
        
        set({ isVoiceEnabled: !isVoiceEnabled });
      },

      // Start listening
      startListening: () => {
        const { recognition, isVoiceEnabled } = get();
        
        if (!isVoiceEnabled || !recognition) return;
        
        set({ isListening: true });
        
        return new Promise((resolve, reject) => {
          let finalTranscript = '';
          
          recognition.onresult = (event) => {
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
              const transcript = event.results[i][0].transcript;
              if (event.results[i].isFinal) {
                finalTranscript += transcript;
              } else {
                interimTranscript += transcript;
              }
            }
          };
          
          recognition.onend = () => {
            set({ isListening: false });
            resolve(finalTranscript);
          };
          
          recognition.onerror = (event) => {
            set({ isListening: false });
            reject(event.error);
          };
          
          try {
            recognition.start();
          } catch (error) {
            set({ isListening: false });
            reject(error);
          }
        });
      },

      // Stop listening
      stopListening: () => {
        const { recognition } = get();
        
        if (recognition) {
          recognition.stop();
          set({ isListening: false });
        }
      },

      // Speak text using TTS
      speak: async (text, voice = null) => {
        const { isVoiceEnabled, selectedVoice, speechRate, volume, synthesis } = get();
        
        if (!isVoiceEnabled) return;
        
        set({ isSpeaking: true });
        
        try {
          // Use OpenAI TTS if available
          const audioUrl = await openaiService.textToSpeech(text, voice || selectedVoice);
          
          if (audioUrl) {
            const audio = new Audio(audioUrl);
            audio.playbackRate = speechRate;
            audio.volume = volume;
            
            audio.onended = () => {
              set({ isSpeaking: false });
            };
            
            await audio.play();
          } else if (synthesis) {
            // Fallback to browser TTS
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = speechRate;
            utterance.volume = volume;
            
            // Try to find a good voice
            const voices = synthesis.getVoices();
            const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft'));
            if (preferredVoice) {
              utterance.voice = preferredVoice;
            }
            
            utterance.onend = () => {
              set({ isSpeaking: false });
            };
            
            synthesis.speak(utterance);
          }
        } catch (error) {
          console.error('Speech failed:', error);
          set({ isSpeaking: false });
        }
      },

      // Stop speaking
      stopSpeaking: () => {
        const { synthesis } = get();
        
        if (synthesis && synthesis.speaking) {
          synthesis.cancel();
        }
        
        set({ isSpeaking: false });
      },

      // Set voice settings
      setVoiceSettings: (settings) => {
        set({
          selectedVoice: settings.voice || get().selectedVoice,
          speechRate: settings.rate || get().speechRate,
          volume: settings.volume || get().volume
        });
      },

      // Speech to text
      speechToText: async (audioBlob) => {
        try {
          const result = await openaiService.speechToText(audioBlob);
          return result.text;
        } catch (error) {
          console.error('Speech to text failed:', error);
          return null;
        }
      },

      // Toggle listening
      toggleListening: async () => {
        const { isListening, startListening, stopListening } = get();
        
        if (isListening) {
          stopListening();
        } else {
          return await startListening();
        }
      }
    }),
    {
      name: 'voice-settings',
      partialize: (state) => ({
        isVoiceEnabled: state.isVoiceEnabled,
        selectedVoice: state.selectedVoice,
        speechRate: state.speechRate,
        volume: state.volume
      })
    }
  )
);

export const useVoice = () => {
  const store = useVoiceStore();
  
  // Initialize on first use
  if (!store.recognition && !store.synthesis) {
    store.initVoice();
  }
  
  return store;
};