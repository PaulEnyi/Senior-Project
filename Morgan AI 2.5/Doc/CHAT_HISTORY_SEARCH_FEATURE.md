# Chat History & Search Feature

## Overview
The Chat History & Search feature provides users with the ability to view, search, and manage their past conversations with Morgan AI. This feature includes automatic session persistence, search functionality across all chat history, and seamless navigation between current and past conversations.

## Features

### 1. **Chat History Page** (`/chat-history`)
- **View All Conversations**: Display all saved chat sessions with titles, dates, and message counts
- **Time-Based Display**: Shows relative time (e.g., "2h ago", "3d ago") with fallback to full date
- **Session Preview**: Each session card shows the chat title and metadata
- **Delete Sessions**: Remove unwanted chat sessions with confirmation
- **Click to Load**: Open any chat session by clicking on its card

### 2. **Search Functionality**
Available in two locations:

#### A. Chat History Page Search
- **Real-time Search**: Search across all chat sessions as you type
- **Content Matching**: Searches both chat titles and message content
- **Grouped Results**: Results are grouped by chat session with match highlights
- **Match Preview**: Shows up to 3 matching messages per thread
- **Direct Navigation**: Click search results to open that specific chat

#### B. In-Chat Search Modal
- **Quick Access**: Search icon button next to Quick Questions
- **Modal Interface**: Clean, focused search experience
- **Same Search Power**: Uses same backend search API
- **Load Results**: Click any result to load that conversation

### 3. **Session Persistence**
- **Automatic Saving**: Every conversation is automatically saved to a thread
- **Thread Management**: Backend ThreadManager handles all storage
- **Title Generation**: First message becomes the chat title
- **Message History**: Complete conversation history maintained
- **Resume Conversations**: Pick up where you left off

## User Interface Components

### Navigation Menu Icon
```jsx
{ path: '/chat-history', label: 'Chat History', icon: FiClock, color: '#10B981' }
```
- **Location**: Navigation sidebar, positioned after "Chat" icon
- **Icon**: FiClock (clock icon) in green (#10B981)
- **Route**: `/chat-history`

### Chat History Page Layout
```
┌─────────────────────────────────────────┐
│ 🕐 Chat History                         │
│ View and search your previous...       │
│                                         │
│ 🔍 [Search messages, titles, dates...] │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 💬 How do I register for classes?   │ │
│ │ 📅 2h ago • 12 messages       🗑️   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 💬 What internships are available?  │ │
│ │ 📅 1d ago • 8 messages        🗑️   │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Search Modal in Chat
```
┌─────────────────────────────────────────┐
│ 🔍 Search Chat History            ✖️   │
├─────────────────────────────────────────┤
│                                         │
│ Search by title or content              │
│ 🔍 [Type to search...]                  │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Untitled Chat                       │ │
│ │ You: How do I register for...       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Career Advice                       │ │
│ │ Morgan AI: I recommend checking...  │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Backend Architecture

### ThreadManager Service
**Location**: `BackEnd/app/app/services/thread_manager.py`

**Key Methods**:
```python
class ThreadManager:
    async def create_thread(user_id, thread_id=None, metadata=None)
    async def get_thread(thread_id)
    async def get_user_threads(user_id, limit=20, offset=0)
    async def add_message(thread_id, message)
    async def get_messages(thread_id, limit=None, before=None, after=None)
    async def delete_thread(thread_id)
    async def search_user_chats(user_id, query, limit=20)
```

### API Endpoints
**Location**: `BackEnd/app/app/api/routes/chat.py`

#### 1. **Get User Threads**
```http
GET /api/chat/threads
Authorization: Bearer <token>
Query Parameters:
  - limit: int (default: 20)
  - offset: int (default: 0)

Response:
{
  "threads": [
    {
      "thread_id": "uuid",
      "user_id": "uuid",
      "title": "Chat title",
      "created_at": "ISO timestamp",
      "updated_at": "ISO timestamp",
      "message_count": 12,
      "is_active": true
    }
  ],
  "total": 5
}
```

#### 2. **Get Thread Messages**
```http
GET /api/chat/threads/{thread_id}
Authorization: Bearer <token>
Query Parameters:
  - limit: int (default: 50)

Response:
{
  "thread_id": "uuid",
  "messages": [
    {
      "message_id": "uuid",
      "role": "user" | "assistant",
      "content": "Message text",
      "timestamp": "ISO timestamp"
    }
  ],
  "total": 12
}
```

#### 3. **Search Chat History**
```http
GET /api/chat/search
Authorization: Bearer <token>
Query Parameters:
  - query: string (required)
  - limit: int (default: 20)

Response:
{
  "results": [
    {
      "thread_id": "uuid",
      "message_id": "uuid",
      "content": "Message content",
      "role": "user" | "assistant",
      "timestamp": "ISO timestamp",
      "thread_title": "Chat title"
    }
  ],
  "total": 8
}
```

#### 4. **Delete Thread**
```http
DELETE /api/chat/threads/{thread_id}
Authorization: Bearer <token>

Response:
{
  "message": "Thread deleted successfully"
}
```

#### 5. **Send Message (with thread_id)**
```http
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "message": "User message",
  "user_id": "uuid",
  "thread_id": "uuid (optional)"
}

Response:
{
  "thread_id": "uuid",
  "message": "AI response",
  "sources": [],
  "timestamp": "ISO timestamp",
  "metadata": {}
}
```

## Frontend Implementation

### Files Modified/Created

#### 1. **NavMenu.jsx** (Modified)
```jsx
// Added import
import { FiClock } from 'react-icons/fi';

// Added navigation item
{ path: '/chat-history', label: 'Chat History', icon: FiClock, color: '#10B981' }
```

#### 2. **ChatHistory.jsx** (New Component)
**Location**: `FrontEnd/src/components/Chat/ChatHistory.jsx`

**Features**:
- Fetches all user threads on mount
- Real-time search with debouncing
- Delete confirmation dialogs
- Navigate to chat with thread context
- Loading and error states
- Empty state with call-to-action

**Key Functions**:
```jsx
const fetchThreads = async () => { ... }
const handleSearchChat = async (query) => { ... }
const handleDeleteThread = async (threadId, e) => { ... }
const handleOpenThread = (threadId) => { 
  navigate('/', { state: { threadId } });
}
```

#### 3. **ChatWindow.jsx** (Modified)
**Location**: `FrontEnd/src/components/Chat/ChatWindow.jsx`

**New State**:
```jsx
const [showSearchModal, setShowSearchModal] = useState(false);
const [searchQuery, setSearchQuery] = useState('');
const [searchResults, setSearchResults] = useState([]);
const [isSearching, setIsSearching] = useState(false);
const [threadId, setThreadId] = useState(null);
```

**New Functions**:
```jsx
const loadThread = async (id) => { ... }
const handleSearchChat = async (query) => { ... }
const handleOpenSearchResult = (resultThreadId) => { ... }
```

**Modified**:
- `handleSendMessage`: Now includes `thread_id` in request
- Added `useEffect` to load thread from navigation state
- Added search button in input actions
- Added search modal with AnimatePresence

#### 4. **App.jsx** (Modified)
```jsx
// Added import
import ChatHistory from './components/Chat/ChatHistory';

// Added route
<Route path="/chat-history" element={<ChatHistory user={user} />} />
```

#### 5. **chat.css** (Modified)
**Location**: `FrontEnd/src/styles/chat.css`

**New Styles Added**:
- `.chat-history-page` - Main page container
- `.header-title-section` - Page header
- `.search-bar-container` - Search input wrapper
- `.threads-list` - Thread cards grid
- `.thread-card` - Individual thread card
- `.search-results-list` - Search results grid
- `.search-result-card` - Search result card
- `.search-modal-overlay` - Modal backdrop
- `.search-modal` - Modal container
- `.search-chat-icon-btn` - Search button styling
- Loading, error, and empty states

## User Workflows

### Workflow 1: View Chat History
1. User clicks "Chat History" icon in navigation menu
2. System navigates to `/chat-history`
3. ChatHistory component fetches user's threads
4. Displays all threads sorted by most recent
5. User can click any thread to load it in chat window

### Workflow 2: Search from History Page
1. User types in search bar on Chat History page
2. System performs real-time search as user types
3. Results are grouped by thread with match previews
4. User clicks a result
5. System navigates to chat and loads that thread

### Workflow 3: Search from Chat Window
1. User clicks search icon (🔍) next to Quick Questions
2. Search modal opens
3. User types search query
4. Results appear in modal
5. User clicks a result
6. Modal closes and thread loads in current chat

### Workflow 4: Delete Chat Session
1. User navigates to Chat History page
2. Hovers over a thread card
3. Clicks delete button (🗑️)
4. Confirmation dialog appears
5. User confirms deletion
6. Thread is removed from list and database

### Workflow 5: Continue Previous Conversation
1. User opens Chat History
2. Clicks on a previous conversation
3. System loads all messages from that thread
4. User can continue chatting in same thread
5. New messages are added to existing conversation

## Data Models

### ChatThread Model
```python
class ChatThread(BaseModel):
    thread_id: str
    user_id: str
    title: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    message_count: int = 0
    metadata: Optional[Dict[str, Any]]
    is_active: bool = True
```

### ChatMessage Model
```python
class ChatMessage(BaseModel):
    message_id: Optional[str]
    role: MessageRole  # "user" | "assistant" | "system"
    content: str
    timestamp: Optional[datetime]
    user_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

## Storage

### In-Memory Storage (Current Implementation)
```python
class ThreadManager:
    self.threads: Dict[str, ChatThread] = {}
    self.messages: Dict[str, List[ChatMessage]] = defaultdict(list)
    self.user_threads: Dict[str, List[str]] = defaultdict(list)
```

**Note**: Current implementation uses in-memory storage. For production, this should be replaced with:
- PostgreSQL for thread metadata
- PostgreSQL or MongoDB for messages
- Redis for caching recent conversations

## Search Algorithm

### Search Process
1. **Input**: User's search query string
2. **Query Normalization**: Convert to lowercase
3. **Thread Iteration**: Loop through user's threads
4. **Message Scanning**: Check each message's content
5. **Match Detection**: Case-insensitive substring matching
6. **Result Building**: Create result objects with context
7. **Limit Application**: Return up to `limit` results

### Search Matching
```python
# Simple substring matching
if query_lower in message.content.lower():
    results.append({
        "thread_id": thread_id,
        "message_id": message.message_id,
        "content": message.content,
        "role": message.role,
        "timestamp": message.timestamp,
        "thread_title": thread.title
    })
```

**Future Enhancements**:
- Fuzzy matching
- Relevance scoring
- Date range filtering
- Role filtering (user/assistant)
- Regex support
- Semantic search using embeddings

## Security & Access Control

### Authentication
- All endpoints require valid JWT token
- Token passed in `Authorization: Bearer <token>` header
- Expired tokens return 401 Unauthorized

### Authorization
- Users can only access their own threads
- Thread ownership verified in all operations
- 404 returned for unauthorized access attempts

### Thread Verification Example
```python
thread = await thread_manager.get_thread(thread_id)
if not thread or thread.user_id != current_user["user_id"]:
    raise HTTPException(status_code=404, detail="Thread not found")
```

## Performance Considerations

### Current Limitations
- In-memory storage limits scalability
- No pagination on search results
- No caching layer
- Full scan for searches

### Recommended Optimizations
1. **Database Migration**: Move to PostgreSQL/MongoDB
2. **Indexing**: Add indexes on `user_id`, `created_at`, `content`
3. **Pagination**: Implement cursor-based pagination
4. **Caching**: Cache recent threads in Redis
5. **Search Indexing**: Use Elasticsearch or full-text search
6. **Lazy Loading**: Load messages on-demand
7. **Compression**: Compress old message content

## Error Handling

### Frontend Error States
```jsx
// Loading state
if (loading) return <LoadingSpinner />

// Error state
if (error) return <ErrorMessage message={error} />

// Empty state
if (threads.length === 0) return <EmptyState />
```

### Backend Error Responses
```python
# Thread not found
raise HTTPException(status_code=404, detail="Thread not found")

# Unauthorized access
raise HTTPException(status_code=401, detail="Unauthorized")

# Server error
raise HTTPException(status_code=500, detail=str(e))
```

## Testing Scenarios

### Manual Testing Checklist
- [ ] Create new chat and verify it appears in history
- [ ] Search for message content and verify results
- [ ] Search for chat title and verify results
- [ ] Delete a chat and verify it's removed
- [ ] Load previous chat and continue conversation
- [ ] Test search modal from chat window
- [ ] Test search from chat history page
- [ ] Verify empty states (no chats, no search results)
- [ ] Test with unauthorized access
- [ ] Test with expired token

## Future Enhancements

### Planned Features
1. **Export Conversations**: Download chat as PDF/TXT
2. **Archive Threads**: Archive old conversations
3. **Star/Favorite**: Mark important chats
4. **Categories/Tags**: Organize chats by topic
5. **Date Range Filter**: Search within specific dates
6. **Advanced Search**: Filter by role, date, relevance
7. **Conversation Sharing**: Share threads with others
8. **Auto-Cleanup**: Automatic deletion of old threads
9. **Analytics**: View chat statistics and insights
10. **Thread Titles**: Edit conversation titles

### Technical Improvements
1. **Database Migration**: PostgreSQL + MongoDB
2. **Vector Search**: Semantic search with embeddings
3. **Real-time Sync**: WebSocket-based updates
4. **Infinite Scroll**: Better pagination
5. **Search Highlighting**: Highlight matching text
6. **Performance Metrics**: Track search speed
7. **A/B Testing**: Optimize search UX
8. **Mobile Optimization**: Better mobile experience

## Deployment Notes

### Environment Variables
No additional environment variables required. Uses existing authentication system.

### Database Schema (Future)
```sql
CREATE TABLE chat_threads (
    thread_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

CREATE TABLE chat_messages (
    message_id UUID PRIMARY KEY,
    thread_id UUID REFERENCES chat_threads(thread_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id UUID,
    metadata JSONB
);

CREATE INDEX idx_threads_user_id ON chat_threads(user_id);
CREATE INDEX idx_threads_updated_at ON chat_threads(updated_at);
CREATE INDEX idx_messages_thread_id ON chat_messages(thread_id);
CREATE INDEX idx_messages_content_search ON chat_messages USING gin(to_tsvector('english', content));
```

## Support & Troubleshooting

### Common Issues

**Issue**: Chat history not appearing
- **Solution**: Verify user is logged in, check browser console for errors

**Issue**: Search not returning results
- **Solution**: Ensure query is at least 1 character, check backend logs

**Issue**: Cannot delete thread
- **Solution**: Verify thread ownership, check network tab for errors

**Issue**: Thread not loading from history
- **Solution**: Check thread_id in URL state, verify backend API response

### Debug Commands
```bash
# Check backend logs
docker-compose logs backend

# Check frontend logs
docker-compose logs frontend

# Restart services
docker-compose restart backend frontend
```

## Conclusion

The Chat History & Search feature provides a comprehensive solution for users to manage and navigate their conversation history. With automatic session persistence, powerful search capabilities, and intuitive UI components, users can easily find and continue previous conversations with Morgan AI.

The feature is built with scalability in mind, with clear paths for future enhancements including database migration, advanced search algorithms, and additional management capabilities.
