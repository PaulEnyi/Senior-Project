Morgan AI 1.0

Project Description:

Morgan AI 1.0 is an intelligent, full-stack chatbot platform designed to assist Morgan State University students, particularly those majoring in Computer Science. Its purpose is to support students from freshman to senior year by providing guidance and information about the Computer Science department and related resources.
This AI system is not intended to replace academic advisors, but rather to complement their efforts, especially for new students who may need help understanding which classes to take, how to join clubs, or where department facilities are located. Morgan AI 1.0 integrates a FastAPI backend (Python) with a modern Vite + React frontend, enabling real-time chat, contextual knowledge retrieval, and personalized academic assistance. The platform is built to enhance student engagement and streamline access to departmental information and support.


The system integrates:

1.OpenAI GPT models for natural language understanding.

2.LangChain for contextual conversation management.

3.Pinecone for semantic search and vector database storage.

4.A responsive, user-friendly web interface built with React and Vite.


Features: 

Frontend

1.Clean and responsive user interface (React + Vite)

2.Real-time chat interface with AI responses

3.Voice interaction and speech synthesis support

4.User authentication and session handling

5.Dynamic thread management for multi-session chat

6.Environment-based configuration via .env



Backend

1.RESTful API powered by FastAPI

2.Modular route structure (chat, voice, admin)

3.Secure configuration management (app/core/security.py)

4.Knowledge base management from data/knowledge_base/

5.LangChain + Pinecone integration for vectorized knowledge retrieval

6.OpenAI API wrapper for custom prompt handling

7.Thread management system for persistent conversations

8.CORS middleware for safe frontend-backend communication


Tech Stack

| Layer                      | Technology                        |
| -------------------------- | --------------------------------- |
| **Frontend**               | React, Vite, Node.js, HTML5, CSS3 |
| **Backend**                | Python, FastAPI, Uvicorn          |
| **AI/ML Services**         | OpenAI API, LangChain             |
| **Vector Database**        | Pinecone                          |
| **Containerization**       | Docker, Docker Compose            |
| **Version Control**        | Git & GitHub                      |
| **Environment Management** | `.env` configuration              |
| **Testing**                | Pytest / React Testing Library    |
| **Documentation**          | Markdown, `/docs` folder          |

Steps to Start the Project

1. Configure Environment Files

Before starting, ensure that you have three .env files:

a.One in the Backend directory
b.One in the Frontend directory
c.One in the Main (Root) directory

Each .env file must include your OpenAI API key.

Locate the placeholder that says:
sk-YourOpenAIApiKeyHere

Remove it and replace it with your own API key, which you can obtain from:

https://platform.openai.com/docs/overview

Once you’ve added your API key to each .env file, you’re ready for the next step.

Start the Backend Server

Open your Windows Terminal or Visual Studio Code Terminal, then navigate to the backend directory:
cd BackEnd
.\venv\Scripts\Activate.ps1
python -m app.main

If the backend runs successfully, you should see messages similar to the following:
2025-10-15 19:32:47,455 - app.main - INFO - ✓ Pinecone service initialized
2025-10-15 19:32:47,455 - app.main - INFO - ✓ All services initialized successfully
2025-10-15 19:32:47,458 - app.main - INFO - Morgan AI Chatbot started successfully on 0.0.0.0:8000
INFO:     Application startup complete.

This indicates that your backend server has started correctly.

Start the Frontend Server

Next, open a new terminal window and navigate to the frontend directory:
cd FrontEnd
npm run dev

When the frontend starts successfully, you’ll see output like this:
morgan-ai-frontend@1.0.0 dev
> vite

VITE v7.1.7  ready in 410 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://10.253.45.244:5173/
  ➜  press h + enter to show help

This means your frontend is now running locally.

Access the Application

Once both the backend and frontend servers are running, open the provided local URL (e.g., http://localhost:5173/) in your web browser.
Your Morgan AI Chatbot platform should now be live and ready to use.
