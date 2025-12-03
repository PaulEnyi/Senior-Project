# Knowledge Base Auto-Update System

## Overview

The Morgan AI chatbot now includes an intelligent knowledge base update system that automatically keeps information current without manual intervention. The system includes file monitoring, incremental updates, and smart change detection.

## Features

### 1. **Automatic File Monitoring**
- Real-time detection of changes to knowledge base files
- Watches for new, modified, or deleted files
- Debounced updates to avoid excessive processing

### 2. **Incremental Updates**
- Only processes files that have changed
- Uses MD5 hash tracking to detect modifications
- Significantly faster than full re-ingestion
- Maintains file hash history in `BackEnd/app/data/processed/file_hashes.json`

### 3. **Scheduled Updates**
- Configurable periodic refresh (default: every 24 hours)
- Runs in background without blocking the API
- Automatic detection and processing of changed files

### 4. **REST API Endpoints**
All knowledge base management endpoints require admin privileges and are available at `/api/knowledge/`:

#### `GET /api/knowledge/status`
Get current knowledge base status including:
- Update service status
- Last update time
- Vector database statistics
- Number of tracked files

**Response:**
```json
{
  "status": "active",
  "update_service": {
    "update_in_progress": false,
    "last_update_time": "2025-11-22T10:30:00",
    "tracked_files": 42,
    "pending_files": 0
  },
  "vector_database": {
    "total_vectors": 1523,
    "index_fullness": 0.15,
    "dimension": 1536
  },
  "timestamp": "2025-11-22T10:35:00"
}
```

#### `POST /api/knowledge/update`
Trigger a knowledge base update (admin only)

**Request:**
```json
{
  "mode": "incremental",  // or "full"
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Incremental knowledge base update initiated",
  "mode": "incremental",
  "initiated_at": "2025-11-22T10:35:00",
  "initiated_by": "admin@morgan.edu"
}
```

#### `POST /api/knowledge/detect-changes`
Detect files that have changed (admin only)

**Response:**
```json
{
  "success": true,
  "changed_files": [
    "courses.json",
    "deadlines.json"
  ],
  "total_changes": 2,
  "checked_at": "2025-11-22T10:35:00"
}
```

#### `POST /api/knowledge/schedule`
Schedule periodic automatic updates (admin only)

**Request:**
```json
{
  "interval_hours": 24
}
```

#### `GET /api/knowledge/history`
Get recent update history

**Query Parameters:**
- `limit`: Number of recent updates to retrieve (default: 10)

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "timestamp": "2025-11-22T09:00:00",
      "success": true,
      "files_processed": 5,
      "vectors_stored": 287,
      "duration_seconds": 45.3
    }
  ],
  "total_entries": 1
}
```

#### `POST /api/knowledge/start-file-watcher`
Start real-time file monitoring (admin only)

## Command Line Usage

### Full Refresh
Complete re-ingestion of all knowledge base files:
```bash
python -m app.scripts.refresh_knowledge --mode full
```

### Incremental Update
Update only changed files:
```bash
python -m app.scripts.refresh_knowledge --mode incremental
```

### Update Specific File
```bash
python -m app.scripts.refresh_knowledge --mode incremental --document "path/to/file.json"
```

### Auto-Update Mode
Start continuous monitoring with periodic updates:
```bash
python -m app.scripts.refresh_knowledge --mode auto --interval 24
```

This will:
- Start file system watcher for real-time updates
- Run periodic checks every 24 hours
- Automatically process changed files

## How It Works

### File Change Detection
1. System maintains MD5 hashes of all knowledge base files
2. Periodically compares current hashes with stored hashes
3. Identifies new, modified, or deleted files
4. Triggers incremental update for changed files only

### Incremental Update Process
1. Load only the changed files
2. Process files into documents using appropriate parsers
3. Delete old vectors for those documents from Pinecone
4. Generate new embeddings and store updated vectors
5. Update file hash registry

### File Monitoring
- Uses `watchdog` library for real-time file system events
- Debounces rapid changes (5-second delay)
- Automatically triggers incremental updates
- Batches multiple file changes together

## Integration with Docker

The knowledge update system is designed to work within the Docker environment. To run periodic updates in production:

1. **Via API** (Recommended):
   - Use the `/api/knowledge/schedule` endpoint to start periodic updates
   - Use the `/api/knowledge/start-file-watcher` endpoint for real-time monitoring

2. **Via Docker Exec**:
   ```bash
   docker exec -it morgan-chatbot-backend python -m app.scripts.refresh_knowledge --mode auto --interval 24
   ```

## Configuration

Key settings in `app/core/config.py`:
- `KNOWLEDGE_BASE_DIR`: Directory containing knowledge files
- `PROCESSED_DIR`: Directory for logs and hash tracking
- `PINECONE_API_KEY`: Pinecone API credentials
- `OPENAI_API_KEY`: OpenAI API credentials

## Performance Considerations

### Incremental vs Full Updates
- **Incremental**: Typically 10-100x faster
- **Full**: Ensures complete consistency, use when:
  - Major structural changes
  - Suspected data corruption
  - Initial setup

### Resource Usage
- File watching: Minimal CPU/memory overhead
- Incremental update: Scales with number of changed files
- Full update: May take several minutes for large knowledge bases

## Monitoring & Logging

All update operations are logged to:
- Application logs: Real-time console output
- Update history: `BackEnd/app/data/processed/ingestion_log_*.json`
- File hashes: `BackEnd/app/data/processed/file_hashes.json`

View logs via Docker:
```bash
docker logs morgan-chatbot-backend -f
```

## Troubleshooting

### Update Stuck/Not Responding
```bash
# Check status
curl -X GET http://localhost:8000/api/knowledge/status

# Force new update
curl -X POST http://localhost:8000/api/knowledge/update \
  -H "Content-Type: application/json" \
  -d '{"mode": "incremental", "force": true}'
```

### Files Not Updating
1. Verify file is in knowledge base directory
2. Check file permissions
3. Review logs for errors
4. Try manual update via API

### Hash File Corruption
Delete hash file to rebuild:
```bash
docker exec -it morgan-chatbot-backend rm /app/data/processed/file_hashes.json
# Next update will rebuild hashes
```

## Enhanced Quick Questions

The quick questions feature has been expanded with social and community-focused questions relevant to CS majors:

### New Categories
1. **Student Organizations & Community**
   - Joining student orgs (WiCS, GDSC)
   - Hackathon participation
   - Networking events
   - Code competitions
   - Collaboration opportunities

2. **Social & Events**
   - Tech talks and guest speakers
   - Study sessions and workshops
   - Finding project partners
   - Peer programming sessions

### Frontend Updates
The QuickQuestions component now displays 12 questions (up from 8) covering:
- Traditional academic topics
- Career resources
- Community engagement
- Social events
- Study groups
- Project collaboration

All questions are categorized and color-coded for easy navigation.

## API Usage Examples

### Check Update Status
```javascript
const response = await fetch('http://localhost:8000/api/knowledge/status', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const status = await response.json();
console.log(`Last update: ${status.update_service.last_update_time}`);
```

### Trigger Update
```javascript
const response = await fetch('http://localhost:8000/api/knowledge/update', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    mode: 'incremental',
    force: false
  })
});
```

### View Update History
```javascript
const response = await fetch('http://localhost:8000/api/knowledge/history?limit=5', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const history = await response.json();
```

## Future Enhancements

Potential improvements:
- Web scraping for automatic data collection from university websites
- Integration with course catalog APIs
- Automated deadlines sync with academic calendar
- Slack/Teams notifications for update completion
- Admin dashboard for knowledge base management
