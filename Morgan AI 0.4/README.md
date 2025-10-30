# Morgan AI 0.4

## Overview
Morgan AI 0.4 is a full-stack AI chatbot platform for Morgan State University's Computer Science Department. It features a modern React frontend, FastAPI backend, advanced authentication, quick questions, voice features, and full Morgan State branding.

---

## Features
- **Quick Questions Modal:** Categorized help questions, beautiful UI, responsive design
- **Authentication System:** Login/signup modal, client-side validation, error handling, loading states
- **Navigation Menu:** Modern sidebar, collapsible sections, quick links, theme toggle, logout
- **Chat Interface:** Welcome screen, message bubbles, avatars, typing indicator, microphone, quick questions, send button
- **Voice Features:** Welcome message, text-to-speech, speech-to-text
- **Admin Dashboard:** System stats, user management, knowledge base updates
- **Internship Management:** List, create, update, delete internships
- **Morgan State Branding:** Official colors, logo, typography, glass morphism, gradients
- **Logo Modal:** Clickable logo in header pops up a modal with a large view
- **Responsive Design:** Mobile, tablet, desktop optimized
- **Accessibility:** Semantic HTML, keyboard navigation, screen reader friendly

---

## Technology Stack
- **Frontend:** React 18.2, Vite 5, React Router 6.20, Framer Motion, React Icons, CSS3
- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic, SQLAlchemy, OpenAI API, Pinecone, PostgreSQL, Redis
- **DevOps:** Docker & Docker Compose, Nginx, Multi-stage builds, Health checks

---

## Installation

### 1. Clone the repository
```sh
git clone <your-repo-url>
cd Morgan AI 0.4
```

### 2. Python dependencies (Backend)
Install all required Python packages:
```sh
pip install -r BackEnd/app/core_requirements.txt
pip install -r BackEnd/app/langchain_requirements.txt
pip install -r BackEnd/app/requirements.txt
```

### 3. Node dependencies (Frontend)
```sh
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

## Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Quick Questions:** http://localhost:8000/api/chat/quick-questions

---

## Documentation
- **Quick Questions Feature:** QUICK_QUESTIONS_FEATURE.md
- **Authentication System:** AUTHENTICATION_SYSTEM.md
- **Feature Summary:** FEATURE_SUMMARY.md
- **Social Login:** SOCIAL_LOGIN_FEATURE.md

---

## Tips for Users
- Click the blue help icon (?) in the chat input for quick questions
- Click the logo in the header to view it in a modal
- Use the hamburger menu for navigation and quick links
- Use the login/signup modal for authentication
- Toggle theme for dark mode

---

## Morgan State Branding
All components follow Morgan State University's official branding:
- Colors: Blue (#003DA5) and Orange (#F47B20)
- Logo: Official Morgan State Computer Science AI Chatbot logo (2025)
- Typography: Professional, readable fonts
- Tone: Academic, helpful, supportive

---

## License
MIT
