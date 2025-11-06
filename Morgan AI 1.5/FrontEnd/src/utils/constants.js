// Constants for Morgan AI Chatbot

export const APP_NAME = 'Morgan AI Assistant'
export const APP_VERSION = '1.0.0'

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || ''
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || '/ws'

// Morgan State Colors
export const COLORS = {
  morganBlue: '#003DA5',
  morganOrange: '#F47B20',
  morganGold: '#FFB81C',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6'
}

// Voice Settings
export const VOICE_SETTINGS = {
  voices: [
    { value: 'alloy', label: 'Alloy' },
    { value: 'echo', label: 'Echo' },
    { value: 'fable', label: 'Fable' },
    { value: 'onyx', label: 'Onyx' },
    { value: 'nova', label: 'Nova' },
    { value: 'shimmer', label: 'Shimmer' }
  ],
  defaultVoice: 'alloy',
  defaultSpeed: 1.0,
  minSpeed: 0.25,
  maxSpeed: 4.0
}

// Chat Settings
export const CHAT_SETTINGS = {
  maxMessageLength: 4000,
  maxTokens: 2000,
  defaultTemperature: 0.7,
  maxHistoryItems: 50,
  typingIndicatorDelay: 300
}

// Admin Settings
export const ADMIN_SETTINGS = {
  sessionTimeout: 60 * 60 * 1000, // 1 hour
  maxLoginAttempts: 5,
  lockoutDuration: 15 * 60 * 1000 // 15 minutes
}

// Morgan State Resources
export const MORGAN_RESOURCES = [
  {
    title: 'WebSIS',
    url: 'https://websis.morgan.edu',
    description: 'Student Information System'
  },
  {
    title: 'Canvas',
    url: 'https://morgan.instructure.com',
    description: 'Course Management'
  },
  {
    title: 'Department Website',
    url: 'https://www.morgan.edu/scmns/computerscience',
    description: 'CS Department Info'
  },
  {
    title: 'Library',
    url: 'https://www.morgan.edu/library',
    description: 'Research Resources'
  }
]

// Quick Questions
export const QUICK_QUESTIONS = [
  {
    id: 1,
    text: "What are the prerequisites for COSC 211 Data Structures?",
    category: "courses"
  },
  {
    id: 2,
    text: "When is the registration deadline for Spring 2025?",
    category: "registration"
  },
  {
    id: 3,
    text: "Who is my academic advisor?",
    category: "advising"
  },
  {
    id: 4,
    text: "How do I apply for internships?",
    category: "career"
  },
  {
    id: 5,
    text: "Where is the CS tutoring center located?",
    category: "resources"
  },
  {
    id: 6,
    text: "What are the department office hours?",
    category: "contact"
  },
  {
    id: 7,
    text: "What scholarships are available for CS students?",
    category: "financial"
  },
  {
    id: 8,
    text: "How do I join student organizations like WiCS or GDSC?",
    category: "organizations"
  }
]

// Error Messages
export const ERROR_MESSAGES = {
  networkError: 'Network error. Please check your connection.',
  authError: 'Authentication failed. Please log in again.',
  serverError: 'Server error. Please try again later.',
  validationError: 'Please check your input and try again.',
  notFoundError: 'The requested resource was not found.',
  permissionError: 'You do not have permission to perform this action.'
}

// Success Messages
export const SUCCESS_MESSAGES = {
  loginSuccess: 'Welcome back!',
  logoutSuccess: 'You have been logged out successfully.',
  settingsSaved: 'Settings have been saved successfully.',
  knowledgeBaseUpdated: 'Knowledge base has been updated successfully.',
  messageSent: 'Message sent successfully.',
  threadCreated: 'New conversation created.'
}

// Local Storage Keys
export const STORAGE_KEYS = {
  authToken: 'auth_token',
  theme: 'theme',
  voiceEnabled: 'voiceEnabled',
  chatThreads: 'chatThreads',
  currentThread: 'currentThread',
  chatMessages: 'chatMessages',
  userPreferences: 'userPreferences'
}

// Routes
export const ROUTES = {
  home: '/',
  admin: '/admin',
  adminLogin: '/admin/login',
  courses: '/courses',
  calendar: '/calendar',
  organizations: '/organizations',
  career: '/career',
  help: '/help'
}

// Regular Expressions
export const REGEX = {
  email: /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$/,
  phone: /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/,
  courseCode: /^[A-Z]{2,4}\s*\d{3}[A-Z]?$/,
  gpa: /^\d\.\d{1,2}$/
}

// Date Formats
export const DATE_FORMATS = {
  display: 'MMM dd, yyyy',
  displayWithTime: 'MMM dd, yyyy h:mm a',
  input: 'yyyy-MM-dd',
  api: 'yyyy-MM-dd\'T\'HH:mm:ss\'Z\''
}

export default {
  APP_NAME,
  APP_VERSION,
  API_BASE_URL,
  WS_BASE_URL,
  COLORS,
  VOICE_SETTINGS,
  CHAT_SETTINGS,
  ADMIN_SETTINGS,
  MORGAN_RESOURCES,
  QUICK_QUESTIONS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  STORAGE_KEYS,
  ROUTES,
  REGEX,
  DATE_FORMATS
}