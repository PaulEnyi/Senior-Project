# Logout & Login Flow Diagram

## Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACTIVE SESSION                               │
│                                                                 │
│  User chatting with Morgan AI...                               │
│  Messages: 15                                                   │
│  Thread: "How to declare a major?"                             │
│  Last message: 2 minutes ago                                   │
│                                                                 │
│  [User clicks "Sign out" button]                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LOGOUT PROCESS                               │
│                                                                 │
│  Step 1: Save Current Chat                                     │
│  ─────────────────────────────────────                         │
│  💾 Component unmounting - attempting to save chat...          │
│  → PUT /api/chat/threads/{id}/title                            │
│  → Title: "How to declare a major?"                            │
│  → Messages: 15 (all saved to database)                        │
│  ✅ Chat saved on unmount                                      │
│                                                                 │
│  Step 2: Backend Logout                                        │
│  ─────────────────────────────────────                         │
│  🔒 Calling backend logout endpoint...                         │
│  → POST /api/auth/logout                                       │
│  → Deactivate all active threads (is_active = False)           │
│  → Update thread timestamps                                    │
│  ✅ Server logout successful - chat saved to history           │
│                                                                 │
│  Step 3: Clear Session Data                                    │
│  ─────────────────────────────────────                         │
│  🗑️ Clearing session data...                                  │
│  → Remove: auth_token ✓                                        │
│  → Remove: token ✓                                             │
│  → Remove: user ✓                                              │
│  → Remove: user_profile ✓                                      │
│  → Remove: chat_threads ✓                                      │
│  → Remove: current_thread_id ✓                                 │
│  → Remove: degree_works_data ✓                                 │
│  → Preserve: chat_favorites ℹ️                                 │
│  ✅ Session data cleared                                       │
│                                                                 │
│  Step 4: Redirect                                              │
│  ─────────────────────────────────────                         │
│  🔄 Redirecting to login...                                    │
│  → window.location.href = '/login'                             │
│  ✅ Logout complete                                            │
│                                                                 │
│  Total Time: <1 second                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LOGIN PAGE                                   │
│                                                                 │
│  ┌───────────────────────────────────────────────────┐        │
│  │  🎓 Morgan State University                       │        │
│  │     Computer Science Department                   │        │
│  │                                                    │        │
│  │  Sign In to Morgan AI Assistant                   │        │
│  │                                                    │        │
│  │  Email:    [________________]                     │        │
│  │  Password: [________________]                     │        │
│  │                                                    │        │
│  │           [Sign In Button]                        │        │
│  │                                                    │        │
│  │  Or sign in with:                                 │        │
│  │  [Google] [Microsoft] [Apple]                     │        │
│  └───────────────────────────────────────────────────┘        │
│                                                                 │
│  [User enters credentials and clicks "Sign In"]                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LOGIN PROCESS                                │
│                                                                 │
│  Step 1: Authentication                                         │
│  ─────────────────────────────────────                         │
│  🔐 Starting login process...                                  │
│  → POST /api/auth/login                                        │
│  → Credentials: john.doe@morgan.edu                            │
│  ✅ Login successful - initializing session...                 │
│                                                                 │
│  Step 2: Store Tokens                                          │
│  ─────────────────────────────────────                         │
│  💾 Storing authentication tokens...                           │
│  → localStorage: auth_token = eyJhbGc...                       │
│  → localStorage: token = eyJhbGc... (backup)                   │
│  ✓ Authentication token stored                                 │
│                                                                 │
│  Step 3: Store User Data                                       │
│  ─────────────────────────────────────                         │
│  💾 Storing user information...                                │
│  → localStorage: user = {                                      │
│      user_id: "user123",                                       │
│      username: "john_doe",                                     │
│      name: "John Doe",                                         │
│      role: "student"                                           │
│    }                                                            │
│  ✓ User data stored                                            │
│                                                                 │
│  Step 4: Load Chat History                                     │
│  ─────────────────────────────────────                         │
│  📥 Loading previous conversations...                          │
│  → localStorage: chat_threads = [                              │
│      { thread_id: "t1", title: "How to declare...", ... },     │
│      { thread_id: "t2", title: "CS course sequence", ... },    │
│      ... (15 total threads)                                    │
│    ]                                                            │
│  ✓ Loaded 15 previous chat threads                             │
│  ℹ️  (Messages not loaded - only metadata)                     │
│                                                                 │
│  Step 5: Load User Profile                                     │
│  ─────────────────────────────────────                         │
│  📥 Loading profile data...                                    │
│  → localStorage: user_profile = {                              │
│      student_id: "20240001",                                   │
│      major: "Computer Science",                                │
│      concentration: "Software Engineering",                    │
│      classification: "Junior",                                 │
│      expected_graduation: "Spring 2026",                       │
│      gpa: 3.7                                                  │
│    }                                                            │
│  ✓ Loaded user profile                                         │
│                                                                 │
│  Step 6: Load DegreeWorks (if available)                       │
│  ─────────────────────────────────────                         │
│  📥 Loading DegreeWorks analysis...                            │
│  → localStorage: degree_works_data = { ... }                   │
│  ✓ Loaded DegreeWorks analysis                                 │
│                                                                 │
│  Step 7: Restore Favorites                                     │
│  ─────────────────────────────────────                         │
│  ✨ Checking for favorites...                                  │
│  → localStorage: chat_favorites = ["t1", "t5", "t8"]           │
│  ✓ Favorites preserved from previous session                   │
│                                                                 │
│  Session Initialized                                           │
│  ─────────────────────────────────────                         │
│  ✅ Session initialized successfully                           │
│  ℹ️  Starting with fresh chat interface                        │
│  ℹ️  Previous chats available in Chat History                  │
│                                                                 │
│  Total Time: <2 seconds                                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRESH CHAT INTERFACE                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────┐          │
│  │  🎓 Morgan AI Assistant                         │          │
│  │     Computer Science Department                 │          │
│  │                                                  │          │
│  │  Welcome, John Doe! 👋                          │          │
│  │                                                  │          │
│  │  How can I help you today?                      │          │
│  │                                                  │          │
│  │  Quick Questions:                                │          │
│  │  ┌──────────────────────────────────┐          │          │
│  │  │ 📚 Academic Advising             │          │          │
│  │  │ 📅 Calendar & Events             │          │          │
│  │  │ 💼 Career & Internships          │          │          │
│  │  │ 🎯 Course Registration           │          │          │
│  │  └──────────────────────────────────┘          │          │
│  │                                                  │          │
│  │  Type your question or select above...          │          │
│  │  [________________________________]   [Send]    │          │
│  │                                                  │          │
│  └─────────────────────────────────────────────────┘          │
│                                                                 │
│  Sidebar Navigation:                                            │
│  ┌──────────────────┐                                          │
│  │ 🏠 Home          │ ← Current page (fresh chat)              │
│  │ 📝 Chat History  │ ← 15 previous chats accessible           │
│  │ 📊 DegreeWorks   │ ← Analysis loaded and ready              │
│  │ 📅 Calendar      │                                          │
│  │ 💼 Career        │                                          │
│  │ ⚙️  Settings     │                                          │
│  │ 🚪 Sign Out      │                                          │
│  └──────────────────┘                                          │
│                                                                 │
│  State:                                                         │
│  • Messages: [] (empty)                                        │
│  • Thread: null (no active thread)                             │
│  • History: 15 threads (metadata only)                         │
│  • Favorites: 3 threads (t1, t5, t8) ⭐                        │
│  • Ready for new conversation ✨                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                   [User Can Now...]
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌──────────────────┐                  ┌──────────────────┐
│  START NEW CHAT  │                  │  VIEW HISTORY    │
│                  │                  │                  │
│  • Type message  │                  │  Click "Chat     │
│  • Select quick  │                  │  History" link   │
│    question      │                  │                  │
│  • Fresh thread  │                  │  See 15 threads: │
│    created       │                  │  ⭐ t1: How to   │
│                  │                  │     declare...   │
│  Creates new     │                  │    t2: CS course │
│  conversation    │                  │       sequence   │
│                  │                  │  ⭐ t5: Internsh │
│                  │                  │       ips...     │
│                  │                  │    ...           │
│                  │                  │                  │
│                  │                  │  Click thread    │
│                  │                  │  → Resume old    │
│                  │                  │     chat         │
└──────────────────┘                  └──────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         LOGOUT                              │
└─────────────────────────────────────────────────────────────┘

Frontend State              localStorage              Backend Database
─────────────────          ───────────────           ─────────────────
messages: [15]                                       
threadId: "t123"      →    CLEAR auth_token          
chatTitle: "How to"   →    CLEAR token               
user: {john_doe}      →    CLEAR user                
                      →    CLEAR user_profile         
                      →    CLEAR chat_threads         
                      →    CLEAR current_thread_id    
                      →    CLEAR degree_works_data    
                      →                               → SAVE thread:
                           PRESERVE chat_favorites        - id: t123
                                                          - title: "How to"
                                                          - messages: [15]
                                                          - is_active: False
                                                          - updated_at: now

                                                     → DEACTIVATE all
                                                       active threads


┌─────────────────────────────────────────────────────────────┐
│                         LOGIN                               │
└─────────────────────────────────────────────────────────────┘

Backend Database           localStorage              Frontend State
─────────────────         ───────────────           ─────────────────
                                                     messages: []
user: {john_doe}      →    SET auth_token           threadId: null
                      →    SET token                chatTitle: ''
threads: [15]         →    SET user                 threads: [15 metadata]
profile: {...}        →    SET user_profile         favorites: [t1,t5,t8]
degree_works: {...}   →    SET chat_threads         
                      →    SET degree_works_data    → FRESH INTERFACE
                      ←    GET chat_favorites       → READY FOR INPUT
```

## Timeline Comparison

```
Logout Timeline:
─────────────────────────────────────────────────────────────
0ms    User clicks "Sign out"
50ms   Component cleanup starts
100ms  Chat save request sent (keepalive)
150ms  Backend logout called
200ms  Threads deactivated
250ms  localStorage cleared
300ms  Redirect to /login
─────────────────────────────────────────────────────────────
Total: ~300ms (<1 second)


Login Timeline:
─────────────────────────────────────────────────────────────
0ms    User submits credentials
200ms  Backend authentication complete
250ms  Token stored to localStorage
300ms  User data stored
350ms  Chat threads metadata stored
400ms  Profile data stored
450ms  DegreeWorks data stored
500ms  Favorites loaded from localStorage
550ms  Navigate to home with newChat state
600ms  Fresh chat interface rendered
─────────────────────────────────────────────────────────────
Total: ~600ms (<2 seconds)
```

## State Transitions

```
┌──────────────┐  Logout   ┌──────────────┐  Login    ┌──────────────┐
│              │ ────────> │              │ ────────> │              │
│   LOGGED IN  │           │ LOGGED OUT   │           │   LOGGED IN  │
│              │ <──────── │              │ <──────── │              │
│              │  Re-login │              │  Logout   │              │
└──────────────┘           └──────────────┘           └──────────────┘

LOGGED IN State:
• Auth token valid
• User data loaded
• Chat history accessible
• Can send messages
• Can view history
• Can manage profile

LOGGED OUT State:
• No auth token
• No user data
• No chat access
• Login page displayed
• Session cleared
• Favorites preserved

TRANSITION States:
Logout → Logged Out:
  • Save current chat ✓
  • Clear session ✓
  • Redirect to login ✓

Logged Out → Logged In:
  • Store token ✓
  • Load user data ✓
  • Load chat metadata ✓
  • Fresh interface ✓
```
