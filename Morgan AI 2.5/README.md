# Morgan AI 2.5: An AI-Powered Chatbot Assistant for Morgan State University Computer Science Department

**Authors:** Morgan State University Computer Science Department, Senior Project Team 2025

**Date:** December 1, 2025

**Version:** 2.5

## Abstract

Morgan AI 2.5 is a comprehensive full-stack AI chatbot platform designed to serve students and faculty of Morgan State University's Computer Science Department. The system integrates modern web technologies (React 18, FastAPI, PostgreSQL) with advanced AI capabilities (GPT-4, LangChain, Pinecone) to provide intelligent assistance with academic advising, course planning, and departmental resources. Key features include real-time chat with conversation history, voice input/output capabilities, Degree Works transcript analysis, automatic knowledge base updates via file system monitoring, and career resource management. The system achieves production-ready status with 14/15 core features fully operational and comprehensive test coverage via automated smoke testing. This paper describes the architecture, implementation, deployment strategy, and validation results of the system.

## 1. Introduction

Morgan State University's Computer Science Department requires a modern platform to assist students with academic advising, course planning, and access to departmental resources. Existing systems lack integrated AI capabilities, centralized knowledge management, and intuitive user interfaces tailored to student needs.

This project addresses these gaps by developing an AI-powered chatbot platform that:
- Provides real-time, context-aware assistance using GPT-4
- Maintains comprehensive chat history with searchable conversation threads
- Analyzes Degree Works transcripts for automated course planning
- Auto-updates knowledge base through intelligent file system monitoring
- Integrates voice capabilities (TTS/STT) for accessibility
- Delivers career resources and internship opportunities
- Operates at production scale with 100+ concurrent users

### 1.1 Problem Statement
Students lack a unified platform to:
- Ask questions about CS courses, prerequisites, and degree requirements
- Receive personalized course recommendations based on transcript analysis
- Access current department information, events, and faculty contact details
- Maintain searchable conversation history for future reference
- Interact via voice for hands-free accessibility

### 1.2 Solution Overview
Morgan AI 2.5 provides an integrated system combining:
- **Frontend:** Modern React 18 UI with advanced navigation and voice controls
- **Backend:** High-performance FastAPI server with PostgreSQL/Redis
- **AI Engine:** GPT-4 with RAG (Retrieval-Augmented Generation) via Pinecone
- **Auto-Update:** Watchdog-based knowledge base synchronization
- **Deployment:** Docker Compose for reproducible, scalable deployment

---

## 2. System Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer (Port 3000)                  │
│  React 18 Frontend (Vite) + Chat + Voice + DegreeWorks      │
└─────────────────────────────────────────────────────────────┘
                           │ HTTPS/WS
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway (Port 8000)                     │
│  FastAPI + Uvicorn (Chat, Voice, Auth, Knowledge, Admin)    │
└─────────────────────────────────────────────────────────────┘
   │ Queries │ File I/O │ Vectors │ Sessions │
   ↓         ↓          ↓         ↓
PostgreSQL  File System Pinecone  Redis
```

### 2.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 18.2 | Component UI |
| | Vite | 5.0 | Fast bundling |
| | Framer Motion | 10.16 | Animations |
| **Backend** | FastAPI | Latest | Async API |
| | SQLAlchemy | 2.0 | ORM |
| **AI/ML** | OpenAI API | GPT-4 | Language model |
| | LangChain | Latest | LLM orchestration |
| | Pinecone | Latest | Vector DB |
| **Database** | PostgreSQL | 15-alpine | Primary data |
| | Redis | 7-alpine | Cache/sessions |
| **DevOps** | Docker Compose | Latest | Orchestration |
| | Nginx | alpine | Reverse proxy |

---

## 3. Key Features (✅ Production-Ready)

### 3.1 Core Communication Features

### 🧭 **Advanced Navigation System**
- **Compact Sidebar Menu:** 220px width with smooth slide animations
- **Smart Toggle:** Click hamburger icon (☰) to open/close navigation
- **Click-Outside Functionality:** Tap anywhere outside navigation to close
- **Course Dropdowns:** Expandable sections for CS courses (COSC 110-480)
- **Career Resources:** Integrated internship and job opportunities
- **Calendar Integration:** Academic calendar and event management
- **Chat History Access:** Quick access to conversation history
- **Voice Settings Access:** Quick access to TTS/STT configuration
- **Theme Toggle:** Light/dark mode switching
- **Perfect Layering:** Navigation appears above all page content
- **Mobile Optimized:** Responsive design for all screen sizes

### 💬 **Chat History & Thread Management**
- **Database-Backed Storage:** All conversations persisted in PostgreSQL
- **Conversation Threads:** Automatic thread creation and management
- **Resume Conversations:** Continue any past chat from where you left off
- **Smart Search:** Search by title, content, or date range
- **Date Grouping:** Organized by Today, Yesterday, This Week, Older
- **New Chat:** Start fresh conversations while preserving history
- **Soft Delete:** Recoverable conversation deletion
- **Thread Activation:** Only one active conversation at a time

### 🎓 **Degree Works Integration**
- **PDF Upload:** Upload degree audit directly in chat interface
- **Transcript Parsing:** Automatic extraction of courses, grades, and credits
- **Academic Summary:** View GPA, completed credits, and classification
- **Course Analysis:** Categorized view of completed, in-progress, and remaining courses
- **Quick Actions:** Pre-built queries for common degree audit questions
- **Version Tracking:** Compare multiple transcript uploads over time
- **Persistent Storage:** Transcript data saved per user with versioning
- **Dedicated Page:** Full Degree Works analysis at `/degree-works`

### 🗣️ **Voice & AI Features**
- **Morgan-Themed Voice Controls:** Translucent university-colored backgrounds
- **Text-to-Speech:** Advanced voice synthesis with multiple voices
- **Speech-to-Text:** Voice input for hands-free interaction
- **Voice Settings:** Rate, pitch, volume, and voice selection
- **Quick Questions:** 28 pre-configured questions across 6 categories
- **Real-time Chat:** Instant AI responses with typing indicators
- **Context-Aware Responses:** Integrated with Degree Works and knowledge base

### 📚 **Knowledge Base & Auto-Updates**
- **Automatic Updates:** Real-time file monitoring with watchdog
- **Incremental Processing:** Hash-based change detection (10-100x faster)
- **Scheduled Refresh:** Configurable periodic updates (default: 24 hours)
- **Admin API:** Complete knowledge management endpoints
- **Vector Database:** Pinecone integration for semantic search
- **Update History:** Comprehensive logging and status monitoring
- **Manual Triggers:** On-demand knowledge base updates

### 💼 **Career Resources**
- **Internship Database:** Searchable internship opportunities
- **Job Listings:** Career opportunities for CS majors
- **Auto-Update System:** Periodic refresh of career resources
- **Dedicated Page:** Full career center at `/career`
- **Application Tracking:** Save and manage applications

### 📅 **Calendar & Events**
- **Academic Calendar:** Important dates and deadlines
- **Event Management:** Campus events and activities
- **Event Categories:** Academic, social, career, and departmental events
- **Dedicated Page:** Full calendar view at `/calendar`

### 🔐 **Authentication & Security**
- **Secure Login System:** JWT token-based authentication
- **User Registration:** Full signup flow with validation
- **Password Security:** Bcrypt hashing and secure storage
- **User Management:** Profile management and preferences
- **Admin Dashboard:** System monitoring and user administration
- **Role-based Access:** Different permissions for students/faculty/admin
- **Session Management:** Secure token handling with refresh

### 🎨 **Morgan State Branding**
- **Official Colors:** Morgan Blue (#003DA5) and Orange (#F47B20)
- **University Logo:** Official Morgan State branding throughout
- **Professional Typography:** Clean, academic-focused design
- **Glass Morphism:** Modern translucent UI elements
- **Responsive Design:** Optimized for all devices and screen sizes
- **Accessibility Compliant:** WCAG guidelines and screen reader support

---

## 🆕 What's New in Version 2.5

### **Chat History System** (November 2025)
- ✨ **PostgreSQL Integration** - All conversations persisted in database
- 💾 **Thread Management** - Automatic thread creation and organization
- 🔍 **Advanced Search** - Search by title, content, or date range
- 📅 **Smart Grouping** - Conversations organized by date (Today, Yesterday, etc.)
- ▶️ **Resume Conversations** - Pick up any chat where you left off
- 🗑️ **Soft Delete** - Recoverable conversation deletion
- 📊 **Full History View** - Dedicated `/chat-history` page

### **Degree Works Feature** (November 2025)
- 📄 **PDF Upload** - Upload degree audit directly in chat
- 🎯 **Smart Parsing** - Extract courses, grades, GPA, and credits
- 📊 **Academic Dashboard** - View completed, in-progress, and remaining courses
- 🚀 **Quick Actions** - Pre-built questions about your transcript
- 📈 **Version Tracking** - Compare multiple transcript uploads
- 💾 **Persistent Storage** - Data saved per user with automatic versioning
- 🖥️ **Dedicated Page** - Full analysis at `/degree-works`

### **Knowledge Base Auto-Updates** (November 2025)
- 🔄 **Real-time Monitoring** - Watchdog file system integration
- ⚡ **Incremental Updates** - 10-100x faster with hash-based change detection
- ⏰ **Scheduled Refresh** - Configurable periodic updates (default: 24 hours)
- 🛠️ **Admin API** - Complete knowledge management endpoints
- 📊 **Update History** - Comprehensive logging and status monitoring
- 🎯 **Manual Triggers** - On-demand knowledge base updates

### **Enhanced Quick Questions** (November 2025)
- 📚 **6 Categories** - Expanded from 4 to 6 question categories
- 💬 **28 Questions** - Increased from 16 to 28 pre-configured queries
- 🎓 **Student Organizations** - Questions about WiCS, GDSC, hackathons
- 🎉 **Social & Events** - Tech talks, workshops, project partners
- 🤝 **Community Focus** - Help students connect and collaborate

### **Career Resources Enhancement**
- 💼 **Internship Database** - Searchable career opportunities
- 🔄 **Auto-Update System** - Periodic refresh of listings
- 📍 **Dedicated Page** - Full career center at `/career`
- 🎯 **Application Tracking** - Save and manage applications

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
- 🏗️ **PostgreSQL Database** - Full relational database integration
- 🔄 **Redis Cache** - High-performance caching layer
- 🐳 **Docker Compose** - Complete containerized deployment
- 🔍 **Adminer** - Database management interface (dev mode)
- 🏥 **Health Checks** - Service monitoring for all containers
- 🎪 **Framer Motion animations** with spring physics
- 🎨 **Advanced CSS transforms** and GPU acceleration
- 🔒 **Robust state management** with React hooks
- 🎯 **Comprehensive error handling** across all services

---

## 🛠️ Technology Stack

### **Frontend**
- **React 18.2** - Modern component-based UI framework
- **Vite 5** - Lightning-fast build tool and dev server
- **React Router 6.20** - Client-side routing and navigation
- **Framer Motion 10.16** - Smooth animations and transitions
- **React Icons 4.12** - Comprehensive icon library
- **Axios 1.6** - HTTP client for API requests
- **Socket.io Client 4.5** - Real-time WebSocket communication
- **React Markdown 9.0** - Markdown rendering for chat messages
- **React Syntax Highlighter 15.5** - Code syntax highlighting
- **Date-fns 2.30** - Modern date utility library
- **Zustand 4.4** - Lightweight state management
- **React Hook Form 7.48** - Form validation and handling
- **CSS3** - Advanced styling with grid, flexbox, and animations
- **Responsive Design** - Mobile-first approach with breakpoints

### **Backend**
- **Python 3.11** - Modern Python with latest features
- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server for production deployment
- **Pydantic** - Data validation and serialization
- **SQLAlchemy 2.0** - Database ORM and query builder
- **Alembic** - Database migrations management
- **OpenAI API** - GPT-4 integration for AI responses
- **LangChain** - LLM orchestration and RAG implementation
- **Pinecone** - Vector database for semantic search
- **PostgreSQL 15** - Robust relational database
- **Redis 7** - In-memory cache and session storage
- **Watchdog 5.0** - File system event monitoring
- **PyPDF2** - PDF parsing for Degree Works
- **Bcrypt** - Password hashing and security
- **JWT** - JSON Web Token authentication
- **python-multipart** - File upload handling

### **Database**
- **PostgreSQL 15-Alpine** - Main relational database
  - User management and authentication
  - Chat threads and messages storage
  - Degree Works data persistence
  - Internship and career data
- **Redis 7-Alpine** - Cache and session storage
  - Session management
  - Rate limiting
  - Temporary data caching
- **Pinecone Vector DB** - Semantic search
  - Knowledge base embeddings
  - Contextual retrieval for AI responses

### **DevOps & Deployment**
- **Docker & Docker Compose** - Containerization and orchestration
- **Nginx Alpine** - Reverse proxy and static file serving
- **Multi-stage Builds** - Optimized container images
- **Health Checks** - Service monitoring and reliability
- **Volume Mounts** - Persistent data storage
- **Network Isolation** - Secure inter-service communication
- **Adminer** - Database management UI (development mode)

---

## 🚀 Complete Setup Guide

### Prerequisites

Before starting, ensure you have the following installed:

#### Required (Docker Method - Recommended)
- **Docker Desktop** (Windows 10/11 or macOS 13+)
  - Download: https://www.docker.com/products/docker-desktop
  - Windows: Enable WSL 2 backend
  - macOS: Grant necessary permissions
- **Git** for version control
  - Windows: https://git-scm.com/download/win
  - macOS: `brew install git` or Xcode Command Line Tools
- **OpenAI API Key** (Required)
  - Sign up: https://platform.openai.com/signup
  - Generate key: https://platform.openai.com/api-keys

#### Optional (For Local Development)
- **Python 3.11+** 
  - Windows: https://www.python.org/downloads/
  - macOS: `brew install python@3.11`
- **Node.js 18+** and **npm**
  - Windows: https://nodejs.org/
  - macOS: `brew install node`
- **Pinecone Account** (Optional - for vector search)
  - Sign up: https://www.pinecone.io/

---

## 📦 Step-by-Step Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repo-url>

# Navigate to project directory
cd "Morgan AI 2.5/Morgan AI 2.5"

# Verify you're in the correct directory (should see docker-compose.yaml)
ls docker-compose.yaml  # macOS/Linux
dir docker-compose.yaml  # Windows
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root (same folder as `docker-compose.yaml`):

**Windows PowerShell:**
```powershell
New-Item -Path .env -ItemType File
notepad .env
```

**macOS/Linux:**
```bash
touch .env
nano .env
```

**Paste this template and replace with your actual keys:**
```env
# Required - OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Optional - Pinecone Vector Database (for enhanced search)
PINECONE_API_KEY=your-pinecone-key-or-leave-blank
PINECONE_ENVIRONMENT=us-east-1-gcp
PINECONE_INDEX_NAME=morgan-chatbot

# Required - Security Settings (change these!)
SECRET_KEY=your-super-secret-jwt-key-change-this
ADMIN_PASSWORD=change-this-admin-password

# Optional - GroupMe Integration
GROUPME_ACCESS_TOKEN=
GROUPME_BOT_ID=
GROUPME_GROUP_ID=

# Database URLs (Auto-configured by Docker - do not change)
DATABASE_URL=postgresql://morgan:morgan123@postgres:5432/morgan_chatbot
REDIS_URL=redis://redis:6379/0
```

**Important Notes:**
- Replace `sk-proj-your-actual-key-here` with your real OpenAI API key
- Change `SECRET_KEY` to a random string (at least 32 characters)
- Change `ADMIN_PASSWORD` to a secure password
- Save the file after editing

### Step 3: Start the Application

#### Option A: Docker (Recommended - One Command Start)

**Start all services:**
```bash
docker-compose up -d
```

**Verify all containers are running:**
```bash
docker-compose ps
```

Expected output (all should show "Up"):
```
NAME                        STATUS
morgan-chatbot-backend      Up (healthy)
morgan-chatbot-frontend     Up
morgan-chatbot-postgres     Up (healthy)
morgan-chatbot-redis        Up (healthy)
morgan-chatbot-nginx        Up
```

**Check health status:**
```bash
# Windows PowerShell
Invoke-WebRequest http://localhost:8000/health

# macOS/Linux
curl http://localhost:8000/health
```

Expected response: `{"status":"healthy"}`

**Access the application:**
- Frontend: http://localhost
- Backend API Docs: http://localhost:8000/docs
- Database Admin (Dev): http://localhost:8080

#### Option B: Local Development (Without Docker)

**Backend Setup:**
```bash
# Navigate to backend
cd BackEnd/app

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup (in a new terminal):**
```bash
# Navigate to frontend
cd FrontEnd

# Install dependencies
npm install

# Start development server
npm run dev
```

**Access:**
- Frontend: http://localhost:5173 (Vite dev server)
- Backend: http://localhost:8000

---

## 🎯 Running Instructions

### First-Time Setup

1. **Start Docker containers:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to initialize** (30-60 seconds)
   - Backend will initialize database tables
   - Vector store will connect to Pinecone (if configured)
   - Health checks will verify all services

3. **Open your browser:**
   - Navigate to http://localhost
   - You should see the Morgan AI login screen

4. **Create an account:**
   - Click "Sign Up"
   - Enter your details
   - Login with your credentials

5. **Start chatting:**
   - Ask questions about Morgan State CS
   - Upload your Degree Works transcript (optional)
   - Explore Quick Questions and features

### Daily Usage

**Start the application:**
```bash
cd "Morgan AI 2.5/Morgan AI 2.5"
docker-compose up -d
```

**Stop the application:**
```bash
docker-compose down
```

**Restart after code changes:**
```bash
# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Rebuild and restart everything
docker-compose up -d --build
```

**View logs (troubleshooting):**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild containers with latest code
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🖥️ Platform-Specific Guides

For detailed platform-specific instructions:
- **Windows:** See `Doc/INSTALL_WINDOWS.md`
- **macOS:** See `Doc/INSTALL_MAC.md`

These guides include:
- Detailed Docker Desktop setup
- Troubleshooting common issues
- Platform-specific commands
- Performance optimization tips

---

## 🔧 Advanced Operations

### Managing Docker Services

**Start all services:**
```bash
docker-compose up -d
```

**Stop all services (preserves data):**
```bash
docker-compose down
```

**Stop and remove all data (complete reset):**
```bash
docker-compose down -v
```

**Restart specific service:**
```bash
docker-compose restart backend
docker-compose restart frontend
docker-compose restart postgres
```

**Rebuild after code changes:**
```bash
# Frontend only
docker-compose build frontend --no-cache
docker-compose up -d frontend nginx

# Backend only
docker-compose build backend --no-cache
docker-compose up -d backend

# Everything (complete rebuild)
docker-compose build --no-cache
docker-compose up -d
```

**View logs:**
```bash
# All services (live streaming)
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

**Check service health:**
```bash
docker-compose ps
docker exec morgan-chatbot-backend curl http://localhost:8000/health
```

### Database Management

**Access database via Adminer (Development):**
1. Open http://localhost:8080
2. Login with:
   - System: `PostgreSQL`
   - Server: `postgres`
   - Username: `morgan`
   - Password: `morgan123`
   - Database: `morgan_chatbot`

**Access database via command line:**
```bash
# Connect to PostgreSQL
docker exec -it morgan-chatbot-postgres psql -U morgan -d morgan_chatbot

# List all tables
\dt

# View users
SELECT * FROM users;

# View chat threads
SELECT * FROM chat_threads WHERE deleted_at IS NULL;

# Exit
\q
```

**Backup database:**
```bash
docker exec morgan-chatbot-postgres pg_dump -U morgan morgan_chatbot > backup.sql
```

**Restore database:**
```bash
docker exec -i morgan-chatbot-postgres psql -U morgan morgan_chatbot < backup.sql
```

### Local Development (Without Docker)

**Backend development:**
```bash
cd BackEnd/app

# Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend development:**
```bash
cd FrontEnd

# Install dependencies
npm install

# Run development server with hot reload
npm run dev

# Build for production
npm run build
```

### Maintenance Commands

**Clean up unused Docker resources:**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused (careful!)
docker system prune -a
```

**Check disk usage:**
```bash
docker system df
```

**Update dependencies:**
```bash
# Backend
cd BackEnd/app
pip install --upgrade -r requirements.txt

# Frontend
cd FrontEnd
npm update
```

---

## 🌐 Access Points
- **🏠 Main Application:** [http://localhost](http://localhost) (via Nginx)
- **💻 Frontend Direct:** [http://localhost:3000](http://localhost:3000)
- **🔧 Backend API:** [http://localhost:8000](http://localhost:8000)
- **📚 API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **💚 Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **🗄️ Database Admin (Dev):** [http://localhost:8080](http://localhost:8080) (Adminer)
- **❓ Quick Questions API:** [http://localhost:8000/api/chat/quick-questions](http://localhost:8000/api/chat/quick-questions)
- **📊 Degree Works API:** [http://localhost:8000/api/degree-works/](http://localhost:8000/api/degree-works/)
- **💾 Chat History API:** [http://localhost:8000/api/chat/threads](http://localhost:8000/api/chat/threads)
- **🔍 Knowledge Status:** [http://localhost:8000/api/knowledge/status](http://localhost:8000/api/knowledge/status)

---

---

## 4. Setup & Installation Instructions

### 4.1 Prerequisites

**Required:**
- Docker Desktop (Windows 10/11, macOS 13+, or Linux)
- Git version control
- OpenAI API Key (https://platform.openai.com/api-keys)

**Optional:**
- Python 3.11+ (for local backend development)
- Node.js 18+ (for local frontend development)
- Pinecone API Key (for vector search enhancement)

### 4.2 Step-by-Step Installation (Docker Method - Recommended)

**Step 1: Clone Repository**
```bash
git clone <your-repo-url>
cd "Morgan AI 2.5/Morgan AI 2.5"
```

**Step 2: Configure Environment**

Create `.env` file in project root:
```bash
# Linux/macOS
touch .env && nano .env

# Windows PowerShell
New-Item .env; notepad .env
```

Add configuration:
```env
# OpenAI (Required)
OPENAI_API_KEY=sk-proj-your-actual-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Security (Change these!)
SECRET_KEY=generate-random-32-char-string-here
ADMIN_PASSWORD=choose-secure-password

# Optional
PINECONE_API_KEY=your-key-or-leave-blank
```

**Step 3: Start Services**
```bash
docker-compose up -d
```

**Step 4: Verify Health**
```bash
# Check containers
docker-compose ps

# Test API
curl http://localhost:8000/health
```

### 4.3 Local Development (Without Docker)

**Backend Setup:**
```bash
cd BackEnd/app
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
uvicorn app.app.main:app --reload --port 8000
```

**Frontend Setup (new terminal):**
```bash
cd FrontEnd
npm install
npm run dev
```

---

## 5. Running Instructions

### 5.1 First-Time Usage

1. Start Docker: `docker-compose up -d`
2. Wait 30-60 seconds for initialization
3. Open browser: http://localhost
4. Sign up with email/password
5. Start chatting or upload Degree Works PDF

### 5.2 Regular Operations

**Start:**
```bash
docker-compose up -d
```

**Stop:**
```bash
docker-compose down
```

**View Logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Rebuild After Code Changes:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## 6. Validation & Testing

### 6.1 Smoke Test

Run automated feature verification:
```bash
.\Test\test-smoke.ps1  # Windows
bash Test/test-smoke.sh  # Linux/macOS
```

**Expected Output:**
- ✅ 14/15 tests passing
- ✅ Backend health: operational
- ✅ All services: database, OpenAI, Pinecone
- ✅ Chat messages: 200 OK
- ✅ Voice TTS: ~49KB MP3 generated
- ✅ Quick Questions: 28 questions available

### 6.2 Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | http://localhost | Main app |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/health | Status check |
| Database UI | http://localhost:8080 | Adminer (dev) |

---

## 7. Feature Verification Matrix

| Feature | Status | Test Method |
|---------|--------|-------------|
| Chat Messages | ✅ Working | Send message, expect 200 OK |
| Voice TTS | ✅ Working | POST /api/voice/text-to-speech |
| Quick Questions | ✅ Working | GET /api/chat/quick-questions |
| Degree Works | ✅ Ready | POST /api/degree-works/upload |
| Authentication | ✅ Working | POST /api/auth/signup |
| Chat Threads | ✅ Working | GET /api/chat/threads |
| Internships | ✅ Working | GET /api/internships/list |
| WebSIS | ✅ Ready | Needs credentials |

---

## 8. References

**[1]** OpenAI API Documentation. "Text Generation Models." https://platform.openai.com/docs/guides/gpt. Accessed December 2025.

**[2]** Tiangolo, S. "FastAPI." https://fastapi.tiangolo.com/. Accessed December 2025.

**[3]** LangChain Community. "LangChain Documentation." https://python.langchain.com/. Accessed December 2025.

**[4]** Pinecone. "Pinecone Vector Database Documentation." https://docs.pinecone.io/. Accessed December 2025.

**[5]** PostgreSQL Global Development Group. "PostgreSQL 15 Documentation." https://www.postgresql.org/docs/15/. Accessed December 2025.

**[6]** Redis Inc. "Redis Documentation." https://redis.io/documentation/. Accessed December 2025.

**[7]** React Team. "React 18 Documentation." https://react.dev/. Accessed December 2025.

**[8]** Vite Contributors. "Vite 5.0 Documentation." https://vitejs.dev/guide/. Accessed December 2025.

**[9]** Pydantic Team. "Pydantic Documentation." https://docs.pydantic.dev/latest/. Accessed December 2025.

**[10]** SQLAlchemy Contributors. "SQLAlchemy 2.0 Documentation." https://docs.sqlalchemy.org/20/. Accessed December 2025.

**[11]** Docker Inc. "Docker Compose Documentation." https://docs.docker.com/compose/. Accessed December 2025.

**[12]** PyPDF Contributors. "PyPDF2 Documentation." https://pypdf.readthedocs.io/. Accessed December 2025.

**[13]** Python Software Foundation. "Bcrypt Library." https://pypi.org/project/bcrypt/. Accessed December 2025.

**[14]** PyJWT Contributors. "PyJWT Documentation." https://pyjwt.readthedocs.io/. Accessed December 2025.

**[15]** Watchdog Contributors. "Watchdog Documentation." https://watchdog.readthedocs.io/. Accessed December 2025.

---

## 9. Appendix: Quick Reference

### 9.1 Essential Commands

```bash
# Start all services
docker-compose up -d

# View service status
docker-compose ps

# Check backend logs
docker-compose logs -f backend

# Restart specific service
docker-compose restart backend

# Complete reset (caution - deletes all data)
docker-compose down -v
```

### 9.2 API Endpoints Summary

**Chat API:**
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/threads` - List chat threads
- `GET /api/chat/quick-questions` - Get 28 quick questions

**Voice API:**
- `POST /api/voice/text-to-speech` - Convert text to speech
- `POST /api/voice/speech-to-text` - Convert speech to text

**Auth API:**
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login

**Degree Works API:**
- `POST /api/degree-works/upload` - Upload PDF transcript
- `GET /api/degree-works/analysis` - Get transcript analysis

---

## 10. Conclusion

Morgan AI 2.5 represents a comprehensive solution for AI-powered academic assistance at Morgan State University. The system achieves production-ready status with all core features operational, robust testing via automated smoke tests, and comprehensive documentation. Future work includes social login integration, mobile app development, and advanced analytics capabilities.

---

**Document Version:** 1.0  
**Last Updated:** December 1, 2025  
**Status:** ✅ Final ACM Format  
**Total Development Time:** 4 months  
**Team Size:** 5 senior project students  
**Institution:** Morgan State University, Computer Science Department


## 📚 API Endpoints

### **Authentication** (`/api/auth/`)
- `POST /login` - User login with JWT token
- `POST /signup` - New user registration
- `GET /me` - Get current user profile
- `POST /logout` - User logout
- `POST /refresh` - Refresh access token

### **Chat** (`/api/chat/`)
- `POST /message` - Send chat message
- `POST /stream` - Stream AI response
- `GET /threads` - List user's chat threads
- `GET /threads/{id}` - Get specific thread
- `GET /threads/{id}/messages` - Get thread messages
- `POST /threads` - Create new thread
- `DELETE /threads/{id}` - Delete thread (soft delete)
- `PUT /threads/{id}/activate` - Activate thread
- `POST /feedback` - Submit message feedback
- `GET /search` - Search chat history
- `GET /quick-questions` - Get categorized quick questions (28 total)

### **Degree Works** (`/api/degree-works/`)
- `POST /upload` - Upload and parse degree audit PDF
- `GET /analysis` - Get latest transcript analysis
- `GET /summary` - Get academic summary for UI
- `GET /versions` - List all transcript versions
- `GET /versions/{id}` - Get specific version
- `GET /versions/{id}/diff/{base}` - Compare versions
- `DELETE /versions/{id}` - Delete specific version
- `DELETE /analysis` - Delete all Degree Works data
- `GET /timeline` - Get course timeline
- `GET /courses` - Query courses by status/category

### **Knowledge Management** (`/api/knowledge/`) - Admin Only
- `GET /status` - View knowledge base update status
- `POST /update` - Trigger manual update (incremental/full)
- `POST /detect-changes` - Detect changed files
- `POST /schedule` - Schedule periodic updates
- `GET /history` - View update history
- `POST /start-file-watcher` - Enable real-time monitoring

### **Voice** (`/api/voice/`)
- `POST /welcome` - Generate welcome message
- `POST /text-to-speech` - Convert text to speech
- `POST /speech-to-text` - Convert speech to text

### **Internships** (`/api/internships/`)
- `GET /` - List internship opportunities
- `POST /` - Create new internship (admin)
- `PUT /{id}` - Update internship (admin)
- `DELETE /{id}` - Delete internship (admin)
- `GET /search` - Search internships

### **Admin** (`/api/admin/`)
- `GET /stats` - System statistics
- `GET /users` - List all users
- `POST /users/{id}/role` - Update user role
- `DELETE /users/{id}` - Delete user

---

## Documentation
Comprehensive documentation available in the `Doc/` folder:

### **Core Features**
- **FEATURE_SUMMARY.md** - Complete feature overview
- **UPDATE_SUMMARY_NOV_2025.md** - Latest updates and changes
- **COMPLETE_SYSTEM_INTEGRATION.md** - Full system architecture

### **Chat & History**
- **CHAT_HISTORY_SYSTEM.md** - Complete chat history implementation
- **CHAT_HISTORY_ENHANCEMENTS.md** - Recent improvements
- **CHAT_HISTORY_SEARCH_FEATURE.md** - Search functionality
- **COMPLETE_CHAT_HISTORY_SYSTEM.md** - Full system guide

### **Degree Works**
- **DEGREE_WORKS_COMPLETE_GUIDE.md** - Complete implementation guide
- **DEGREE_WORKS_FEATURE.md** - Feature overview
- **DEGREE_WORKS_AI_INTEGRATION.md** - AI integration details
- **DEGREE_WORKS_IMPLEMENTATION_STATUS.md** - Current status

### **Authentication & Security**
- **AUTHENTICATION_SYSTEM.md** - Authentication implementation
- **AUTHENTICATION_IMPLEMENTATION_STATUS.md** - Auth status
- **SOCIAL_LOGIN_FEATURE.md** - Social login integration
- **LOGOUT_LOGIN_BEHAVIOR.md** - Login/logout flow
- **LOGOUT_LOGIN_FLOW_DIAGRAM.md** - Visual flow diagram
- **LOGOUT_LOGIN_QUICK_REFERENCE.md** - Quick reference guide

### **Knowledge Base**
- **KNOWLEDGE_AUTO_UPDATE.md** - Auto-update system guide
- **INTERNSHIP_AUTO_UPDATE_SYSTEM.md** - Internship updates

### **Database**
- **DATABASE_IMPLEMENTATION.md** - Database schema and setup
- **DATABASE_SUMMARY.md** - Database overview

### **UI/UX**
- **UI_UX_ENHANCEMENTS.md** - UI improvements
- **UI_UX_IMPLEMENTATION_SUMMARY.md** - Implementation details
- **UI_UX_QUICK_REFERENCE.md** - Quick reference
- **UI_UX_VISUAL_GUIDE.md** - Visual guide
- **NAVIGATION_AND_STORAGE_GUIDE.md** - Navigation system

### **Quick Features**
- **QUICK_QUESTIONS_FEATURE.md** - Quick questions implementation
- **IMPLEMENTATION_SUMMARY.md** - General implementation notes
- **IMPLEMENTATION_SUMMARY_NOV_22_2025.md** - November updates

---

## 💡 User Guide

### 🧭 **Navigation**
- **📱 Open Menu:** Click the hamburger icon (☰) in the top-left corner
- **❌ Close Menu:** Click anywhere outside the navigation or press Escape
- **📚 Explore Courses:** Expand course sections to see CS curriculum
- **💼 Career Resources:** Access internships and job opportunities at `/career`
- **📅 Calendar:** View academic schedules and important dates at `/calendar`
- **💬 Chat History:** View all past conversations at `/chat-history`
- **📊 Degree Works:** Access transcript analysis at `/degree-works`

### 💬 **Chat Features**
- **💬 New Chat:** Click "New Chat" button to start fresh conversation
- **📝 Send Message:** Type and press Enter or click send button
- **❓ Quick Questions:** Click help icon (?) for 28 pre-configured questions
- **🔍 Search:** Click search icon to search chat history by title or content
- **📄 Upload Transcript:** Click Degree Works icon to upload degree audit
- **📜 Resume Chat:** Click any conversation in history to continue
- **🗑️ Delete Chat:** Delete unwanted conversations (recoverable)

### 📊 **Degree Works**
- **📤 Upload PDF:** Click file icon in chat, select your degree audit PDF
- **📊 View Summary:** See GPA, credits, and classification after upload
- **🚀 Quick Actions:** Use pre-built questions about your transcript
- **📈 Track Progress:** Compare multiple uploads to see progress
- **🔍 Course Search:** Query specific courses and requirements
- **📅 Timeline:** View course completion timeline
- **🗑️ Delete Data:** Remove transcript data anytime

### 🗣️ **Voice Features**
- **🎤 Voice Input:** Click microphone button to speak your questions
- **🔊 Voice Output:** Enable text-to-speech for AI responses
- **⚙️ Voice Settings:** Access via navigation menu for advanced controls
- **🎭 Voice Selection:** Choose from multiple voice options and languages
- **⚡ Quick Access:** Voice controls always visible in chat input

### 🔍 **Search & History**
- **🔍 Search Chats:** Click search icon to find past conversations
- **📅 Date Filter:** Filter conversations by date range
- **💬 Content Search:** Search within message content
- **📋 Title Search:** Find chats by title
- **📊 Results Preview:** See matching messages with context
- **▶️ Load Conversation:** Click result to resume full chat

### 🎨 **Interface**
- **🌙 Dark Mode:** Toggle between light and dark themes
- **📱 Responsive:** Optimized for desktop, tablet, and mobile
- **🖼️ Logo Modal:** Click the Morgan State logo for enlarged view
- **❓ Quick Questions:** Use the help icon for pre-configured queries
- **🎨 Glass Morphism:** Modern translucent UI effects throughout

### 🔐 **Account Management**
- **👤 Login/Signup:** Use the authentication modal for account access
- **👨‍💼 Admin Access:** Special features for faculty and administrators
- **⚙️ Profile Settings:** Manage your preferences and information
- **🔒 Secure Sessions:** JWT-based authentication with auto-refresh
- **🚪 Logout:** Safely logout from navigation menu

### 💼 **Career Resources**
- **🔍 Browse Internships:** View searchable internship opportunities
- **📝 Application Tracking:** Save and manage your applications
- **🔄 Auto-Updates:** Listings refresh automatically
- **🎯 Filter Options:** Search by company, role, or location
- **📅 Deadlines:** Track application deadlines

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
Morgan AI 2.5/
├── BackEnd/
│   ├── app/
│   │   ├── core_requirements.txt
│   │   ├── langchain_requirements.txt
│   │   ├── requirements.txt
│   │   ├── Docker.dockerfile
│   │   ├── main.py
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       ├── auth.py
│   │   │   │       ├── chat.py
│   │   │   │       ├── degree_works.py
│   │   │   │       ├── knowledge.py
│   │   │   │       ├── internships.py
│   │   │   │       ├── voice.py
│   │   │   │       └── admin.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── database.py
│   │   │   │   ├── security.py
│   │   │   │   └── dependencies.py
│   │   │   ├── models/
│   │   │   │   ├── user.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── degree_works.py
│   │   │   │   └── internship.py
│   │   │   ├── services/
│   │   │   │   ├── chat_service.py
│   │   │   │   ├── degree_works_parser.py
│   │   │   │   ├── knowledge_updater.py
│   │   │   │   ├── vector_store.py
│   │   │   │   └── openai_service.py
│   │   │   ├── utils/
│   │   │   │   ├── logger.py
│   │   │   │   └── validators.py
│   │   │   └── scripts/
│   │   │       ├── ingest_data.py
│   │   │       ├── simple_ingest.py
│   │   │       └── refresh_knowledge.py
│   │   └── data/
│   │       ├── knowledge_base/
│   │       ├── processed/
│   │       ├── threads/
│   │       ├── users/
│   │       └── internships_cache.json
│   └── uploads/
├── FrontEnd/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.js
│   ├── index.html
│   ├── App.css
│   ├── public/
│   │   ├── index.html
│   │   ├── index.css
│   │   ├── manifest.json
│   │   ├── favicon.ico
│   │   ├── apple-touch-icon.png
│   │   └── assets/
│   │       ├── morgan-logo/
│   │       └── audio/
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── components/
│       │   ├── Admin/
│       │   │   ├── AdminDashboard.jsx
│       │   │   └── UserManagement.jsx
│       │   ├── Auth/
│       │   │   ├── LoginModal.jsx
│       │   │   └── ProtectedRoute.jsx
│       │   ├── Calendar/
│       │   │   └── CalendarView.jsx
│       │   ├── Career/
│       │   │   ├── InternshipList.jsx
│       │   │   └── CareerResources.jsx
│       │   ├── Chart/
│       │   │   ├── ChatHistory.jsx
│       │   │   ├── SearchModal.jsx
│       │   │   └── QuickQuestions.jsx
│       │   ├── Chat/
│       │   │   ├── ChatWindow.jsx
│       │   │   ├── MessageList.jsx
│       │   │   ├── ChatInput.jsx
│       │   │   └── TypingIndicator.jsx
│       │   ├── DegreeWorks/
│       │   │   ├── DegreeWorksPage.jsx
│       │   │   ├── UploadModal.jsx
│       │   │   ├── TranscriptView.jsx
│       │   │   └── CourseTimeline.jsx
│       │   ├── Navigation/
│       │   │   ├── NavMenu.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   └── Header.jsx
│       │   └── UI/
│       │       ├── LoadingSpinner.jsx
│       │       ├── Modal.jsx
│       │       ├── Button.jsx
│       │       └── LogoModal.jsx
│       ├── context/
│       │   ├── AuthContext.jsx
│       │   ├── ChatContext.jsx
│       │   ├── VoiceContext.jsx
│       │   └── ThemeContext.jsx
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useChat.js
│       │   ├── useVoice.js
│       │   ├── useTheme.js
│       │   ├── useAdmin.js
│       │   └── useWebSocket.js
│       ├── services/
│       │   ├── api.js
│       │   ├── authService.js
│       │   ├── chatService.js
│       │   ├── degreeWorksService.js
│       │   ├── voiceService.js
│       │   ├── adminService.js
│       │   └── realtimeAPI.js
│       ├── styles/
│       │   ├── globals.css
│       │   ├── app.css
│       │   ├── auth.css
│       │   ├── chat.css
│       │   ├── navigation.css
│       │   ├── theme.css
│       │   ├── admin.css
│       │   └── index.css
│       └── utils/
│           ├── constants.js
│           ├── formatters.js
│           └── validators.js
├── Doc/
│   ├── FEATURE_SUMMARY.md
│   ├── UPDATE_SUMMARY_NOV_2025.md
│   ├── COMPLETE_SYSTEM_INTEGRATION.md
│   ├── CHAT_HISTORY_SYSTEM.md
│   ├── CHAT_HISTORY_ENHANCEMENTS.md
│   ├── CHAT_HISTORY_SEARCH_FEATURE.md
│   ├── COMPLETE_CHAT_HISTORY_SYSTEM.md
│   ├── DEGREE_WORKS_COMPLETE_GUIDE.md
│   ├── DEGREE_WORKS_FEATURE.md
│   ├── DEGREE_WORKS_AI_INTEGRATION.md
│   ├── DEGREE_WORKS_IMPLEMENTATION_STATUS.md
│   ├── AUTHENTICATION_SYSTEM.md
│   ├── AUTHENTICATION_IMPLEMENTATION_STATUS.md
│   ├── SOCIAL_LOGIN_FEATURE.md
│   ├── LOGOUT_LOGIN_BEHAVIOR.md
│   ├── LOGOUT_LOGIN_FLOW_DIAGRAM.md
│   ├── LOGOUT_LOGIN_QUICK_REFERENCE.md
│   ├── KNOWLEDGE_AUTO_UPDATE.md
│   ├── INTERNSHIP_AUTO_UPDATE_SYSTEM.md
│   ├── DATABASE_IMPLEMENTATION.md
│   ├── DATABASE_SUMMARY.md
│   ├── UI_UX_ENHANCEMENTS.md
│   ├── UI_UX_IMPLEMENTATION_SUMMARY.md
│   ├── UI_UX_QUICK_REFERENCE.md
│   ├── UI_UX_VISUAL_GUIDE.md
│   ├── NAVIGATION_AND_STORAGE_GUIDE.md
│   ├── QUICK_QUESTIONS_FEATURE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── IMPLEMENTATION_SUMMARY_NOV_22_2025.md
├── nginx/
│   └── nginx.conf
├── Test/
│   ├── test_auth.ps1
│   ├── test_degree_works_chatbot.ps1
│   └── test_web_fallback.ps1
├── docker-compose.yaml
├── package.json
├── README.md
└── .env (not in repo - create from template)
```

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Docker Issues

**Problem: Port already in use**
```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :8000
# macOS/Linux:
lsof -i :8000

# Kill the process
# Windows:
taskkill /PID <process_id> /F
# macOS/Linux:
kill -9 <process_id>
```

**Problem: Docker containers won't start**
```bash
# Check Docker Desktop is running
docker --version

# Clean rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

**Problem: "Cannot connect to Docker daemon"**
- Ensure Docker Desktop is running
- Windows: Check WSL 2 is enabled
- macOS: Grant Full Disk Access to Docker
- Restart Docker Desktop

#### Application Issues

**Problem: Backend API returns 500 errors**
```bash
# Check backend logs
docker-compose logs backend

# Common causes:
# - Missing OPENAI_API_KEY in .env
# - Invalid Pinecone credentials
# - Database connection failed

# Verify environment variables
docker exec morgan-chatbot-backend env | grep OPENAI
```

**Problem: Frontend shows blank page**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose restart frontend nginx

# Clear browser cache (Ctrl+Shift+Delete)
# Hard refresh (Ctrl+F5 or Cmd+Shift+R)
```

**Problem: Database connection errors**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check health
docker exec morgan-chatbot-postgres pg_isready -U morgan

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

**Problem: Chat messages not saving**
- Verify PostgreSQL container is healthy
- Check database connection in backend logs
- Ensure `DATABASE_URL` in `.env` is correct
- Restart backend: `docker-compose restart backend`

**Problem: AI responses timeout**
- Verify OpenAI API key is valid
- Check OpenAI account has credits
- Review backend logs for API errors
- Increase timeout in settings

#### Knowledge Base Issues

**Problem: Knowledge base not updating**
```bash
# Check watchdog is running
docker-compose logs backend | grep watchdog

# Trigger manual update
curl -X POST http://localhost:8000/api/knowledge/update

# Check permissions
docker exec morgan-chatbot-backend ls -la /app/data/knowledge_base
```

**Problem: Pinecone connection fails**
- Verify `PINECONE_API_KEY` is set correctly
- Check Pinecone index exists
- Ensure index name matches `.env` configuration
- Review API quota limits

#### Degree Works Issues

**Problem: PDF upload fails**
- File must be PDF format
- Maximum size: 10MB
- Ensure file is a Morgan State degree audit
- Check upload directory permissions

**Problem: Parsing errors**
- PDF must be text-based (not scanned image)
- Verify Morgan State format
- Check backend logs for specific errors

### Performance Issues

**Problem: Slow response times**
```bash
# Check container resources
docker stats

# Increase Docker Desktop memory allocation
# Settings > Resources > Memory (4GB+ recommended)

# Check network connectivity
ping 8.8.8.8
```

**Problem: High memory usage**
- Reduce `OPENAI_MAX_TOKENS` in `.env`
- Clear Redis cache: `docker-compose restart redis`
- Restart services: `docker-compose restart`

### Getting Help

**Check logs systematically:**
```bash
# Step 1: Check all service status
docker-compose ps

# Step 2: View backend logs
docker-compose logs backend --tail=50

# Step 3: View frontend logs
docker-compose logs frontend --tail=50

# Step 4: Check database
docker-compose logs postgres --tail=50
```

**Verify health endpoints:**
```bash
# Backend health
curl http://localhost:8000/health

# Frontend (should return HTML)
curl http://localhost

# Database
docker exec morgan-chatbot-postgres pg_isready
```

**Complete reset (last resort):**
```bash
# WARNING: This deletes all data
docker-compose down -v
docker system prune -a -f
rm -rf BackEnd/app/data/users/*
docker-compose up -d --build
```

### Platform-Specific Issues

**Windows:**
- Ensure WSL 2 is installed and updated
- Enable virtualization in BIOS
- Docker Desktop requires Windows 10/11 Pro or Enterprise

**macOS:**
- Grant Docker Desktop "Full Disk Access"
- On Apple Silicon, enable "Use Rosetta for x86 emulation"
- Check FileSharing settings in Docker preferences

**Linux:**
- Add user to docker group: `sudo usermod -aG docker $USER`
- Restart after group change: `newgrp docker`
- Check Docker daemon status: `systemctl status docker`

---

## 📝 License
MIT License - See LICENSE file for details

---

## 👥 Contributors
Morgan State University Computer Science Department
- Development Team: Senior Project 2025
- Faculty Advisor: [Faculty Name]
- Project Lead: [Student Name]

---

## 🏫 About Morgan State University
Morgan State University is a public research university in Baltimore, Maryland. The Computer Science Department is committed to providing excellent education and innovative AI solutions for students and faculty.

**Department Contact:**
- 📍 Science Complex, Room 325
- 📞 (443) 885-3130  
- 📧 cs@morgan.edu
- 🌐 [morgan.edu/computer-science](https://www.morgan.edu/computer-science)

---

## 🎯 Project Milestones

### **Version 2.5** (November 2025) - Current
- ✅ Chat History with PostgreSQL integration
- ✅ Degree Works feature with PDF parsing
- ✅ Knowledge base auto-update system
- ✅ Enhanced Quick Questions (28 questions)
- ✅ Career resources integration
- ✅ Complete Docker Compose setup
- ✅ Database administration interface

### **Version 2.0** (October 2025)
- ✅ Complete authentication system
- ✅ PostgreSQL and Redis integration
- ✅ Advanced navigation menu
- ✅ Voice features (TTS/STT)
- ✅ Admin dashboard
- ✅ Theme system

### **Version 1.5** (September 2025)
- ✅ Modern React frontend
- ✅ FastAPI backend
- ✅ Basic chat functionality
- ✅ OpenAI integration
- ✅ Morgan State branding

### **Future Roadmap**
- 🔄 Social login integration (Google, Microsoft)
- 🔄 Email verification system
- 🔄 Password reset functionality
- 🔄 Push notifications
- 🔄 Mobile app (React Native)
- 🔄 Analytics dashboard
- 🔄 Multi-language support
- 🔄 Advanced admin controls
- 🔄 Course registration integration
- 🔄 Academic advisor matching

---

## 📞 Support

### **For Students**
- 💬 Use the chatbot for academic questions
- 📧 Email: cs@morgan.edu for technical support
- 🏢 Visit: Science Complex, Room 325 during office hours

### **For Developers**
- 📚 Check documentation in `Doc/` folder
- 🐛 Report issues via project repository
- 💡 Suggest features through issue tracker
- 🤝 Contribute via pull requests

### **For Administrators**
- 🔧 Access admin dashboard at `/admin`
- 📊 Monitor system health at `/api/health`
- 📝 View logs with `docker-compose logs`
- 🗄️ Manage database at http://localhost:8080 (dev mode)

---

## 🔒 Security Considerations

### **Authentication**
- JWT tokens with 24-hour expiration
- Bcrypt password hashing
- Secure session management
- Role-based access control (RBAC)

### **Data Protection**
- User data isolated by user_id
- Soft delete for data recovery
- Encrypted API communications
- Environment variable protection

### **Best Practices**
- Never commit `.env` file
- Rotate JWT secret regularly
- Update dependencies monthly
- Monitor logs for suspicious activity
- Use HTTPS in production

---

## 🚀 Production Deployment

### **Recommended Setup**
1. **Use reverse proxy** (Nginx with SSL/TLS)
2. **Enable HTTPS** with Let's Encrypt certificates
3. **Set up domain** with proper DNS configuration
4. **Configure firewall** to allow only necessary ports
5. **Enable monitoring** with health checks
6. **Set up backups** for PostgreSQL data
7. **Use secrets management** (not environment files)
8. **Enable rate limiting** to prevent abuse
9. **Configure CORS** properly for frontend domain
10. **Set up logging** and alerting

### **Environment Configuration**
```powershell
# Production environment variables
NODE_ENV=production
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_SSL=true
REDIS_SSL=true
```

---

## 📈 Performance Metrics

### **Target Performance**
- **Page Load:** < 2 seconds
- **API Response:** < 500ms (average)
- **Chat Response:** < 3 seconds (with AI)
- **Search Results:** < 200ms
- **PDF Upload:** < 5 seconds
- **Knowledge Update:** < 30 seconds (incremental)

### **Scalability**
- **Concurrent Users:** 100+ supported
- **Database Size:** Scalable with PostgreSQL
- **Knowledge Base:** 10,000+ documents supported
- **Chat History:** Unlimited with pagination
- **File Uploads:** 10MB per file limit

---

**Last Updated:** November 24, 2025  
**Version:** 2.5  
**Status:** ✅ Production Ready

