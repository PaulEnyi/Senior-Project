# Morgan AI 1.0 🤖

<div align="center">

![Morgan AI](https://img.shields.io/badge/Morgan-AI%201.0-blue?style=for-the-badge&logo=ai)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-orange?style=for-the-badge)

**Intelligent Chatbot Platform for Morgan State University Computer Science Students**



</div>

## 📖 Overview

Morgan AI 1.0 is an intelligent, full-stack chatbot platform designed to support Morgan State University Computer Science students throughout their academic journey. From freshman orientation to senior year capstone projects, Morgan AI provides personalized guidance and instant access to departmental resources.

> **Note**: Morgan AI complements academic advisors it doesn't replace them. Think of it as your 24/7 departmental assistant!

### 🎯 Purpose

- **Guidance**: Help students understand course requirements and academic pathways
- **Resources**: Connect students with clubs, facilities, and departmental services
- **Accessibility**: Provide instant answers to common questions anytime, anywhere
- **Engagement**: Enhance student experience through personalized academic support

## ✨ Features

### 🎨 Frontend
- **Modern Interface**: Clean, responsive React + Vite application
- **Real-time Chat**: Interactive AI conversation interface
- **Voice Integration**: Speech-to-text and text-to-speech capabilities
- **Multi-session Support**: Dynamic thread management for different conversations
- **User Authentication**: Secure session handling and user management

### ⚙️ Backend
- **RESTful API**: FastAPI-powered backend with comprehensive endpoints
- **Intelligent Retrieval**: LangChain + Pinecone for contextual knowledge search
- **Conversation Memory**: Persistent thread management system
- **Security First**: Secure configuration and CORS middleware
- **Modular Architecture**: Well-organized route structure (chat, voice, admin)

## 🛠 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React, Vite, Node.js, HTML5, CSS3 |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI/ML** | OpenAI API, LangChain |
| **Database** | Pinecone (Vector Database) |
| **Infrastructure** | Docker, Docker Compose |
| **Development** | Git, GitHub, Pytest, React Testing Library |

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/docs/overview))
- **Pinecone Account** (for vector database)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/morgan-state/morgan-ai.git
cd morgan-ai
```

#### 2. Environment Configuration

Create and configure these three `.env` files:

**Root Directory (.env)**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
```

**Backend Directory (Backend/.env)**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=sqlite:///./morgan_ai.db
SECRET_KEY=your-secret-key-here
```

**Frontend Directory (Frontend/.env)**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 3. Backend Setup

```bash
# Navigate to backend directory
cd BackEnd

# Create virtual environment (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python -m app.main
```

**Expected Output:**
```
2025-10-15 19:32:47,455 - app.main - INFO - ✓ Pinecone service initialized
2025-10-15 19:32:47,455 - app.main - INFO - ✓ All services initialized successfully
2025-10-15 19:32:47,458 - app.main - INFO - Morgan AI Chatbot started on 0.0.0.0:8000
INFO: Application startup complete.
```

#### 4. Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd FrontEnd

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
morgan-ai-frontend@1.0.0 dev
vite

VITE v7.1.7 ready in 410 ms

➜ Local:   http://localhost:5173/
➜ Network: http://10.253.45.244:5173/
➜ press h + enter to show help
```

#### 5. Access the Application

Open your browser and navigate to: **http://localhost:5173/**

## 📚 Usage Guide

### For Students

1. **Academic Planning**: Ask about course sequences, prerequisites, and graduation requirements
2. **Department Resources**: Locate labs, faculty offices, and study spaces
3. **Club Information**: Get details about ACM, NSBE, and other student organizations
4. **Career Guidance**: Learn about internships, research opportunities, and career paths

### Example Queries

- "What classes should I take as a freshman CS major?"
- "Where is the computer science department office?"
- "How do I join the programming team?"
- "What are the requirements for the AI concentration?"

## 🔧 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message and receive AI response |
| `POST` | `/api/chat/voice` | Voice interaction endpoint |
| `GET` | `/api/threads` | Retrieve user conversation threads |
| `POST` | `/api/threads` | Create new conversation thread |
| `GET` | `/api/admin/knowledge` | Knowledge base management |

### Example API Call

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "What CS courses are required for freshmen?",
        "thread_id": "user-123-session-1"
    }
)

print(response.json()["response"])
```

## 🗂 Project Structure

```
morgan-ai/
├── BackEnd/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/                # Security and configuration
│   │   ├── routes/              # API endpoints (chat, voice, admin)
│   │   └── services/            # Business logic and AI integration
│   ├── data/
│   │   └── knowledge_base/      # Departmental information files
│   └── requirements.txt
├── FrontEnd/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API service calls
│   │   └── styles/              # CSS and styling
│   └── package.json
└── docs/                        # Additional documentation
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Verify Python virtual environment is activated
   - Check all required packages are installed: `pip list`
   - Ensure OpenAI API key is correctly set in Backend/.env

2. **Frontend connection errors**
   - Confirm backend is running on port 8000
   - Check `VITE_API_BASE_URL` in Frontend/.env
   - Verify no CORS issues in browser console

3. **AI responses not working**
   - Validate OpenAI API key permissions
   - Check Pinecone vector database connection
   - Verify knowledge base files are properly formatted

### Getting Help

- Check the `/docs` folder for detailed documentation
- Review browser console for frontend errors
- Examine backend logs for API issues
- Contact the development team for persistent problems

## 🤝 Contributing

We welcome contributions from Morgan State University students and faculty! 

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Morgan State University Computer Science Department
- OpenAI for powerful language models
- The open-source community for amazing tools and libraries

---

<div align="center">

**Built with ❤️ for Morgan State University Computer Science Students**

*Empowering the next generation of tech leaders*

</div>
