/**
 * Utility functions for formatting text, dates, numbers, and other data
 * for the Morgan AI Chatbot frontend
 */

// Date and Time Formatters
export const formatters = {
  
  // Date formatting
  date: {
    /**
     * Format date for chat messages (e.g., "2 minutes ago", "Yesterday", "Jan 15")
     */
    chatMessage: (date) => {
      if (!date) return '';
      
      const now = new Date();
      const messageDate = new Date(date);
      const diffInMinutes = Math.floor((now - messageDate) / (1000 * 60));
      const diffInHours = Math.floor(diffInMinutes / 60);
      const diffInDays = Math.floor(diffInHours / 24);
      
      if (diffInMinutes < 1) return 'Just now';
      if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes === 1 ? '' : 's'} ago`;
      if (diffInHours < 24) return `${diffInHours} hour${diffInHours === 1 ? '' : 's'} ago`;
      if (diffInDays === 1) return 'Yesterday';
      if (diffInDays < 7) return `${diffInDays} days ago`;
      
      // For older dates, show formatted date
      return messageDate.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: messageDate.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    },

    /**
     * Format time for message timestamps (e.g., "2:30 PM")
     */
    timeOnly: (date) => {
      if (!date) return '';
      return new Date(date).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    },

    /**
     * Format full date and time for admin panels
     */
    fullDateTime: (date) => {
      if (!date) return '';
      return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    },

    /**
     * Format date for Morgan State academic calendar (e.g., "Fall 2024")
     */
    academicSemester: (date) => {
      if (!date) return '';
      const d = new Date(date);
      const month = d.getMonth();
      const year = d.getFullYear();
      
      if (month >= 7 && month <= 11) return `Fall ${year}`;
      if (month >= 0 && month <= 4) return `Spring ${year}`;
      return `Summer ${year}`;
    }
  },

  // Text formatting
  text: {
    /**
     * Truncate text with ellipsis
     */
    truncate: (text, maxLength = 100) => {
      if (!text || text.length <= maxLength) return text;
      return text.substring(0, maxLength).trim() + '...';
    },

    /**
     * Capitalize first letter of each word
     */
    titleCase: (text) => {
      if (!text) return '';
      return text.replace(/\w\S*/g, (txt) => 
        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
      );
    },

    /**
     * Format text for display in chat (preserve line breaks, etc.)
     */
    chatText: (text) => {
      if (!text) return '';
      return text
        .replace(/\n\n/g, '\n') // Remove excessive line breaks
        .trim();
    },

    /**
     * Extract and format course codes (e.g., "COSC 111" -> "COSC 111")
     */
    courseCode: (text) => {
      if (!text) return text;
      return text.replace(/([A-Z]{3,4})\s*(\d{3})/g, '$1 $2');
    },

    /**
     * Format faculty names consistently
     */
    facultyName: (name) => {
      if (!name) return '';
      // Handle "Dr. LastName" or "FirstName LastName" formats
      if (name.startsWith('Dr. ')) return name;
      if (name.includes(',')) {
        // Handle "LastName, FirstName" format
        const [last, first] = name.split(',').map(s => s.trim());
        return `${first} ${last}`;
      }
      return name;
    }
  },

  // Number formatting
  number: {
    /**
     * Format file sizes (bytes to human readable)
     */
    fileSize: (bytes) => {
      if (!bytes || bytes === 0) return '0 B';
      
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(1024));
      
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    },

    /**
     * Format percentages
     */
    percentage: (value, decimals = 1) => {
      if (value === null || value === undefined) return '0%';
      return `${(value * 100).toFixed(decimals)}%`;
    },

    /**
     * Format large numbers with commas
     */
    withCommas: (number) => {
      if (!number && number !== 0) return '';
      return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
  },

  // Status and state formatting
  status: {
    /**
     * Format connection status
     */
    connection: (status) => {
      const statusMap = {
        'connected': 'Connected',
        'connecting': 'Connecting...',
        'disconnected': 'Disconnected',
        'error': 'Connection Error'
      };
      return statusMap[status] || status;
    },

    /**
     * Format backup status
     */
    backup: (status) => {
      const statusMap = {
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'failed': 'Failed',
        'pending': 'Pending'
      };
      return statusMap[status] || status;
    },

    /**
     * Format system health status
     */
    health: (status) => {
      const statusMap = {
        'healthy': 'Healthy',
        'degraded': 'Degraded',
        'unhealthy': 'Unhealthy',
        'unknown': 'Unknown'
      };
      return statusMap[status] || status;
    }
  },

  // Morgan State specific formatters
  morgan: {
    /**
     * Format student organizations consistently
     */
    organization: (orgName) => {
      const orgMap = {
        'wics': 'WiCS (Women in Computer Science)',
        'gdsc': 'GDSC (Google Developer Student Club)',
        'sacs': 'SACS (Student Association for Computing Systems)',
        'acm': 'ACM Student Chapter'
      };
      
      const lowerName = orgName?.toLowerCase();
      return orgMap[lowerName] || orgName;
    },

    /**
     * Format GPA consistently
     */
    gpa: (gpa) => {
      if (!gpa && gpa !== 0) return 'N/A';
      return parseFloat(gpa).toFixed(2);
    },

    /**
     * Format semester and year
     */
    semester: (semesterCode) => {
      if (!semesterCode) return '';
      
      const year = semesterCode.slice(-4);
      const season = semesterCode.slice(0, -4).toLowerCase();
      
      const seasonMap = {
        'fall': 'Fall',
        'spring': 'Spring', 
        'summer': 'Summer'
      };
      
      return `${seasonMap[season] || season} ${year}`;
    }
  }
};

// URL and link formatters
export const linkFormatters = {
  /**
   * Format Morgan State URLs consistently
   */
  morganUrl: (path) => {
    const baseUrl = 'https://www.morgan.edu';
    return path.startsWith('http') ? path : `${baseUrl}${path.startsWith('/') ? '' : '/'}${path}`;
  },

  /**
   * Extract domain from URL for display
   */
  domain: (url) => {
    if (!url) return '';
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  },

  /**
   * Format email addresses consistently
   */
  email: (email) => {
    if (!email) return '';
    return email.toLowerCase().trim();
  }
};

// Validation helpers that also format
export const validators = {
  /**
   * Format and validate phone numbers
   */
  phone: (phone) => {
    if (!phone) return '';
    
    // Remove all non-digits
    const digits = phone.replace(/\D/g, '');
    
    // Format as (XXX) XXX-XXXX if 10 digits
    if (digits.length === 10) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    }
    
    return phone; // Return original if can't format
  },

  /**
   * Format course codes consistently
   */
  courseCode: (code) => {
    if (!code) return '';
    
    // Match patterns like "COSC111", "cosc 111", etc.
    const match = code.match(/([A-Za-z]{3,4})\s*(\d{3})/);
    if (match) {
      return `${match[1].toUpperCase()} ${match[2]}`;
    }
    
    return code.toUpperCase();
  }
};

// Array and list formatters
export const listFormatters = {
  /**
   * Join array with proper grammar (Oxford comma)
   */
  oxfordComma: (items) => {
    if (!items || !Array.isArray(items)) return '';
    
    if (items.length === 0) return '';
    if (items.length === 1) return items[0];
    if (items.length === 2) return `${items[0]} and ${items[1]}`;
    
    return `${items.slice(0, -1).join(', ')}, and ${items[items.length - 1]}`;
  },

  /**
   * Format prerequisites list
   */
  prerequisites: (prereqs) => {
    if (!prereqs || !Array.isArray(prereqs)) return 'None';
    
    const formatted = prereqs.map(prereq => 
      validators.courseCode(prereq)
    );
    
    return listFormatters.oxfordComma(formatted);
  }
};

// Theme and color formatters
export const themeFormatters = {
  /**
   * Get CSS class for status colors
   */
  statusClass: (status) => {
    const classMap = {
      'success': 'text-success bg-success-light',
      'warning': 'text-warning bg-warning-light',
      'error': 'text-error bg-error-light',
      'info': 'text-info bg-info-light',
      'healthy': 'text-success',
      'unhealthy': 'text-error',
      'degraded': 'text-warning'
    };
    
    return classMap[status] || 'text-gray-medium';
  },

  /**
   * Get Morgan State themed class names
   */
  morganClass: (element) => {
    const classMap = {
      'primary': 'text-morgan-orange bg-morgan-orange',
      'secondary': 'text-morgan-blue bg-morgan-blue', 
      'accent': 'text-morgan-white bg-gradient-primary',
      'card': 'bg-morgan-white shadow-md rounded-lg border-morgan-gray'
    };
    
    return classMap[element] || '';
  }
};

// Export everything as default for easy importing
export default {
  ...formatters,
  link: linkFormatters,
  validate: validators,
  list: listFormatters,
  theme: themeFormatters
};