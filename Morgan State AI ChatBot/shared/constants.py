"""
Shared constants for the Morgan AI Chatbot project.
Contains application-wide constants, Morgan State specific data,
and configuration values used across frontend and backend.
"""

# Application Constants
APP_NAME = "Morgan AI Chatbot"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI Chatbot for Morgan State University Computer Science Department"

# Morgan State University Information
UNIVERSITY_NAME = "Morgan State University"
UNIVERSITY_LOCATION = "Baltimore, Maryland"
UNIVERSITY_WEBSITE = "https://www.morgan.edu"

DEPARTMENT_NAME = "Computer Science"
DEPARTMENT_FULL_NAME = "Department of Computer Science"
DEPARTMENT_WEBSITE = "https://www.morgan.edu/scmns/computerscience"
DEPARTMENT_EMAIL = "computer.science@morgan.edu"
DEPARTMENT_PHONE = "(443) 885-3130"

# Department Location
DEPARTMENT_BUILDING = "Science Complex"
DEPARTMENT_ROOM = "325"
DEPARTMENT_ADDRESS = "1700 E Cold Spring Ln, Baltimore, MD 21251"

# Morgan State Colors (Official Branding)
MORGAN_ORANGE = "#FF9100"
MORGAN_ORANGE_LIGHT = "#FFB74D"
MORGAN_ORANGE_DARK = "#E65100"
MORGAN_ORANGE_HOVER = "#FFA733"

MORGAN_BLUE = "#001B3A"
MORGAN_BLUE_LIGHT = "#1E3A5F"
MORGAN_BLUE_DARK = "#000D1A"
MORGAN_BLUE_ACCENT = "#003366"

# API Configuration
DEFAULT_API_TIMEOUT = 30  # seconds
DEFAULT_REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Rate Limiting
DEFAULT_RATE_LIMIT = 100  # requests per hour
BURST_RATE_LIMIT = 10  # requests per minute
ADMIN_RATE_LIMIT = 1000  # requests per hour for admin users

# OpenAI Configuration
OPENAI_MODEL_DEFAULT = "gpt-3.5-turbo"
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.7
OPENAI_EMBEDDING_DIMENSION = 1536

# Voice Configuration
TTS_VOICES = [
    "alloy", "echo", "fable", "onyx", "nova", "shimmer"
]
DEFAULT_TTS_VOICE = "alloy"
TTS_MAX_CHARACTERS = 4000
STT_MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

SUPPORTED_AUDIO_FORMATS = [
    ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"
]

# Chat Configuration
MAX_MESSAGE_LENGTH = 2000
MAX_THREAD_HISTORY = 50
DEFAULT_RESPONSE_TOKENS = 500
MIN_RESPONSE_TOKENS = 50
MAX_RESPONSE_TOKENS = 4000

# Knowledge Base Categories
KNOWLEDGE_CATEGORIES = [
    "department_info",
    "faculty_staff", 
    "academics",
    "courses",
    "programs",
    "student_resources",
    "organizations",
    "career_prep",
    "administrative",
    "registration",
    "advising",
    "general"
]

# Morgan State Faculty Information
FACULTY_CHAIR = {
    "name": "Dr. Debra Pettit",
    "title": "Department Chair",
    "office": "Science Complex 325",
    "email": "debra.pettit@morgan.edu",
    "phone": "(443) 885-3130"
}

CORE_FACULTY = [
    {
        "name": "Dr. Mohinder Grewal",
        "title": "Professor",
        "office": "Science Complex 327",
        "email": "mohinder.grewal@morgan.edu",
        "research_areas": ["Artificial Intelligence", "Machine Learning"],
        "office_hours": "MW 2:00-4:00 PM"
    },
    {
        "name": "Dr. Enyue Lu",
        "title": "Associate Professor", 
        "office": "Science Complex 329",
        "email": "enyue.lu@morgan.edu",
        "research_areas": ["Computer Graphics", "Virtual Reality"],
        "office_hours": "TTh 1:00-3:00 PM"
    },
    {
        "name": "Dr. Shaojie Zhang",
        "title": "Associate Professor",
        "office": "Science Complex 331", 
        "email": "shaojie.zhang@morgan.edu",
        "research_areas": ["Bioinformatics", "Data Mining"],
        "office_hours": "MWF 10:00-11:00 AM"
    },
    {
        "name": "Dr. Craig Scott",
        "title": "Assistant Professor",
        "office": "Science Complex 333",
        "email": "craig.scott@morgan.edu", 
        "research_areas": ["Cybersecurity", "Network Security"],
        "office_hours": "TTh 2:00-4:00 PM"
    },
    {
        "name": "Prof. Angela Johnson",
        "title": "Lecturer",
        "office": "Science Complex 335",
        "email": "angela.johnson@morgan.edu",
        "specialization": ["Programming Languages", "Software Development"],
        "office_hours": "MW 3:00-5:00 PM"
    }
]

# Student Organizations
STUDENT_ORGANIZATIONS = [
    {
        "name": "Women in Computer Science (WiCS)",
        "purpose": "Support and empower women in computing",
        "meeting_time": "Every other Wednesday at 6:00 PM",
        "location": "Science Complex 340",
        "contact": "wics@morgan.edu",
        "advisor": "Dr. Angela Johnson"
    },
    {
        "name": "Google Developer Student Club (GDSC)",
        "purpose": "Learn Google technologies and build solutions",
        "meeting_time": "Fridays at 5:00 PM", 
        "location": "Science Complex 342",
        "contact": "gdsc.morgan@gmail.com",
        "advisor": "Dr. Enyue Lu"
    },
    {
        "name": "Student Association for Computing Systems (SACS)",
        "purpose": "General CS student organization",
        "meeting_time": "Thursdays at 6:00 PM",
        "location": "Science Complex 340", 
        "contact": "sacs.morgan@gmail.com",
        "advisor": "Dr. Craig Scott"
    }
]

# Career Resources
CAREER_RESOURCES = {
    "internship_programs": [
        "Google STEP (Student Training in Engineering Program)",
        "Microsoft Explore Program", 
        "NASA USRP (Undergraduate Student Research Program)",
        "NSA STIP (Student Training in Information Protection)",
        "IBM Summer Internship Program",
        "Lockheed Martin Internship Program"
    ],
    "interview_prep": [
        "NeetCode (neetcode.io)",
        "LeetCode (leetcode.com)",
        "ColorStack (colorstack.org)",
        "CodePath (codepath.org)"
    ],
    "career_development": [
        "Resume reviews with career center",
        "Mock technical interviews",
        "Career fairs with tech focus",
        "Alumni networking events"
    ]
}

# Course Information
CORE_COURSES = [
    {"code": "COSC 111", "title": "Programming I", "credits": 4},
    {"code": "COSC 112", "title": "Programming II", "credits": 4},
    {"code": "COSC 211", "title": "Data Structures", "credits": 4},
    {"code": "COSC 225", "title": "Computer Architecture", "credits": 3},
    {"code": "COSC 231", "title": "Algorithms", "credits": 3},
    {"code": "COSC 280", "title": "Software Engineering", "credits": 3},
    {"code": "COSC 310", "title": "Database Systems", "credits": 3},
    {"code": "COSC 315", "title": "Operating Systems", "credits": 3},
    {"code": "COSC 320", "title": "Computer Networks", "credits": 3},
    {"code": "COSC 330", "title": "Programming Languages", "credits": 3},
    {"code": "COSC 340", "title": "Artificial Intelligence", "credits": 3},
    {"code": "COSC 350", "title": "Computer Graphics", "credits": 3},
    {"code": "COSC 360", "title": "Cybersecurity Fundamentals", "credits": 3},
    {"code": "COSC 400", "title": "Senior Capstone I", "credits": 3},
    {"code": "COSC 401", "title": "Senior Capstone II", "credits": 3}
]

MATH_REQUIREMENTS = [
    {"code": "MATH 152", "title": "Calculus I", "credits": 4},
    {"code": "MATH 153", "title": "Calculus II", "credits": 4},
    {"code": "MATH 251", "title": "Calculus III", "credits": 3},
    {"code": "MATH 254", "title": "Differential Equations", "credits": 3},
    {"code": "MATH 295", "title": "Discrete Mathematics", "credits": 4}
]

# Quick Questions for the Chatbot
QUICK_QUESTIONS = [
    "Where is the Computer Science department located?",
    "Who are the faculty members in Computer Science?",
    "What courses do I need for a CS degree?",
    "How do I join student organizations like WiCS or GDSC?",
    "What tutoring services are available for CS students?",
    "How do I get help with programming assignments?",
    "What internship programs are recommended?",
    "How do I prepare for technical interviews?",
    "Who is my academic advisor and how do I contact them?",
    "How do I get an enrollment PIN for registration?",
    "What are the prerequisites for advanced CS courses?",
    "When are the add/drop deadlines for this semester?",
    "How do I submit an override request for a full class?",
    "What career resources are available through the department?",
    "How do I access NeetCode, LeetCode, and other prep resources?",
    "What research opportunities are available for undergraduates?",
    "How do I apply for the Google STEP or Microsoft Explore programs?"
]

# Database Configuration
DATABASE_DEFAULTS = {
    "host": "localhost",
    "port": 5432,
    "database": "morgan_ai",
    "ssl_mode": "prefer",
    "pool_size": 10,
    "max_overflow": 20
}

# Security Configuration
SECURITY_DEFAULTS = {
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
    "password_reset_expire_minutes": 15,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 15
}

# File Upload Limits
MAX_FILE_SIZE = {
    "audio": 25 * 1024 * 1024,  # 25MB for audio files
    "document": 10 * 1024 * 1024,  # 10MB for documents
    "image": 5 * 1024 * 1024,   # 5MB for images
    "backup": 1024 * 1024 * 1024  # 1GB for backups
}

# Error Codes
ERROR_CODES = {
    "INVALID_CREDENTIALS": "INVALID_CREDENTIALS",
    "TOKEN_EXPIRED": "TOKEN_EXPIRED", 
    "RATE_LIMIT_EXCEEDED": "RATE_LIMIT_EXCEEDED",
    "SERVICE_UNAVAILABLE": "SERVICE_UNAVAILABLE",
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "UNAUTHORIZED": "UNAUTHORIZED",
    "FORBIDDEN": "FORBIDDEN",
    "NOT_FOUND": "NOT_FOUND",
    "INTERNAL_ERROR": "INTERNAL_ERROR"
}

# HTTP Status Codes
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503
}

# Logging Configuration
LOG_LEVELS = {
    "DEBUG": "DEBUG",
    "INFO": "INFO", 
    "WARNING": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL"
}

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cache Configuration
CACHE_TTL = {
    "health_check": 60,      # 1 minute
    "user_session": 1800,    # 30 minutes
    "knowledge_base": 3600,  # 1 hour
    "embeddings": 86400,     # 24 hours
    "analytics": 3600        # 1 hour
}

# Monitoring and Analytics
ANALYTICS_EVENTS = [
    "message_sent",
    "voice_used",
    "thread_created",
    "admin_login",
    "knowledge_refresh",
    "backup_created",
    "error_occurred"
]

# Development/Testing Constants
DEV_CONSTANTS = {
    "test_user_id": "test_user_123",
    "test_thread_id": "test_thread_456", 
    "test_admin_username": "admin",
    "mock_response_delay": 1.0  # seconds
}

# Feature Flags (for enabling/disabling features)
FEATURE_FLAGS = {
    "voice_enabled": True,
    "admin_portal": True,
    "analytics": True,
    "backup_system": True,
    "rate_limiting": True,
    "caching": True,
    "monitoring": True
}