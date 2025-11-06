/**
 * Format a date into a human-readable string.
 * @param {string|Date} date - The date to format.
 * @param {Object} [options] - Intl.DateTimeFormat options.
 * @returns {string}
 */
export const formatDate = (date, options = {}) => {
  if (!date) return '';
  try {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      ...options,
    }).format(new Date(date));
  } catch (error) {
    console.error('Date formatting error:', error);
    return '';
  }
};

/**
 * Format a number with commas or locale-specific separators.
 * @param {number|string} value
 * @param {Object} [options] - Intl.NumberFormat options.
 * @returns {string}
 */
export const formatNumber = (value, options = {}) => {
  if (value === undefined || value === null || isNaN(value)) return '';
  try {
    return new Intl.NumberFormat('en-US', options).format(value);
  } catch (error) {
    console.error('Number formatting error:', error);
    return String(value);
  }
};

/**
 * Format a currency value (default: USD).
 * @param {number} value
 * @param {string} [currency='USD']
 * @returns {string}
 */
export const formatCurrency = (value, currency = 'USD') => {
  return formatNumber(value, { style: 'currency', currency });
};
