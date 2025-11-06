# Morgan AI 1.0

## Overview
Morgan AI 1.0 is a comprehensive full-stack AI chatbot platform for Morgan State University's Computer Science Department. It features a modern React frontend with advanced navigation, FastAPI backend, comprehensive authentication, voice capabilities, and complete Morgan State University branding integration.

---

## ✨ Key Features

### 🧭 **Advanced Navigation System**
- **Compact Sidebar Menu:** 220px width with smooth slide animations
- **Smart Toggle:** Click hamburger icon (☰) to open/close navigation
- **Click-Outside Functionality:** Tap anywhere outside navigation to close
- **Course Dropdowns:** Expandable sections for CS courses (COSC 110-480)
- **Career Resources:** Integrated internship and job opportunities
- **Calendar Integration:** Academic calendar and event management
- **Voice Settings Access:** Quick access to TTS/STT configuration
- **Theme Toggle:** Light/dark mode switching
- **Perfect Layering:** Navigation appears above all page content
- **Mobile Optimized:** Responsive design for all screen sizes

### 🗣️ **Voice & AI Features**
- **Morgan-Themed Voice Controls:** Translucent university-colored backgrounds
- **Text-to-Speech:** Advanced voice synthesis with multiple voices
- **Speech-to-Text:** Voice input for hands-free interaction
- **Voice Settings:** Rate, pitch, volume, and voice selection
- **Quick Questions:** Pre-configured academic queries
- **Real-time Chat:** Instant AI responses with typing indicators

### 🎓 **Academic Integration**
- **Course Catalog:** Complete CS curriculum from COSC 110 to 480
- **Study Resources:** Organized academic materials and guides
- **Calendar View:** Academic schedules and important dates
- **Student Organizations:** Campus groups and activities
- **Career Center:** Internships and job placement resources
- **Department Info:** Faculty contacts and office hours

### 🔐 **Authentication & Security**
- **Secure Login System:** JWT token-based authentication
- **User Management:** Profile management and preferences
- **Admin Dashboard:** System monitoring and user administration
- **Role-based Access:** Different permissions for students/faculty/admin

### 🎨 **Morgan State Branding**
- **Official Colors:** Morgan Blue (#003DA5) and Orange (#F47B20)
- **University Logo:** Official Morgan State branding throughout
- **Professional Typography:** Clean, academic-focused design
- **Glass Morphism:** Modern translucent UI elements
- **Responsive Design:** Optimized for all devices and screen sizes
- **Accessibility Compliant:** WCAG guidelines and screen reader support

---

## 🆕 What's New in Version 1.5

### **Enhanced Navigation System**
- ✨ **Compact 220px sidebar** with smooth animations
- 🎯 **Perfect click-outside functionality** - tap anywhere to close
- 🎨 **Morgan-themed voice control buttons** with translucent backgrounds
- 📚 **Advanced course dropdowns** for complete CS curriculum
- 💼 **Integrated career resources** and internship management
- 📅 **Calendar component** for academic scheduling
- 🔊 **Enhanced voice settings** with comprehensive controls
- 📱 **Mobile-optimized** responsive design
- ♿ **Full accessibility** with ARIA attributes and keyboard navigation
- 🎭 **Superior z-index management** ensures navigation always appears on top

### **Technical Improvements**
- 🏗️ **DOM structure optimization** for better layering
- 🎪 **Framer Motion animations** with spring physics
- 🎨 **Advanced CSS transforms** and GPU acceleration
- 🔍 **Enhanced event handling** with capture phase listeners
- 📱 **Touch-friendly interactions** for mobile devices
- 🔒 **Robust state management** with React hooks
- 🎯 **Comprehensive click detection** with multiple selector support

---

## 🛠️ Technology Stack

### **Frontend**
- **React 18.2** - Modern component-based UI framework
- **Vite 5** - Lightning-fast build tool and dev server
- **React Router 6.20** - Client-side routing and navigation
- **Framer Motion** - Smooth animations and transitions
- **React Icons** - Comprehensive icon library
- **CSS3** - Advanced styling with grid, flexbox, and animations
- **Responsive Design** - Mobile-first approach with breakpoints

### **Backend**
- **Python 3.11** - Modern Python with latest features
- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and serialization
- **SQLAlchemy** - Database ORM and query builder
- **OpenAI API** - GPT integration for AI responses
- **Pinecone** - Vector database for semantic search
- **PostgreSQL** - Robust relational database
- **Redis** - In-memory cache and session storage

### **DevOps & Deployment**
- **Docker & Docker Compose** - Containerization and orchestration
- **Nginx** - Reverse proxy and static file serving
- **Multi-stage Builds** - Optimized container images
- **Health Checks** - Service monitoring and reliability
- **Volume Mounts** - Persistent data storage

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (Recommended)
- **Node.js 18+** and **npm** (for local development)
- **Python 3.11+** (for local development)
- **Git** for version control

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd "Morgan AI 1.5"
```

### 2. Docker Deployment (Recommended)
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Manual Installation (Development)

#### Backend Dependencies
```bash
cd BackEnd/app
pip install -r core_requirements.txt
pip install -r langchain_requirements.txt
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd FrontEnd
npm install
```

---

## How to Start

### Start All Services (Recommended)
```sh
docker-compose up -d
```

### Rebuild After Changes
```sh
# Frontend only
docker-compose build frontend --no-cache
docker-compose up -d frontend nginx

# Backend only
docker-compose build backend --no-cache
docker-compose up -d backend

# Everything
docker-compose build --no-cache
docker-compose up -d
```

### View Logs
```sh
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services
```sh
docker-compose down
```

---

## How to Run Without Docker

### Backend
```sh
cd BackEnd/app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```sh
cd FrontEnd
npm run dev
```

---

## 🌐 Access Points
- **🏠 Main Application:** [http://localhost](http://localhost) (via Nginx)
- **💻 Frontend Direct:** [http://localhost:3000](http://localhost:3000)
- **🔧 Backend API:** [http://localhost:8000](http://localhost:8000)
- **📚 API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **💚 Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **❓ Quick Questions API:** [http://localhost:8000/api/chat/quick-questions](http://localhost:8000/api/chat/quick-questions)

---

## Documentation
- **Quick Questions Feature:** QUICK_QUESTIONS_FEATURE.md
- **Authentication System:** AUTHENTICATION_SYSTEM.md
- **Feature Summary:** FEATURE_SUMMARY.md
- **Social Login:** SOCIAL_LOGIN_FEATURE.md

---

## 💡 User Guide

### 🧭 **Navigation**
- **📱 Open Menu:** Click the hamburger icon (☰) in the top-left corner
- **❌ Close Menu:** Click anywhere outside the navigation or press Escape
- **📚 Explore Courses:** Expand course sections to see CS curriculum
- **💼 Career Resources:** Access internships and job opportunities
- **📅 Calendar:** View academic schedules and important dates

### 🗣️ **Voice Features**
- **🎤 Voice Input:** Click microphone button to speak your questions
- **🔊 Voice Output:** Enable text-to-speech for AI responses
- **⚙️ Voice Settings:** Access via navigation menu for advanced controls
- **🎭 Voice Selection:** Choose from multiple voice options and languages

### 🎨 **Interface**
- **🌙 Dark Mode:** Toggle between light and dark themes
- **📱 Responsive:** Optimized for desktop, tablet, and mobile
- **🖼️ Logo Modal:** Click the Morgan State logo for enlarged view
- **❓ Quick Questions:** Use the help icon for pre-configured queries

### 🔐 **Account Management**
- **👤 Login/Signup:** Use the authentication modal for account access
- **👨‍💼 Admin Access:** Special features for faculty and administrators
- **⚙️ Profile Settings:** Manage your preferences and information

---

## Morgan State Branding
All components follow Morgan State University's official branding:
- Colors: Blue (#003DA5) and Orange (#F47B20)
- Logo: Official Morgan State Computer Science AI Chatbot logo (2025)
- Typography: Professional, readable fonts
- Tone: Academic, helpful, supportive

---
## 📁 Project Structure
```
Morgan AI 1.5/
├── BackEnd/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── chat.py
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── scripts/
│   │   │   ├── services/
│   │   │   ├── utils/
│   │   │   └── __init__.py
│   │   ├── core_requirements.txt
│   │   ├── data/
│   │   ├── Docker.dockerfile
│   │   ├── langchain_requirements.txt
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── scripts/
│   │   │   ├── ingest_data.py
│   │   │   └── simple_ingest.py
│   │   ├── temp_requirements_for_install.txt
│   │   └── __pycache__/
├── FrontEnd/
│   ├── App.css
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   ├── public/
│   │   ├── apple-touch-icon.png
│   │   ├── assets/
│   │   ├── favicon.ico
│   │   ├── index.css
│   │   ├── index.html
│   │   └── manifest.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Admin/
│   │   │   ├── Auth/
│   │   │   ├── Chart/
│   │   │   ├── Chat/
│   │   │   ├── Navigation/
│   │   │   └── UI/
│   │   ├── context/
│   │   │   ├── ChatContext.jsx
│   │   │   └── VoiceContext.jsx
│   │   ├── hooks/
│   │   │   ├── useaAmin.js
│   │   │   ├── useAuth.js
│   │   │   ├── useChat.js
│   │   │   ├── useTheme.js
│   │   │   ├── useVoice.js
│   │   │   └── useWebSocket.js
│   │   ├── main.jsx
│   │   ├── services/
│   │   │   ├── adminService.js
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   ├── realtimeAPI.js
│   │   │   └── voiceService.js
│   │   ├── styles/
│   │   │   ├── admin.css
│   │   │   ├── app.css
│   │   │   ├── auth.css
│   │   │   ├── chat.css
│   │   │   ├── globals.css
│   │   │   ├── index.css
│   │   │   ├── login.css
│   │   │   ├── navigation.css
│   │   │   └── theme.css
│   │   └── utils/
│   │       ├── constants.js
│   │       ├── formatters.js
│   │       └── validators.js
├── Doc/
│   ├── AUTHENTICATION_SYSTEM.md
│   ├── FEATURE_SUMMARY.md
│   ├── QUICK_QUESTIONS_FEATURE.md
│   └── SOCIAL_LOGIN_FEATURE.md
├── uploads/
├── nginx/
│   └── nginx.conf
├── Test/
│   └── test_auth.ps1
├── docker-compose.yaml
├── package.json
├── README.md
└── logoai.png
```

---

## 🔧 Troubleshooting

### **Navigation Issues**
- **Navigation not opening:** Check that the hamburger menu icon (☰) is clickable
- **Navigation stuck open:** Click outside the navigation area or press Escape
- **Navigation appears behind content:** Restart the frontend container with `docker-compose restart frontend`

### **Docker Issues**
```bash
# Clean rebuild all containers
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d

# Check container status
docker-compose ps

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f backend
```

### **Common Problems**
- **Port already in use:** Stop other services using ports 80, 3000, 8000, 5432, 6379
- **Build failures:** Ensure Docker has sufficient memory (4GB+ recommended)
- **Navigation layering:** Clear browser cache and hard refresh (Ctrl+F5)

### **Development**
```bash
# Frontend development server
cd FrontEnd
npm run dev

# Backend development server  
cd BackEnd/app
uvicorn app.main:app --reload

# Hot reload both services
docker-compose up --build
```

---

## 📝 License
MIT License - See LICENSE file for details

---

## 🏫 About Morgan State University
Morgan State University is a public research university in Baltimore, Maryland. The Computer Science Department is committed to providing excellent education and innovative AI solutions for students and faculty.

**Department Contact:**
- 📍 Science Complex, Room 325
- 📞 (443) 885-3130  
- 📧 cs@morgan.edu
- 🌐 [morgan.edu/computer-science](https://www.morgan.edu/computer-science)

