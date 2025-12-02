# Navigation Icons Location Guide

## ✅ Chat History Icon - FOUND

**Location:** `FrontEnd/src/components/Navigation/NavMenu.jsx`

**Line:** 33

**Code:**
```javascript
{ path: '/chat-history', label: 'Chat History', icon: FiClock, color: '#10B981' },
```

**Icon:** Clock icon (FiClock) from react-icons/fi

**How it appears in the navigation menu:**
- **Label:** "Chat History"
- **Icon:** 🕐 (Clock)
- **Color:** Green (#10B981)
- **Route:** `/chat-history`

**Screenshot description:**
When you open the navigation menu (hamburger menu), you'll see:
```
🏠 Chat
🕐 Chat History          ← THIS IS YOUR CHAT HISTORY ICON
🎓 Degree Works
📖 Courses
📅 Calendar
👥 Organizations
💼 Career
📚 Study
❓ Help
```

---

## ✅ Search Icon - FOUND

**Location:** `FrontEnd/src/components/Chat/ChatWindow.jsx`

**Line:** 742-747

**Code:**
```javascript
<button
  className="search-btn"
  onClick={() => setShowSearchModal(true)}
  title="Search chat history"
>
  <FiSearch />
</button>
```

**Icon:** Search icon (FiSearch) from react-icons/fi

**How it appears in the chat interface:**
The search icon is located in the input area, **BEFORE** the quick questions button.

**Layout in chat input area (left to right):**
```
[🔍 Search] [❓ Quick Questions] [🎤 Voice] [▶️ TTS Controls] [🗑️ Clear] [📤 Send]
     ↑
  THIS IS YOUR SEARCH ICON
```

**Functionality:**
- Click the search icon (🔍)
- Opens a modal for searching chat history
- Can search by title, message content, and date
- Results show matching threads grouped with message previews
- Click any result to load that conversation

---

## User Data Storage Location

### New File-Based Storage System

**Base Directory:** `BackEnd/app/data/users/`

**Structure:**
```
data/
└── users/
    ├── {user-id-1}/
    │   ├── user_info.json         # Username, password hash, email, timestamps
    │   ├── profile.json           # Additional profile data
    │   ├── chat_history/          # All previous chats
    │   │   ├── {thread-id-1}.json
    │   │   ├── {thread-id-2}.json
    │   │   └── {thread-id-3}.json
    │   ├── degree_works/          # DegreeWorks files
    │   │   ├── transcript.pdf
    │   │   ├── transcript.pdf.meta.json
    │   │   └── ...
    │   ├── files/                 # Other user files
    │   └── temp/                  # Temporary files
    │
    ├── {user-id-2}/
    │   ├── user_info.json
    │   ├── profile.json
    │   ├── chat_history/
    │   ├── degree_works/
    │   ├── files/
    │   └── temp/
    │
    └── {user-id-3}/
        └── ... (same structure)
```

### user_info.json Example
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "student123",
  "email": "student123@morgan.edu",
  "password_hash": "$2b$12$...",
  "full_name": "John Doe",
  "role": "student",
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-15T14:20:00Z",
  "is_deleted": false
}
```

### Chat Thread Example (chat_history/{thread-id}.json)
```json
{
  "thread_id": "thread-uuid-here",
  "user_id": "user-uuid-here",
  "title": "How do I register for CS classes?",
  "message_count": 5,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T11:45:00Z",
  "is_active": true,
  "is_deleted": false,
  "messages": [
    {
      "message_id": "msg-uuid-1",
      "content": "How do I register for CS classes?",
      "role": "user",
      "timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "message_id": "msg-uuid-2",
      "content": "To register for Computer Science classes, you need to...",
      "role": "assistant",
      "timestamp": "2025-01-15T10:30:15Z"
    }
  ]
}
```

### DegreeWorks Metadata Example
```json
{
  "file_name": "degree_audit.pdf",
  "file_path": "data/users/{user-id}/degree_works/degree_audit.pdf",
  "uploaded_at": "2025-01-15T10:30:00Z",
  "file_size": 245632,
  "parsed_data": {
    "student_name": "John Doe",
    "student_id": "12345678",
    "major": "Computer Science",
    "gpa": 3.75,
    "credits_completed": 90,
    "courses": [...]
  }
}
```

---

## How the File Storage System Works

### 1. **User Signup**
When a user signs up:
1. Generate unique `user_id` (UUID)
2. Create folder: `data/users/{user_id}/`
3. Create subfolders: `chat_history/`, `degree_works/`, `files/`, `temp/`
4. Save `user_info.json` with:
   - Username
   - Password hash (bcrypt)
   - Email
   - Created timestamp
   - Role (student/admin)

### 2. **User Login**
When a user logs in:
1. Search all `user_info.json` files for matching email
2. Verify password hash
3. Update `last_login` timestamp in `user_info.json`
4. Return user data

### 3. **Chat Messages**
When a user sends a message:
1. Load or create thread file: `data/users/{user_id}/chat_history/{thread_id}.json`
2. Append user message to `messages` array
3. Get AI response
4. Append assistant message to `messages` array
5. Update `message_count` and `updated_at`
6. Save thread file

### 4. **Chat History**
When a user views chat history:
1. List all JSON files in `data/users/{user_id}/chat_history/`
2. Load each thread file
3. Filter out soft-deleted threads (`is_deleted: true`)
4. Sort by `updated_at` (most recent first)
5. Return thread list with titles, message counts, timestamps

### 5. **Search**
When a user searches:
1. Load all threads for user
2. Search in `title` field
3. Search in all message `content` fields
4. Find matching threads
5. Return results grouped by thread with message previews

### 6. **DegreeWorks Upload**
When a user uploads DegreeWorks:
1. Save PDF file: `data/users/{user_id}/degree_works/{filename}.pdf`
2. Parse PDF to extract academic data
3. Save metadata: `data/users/{user_id}/degree_works/{filename}.pdf.meta.json`
4. Store parsed data in metadata file

### 7. **Data Persistence**
- All data stored in JSON files
- Survives server restarts
- Survives Docker rebuilds
- Easy to backup (just copy `data/users/` folder)
- Easy to migrate (move files to new server)

---

## File Storage Service API

### Available Functions

```python
from app.core.file_storage import get_file_storage

storage = get_file_storage()

# User Management
storage.save_user_info(user_id, user_data)
storage.load_user_info(user_id)
storage.find_user_by_email(email)
storage.find_user_by_username(username)
storage.delete_user(user_id, permanent=False)

# Chat Threads
storage.save_chat_thread(user_id, thread_id, thread_data)
storage.load_chat_thread(user_id, thread_id)
storage.get_user_chat_threads(user_id, limit=20)
storage.delete_chat_thread(user_id, thread_id, soft_delete=True)
storage.search_chat_threads(user_id, query, limit=20)

# DegreeWorks Files
storage.save_degree_works_file(user_id, file_name, file_data, parsed_data)
storage.get_user_degree_works_files(user_id)

# User Profile
storage.save_user_profile(user_id, profile_data)
storage.load_user_profile(user_id)

# Statistics
storage.get_all_users()
storage.get_storage_stats()
```

---

## Benefits of File-Based Storage

### ✅ Advantages
1. **Simple Structure** - Easy to understand and navigate
2. **Human-Readable** - JSON files can be opened and read
3. **Easy Backup** - Just copy the `data/users/` folder
4. **No Database Required** - No PostgreSQL setup needed
5. **Portable** - Move files between servers easily
6. **Version Control Friendly** - Can track changes in Git
7. **Easy Debugging** - Just open the JSON files
8. **Scalable** - Works for small to medium user bases

### ⚠️ Considerations
1. **Performance** - May slow down with 1000+ users
2. **Concurrent Access** - Need file locking for simultaneous writes
3. **Search Speed** - Slower than database indexes
4. **Backups** - Need manual backup strategy

---

## Migration Path

### Current System (Database)
- PostgreSQL database
- 6 tables (users, threads, messages, sessions, audit, files)
- Requires Docker container

### New System (File-Based)
- JSON files in `data/users/` folder
- One folder per user
- No database required
- Works without Docker

### You Can Use **BOTH**:
1. **Database** - For production with many users
2. **File Storage** - For development or small deployments
3. **Hybrid** - User info in database, chats in files

---

## Visual Summary

```
📁 Morgan AI 2.5/
  └── 📁 BackEnd/
      └── 📁 app/
          └── 📁 data/
              └── 📁 users/               ← ALL USER DATA HERE
                  ├── 📁 user-abc123/
                  │   ├── 📄 user_info.json       (username, password, email)
                  │   ├── 📄 profile.json         (profile data)
                  │   ├── 📁 chat_history/        (all previous chats)
                  │   │   ├── 📄 thread-1.json
                  │   │   ├── 📄 thread-2.json
                  │   │   └── 📄 thread-3.json
                  │   ├── 📁 degree_works/        (transcripts, audits)
                  │   │   ├── 📄 transcript.pdf
                  │   │   └── 📄 transcript.pdf.meta.json
                  │   ├── 📁 files/               (other files)
                  │   └── 📁 temp/                (temporary files)
                  │
                  ├── 📁 user-def456/
                  │   └── ... (same structure)
                  │
                  └── 📁 user-ghi789/
                      └── ... (same structure)
```

---

## Next Steps

To integrate this file-based storage system:

1. ✅ **Created:** `file_storage.py` - Complete file storage service
2. ⏳ **Next:** Update `auth.py` to use file storage instead of database
3. ⏳ **Next:** Update `chat.py` to save threads to files
4. ⏳ **Next:** Test signup, login, chat, and search with file storage
5. ⏳ **Next:** Add migration script to convert database data to files

Would you like me to integrate the file storage system into the authentication and chat routes now?
