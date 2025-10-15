Morgan AI 1.0
Project Description
Morgan AI 1.0 is a full-stack AI chatbot platform designed to provide intelligent, conversational support for academic and administrative use cases.
 It combines a FastAPI backend (Python) with a modern Vite + React frontend to deliver real-time chat, contextual knowledge retrieval, and personalized assistance.
The system integrates:
OpenAI GPT models for natural language understanding.


LangChain for contextual conversation management.


Pinecone for semantic search and vector database storage.


A responsive, user-friendly web interface built with React and Vite.



Features:
Frontend
Clean and responsive user interface (React + Vite)


Real-time chat interface with AI responses


Voice interaction and speech synthesis support


User authentication and session handling


Dynamic thread management for multi-session chat


Environment-based configuration via .env


 Backend
RESTful API powered by FastAPI


Modular route structure (chat, voice, admin)


Secure configuration management (app/core/security.py)


Knowledge base management from data/knowledge_base/


LangChain + Pinecone integration for vectorized knowledge retrieval


OpenAI API wrapper for custom prompt handling


Thread management system for persistent conversations


CORS middleware for safe frontend-backend communication



 Tech Stack
Layer
Technology
Frontend
React, Vite, Node.js, HTML5, CSS3
Backend
Python, FastAPI, Uvicorn
AI/ML Services
OpenAI API, LangChain
Vector Database
Pinecone
Containerization
Docker, Docker Compose
Version Control
Git & GitHub
Environment Management
.env configuration
Testing
Pytest / React Testing Library
Documentation
Markdown, /docs folder


