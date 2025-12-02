# Internship Auto-Update System Documentation

## Overview
The Internship Auto-Update System provides automatic and continuous updates of internship data from multiple configured sources. The system ensures that students always see the latest available internship opportunities without manual intervention.

## Features Implemented

### 1. Multi-Source Data Collection
The system fetches internship data from multiple configured sources:
- **GroupMe API** - CS department messaging groups
- **Handshake API** - University career services platform
- **LinkedIn API** - Professional networking platform
- **Indeed API** - Job search platform
- **Glassdoor API** - Company reviews and jobs
- **Internal Database** - Manually curated opportunities

### 2. Automatic Update Triggers
Internships are automatically updated on:
- **Application Startup** - Initial data fetch when backend starts
- **User Login** - Fresh data on authentication
- **Dashboard/Page Load** - When internship section is accessed
- **Periodic Intervals** - Every 30 minutes (configurable)
- **Manual Refresh** - User-triggered immediate update

### 3. No Hard-Coded API Keys
All API credentials are read from environment variables:
```bash
# .env file configuration
GROUPME_ACCESS_TOKEN=your_groupme_token_here
GROUPME_GROUP_ID=your_group_id_here
HANDSHAKE_API_KEY=your_handshake_key_here
LINKEDIN_API_KEY=your_linkedin_key_here
INDEED_API_KEY=your_indeed_key_here
GLASSDOOR_API_KEY=your_glassdoor_key_here

# Update settings
INTERNSHIP_UPDATE_INTERVAL_MINUTES=30
INTERNSHIP_AUTO_UPDATE_ON_LOGIN=true
INTERNSHIP_AUTO_UPDATE_ON_REFRESH=true
```

## Architecture

### Backend Components

#### 1. InternshipUpdateService (`app/services/internship_update_service.py`)
Core service managing all update operations:

```python
class InternshipUpdateService:
    - update_internships(force=False)  # Main update function
    - get_internships(filters)         # Retrieve cached data
    - start_periodic_updates()         # Background task
    - _fetch_from_source(source)       # Fetch from specific API
    - _deduplicate_internships()       # Remove duplicates
```

**Key Features:**
- Async/await for non-blocking operations
- Parallel fetching from multiple sources
- Automatic deduplication by title + company
- Persistent caching to JSON file
- Update locking to prevent concurrent updates
- Configurable update intervals

#### 2. Updated API Endpoints (`app/api/routes/internship.py`)

**GET /api/internships/list**
- Returns paginated list of internships
- Supports filtering (type, location, company, search)
- Auto-triggers background update if configured
- Parameters:
  ```
  limit: int = 20
  offset: int = 0
  type: Optional[str] = None
  location: Optional[str] = None
  company: Optional[str] = None
  search: Optional[str] = None
  auto_update: bool = True
  ```

**POST /api/internships/refresh**
- Manually trigger background update
- Available to all authenticated users
- Returns source information

**POST /api/internships/update-now**
- Immediately update and wait for completion
- Returns update statistics
- Use for critical updates

**GET /api/internships/statistics**
- Current internship statistics
- Breakdown by type, location, source
- Last update timestamp

### Frontend Components

#### Updated InternshipsPage (`FrontEnd/src/components/Career/InternshipsPage.jsx`)

**New Features:**
- Fetches from API instead of hardcoded data
- Auto-updates on component mount
- Auto-updates on user login/logout
- Auto-refresh every 5 minutes
- Manual refresh button
- Loading states and spinners
- Last update timestamp display

**Key Functions:**
```javascript
fetchInternships(autoUpdate)  // Fetch from API
handleRefresh()                // Manual refresh
```

**State Management:**
```javascript
const [loading, setLoading] = useState(true);
const [lastUpdate, setLastUpdate] = useState(null);
const [isRefreshing, setIsRefreshing] = useState(false);
```

### Chatbot Integration

#### OpenAI Service Context Injection (`app/services/openai_service.py`)

Added `_get_internship_context()` method that:
- Retrieves latest 10 internships from cache
- Formats as structured text context
- Injects into chat completion request
- Enables AI to answer questions like:
  - "What internships are currently available for Morgan CS majors?"
  - "Tell me about the latest software engineering internships"
  - "Are there any remote internship opportunities?"

**Context Format:**
```
=== CURRENT INTERNSHIP OPPORTUNITIES FOR MORGAN CS MAJORS ===

1. Software Engineering Intern
   Company: Microsoft
   Location: Redmond, WA
   Type: Software Development
   Salary: $7,000/month
   Deadline: 2024-03-15
   Description: Work on cutting-edge cloud technologies...

2. Data Science Intern
   Company: Google
   ...

Total available internships: 45
Last updated: 2024-11-22T10:30:00
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Triggers Update                         │
│  (Login / Page Load / Manual Refresh / Periodic Timer)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            InternshipUpdateService.update_internships()          │
│  - Check if update needed (interval threshold)                   │
│  - Acquire update lock                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Parallel Fetch from All Sources                     │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐   │
│  │   GroupMe    │  Handshake   │   LinkedIn   │  Database  │   │
│  │  API Fetch   │  API Fetch   │  API Fetch   │   Query    │   │
│  └──────┬───────┴──────┬───────┴──────┬───────┴──────┬─────┘   │
└─────────┼──────────────┼──────────────┼──────────────┼─────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Aggregate All Results                           │
│  - Parse each source's format                                    │
│  - Normalize to common schema                                    │
│  - Deduplicate by title + company                                │
│  - Sort by posted date (newest first)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Update Cache                                  │
│  - internships_cache (in-memory list)                            │
│  - data/internships_cache.json (persistent file)                 │
│  - Set last_update timestamp                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Return Updated Data to Client                       │
│  - Frontend displays latest internships                          │
│  - Chatbot uses fresh context                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# Required for auto-update to work
GROUPME_ACCESS_TOKEN=<your_token>
GROUPME_GROUP_ID=<group_id>

# Optional data sources (enable as needed)
HANDSHAKE_API_KEY=<your_key>
LINKEDIN_API_KEY=<your_key>
INDEED_API_KEY=<your_key>
GLASSDOOR_API_KEY=<your_key>

# Update behavior
INTERNSHIP_UPDATE_INTERVAL_MINUTES=30  # How often to auto-update
INTERNSHIP_AUTO_UPDATE_ON_LOGIN=true   # Update when user logs in
INTERNSHIP_AUTO_UPDATE_ON_REFRESH=true # Update on page load
```

### Adding New Data Sources

To add a new internship data source:

1. **Add API key to config.py:**
```python
NEW_SOURCE_API_KEY: Optional[str] = Field(default=None, env="NEW_SOURCE_API_KEY")
```

2. **Register in InternshipUpdateService:**
```python
def _initialize_data_sources(self):
    if settings.NEW_SOURCE_API_KEY:
        sources['new_source'] = {
            'enabled': True,
            'api_key': settings.NEW_SOURCE_API_KEY,
            'base_url': 'https://api.newsource.com',
            'priority': 4
        }
```

3. **Implement fetch method:**
```python
async def _fetch_from_new_source(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    # API call implementation
    # Parse response to standard format
    # Return list of internship dicts
```

4. **Add to routing in _fetch_from_source():**
```python
elif source_name == 'new_source':
    return await self._fetch_from_new_source(config)
```

## Internship Data Schema

Standard format for all internships regardless of source:

```python
{
    "id": "string",              # Unique ID (source_id)
    "title": "string",           # Position title
    "company": "string",         # Company name
    "location": "string",        # Location (City, State or Remote)
    "type": "string",            # Category (Software Development, Data Science, etc.)
    "duration": "string",        # Length (e.g., "10-12 weeks")
    "salary": "string",          # Compensation
    "deadline": "string",        # Application deadline (ISO format)
    "posted_date": "string",     # When posted (ISO format)
    "description": "string",     # Full description
    "requirements": ["list"],    # Required qualifications
    "benefits": ["list"],        # Offered benefits
    "apply_url": "string",       # Application link
    "source": "string",          # Data source name
    "featured": boolean,         # Featured/sponsored listing
    "raw_message": "string"      # Original source data (optional)
}
```

## Cache Management

### In-Memory Cache
- Stored in `InternshipUpdateService.internships_cache`
- Fast access for API requests
- Lost on server restart

### Persistent Cache
- File: `data/internships_cache.json`
- Loaded on service initialization
- Saved after each update
- Survives restarts

### Cache Structure
```json
{
  "internships": [...],
  "last_update": "2024-11-22T10:30:00",
  "total_count": 45
}
```

## Update Logic

### Smart Update Throttling
```python
# Only update if:
# 1. Force update requested, OR
# 2. Last update was more than interval minutes ago

if not force and self.last_update:
    time_since_update = datetime.utcnow() - self.last_update
    if time_since_update < timedelta(minutes=self.update_interval_minutes):
        return {'status': 'skipped', 'reason': 'recently_updated'}
```

### Deduplication Algorithm
```python
def _deduplicate_internships(self, internships):
    seen = set()
    unique = []
    for internship in internships:
        # Create unique key from normalized title + company
        key = f"{internship['title'].lower()}_{internship['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique.append(internship)
    return unique
```

## Performance Considerations

### Parallel Fetching
- All sources fetched concurrently using `asyncio.gather()`
- Total fetch time = slowest source, not sum of all
- Typical update: 2-5 seconds for all sources

### Caching Strategy
- In-memory cache for instant API responses (<10ms)
- File cache for persistence across restarts
- Update in background without blocking requests

### Rate Limiting
- Respect API rate limits for each source
- Implement exponential backoff for errors
- Log warnings for failed sources, don't crash

## Monitoring & Logging

### Update Events
```python
logger.info(f"Fetched {len(result)} internships from {source_name}")
logger.info(f"Update complete: {len(unique_internships)} unique internships")
logger.warning(f"GroupMe API error: {response.status}")
logger.error(f"Error fetching from LinkedIn: {e}")
```

### Statistics Endpoint
GET `/api/internships/statistics` provides:
- Total internship count
- Breakdown by type/location/source
- Last update timestamp
- Currently updating status

## Chatbot Integration

### Context Injection
When user asks about internships, the AI receives:
1. **Knowledge Base Context** - General internship info
2. **Latest Internships Context** - Current opportunities (top 10)
3. **Student Context** - User's Degree Works (if available)

### Example Queries
✅ "What internships are currently available for Morgan CS majors?"
✅ "Tell me about software engineering internships"
✅ "Are there any remote internship opportunities?"
✅ "What companies are hiring interns right now?"
✅ "Show me internships with high salaries"

### Response Quality
AI can provide:
- Specific company names and positions
- Current deadlines
- Salary information
- Location details
- Direct application links

## Frontend User Experience

### Loading States
- Spinner while fetching initial data
- Refresh button shows "Refreshing..." state
- Smooth transitions with Framer Motion

### Auto-Update Feedback
- Last update timestamp displayed
- Total count of available positions
- Visual indicator when updating

### Manual Refresh
- Prominent refresh button in header
- Immediate feedback on click
- Data refreshes without page reload

## Troubleshooting

### No Internships Showing
1. Check API keys in `.env` file
2. Verify backend logs for fetch errors
3. Check network connectivity
4. Ensure at least one data source is configured

### Updates Not Working
1. Check `INTERNSHIP_AUTO_UPDATE_ON_REFRESH` setting
2. Verify update interval hasn't expired
3. Check backend logs for update service errors
4. Ensure data sources are configured correctly

### Chatbot Not Using Latest Data
1. Verify internship context is being injected (check logs)
2. Ensure cache has data (`internships_cache` not empty)
3. Check AI system prompt includes internship instructions

### Duplicate Internships
1. Deduplication uses title + company
2. Different sources may list same opportunity with slight variations
3. Adjust `_deduplicate_internships()` logic if needed

## Future Enhancements

### Database Integration
- Migrate from in-memory/file cache to PostgreSQL
- Store full internship history
- Enable analytics and trending

### Advanced Parsing
- Use NLP to extract structured data from unstructured messages
- Implement machine learning for better categorization
- Auto-detect location, salary, deadline from text

### User Preferences
- Save favorite internships
- Get notifications for new matching opportunities
- Personalized recommendations based on major/interests

### Analytics
- Track application rates
- Most popular companies/positions
- Deadline reminders

## Security Considerations

✅ API keys read from environment variables only
✅ Never commit credentials to git
✅ User authentication required for all endpoints
✅ Rate limiting prevents abuse
✅ Input validation on all filters
✅ CORS configured for allowed origins

## Testing

### Manual Testing
```bash
# Check health
curl http://localhost:8000/health

# Get internships (requires auth)
curl http://localhost:8000/api/internships/list \
  -H "Authorization: Bearer YOUR_TOKEN"

# Trigger update
curl -X POST http://localhost:8000/api/internships/update-now \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl http://localhost:8000/api/internships/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Unit Testing
```python
# Test deduplication
def test_deduplicate():
    service = InternshipUpdateService()
    duplicates = [
        {'title': 'SWE Intern', 'company': 'Google'},
        {'title': 'swe intern', 'company': 'google'},  # Duplicate
    ]
    unique = service._deduplicate_internships(duplicates)
    assert len(unique) == 1
```

## Deployment Checklist

- [ ] Configure all API keys in production `.env`
- [ ] Set `INTERNSHIP_UPDATE_INTERVAL_MINUTES` appropriately
- [ ] Enable desired data sources
- [ ] Test update triggers (login, refresh, periodic)
- [ ] Verify chatbot receives internship context
- [ ] Check frontend displays updated data
- [ ] Monitor backend logs for errors
- [ ] Set up alerts for failed updates
- [ ] Document API rate limits
- [ ] Configure backup/restore for cache file

## Support

For issues or questions:
- Backend logs: `docker logs morgan-chatbot-backend`
- Frontend console: Browser DevTools
- API docs: `http://localhost:8000/docs`
- Contact: Morgan CS Department IT Support

## Version History

- **v1.0.0** (Nov 2024): Initial implementation
  - Multi-source data fetching
  - Auto-update on login/refresh/periodic
  - Chatbot integration
  - Frontend integration
  - No hard-coded API keys
