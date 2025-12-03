# Morgan AI 2.5 — Windows Setup Guide

This guide covers installing and running the Morgan AI chatbot on Windows using Docker. It also includes a local (non-Docker) option for development.

## Prerequisites

- Windows 10/11 x64
- Admin rights to install software
- Docker Desktop for Windows (required)
- PowerShell (default shell)
- Optional: Python 3.11+, Node.js 18+ for local dev

## Install Docker Desktop

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and enable "Use WSL 2 based engine".
3. Reboot if prompted and start Docker Desktop.

## Clone the Repository

```pwsh
# Choose a folder and clone the project
git clone "<REPO_URL>" "MorganAI"
cd MorganAI/Morgan AI 2.5/Morgan AI 2.5
```

## Configure Environment Variables

Create a `.env` file in the project root (same folder as `docker-compose.yaml`). Minimal required variables:

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Pinecone (if using RAG)
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1-gcp
PINECONE_INDEX_NAME=morgan-chatbot

# App secrets
SECRET_KEY=change-this-secret
ADMIN_PASSWORD=change-this-admin

# Optional GroupMe integration
GROUPME_ACCESS_TOKEN=
GROUPME_BOT_ID=
GROUPME_GROUP_ID=
```

Note: Do not commit real keys; use environment injection.

## Start with Docker

```pwsh
# From the project root where docker-compose.yaml exists
docker-compose up -d
# Check status
docker ps
```

Services:
- Backend API: http://localhost:8000
- Frontend (Nginx): http://localhost

Restart containers:
```pwsh
docker-compose restart backend
```

Stop containers:
```pwsh
docker-compose down
```

## Local Dev (Optional)

### Backend
```pwsh
# Create venv
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r BackEnd/app/requirements.txt
# Run FastAPI (uvicorn)
uvicorn app.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```pwsh
# Node.js 18+
cd FrontEnd
npm install
npm run dev
```

## Health Checks

- Backend: http://localhost:8000/health
- Frontend: http://localhost

## Common Issues

- `GROUPME_BOT_ID` warning: Safe to ignore unless using GroupMe features.
- Docker not starting: Ensure WSL2 and virtualization are enabled.
- 5xx API errors: Verify `.env` keys and network connectivity.

## Updating

```pwsh
git pull
docker-compose up -d --build
```

## Uninstall

```pwsh
docker-compose down -v
# Optionally remove Docker images via Docker Desktop UI
```
