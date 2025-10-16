// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

// API Endpoints
export const API_ENDPOINTS = {
  // Chat endpoints
  CHAT: {
    SEND: '/api/chat/send',
    THREADS: '/api/chat/threads',
    THREAD_MESSAGES: (threadId) => `/api/chat/threads/${threadId}`,
    DELETE_THREAD: (threadId) => `/api/chat/threads/${threadId}`,
    CLEAR_THREAD: (threadId) => `/api/chat/threads/${threadId}/clear`,
    CATEGORIES: '/api/chat/categories',
    QUICK_QUESTIONS: '/api/chat/quick-questions',
    HEALTH: '/api/chat/health',
  },
  
  // Voice endpoints
  VOICE: {
    TEXT_TO_SPEECH: '/api/voice/text-to-speech',
    SPEECH_TO_TEXT: '/api/voice/speech-to-text',
    VOICES: '/api/voice/voices',
    FORMATS: '/api/voice/supported-formats',
    HEALTH: '/api/voice/health',
  },
  
  // Admin endpoints
  ADMIN: {
    LOGIN: '/api/admin/login',
    LOGOUT: '/api/admin/logout',
    HEALTH: '/api/admin/system-health',
    REFRESH_KNOWLEDGE: '/api/admin/refresh-knowledge',
    CLEAR_DATABASE: '/api/admin/clear-database',
    BACKUP: '/api/admin/backup',
    BACKUPS: '/api/admin/backups',
    DELETE_BACKUP: (backupName) => `/api/admin/backups/${backupName}`,
    ANALYTICS: '/api/admin/analytics',
    LOGS: '/api/admin/logs',
    USERS: '/api/admin/users',
  },
  
  // System endpoints
  HEALTH: '/health',
  DETAILED_HEALTH: '/health/detailed',
  ROOT: '/',
};

// Morgan State University Branding
export const MORGAN_BRANDING = {
  UNIVERSITY_NAME: 'Morgan State University',
  DEPARTMENT_NAME: 'Computer Science Department',
  APP_NAME: 'Morgan AI',
  APP_DESCRIPTION: 'Your Computer Science Department Assistant',
  
  COLORS: {
    ORANGE: '#FF9100',
    ORANGE_LIGHT: '#FFB74D',
    ORANGE_DARK: '#E65100',
    ORANGE_HOVER: '#FFA733',
    
    BLUE: '#001B3A',
    BLUE_LIGHT: '#1E3A5F',
    BLUE_DARK: '#000D1A',
    BLUE_ACCENT: '#003366',
    
    WHITE: '#FFFFFF',
    CREAM: '#FFF8E1',
    GRAY_LIGHT: '#F5F5F5',
    GRAY: '#E0E0E0',
    GRAY_MEDIUM: '#9E9E9E',
    GRAY_DARK: '#424242',
    BLACK: '#212121',
  },
  
  GRADIENTS: {
    PRIMARY: 'linear-gradient(135deg, #FF9100 0%, #E65100 100%)',
    SECONDARY: 'linear-gradient(135deg, #001B3A 0%, #1E3A5F 100%)',
    ACCENT: 'linear-gradient(45deg, #FF9100 0%, #001B3A 100%)',
  },
};

// Application Settings
export const APP_SETTINGS = {
  NAME: import.meta.env.VITE_APP_NAME || 'Morgan AI',
  VERSION: '1.0.0',
  BUILD_TIME: '__BUILD_TIME__', // Replaced during build
  
  // Chat settings
  MAX_MESSAGE_LENGTH: 2000,
  MAX_THREAD_HISTORY: 50,
  TYPING_INDICATOR_DELAY: 1000,
  MESSAGE_RETRY_ATTEMPTS: 3,
  
  // Voice settings
  VOICE_ENABLED: import.meta.env.VITE_ENABLE_VOICE !== 'false',
  MAX_AUDIO_FILE_SIZE: 25 * 1024 * 1024, // 25MB
  DEFAULT_VOICE: 'alloy',
  AUTO_STOP_LISTENING: true,
  VOICE_TIMEOUT: 3000, // 3 seconds
  
  // UI settings
  ANIMATION_DURATION: 300,
  DEBOUNCE_DELAY: 500,
  SCROLL_THRESHOLD: 100,
  
  // Storage keys
  STORAGE_KEYS: {
    CURRENT_THREAD: 'currentThread',
    VOICE_SETTINGS: 'voiceSettings',
    USER_PREFERENCES: 'userPreferences',
    ADMIN_TOKEN: 'adminToken',
    THEME: 'theme',
  },
};

// Voice Configuration
export const VOICE_CONFIG = {
  AVAILABLE_VOICES: [
    {
      id: 'alloy',
      name: 'Alloy',
      description: 'Neutral and versatile voice',
      gender: 'neutral',
      recommended: true,
    },
    {
      id: 'echo',
      name: 'Echo',
      description: 'Male voice with warm tone',
      gender: 'male',
    },
    {
      id: 'fable',
      name: 'Fable',
      description: 'British accent, storytelling',
      gender: 'male',
    },
    {
      id: 'onyx',
      name: 'Onyx',
      description: 'Deep male, authoritative',
      gender: 'male',
    },
    {
      id: 'nova',
      name: 'Nova',
      description: 'Female, energetic',
      gender: 'female',
    },
    {
      id: 'shimmer',
      name: 'Shimmer',
      description: 'Soft female, gentle',
      gender: 'female',
    },
  ],
  
  SUPPORTED_FORMATS: [
    'audio/mp3',
    'audio/mp4',
    'audio/mpeg',
    'audio/mpga',
    'audio/m4a',
    'audio/wav',
    'audio/webm',
  ],
  
  RECOGNITION_CONFIG: {
    continuous: false,
    interimResults: true,
    lang: 'en-US',
    maxAlternatives: 1,
  },
};

// Quick Questions for Morgan State CS
export const QUICK_QUESTIONS = {
  DEPARTMENT: [
    "Where is the Computer Science department located?",
    "Who are the faculty members in Computer Science?",
    "What are the department's office hours?",
    "How do I contact the CS department?",
  ],
  
  ACADEMIC: [
    "What courses do I need for a CS degree?",
    "What are the prerequisites for advanced CS courses?",
    "How do I register for CS classes?",
    "When are the add/drop deadlines?",
  ],
  
  STUDENT_LIFE: [
    "How do I join WiCS, GDSC, or SACS?",
    "What tutoring services are available?",
    "Where can I get help with programming assignments?",
    "What study spaces are available for CS students?",
  ],
  
  CAREER: [
    "What internship programs are recommended?",
    "How do I prepare for technical interviews?",
    "How do I access NeetCode, LeetCode, and other resources?",
    "What career services are available?",
  ],
  
  ADVISING: [
    "Who is my academic advisor?",
    "How do I get an enrollment PIN?",
    "How do I submit an override request?",
    "What forms do I need for graduation?",
  ],
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK: {
    CONNECTION_FAILED: 'Unable to connect to Morgan AI. Please check your internet connection.',
    TIMEOUT: 'Request timed out. Please try again.',
    SERVER_ERROR: 'Server error occurred. Please try again later.',
    RATE_LIMITED: 'Too many requests. Please wait a moment before trying again.',
  },
  
  CHAT: {
    MESSAGE_TOO_LONG: `Message is too long. Please keep it under ${APP_SETTINGS.MAX_MESSAGE_LENGTH} characters.`,
    SEND_FAILED: 'Failed to send message. Please try again.',
    THREAD_LOAD_FAILED: 'Failed to load conversation. Please refresh the page.',
    EMPTY_MESSAGE: 'Please enter a message before sending.',
  },
  
  VOICE: {
    NOT_SUPPORTED: 'Voice features are not supported in this browser.',
    MICROPHONE_ACCESS: 'Please allow microphone access to use voice input.',
    AUDIO_PROCESSING: 'Failed to process audio. Please try again.',
    FILE_TOO_LARGE: `Audio file is too large. Maximum size is ${APP_SETTINGS.MAX_AUDIO_FILE_SIZE / (1024 * 1024)}MB.`,
    UNSUPPORTED_FORMAT: 'Unsupported audio format. Please use MP3, WAV, or other supported formats.',
  },
  
  ADMIN: {
    UNAUTHORIZED: 'You are not authorized to access this feature.',
    LOGIN_FAILED: 'Login failed. Please check your credentials.',
    SESSION_EXPIRED: 'Your session has expired. Please log in again.',
    OPERATION_FAILED: 'Operation failed. Please try again.',
  },
};

// Success Messages
export const SUCCESS_MESSAGES = {
  CHAT: {
    MESSAGE_SENT: 'Message sent successfully',
    THREAD_CREATED: 'New conversation started',
    THREAD_CLEARED: 'Conversation cleared',
    THREAD_DELETED: 'Conversation deleted',
  },
  
  VOICE: {
    RECORDING_STARTED: 'Recording started - speak now',
    RECORDING_STOPPED: 'Recording stopped',
    TRANSCRIPTION_COMPLETE: 'Voice transcription complete',
    PLAYBACK_STARTED: 'Playing response',
  },
  
  ADMIN: {
    LOGIN_SUCCESS: 'Successfully logged in',
    LOGOUT_SUCCESS: 'Successfully logged out',
    BACKUP_STARTED: 'Backup process started',
    KNOWLEDGE_REFRESH: 'Knowledge base refresh initiated',
    OPERATION_SUCCESS: 'Operation completed successfully',
  },
};

// Status Constants
export const STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  PENDING: 'pending',
};

// Message Types
export const MESSAGE_TYPES = {
  USER: 'user',
  ASSISTANT: 'assistant',
  SYSTEM: 'system',
  ERROR: 'error',
};

// Theme Constants
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto',
};

// Animation Constants
export const ANIMATIONS = {
  FADE_IN: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  
  SLIDE_UP: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  },
  
  SCALE_IN: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
  },
  
  PULSE: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Keyboard Shortcuts
export const SHORTCUTS = {
  SEND_MESSAGE: 'Enter',
  NEW_LINE: 'Shift+Enter',
  NEW_THREAD: 'Ctrl+N',
  FOCUS_INPUT: 'Ctrl+K',
  TOGGLE_VOICE: 'Ctrl+M',
  ESCAPE: 'Escape',
};

// Development Constants
export const DEV_CONFIG = {
  ENABLE_DEBUG: import.meta.env.DEV,
  LOG_LEVEL: import.meta.env.DEV ? 'debug' : 'error',
  MOCK_DELAYS: import.meta.env.DEV ? 1000 : 0,
  SHOW_DEV_TOOLS: import.meta.env.DEV,
};

// Regular Expressions
export const REGEX = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  URL: /^https?:\/\/[^\s/$.?#].[^\s]*$/i,
  WHITESPACE_ONLY: /^\s*$/,
  SPECIAL_CHARACTERS: /[!@#$%^&*(),.?":{}|<>]/g,
};

// Feature Flags
export const FEATURES = {
  VOICE_ENABLED: import.meta.env.VITE_ENABLE_VOICE !== 'false',
  ADMIN_PANEL: true,
  DARK_MODE: true,
  ANALYTICS: false,
  EXPORT_CONVERSATIONS: false,
  CONVERSATION_SHARING: false,
};

// Export all constants as default
export default {
  API_CONFIG,
  API_ENDPOINTS,
  MORGAN_BRANDING,
  APP_SETTINGS,
  VOICE_CONFIG,
  QUICK_QUESTIONS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  STATUS,
  MESSAGE_TYPES,
  THEMES,
  ANIMATIONS,
  SHORTCUTS,
  DEV_CONFIG,
  REGEX,
  FEATURES,
};