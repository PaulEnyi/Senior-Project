Overview

Morgan AI is an intelligent chatbot designed to assist students, faculty, and staff with information about the Morgan State University Computer Science Department. Built with FastAPI (backend) and React (frontend), it uses OpenAI's GPT models and Pinecone vector database for accurate, context-aware responses.

Features

AI-Powered Responses - Natural language understanding using OpenAI GPT
RAG Architecture - Retrieval-Augmented Generation with Pinecone vector database
Voice Input/Output - Speech recognition and text-to-speech capabilities
Conversation History - Thread-based chat management
Admin Panel - Knowledge base management and system monitoring
Responsive Design - Works on desktop, tablet, and mobile devices
Real-time Updates - Fast, interactive user experience

TO RUN IT

Step 1: Start Backend Server
Open PowerShell:


# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Initialize Pinecone (first time only)
python scripts\setup_pinecone.py

# Ingest knowledge base (first time only)
python scripts\ingest_data.py

# Start backend
python -m app.main


Step 2: Start Frontend (New Terminal)
Open a new PowerShell window:

# Start frontend
npm run dev

