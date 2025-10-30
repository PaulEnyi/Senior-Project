FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN mkdir -p /app/app
RUN if [ -f main.py ]; then mv main.py app/main.py; fi

# Create necessary directories
RUN mkdir -p /app/data/knowledge_base /app/data/processed

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application (production - no reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]