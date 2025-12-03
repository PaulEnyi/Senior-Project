/**
 * Check if a string is a valid email address.
 * @param {string} email
 * @returns {boolean}
 */
export const isValidEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(String(email).toLowerCase());
};

/**
 * Check if a string is a valid phone number (basic pattern).
 * @param {string} phone
 * @returns {boolean}
 */
export const isValidPhone = (phone) => {
  const regex = /^\+?[\d\s\-()]{7,}$/;
  return regex.test(String(phone));
};

/**
 * Check if a value is non-empty (for text inputs).
 * @param {string|number} value
 * @returns {boolean}
 */
export const isRequired = (value) => {
  return value !== null && value !== undefined && String(value).trim() !== '';
};

/**
 * Check if a string meets a minimum and/or maximum length requirement.
 * @param {string} str
 * @param {number} [min=0]
 * @param {number} [max=Infinity]
 * @returns {boolean}
 */
export const isLengthValid = (str, min = 0, max = Infinity) => {
  if (typeof str !== 'string') return false;
  return str.length >= min && str.length <= max;
};

/**
 * Check if a password meets strength requirements.
 * - Minimum 8 characters
 * - Includes uppercase, lowercase, number, and special character
 * @param {string} password
 * @returns {boolean}
 */
export const isStrongPassword = (password) => {
  const regex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?#&])[A-Za-z\d@$!%*?#&]{8,}$/;
  return regex.test(password);
};
