/**
 * Validation utilities for Morgan AI Chatbot
 * Provides client-side validation for forms, inputs, and data
 */

// Regular expressions for common patterns
const REGEX_PATTERNS = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^[\+]?[1-9][\d]{0,15}$/,
  username: /^[a-zA-Z0-9_]{3,20}$/,
  password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
  url: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
  threadId: /^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$/,
  morganEmail: /^[a-zA-Z0-9._%+-]+@(morgan\.edu|students?\.morgan\.edu)$/i
};

// Message validation
export const validateMessage = (message) => {
  const errors = [];
  
  if (!message || typeof message !== 'string') {
    errors.push('Message is required');
    return { isValid: false, errors };
  }

  const trimmedMessage = message.trim();
  
  if (trimmedMessage.length === 0) {
    errors.push('Message cannot be empty');
  }
  
  if (trimmedMessage.length > 2000) {
    errors.push('Message is too long (maximum 2000 characters)');
  }
  
  if (trimmedMessage.length < 1) {
    errors.push('Message is too short (minimum 1 character)');
  }

  // Check for potentially harmful content
  const suspiciousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i
  ];

  if (suspiciousPatterns.some(pattern => pattern.test(trimmedMessage))) {
    errors.push('Message contains potentially unsafe content');
  }

  return {
    isValid: errors.length === 0,
    errors,
    sanitized: trimmedMessage
  };
};

// Admin login validation
export const validateAdminLogin = (credentials) => {
  const errors = {};
  
  if (!credentials.username || credentials.username.trim().length === 0) {
    errors.username = 'Username is required';
  } else if (!REGEX_PATTERNS.username.test(credentials.username)) {
    errors.username = 'Invalid username format (3-20 characters, letters, numbers, underscore only)';
  }
  
  if (!credentials.password || credentials.password.length === 0) {
    errors.password = 'Password is required';
  } else if (credentials.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Email validation (with Morgan State specific validation)
export const validateEmail = (email, requireMorgan = false) => {
  const errors = [];
  
  if (!email || typeof email !== 'string') {
    errors.push('Email is required');
    return { isValid: false, errors };
  }

  const trimmedEmail = email.trim().toLowerCase();
  
  if (!REGEX_PATTERNS.email.test(trimmedEmail)) {
    errors.push('Invalid email format');
  }
  
  if (requireMorgan && !REGEX_PATTERNS.morganEmail.test(trimmedEmail)) {
    errors.push('Must use a Morgan State University email address (@morgan.edu)');
  }

  return {
    isValid: errors.length === 0,
    errors,
    sanitized: trimmedEmail
  };
};

// Thread ID validation
export const validateThreadId = (threadId) => {
  if (!threadId || typeof threadId !== 'string') {
    return { isValid: false, error: 'Thread ID is required' };
  }
  
  if (!REGEX_PATTERNS.threadId.test(threadId)) {
    return { isValid: false, error: 'Invalid thread ID format' };
  }
  
  return { isValid: true };
};

// Voice settings validation
export const validateVoiceSettings = (settings) => {
  const errors = {};
  const validVoices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];
  
  if (settings.voice && !validVoices.includes(settings.voice)) {
    errors.voice = `Invalid voice. Must be one of: ${validVoices.join(', ')}`;
  }
  
  if (settings.sensitivity !== undefined) {
    const sensitivity = Number(settings.sensitivity);
    if (isNaN(sensitivity) || sensitivity < 1 || sensitivity > 10) {
      errors.sensitivity = 'Sensitivity must be a number between 1 and 10';
    }
  }
  
  if (settings.autoStop !== undefined && typeof settings.autoStop !== 'boolean') {
    errors.autoStop = 'Auto-stop must be a boolean value';
  }
  
  if (settings.pushToTalk !== undefined && typeof settings.pushToTalk !== 'boolean') {
    errors.pushToTalk = 'Push-to-talk must be a boolean value';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// File upload validation
export const validateAudioFile = (file) => {
  const errors = [];
  const maxSize = 25 * 1024 * 1024; // 25MB
  const allowedTypes = [
    'audio/mp3',
    'audio/mpeg',
    'audio/wav',
    'audio/webm',
    'audio/m4a',
    'audio/mp4'
  ];
  
  if (!file) {
    errors.push('Audio file is required');
    return { isValid: false, errors };
  }
  
  if (file.size > maxSize) {
    errors.push('Audio file is too large (maximum 25MB)');
  }
  
  if (file.size === 0) {
    errors.push('Audio file is empty');
  }
  
  if (!allowedTypes.includes(file.type)) {
    errors.push(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

// URL validation
export const validateUrl = (url) => {
  if (!url || typeof url !== 'string') {
    return { isValid: false, error: 'URL is required' };
  }
  
  try {
    new URL(url);
    return { isValid: true };
  } catch {
    return { isValid: false, error: 'Invalid URL format' };
  }
};

// Search query validation
export const validateSearchQuery = (query) => {
  const errors = [];
  
  if (!query || typeof query !== 'string') {
    errors.push('Search query is required');
    return { isValid: false, errors };
  }

  const trimmedQuery = query.trim();
  
  if (trimmedQuery.length === 0) {
    errors.push('Search query cannot be empty');
  }
  
  if (trimmedQuery.length > 100) {
    errors.push('Search query is too long (maximum 100 characters)');
  }
  
  if (trimmedQuery.length < 2) {
    errors.push('Search query is too short (minimum 2 characters)');
  }

  return {
    isValid: errors.length === 0,
    errors,
    sanitized: trimmedQuery
  };
};

// Knowledge base category validation
export const validateCategory = (category) => {
  const validCategories = [
    'department_info',
    'faculty_staff',
    'academics',
    'courses',
    'programs',
    'student_resources',
    'organizations',
    'career_prep',
    'administrative',
    'registration',
    'advising',
    'general'
  ];
  
  if (!category) {
    return { isValid: true }; // Category is optional
  }
  
  if (!validCategories.includes(category)) {
    return { 
      isValid: false, 
      error: `Invalid category. Must be one of: ${validCategories.join(', ')}` 
    };
  }
  
  return { isValid: true };
};

// Rate limiting validation
export const validateRateLimit = (requests, timeWindow = 3600) => {
  const maxRequests = 100; // requests per hour
  
  if (requests >= maxRequests) {
    const resetTime = Math.ceil(timeWindow / 60); // minutes
    return {
      isValid: false,
      error: `Rate limit exceeded. Try again in ${resetTime} minutes.`,
      retryAfter: resetTime * 60 // seconds
    };
  }
  
  return {
    isValid: true,
    remaining: maxRequests - requests
  };
};

// Input sanitization
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocols
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .substring(0, 2000); // Limit length
};

// HTML sanitization for display
export const sanitizeHtml = (html) => {
  if (typeof html !== 'string') return html;
  
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
};

// Morgan State student ID validation
export const validateStudentId = (studentId) => {
  const errors = [];
  
  if (!studentId || typeof studentId !== 'string') {
    errors.push('Student ID is required');
    return { isValid: false, errors };
  }
  
  const cleanId = studentId.trim().replace(/\D/g, ''); // Remove non-digits
  
  if (cleanId.length !== 8) {
    errors.push('Student ID must be 8 digits');
  }
  
  if (!/^\d{8}$/.test(cleanId)) {
    errors.push('Student ID must contain only numbers');
  }

  return {
    isValid: errors.length === 0,
    errors,
    sanitized: cleanId
  };
};

// Date validation for academic calendar
export const validateDate = (dateString, futureOnly = false) => {
  const errors = [];
  
  if (!dateString) {
    errors.push('Date is required');
    return { isValid: false, errors };
  }
  
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) {
    errors.push('Invalid date format');
  }
  
  if (futureOnly && date < new Date()) {
    errors.push('Date must be in the future');
  }

  return {
    isValid: errors.length === 0,
    errors,
    date
  };
};

// Comprehensive form validation
export const validateForm = (formData, rules) => {
  const errors = {};
  
  Object.keys(rules).forEach(field => {
    const value = formData[field];
    const fieldRules = rules[field];
    const fieldErrors = [];
    
    // Required validation
    if (fieldRules.required && (!value || value.trim() === '')) {
      fieldErrors.push(`${field} is required`);
    }
    
    // Length validation
    if (value && fieldRules.minLength && value.length < fieldRules.minLength) {
      fieldErrors.push(`${field} must be at least ${fieldRules.minLength} characters`);
    }
    
    if (value && fieldRules.maxLength && value.length > fieldRules.maxLength) {
      fieldErrors.push(`${field} must be no more than ${fieldRules.maxLength} characters`);
    }
    
    // Pattern validation
    if (value && fieldRules.pattern && !fieldRules.pattern.test(value)) {
      fieldErrors.push(fieldRules.patternMessage || `${field} format is invalid`);
    }
    
    // Custom validation
    if (value && fieldRules.custom) {
      const customResult = fieldRules.custom(value);
      if (!customResult.isValid) {
        fieldErrors.push(...customResult.errors);
      }
    }
    
    if (fieldErrors.length > 0) {
      errors[field] = fieldErrors;
    }
  });
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Export validation utilities as default
export default {
  validateMessage,
  validateAdminLogin,
  validateEmail,
  validateThreadId,
  validateVoiceSettings,
  validateAudioFile,
  validateUrl,
  validateSearchQuery,
  validateCategory,
  validateRateLimit,
  validateStudentId,
  validateDate,
  validateForm,
  sanitizeInput,
  sanitizeHtml,
  REGEX_PATTERNS
};