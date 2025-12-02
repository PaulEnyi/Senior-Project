# Installation Guide (BackEnd)

This guide helps students set up and run the BackEnd locally for development on Windows, macOS, or Linux. It also includes troubleshooting tips for common dependency issues.

## Recommended (Docker)
If you have Docker and Docker Compose installed, this is the simplest option and avoids local dependency issues:

```powershell
# From project root
docker compose up -d
# View backend logs
docker compose logs -f backend
```

The `docker-compose.yaml` configures PostgreSQL, Redis, backend, frontend and nginx for local development.

## Local Setup (Python virtualenv) — Windows (PowerShell)

1. Create and activate a venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Upgrade packaging tools and install requirements:

```powershell
pip install --upgrade pip setuptools wheel
pip install -r BackEnd/app/requirements.txt
```

3. Create a `.env` in the project root with required environment variables (example):

```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_env
SECRET_KEY=some_random_secret
ADMIN_PASSWORD=admin_password_here
# Optional (for local Docker DB):
DATABASE_URL=postgresql://morgan:morgan123@postgres:5432/morgan_chatbot
REDIS_URL=redis://redis:6379/0
```

4. Run the backend for development:

```powershell
cd BackEnd/app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Local Setup — macOS / Linux (bash or zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r BackEnd/app/requirements.txt
cd BackEnd/app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## If pip install fails (common fixes)
- Use a fresh virtualenv to avoid conflicts.
- If `psycopg2` fails to build on Windows, `psycopg2-binary` is already used in `requirements.txt` to avoid build tools; ensure you installed the right package.
- On Windows, install "Build Tools for Visual Studio" if compilation errors reference `cl.exe`.
- On macOS, you may need: `brew install openssl libpq` and then `export LDFLAGS`/`CPPFLAGS` accordingly before install.
- If `numpy` conflicts arise, use the pinned `numpy==1.26.4` in `requirements.txt` or install `temp_requirements_for_install.txt` instead:

```bash
pip install -r BackEnd/app/temp_requirements_for_install.txt
```

## Troubleshooting specific errors
- "ERROR: Could not build wheels for ..." : Install system build deps or use the `-binary` wheel package if available.
- OpenAI / Pinecone auth errors: ensure `OPENAI_API_KEY` and `PINECONE_API_KEY` are set.
- Watchdog permission errors: ensure Python can read the `BackEnd/app/data/knowledge_base` directory.

### Permission error when upgrading pip on Windows (WinError 5)
If you see an error like:

```
OSError: [WinError 5] Access is denied: '...\pip.exe'
```
This happens when pip tries to replace the running `pip.exe` while it is in use or when you lack permissions for the temporary uninstall/install location.

Workarounds:
- Re-run PowerShell as Administrator and retry the upgrade step:

```powershell
Start-Process powershell -Verb RunAs
# then inside elevated session
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r BackEnd/app/requirements.txt
```

- Skip the pip upgrade step (safer) and install directly (this is what I can re-run for you):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r BackEnd/app/requirements.txt
```

- Use an alternate temp dir that you control:

```powershell
#set TEMP to a folder you own
$env:TEMP = "$PWD\\pip_temp"
mkdir .\pip_temp
pip install -r BackEnd/app/requirements.txt
```

- If you prefer not to run an elevated shell, create the venv from an elevated prompt only for the pip upgrade step, or run the pip upgrade inside the venv after you deactivate other shells that may be using pip.

### macOS notes (expanded)
- Ensure Xcode command-line tools are installed:

```bash
xcode-select --install
```

- Install Homebrew packages required by some wheels:

```bash
brew install openssl libpq pkg-config
export LDFLAGS="-L$(brew --prefix openssl)/lib -L$(brew --prefix libpq)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include -I$(brew --prefix libpq)/include"
export PKG_CONFIG_PATH="$(brew --prefix openssl)/lib/pkgconfig:$(brew --prefix libpq)/lib/pkgconfig"
```

- If `psycopg2` still fails, prefer `psycopg2-binary` for local development as included here.

### Android (Termux) support — practical options and limitations
Running the full backend on Android is possible but commonly impractical due to heavy native wheels and system dependencies (numpy, lxml, cryptography). Recommended approaches:

1) Recommended: Use a remote development environment (Codespaces, GitHub VM, or a laptop) or Docker on a laptop/desktop. This is the most reliable approach for students.

2) Termux (advanced, best-effort): If you want to try on Android using Termux, here are steps and caveats:

```bash
# Install Termux from F-Droid or Termux app store
pkg update && pkg upgrade
pkg install python clang fftw libcrypt libffi openssl pkg-config build-essential
python -m pip install --upgrade pip setuptools wheel
# Create a venv and activate
python -m venv .venv
source .venv/bin/activate
# Then try installing (expect some packages to fail to build)
pip install -r BackEnd/app/temp_requirements_for_install.txt
```

Caveats:
- Many packages (numpy, orjson, pydantic-core, some binary wheels) may not have prebuilt wheels for Android/Termux and will attempt to compile — compilation may fail or be very slow.
- Pinecone, OpenAI, and external services will work if you have network access and API keys, but heavy ML/vector work is not practical on most phones.
- If Termux install fails, use a remote environment instead (GitHub Codespaces, a cloud VM, or your laptop).

3) Alternative lightweight approach on Android: Use a thin client (the frontend mobile browser or a PWA) that talks to a hosted backend (run on a cloud VM or laptop). This is the recommended production-like setup for mobile users.

## Re-running install safely (no pip upgrade)
If you'd like me to re-run the install but avoid the pip/setuptools upgrade step (to prevent WinError 5), run:

Windows (PowerShell):
```powershell
python -m venv .venv_test_install
.\.venv_test_install\Scripts\Activate.ps1
pip install -r BackEnd/app/requirements.txt
```

macOS / Linux:
```bash
python3 -m venv .venv_test_install
source .venv_test_install/bin/activate
pip install -r BackEnd/app/requirements.txt
```

---

## Quick test commands
- Health check (backend running): `curl http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

## Notes for Students
- Prefer Docker if available — it's reproducible and isolates dependencies.
- Keep your `.env` out of version control.
- If you need help, include the full pip output and OS details when opening an issue.

---

Last updated: November 24, 2025