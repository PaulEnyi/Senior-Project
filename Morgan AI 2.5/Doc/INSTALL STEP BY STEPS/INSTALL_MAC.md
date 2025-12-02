# Morgan AI 2.5 — macOS Setup Guide

Setup and run the Morgan AI chatbot on macOS (Intel or Apple Silicon) using Docker Desktop. Includes optional local dev instructions.

## Prerequisites

- macOS 13+ (Ventura or later recommended)
- Admin rights
- Docker Desktop for Mac
- Terminal (zsh)
- Optional: Homebrew, Python 3.11+, Node.js 18+

## Install Docker Desktop

1. Download: https://www.docker.com/products/docker-desktop
2. Install and grant necessary permissions.
3. Start Docker Desktop.

## Clone the Repository

```bash
# Choose a folder and clone
git clone <REPO_URL> MorganAI
cd "Morgan AI 2.5/Morgan AI 2.5"
```

## Configure Environment Variables

Create `.env` in project root (beside `docker-compose.yaml`):

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1-gcp
PINECONE_INDEX_NAME=morgan-chatbot

SECRET_KEY=change-this-secret
ADMIN_PASSWORD=change-this-admin

GROUPME_ACCESS_TOKEN=
GROUPME_BOT_ID=
GROUPME_GROUP_ID=
```

## Start with Docker

```bash
docker-compose up -d
docker ps
```

Services:
- Backend API: http://localhost:8000
- Frontend: http://localhost

Restart containers:
```bash
docker-compose restart backend
```

Stop containers:
```bash
docker-compose down
```

## Optional: Local Development

### Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r BackEnd/app/requirements.txt
uvicorn app.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd FrontEnd
npm install
npm run dev
```

## Health Checks

- Backend: http://localhost:8000/health
- Frontend: http://localhost

## Troubleshooting

- Permissions: If Docker bind mounts fail, grant Full Disk Access to Docker.
- SSL/Network: Corporate proxies may require Docker proxy configuration.
- Missing keys: Ensure `.env` has valid OpenAI and Pinecone keys.

## Update

```bash
git pull
docker-compose up -d --build
```

## Uninstall

```bash
docker-compose down -v
# Remove Docker images via UI if desired
```
