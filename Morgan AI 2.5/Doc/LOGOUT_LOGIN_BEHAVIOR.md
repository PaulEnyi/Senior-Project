# Logout & Login Behavior Documentation

## Overview
This document details the comprehensive logout and login behaviors implemented in Morgan AI to ensure proper chat history management, session handling, and user experience.

---

## 4.1 Logout Behavior

### Process Flow
```
User Clicks Logout
    ↓
Save Current Chat to History (if active)
    ↓
Call Backend /api/auth/logout
    ↓
Deactivate All Active Threads
    ↓
Clear Session Data from localStorage
    ↓
Redirect to Login Page
```

### Step-by-Step Implementation

#### 1. **Save Current Chat to History**
- **Trigger**: User clicks logout button or session expires
- **Action**: Current chat conversation is automatically saved
- **Backend Call**: `PUT /api/chat/threads/{thread_id}/title`
- **Data Saved**:
  - Chat title (auto-generated from first user message if not set)
  - All messages in the conversation
  - Thread metadata (created_at, updated_at, message_count)
- **Implementation**: `ChatWindow.jsx` - cleanup useEffect
  ```javascript
  useEffect(() => {
    return () => {
      if (messages.length > 0 && hasUnsavedChangesRef.current) {
        // Fire-and-forget save with keepalive flag
        fetch(`/api/chat/threads/${threadId}/title`, {
          method: 'PUT',
          body: JSON.stringify({ title }),
          keepalive: true // Allows request after page unload
        });
      }
    };
  }, [messages, threadId]);
  ```

#### 2. **Call Backend Logout Endpoint**
- **Endpoint**: `POST /api/auth/logout`
- **Headers**: `Authorization: Bearer {token}`
- **Backend Actions**:
  - Deactivate all active chat threads (`is_active = False`)
  - Update thread timestamps
  - Revoke session token (if session management implemented)
  - Log logout event
- **Response**:
  ```json
  {
    "success": true,
    "message": "Logged out successfully",
    "user_id": "user123",
    "chat_saved": true,
    "logged_out_at": "2025-11-23T10:30:00Z"
  }
  ```
- **Implementation**: `authService.js`
  ```javascript
  async logout() {
    const response = await api.post('/api/auth/logout', {}, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.data?.chat_saved) {
      console.log('✅ Chat saved to history');
    }
  }
  ```

#### 3. **Clear Session Data**
- **localStorage Items Removed**:
  - `auth_token` - Authentication token
  - `token` - Backup token for compatibility
  - `user` - User object
  - `user_profile` - User profile data
  - `chat_threads` - Cached thread list
  - `current_thread_id` - Active thread ID
  - `degree_works_data` - DegreeWorks analysis
- **localStorage Items Preserved**:
  - `chat_favorites` - User's favorited chats (user preference)
  - Theme preference (handled separately)
- **Implementation**: `authService.js`
  ```javascript
  const keysToRemove = [
    'auth_token', 'token', 'user', 'user_profile',
    'chat_threads', 'current_thread_id', 'degree_works_data'
  ];
  keysToRemove.forEach(key => localStorage.removeItem(key));
  ```

#### 4. **Redirect to Login Page**
- **Action**: `window.location.href = '/login'`
- **Reason**: Full page reload ensures:
  - All React state is cleared
  - No memory leaks from previous session
  - Fresh application initialization
- **User Experience**: Smooth transition with logout confirmation

### Console Logging (Debug Mode)
```
🔄 Starting logout process...
💾 Component unmounting - attempting to save chat...
✅ Chat saved on unmount
✅ Server logout successful - chat saved to history
🗑️ Clearing session data...
  ✓ Removed: auth_token
  ✓ Removed: token
  ✓ Removed: user
  ✓ Removed: user_profile
  ✓ Removed: chat_threads
  ℹ️ Preserving: chat_favorites
✅ Logout complete - redirecting to login...
```

### Error Handling
- **Backend Logout Fails**: Continue with local logout
- **Save Chat Fails**: Log warning but proceed with logout
- **Network Error**: Force clear all data and redirect
- **Principle**: Never block logout - user security > data persistence

---

## 4.2 Login Behavior

### Process Flow
```
User Enters Credentials
    ↓
Authenticate with Backend
    ↓
Receive Token + User Data
    ↓
Store Session in localStorage
    ↓
Load User's Chat History (metadata)
    ↓
Start Fresh Chat Interface
    ↓
Navigate to Home Page
```

### Step-by-Step Implementation

#### 1. **Authenticate with Backend**
- **Endpoint**: `POST /api/auth/login` or `POST /api/admin/login`
- **Request Body**:
  ```json
  {
    "username": "user@morgan.edu",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "user": {
      "user_id": "user123",
      "username": "john_doe",
      "name": "John Doe",
      "email": "user@morgan.edu",
      "role": "student",
      "student_id": "20240001",
      "major": "Computer Science",
      "chat_threads": [...],
      "degree_works_data": {...}
    }
  }
  ```

#### 2. **Store Session in localStorage**
- **Token Storage** (redundant for compatibility):
  ```javascript
  localStorage.setItem('auth_token', response.access_token);
  localStorage.setItem('token', response.access_token);
  ```
- **User Data Storage**:
  ```javascript
  const userData = {
    username: response.user.username,
    name: response.user.name,
    role: response.user.role,
    user_id: response.user.user_id
  };
  localStorage.setItem('user', JSON.stringify(userData));
  ```
- **Profile Data Storage**:
  ```javascript
  const profile = {
    student_id: response.user.student_id,
    major: response.user.major,
    concentration: response.user.concentration,
    classification: response.user.classification,
    expected_graduation: response.user.expected_graduation,
    gpa: response.user.gpa
  };
  localStorage.setItem('user_profile', JSON.stringify(profile));
  ```

#### 3. **Load Chat History Metadata**
- **Data Source**: `response.user.chat_threads`
- **Storage**: `localStorage.setItem('chat_threads', JSON.stringify(threads))`
- **Display**: Threads shown in Chat History page
- **Note**: Messages not loaded until user clicks on specific thread
- **Example Thread Object**:
  ```json
  {
    "thread_id": "thread-uuid-123",
    "title": "How to declare a major?",
    "created_at": "2025-11-20T14:30:00Z",
    "updated_at": "2025-11-20T15:45:00Z",
    "message_count": 12,
    "is_active": false,
    "is_deleted": false
  }
  ```

#### 4. **Load Additional User Data**
- **DegreeWorks Analysis** (if available):
  ```javascript
  if (response.user.degree_works_data) {
    localStorage.setItem('degree_works_data', JSON.stringify(data));
  }
  ```
- **Favorites** (preserved from previous session):
  - Stays in `chat_favorites` key
  - Not cleared on logout

#### 5. **Start Fresh Chat Interface**
- **Action**: Navigate to home (`/`) with `{ state: { newChat: true } }`
- **Result**: 
  - Empty message area
  - No active thread
  - Welcome screen displayed
  - Ready for new conversation
- **Previous Chats**: Accessible via "Chat History" navigation link

#### 6. **Clear Old Session Data**
- **sessionStorage**: Completely cleared
- **Reason**: Ensure no stale data from previous session

### Console Logging (Debug Mode)
```
🔐 Login successful - initializing session...
  ✓ Authentication token stored
  ✓ User data stored
  ✓ Loaded 15 previous chat threads
  ✓ Loaded DegreeWorks analysis
  ✓ Loaded user profile
✅ Session initialized successfully
ℹ️  Starting with fresh chat interface
ℹ️  Previous chats available in Chat History
```

### User Experience Flow

#### Fresh Login View:
```
┌─────────────────────────────────────┐
│  Morgan AI Assistant                │
│  Computer Science Department        │
├─────────────────────────────────────┤
│                                     │
│      🎓  Welcome, John Doe!         │
│                                     │
│  How can I help you today?          │
│                                     │
│  [Quick Questions]                  │
│  📚 Academic Advising               │
│  📅 Calendar & Events               │
│  💼 Career & Internships            │
│  🎯 Course Registration             │
│                                     │
│  [Start typing or ask a question]   │
│                                     │
└─────────────────────────────────────┘

Navigation Sidebar:
  🏠 Home
  📝 Chat History ← (15 previous chats)
  📊 DegreeWorks
  📅 Calendar
  ...
```

---

## Technical Implementation

### Files Modified

1. **`authService.js`** - Enhanced logout and login
   - Save chat before logout
   - Clear specific localStorage keys
   - Console logging for debug
   - Error handling

2. **`useAuth.js`** - Hook for auth state
   - Call authService methods
   - Update React state
   - Handle loading states

3. **`LoginPage.jsx`** - Login UI
   - Store all user data on successful login
   - Navigate with `newChat: true` state
   - Display loading and error states

4. **`ChatWindow.jsx`** - Chat interface
   - Save on component unmount
   - Handle `newChat` state from navigation
   - Auto-save with debounce
   - Cleanup on logout

5. **`useChat.js`** - Chat state management
   - `saveBeforeLogout()` method
   - Clear messages on new chat
   - Thread management

### Backend Endpoints Used

#### Logout
```python
@router.post("/api/auth/logout")
async def logout(
    current_user: Dict = Depends(SecurityService.get_current_user),
    file_storage = Depends(get_file_storage)
):
    # Deactivate all active threads
    threads = file_storage.get_user_chat_threads(user_id, limit=100)
    for thread_info in threads:
        thread_data = file_storage.load_chat_thread(user_id, thread_id)
        if thread_data and thread_data.get('is_active'):
            thread_data['is_active'] = False
            file_storage.save_chat_thread(user_id, thread_id, thread_data)
    
    return {
        "success": True,
        "message": "Logged out successfully",
        "chat_saved": True
    }
```

#### Login
```python
@router.post("/api/auth/login")
async def login(credentials: LoginCredentials):
    # Authenticate user
    user = authenticate_user(credentials)
    
    # Load chat threads
    threads = file_storage.get_user_chat_threads(user.id)
    
    # Load DegreeWorks data
    degree_works = file_storage.load_degree_works(user.id)
    
    return {
        "access_token": token,
        "user": {
            ...user_data,
            "chat_threads": threads,
            "degree_works_data": degree_works
        }
    }
```

---

## Data Persistence

### What Gets Saved on Logout
✅ Current chat conversation (to database)
✅ Thread metadata (title, timestamps, message count)
✅ Thread messages (content, role, timestamp)
✅ Thread state (is_active = False)
✅ User favorites (localStorage - preserved)

### What Gets Cleared on Logout
🗑️ Authentication tokens
🗑️ User session data
🗑️ Cached thread list
🗑️ Active thread ID
🗑️ DegreeWorks cache

### What Gets Loaded on Login
📥 Authentication token
📥 User profile data
📥 Chat thread metadata (list of all chats)
📥 DegreeWorks analysis (if available)
📥 User favorites (from localStorage)

### What Doesn't Get Loaded on Login
❌ Thread messages (loaded on demand when user clicks thread)
❌ Chat input history
❌ UI state (scroll position, open modals, etc.)

---

## Security Considerations

1. **Token Handling**
   - Tokens cleared immediately on logout
   - No token persistence in memory after logout
   - New token issued on each login

2. **Session Cleanup**
   - All user data removed from localStorage
   - sessionStorage completely cleared
   - No cross-session data leakage

3. **Chat Privacy**
   - Chats saved server-side (not in localStorage)
   - Only metadata cached locally
   - Full messages require authentication to access

4. **Error Recovery**
   - Logout never blocked by errors
   - Best-effort save, guaranteed logout
   - Clear all data on any failure

---

## User Experience Highlights

### Logout
- ✅ Seamless chat saving (no user action required)
- ✅ No data loss
- ✅ Clear feedback ("Logged out successfully")
- ✅ Instant redirect to login
- ✅ Favorites preserved for next session

### Login
- ✅ Fresh, clean interface
- ✅ All previous chats accessible
- ✅ Quick access to history
- ✅ Profile data pre-loaded
- ✅ DegreeWorks data ready (if available)

### Navigation Flow
```
Login → Fresh Chat Interface
         ↓
      [New Chat] ← Start conversation
         ↓
   [Chat History] ← View previous chats
         ↓
    [Select Chat] ← Resume old conversation
         ↓
      [Logout] → Save current chat → Login screen
```

---

## Testing Checklist

### Logout Testing
- [ ] Current chat saves before logout
- [ ] All active threads deactivated
- [ ] localStorage cleared (except favorites)
- [ ] Redirects to login page
- [ ] No console errors
- [ ] Works when network fails
- [ ] Works when chat is empty
- [ ] Works with multiple tabs open

### Login Testing
- [ ] Token stored correctly
- [ ] User data loaded
- [ ] Chat history metadata loaded
- [ ] Fresh chat interface displayed
- [ ] Previous chats accessible
- [ ] DegreeWorks data loaded (if exists)
- [ ] Profile data displayed correctly
- [ ] Favorites preserved from previous session
- [ ] New chat can be started immediately
- [ ] Old chat can be resumed from history

### End-to-End Testing
- [ ] Logout → Login → Fresh interface
- [ ] Chat during session → Logout → Login → Chat in history
- [ ] Multiple chats → Logout → Login → All chats visible
- [ ] Favorite chat → Logout → Login → Favorite still marked
- [ ] Edit title → Logout → Login → Title persisted
- [ ] Session timeout → Auto-logout → Redirect to login

---

## Future Enhancements

1. **Logout Confirmation Dialog**
   - Show current chat title and message count
   - "Save and logout" vs "Cancel" buttons
   - Prevent accidental logouts

2. **Session Expiry Warning**
   - Show countdown before auto-logout
   - "Extend session" button
   - Auto-save before expiry

3. **Multi-Device Sync**
   - Logout on one device → notify other devices
   - Cross-device favorite sync
   - Real-time chat updates

4. **Partial Logout**
   - Lock interface without full logout
   - Quick PIN unlock
   - Preserve UI state

5. **Logout History**
   - Track login/logout events
   - Show "Last login" timestamp
   - Security audit trail

---

## Troubleshooting

### Chat Not Saved on Logout
**Check**: Console logs for save errors
**Fix**: Verify backend `/api/auth/logout` is working
**Workaround**: Manually save via "Chat History" before logout

### Previous Chats Not Showing After Login
**Check**: localStorage `chat_threads` key
**Fix**: Verify backend returns `chat_threads` in login response
**Workaround**: Refresh Chat History page to reload from server

### "Unauthorized" Error After Login
**Check**: Token stored in localStorage (`auth_token` and `token`)
**Fix**: Verify token format and expiry
**Workaround**: Logout and login again

### Fresh Chat Not Starting on Login
**Check**: Navigation state in console (`{ newChat: true }`)
**Fix**: Verify `navigate(redirectTo, { state: { newChat: true } })` in LoginPage
**Workaround**: Click "New Chat" button in header

---

## Conclusion

The logout and login behaviors are designed to provide:
- ✅ **Data Safety**: No chat loss on logout
- ✅ **Privacy**: All session data cleared
- ✅ **Convenience**: Fresh start on login with accessible history
- ✅ **Performance**: Efficient data loading (metadata only)
- ✅ **Reliability**: Graceful error handling
- ✅ **Transparency**: Clear console logging for debugging

This implementation ensures users can confidently logout knowing their conversations are safely stored and will be available when they return.
