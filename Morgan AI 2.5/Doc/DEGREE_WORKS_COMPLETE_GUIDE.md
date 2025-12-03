# Degree Works Feature - Complete Implementation Guide

## Overview

The Degree Works feature enables students to upload their degree audit PDF and receive personalized academic answers from the Morgan AI chatbot. The system parses transcripts, stores data persistently, and integrates seamlessly with the chat interface.

---

## 🎯 User Experience Flow

### 1. **Upload via Chat Interface**
- **Icon Location**: Chat input area, positioned between the Quick Questions icon and Send button
- **Icon Design**: 📄 File document icon (`FiFileText`) with blue gradient matching UI theme
- **Badge Indicator**: Green pulsing badge appears when transcript is loaded (shows GPA in tooltip)

### 2. **Upload Modal**
When clicking the Degree Works icon, a modal opens with:
- **PDF Upload**: File input accepting `.pdf` files only
- **Summary Preview**: Displays GPA, completed credits, and classification after successful upload
- **Quick Action Buttons**:
  - 📊 **GPA & Credits** - "What is my current GPA and how many credits have I completed?"
  - 📚 **In-Progress Courses** - "Which courses am I currently taking?"
  - 📝 **Remaining Courses** - "Which required computer science courses do I still need to complete?"
  - ✅ **Completed Courses** - "List all completed courses with grades."
  - 🔍 **Course & Grade Check** - Custom input (e.g., "COSC 111") to verify specific course completion

### 3. **Persistent Storage**
- PDF and parsed data saved to `BackEnd/app/data/users/{user_id}/degree_works/`
- Data persists across server restarts
- Versioning system tracks all uploads with diff analysis
- User can delete data anytime via Delete button in modal

### 4. **Degree Works Page**
- Navigate to `/degree-works` to view full analysis
- Displays all uploaded versions with timestamps
- Shows detailed course breakdowns by category
- Provides comparison tools between versions
- Delete functionality for individual versions or all data

---

## 🔧 Technical Implementation

### Backend Architecture

#### 1. **API Endpoints** (`BackEnd/app/app/api/routes/degree_works.py`)

```python
POST   /api/degree-works/upload          # Upload and parse PDF
GET    /api/degree-works/analysis        # Get latest analysis
GET    /api/degree-works/summary         # Get summary for UI
GET    /api/degree-works/versions        # List all versions
GET    /api/degree-works/versions/{id}   # Get specific version
GET    /api/degree-works/versions/{id}/diff/{base}  # Compare versions
DELETE /api/degree-works/versions/{id}   # Delete specific version
DELETE /api/degree-works/analysis        # Delete all data
GET    /api/degree-works/timeline        # Get course timeline
GET    /api/degree-works/courses         # Query courses by status/category
```

#### 2. **PDF Parser** (`BackEnd/app/app/services/degree_works_parser.py`)

**Key Features:**
- Extracts student info (name, major, ID)
- Calculates GPA and credits (completed, in-progress, remaining)
- Categorizes courses by status:
  - **Completed**: Courses with passing grades (A-D, P, S)
  - **In-Progress**: Current semester courses (IP status)
  - **Remaining**: Required courses not yet taken
- Groups courses by requirement category (Major Core, Gen Ed, Electives, etc.)
- Builds semester timeline for progress tracking
- Determines classification (Freshman/Sophomore/Junior/Senior)

**Robust Pattern Recognition:**
- Handles multiple course code formats (COSC 111, CS-111, CSCI111, etc.)
- Recognizes all Morgan State grade types (A-F, P/NP, W/WF, I, IP, AU, S/U)
- Dynamically detects current semester for in-progress classification
- Validates against whitelist of Morgan State department codes

**Output Format:**
```python
{
  "success": True,
  "student_info": {
    "name": "Student Name",
    "student_id": "12345678",
    "major": "Computer Science",
    "degree": "Bachelor of Science"
  },
  "academic_summary": {
    "gpa": 3.45,
    "completed_credits": 75.0,
    "in_progress_credits": 15.0,
    "remaining_credits": 30.0,
    "total_credits_required": 120.0,
    "classification": "Junior"
  },
  "courses": {
    "completed": [...],    # Full course objects with code, name, credits, grade, term
    "in_progress": [...],  # Current semester courses
    "remaining": [...]     # Still needed courses
  },
  "requirements": {
    "Major Core": {...},
    "General Education": {...},
    "Electives": {...}
  },
  "course_timeline": {
    "Fall 2023": {...},
    "Spring 2024": {...}
  }
}
```

#### 3. **Chat Integration** (`BackEnd/app/app/services/openai_service.py`)

**Automatic Context Injection:**

When a user with an uploaded Degree Works file sends a chat message:

1. System retrieves parsed data from file storage
2. Formats data using `DegreeWorksParser.format_for_chatbot()`
3. Injects as system context: "Student's Academic Record:\n{formatted_data}"
4. GPT-4 uses this as ground truth for all academic questions

**Sample Context Injected:**
```
STUDENT DEGREE WORKS ANALYSIS
================================

Student: John Doe
Major: Computer Science
Classification: Junior
GPA: 3.45

ACADEMIC PROGRESS:
- Credits Completed: 75
- Credits In Progress: 15
- Credits Required: 120
- Credits Remaining: 30

COMPLETED COURSES (25 courses):
- COSC 111: Introduction to Computer Science I (4 credits) - Grade: A - Category: Major Core
- COSC 112: Introduction to Computer Science II (4 credits) - Grade: B+ - Category: Major Core
- MATH 141: Calculus I (4 credits) - Grade: A- - Category: Supporting Courses
...

IN-PROGRESS COURSES (5 courses):
- COSC 300: Data Structures (3 credits) - Category: Major Core
- COSC 320: Computer Organization (3 credits) - Category: Major Core
...

REMAINING REQUIRED COURSES (10 courses):
- COSC 450: Operating Systems (3 credits) - Category: Major Core
- COSC 460: Database Systems (3 credits) - Category: Major Core
...
```

**System Prompt Enhancement:**

The chatbot is explicitly instructed to:
- Use Degree Works data as ground truth for all academic questions
- Check COMPLETED COURSES list before saying a course hasn't been taken
- Reference specific grades and terms from the transcript
- Distinguish clearly between completed, in-progress, and remaining courses
- **Never contradict the Degree Works data** (fixes the bug where chatbot denied completed courses)

### Frontend Architecture

#### 1. **Global Context Provider** (`FrontEnd/src/context/DegreeWorksContext.jsx`)

```javascript
<DegreeWorksProvider>
  {/* Provides: */}
  - hasTranscript: boolean
  - summary: academic_summary object
  - gpa, completedCredits, inProgressCredits, etc.
  - refresh(): async function to reload data
  - refreshing: boolean loading state
</DegreeWorksProvider>
```

**Automatic Loading:**
- Fetches `/api/degree-works/summary` on app mount
- Re-fetches after uploads or deletes
- Shares state across all components (chat, Degree Works page, etc.)

#### 2. **Chat Window Integration** (`FrontEnd/src/components/Chat/ChatWindow.jsx`)

**Upload Icon:**
```jsx
<button className="dw-upload-icon-btn" onClick={() => setShowDWUpload(true)}>
  <FiFileText />
  {hasTranscript && <span className="dw-transcript-badge" />}
</button>
```

**Upload Modal Features:**
- File input with validation (PDF only)
- Loading state during parsing
- Error display if upload fails
- Summary preview on success
- Quick action buttons that populate chat input
- Course check input for custom queries
- Delete button to remove all data

**State Management:**
```javascript
const [showDWUpload, setShowDWUpload] = useState(false);
const [dwUploading, setDwUploading] = useState(false);
const [dwUploadError, setDwUploadError] = useState(null);
const [dwSummary, setDwSummary] = useState(null);
const [courseCheckCode, setCourseCheckCode] = useState('');

const { hasTranscript, summary, refresh } = useContext(DegreeWorksContext);
```

**Upload Handler:**
```javascript
async function handleDegreeWorksFile(e) {
  const file = e.target.files[0];
  // Validate PDF
  // Call degreeWorksService.uploadDegreeWorks(file)
  // Fetch summary
  // Refresh global context
  // Show confirmation message in chat
}
```

#### 3. **Styling** (`FrontEnd/src/styles/chat.css`)

**Key Classes:**
- `.dw-upload-icon-btn` - Blue gradient button with hover effects
- `.dw-transcript-badge` - Green pulsing indicator
- `.dw-upload-modal` - Centered modal with backdrop blur
- `.dw-actions-grid` - Responsive grid for quick action buttons
- `.dw-action-btn` - Styled action buttons with hover animations
- `.dw-course-check-input` - Custom course code input field

---

## 🤖 Chatbot Question Handling

### Supported Question Types

#### 1. **Completed Courses**
**Questions:**
- "What classes have I already taken?"
- "Did I take COSC 111?"
- "Have I completed Data Structures?"
- "Show me all my completed courses."

**Chatbot Behavior:**
- Checks `courses.completed` list in Degree Works data
- Lists course codes, names, grades, and terms
- **NEVER says a course hasn't been taken if it's in the completed list**
- References specific grades: "You completed COSC 111 with an A in Fall 2023"

#### 2. **In-Progress Courses**
**Questions:**
- "What classes am I currently taking?"
- "What courses am I enrolled in this semester?"
- "What's my current course load?"

**Chatbot Behavior:**
- Checks `courses.in_progress` list
- Shows current semester courses
- Mentions credit hours and requirement categories

#### 3. **Remaining Courses**
**Questions:**
- "What classes do I still need to take?"
- "What CS courses are left for graduation?"
- "Which major requirements haven't I completed?"

**Chatbot Behavior:**
- Checks `courses.remaining` list
- Groups by category (Major Core, Electives, etc.)
- Estimates remaining credits

#### 4. **Academic Planning**
**Questions:**
- "What should I take next semester as a junior CS major?"
- "What are my options for next term?"
- "Recommend courses for next semester."

**Chatbot Behavior:**
- Uses classification (Junior) from Degree Works
- Analyzes remaining required courses
- Checks prerequisites (if available in requirement groups)
- Provides logical recommendations based on:
  - Remaining major core courses
  - Available electives
  - Prerequisite chains
  - Credit hour balance
- Clearly states recommendations are based on Degree Works data

#### 5. **Academic Status**
**Questions:**
- "What's my GPA?"
- "How many credits do I have?"
- "What's my classification?"
- "How far am I from graduation?"

**Chatbot Behavior:**
- Uses `academic_summary` directly from Degree Works
- Provides exact numbers (not estimates)
- Shows progress toward degree completion

---

## 🧪 Testing Guide

### Manual Testing Checklist

#### A. Upload Functionality
1. ✅ Log into the application
2. ✅ Navigate to chat interface
3. ✅ Verify Degree Works icon is visible (between Quick Questions and Send)
4. ✅ Click icon → modal opens
5. ✅ Select a Degree Works PDF
6. ✅ Verify "Analyzing PDF..." status appears
7. ✅ Verify summary preview shows (GPA, credits, classification)
8. ✅ Verify confirmation message appears in chat
9. ✅ Verify green badge appears on icon

#### B. Quick Action Buttons
1. ✅ Open upload modal after successful upload
2. ✅ Click "GPA & Credits" → input populated with question
3. ✅ Send message → verify chatbot answers with exact data
4. ✅ Click "In-Progress Courses" → verify accurate list
5. ✅ Click "Remaining Courses" → verify correct remaining courses
6. ✅ Click "Completed Courses" → verify all completed courses listed
7. ✅ Enter "COSC 111" in Course Check → verify chatbot confirms/denies with grade

#### C. Chat Integration
**Test Questions:**

```
Q: "Did I take COSC 111 and what grade did I earn?"
Expected: "Yes, you completed COSC 111 with a grade of A in Fall 2023."
Bug Check: Should NEVER say "You have not taken COSC 111" if it's in completed courses.

Q: "What classes am I currently taking?"
Expected: List of in-progress courses from current semester.

Q: "What classes do I still need to take?"
Expected: List of remaining required courses by category.

Q: "What should I take next semester as a junior CS major?"
Expected: Recommendations based on remaining courses, classification, and prerequisites.
```

#### D. Persistence
1. ✅ Upload Degree Works
2. ✅ Close browser
3. ✅ Restart Docker containers: `docker-compose restart`
4. ✅ Log back in
5. ✅ Verify green badge still shows
6. ✅ Ask chatbot a Degree Works question
7. ✅ Verify chatbot still has access to data

#### E. Deletion
1. ✅ Open upload modal
2. ✅ Click "Delete Data" button
3. ✅ Confirm deletion
4. ✅ Verify green badge disappears
5. ✅ Ask chatbot a Degree Works question
6. ✅ Verify chatbot says no data available and suggests uploading

#### F. Degree Works Page
1. ✅ Navigate to `/degree-works`
2. ✅ Verify uploaded file appears in list
3. ✅ Verify file name, upload date, and status
4. ✅ Verify detailed analysis displays correctly
5. ✅ Test version comparison (if multiple uploads)
6. ✅ Test individual version deletion

### Automated Test Script

Located at: `BackEnd/app/app/scripts/test_degree_works.py`

**Run with:**
```bash
docker exec morgan-chatbot-backend python /app/app/scripts/test_degree_works.py
```

**Tests:**
- PDF parsing accuracy
- Context formatting
- File storage operations
- API endpoint responses
- Chat integration

---

## 📊 Data Flow Diagram

```
┌─────────────────┐
│   Student       │
│  (Frontend)     │
└────────┬────────┘
         │
         │ 1. Click Degree Works Icon
         ▼
┌─────────────────────┐
│  Upload Modal       │
│  (ChatWindow.jsx)   │
└────────┬────────────┘
         │
         │ 2. Select PDF File
         ▼
┌──────────────────────────┐
│ degreeWorksService.js    │
│ POST /api/degree-works/  │
│           upload          │
└────────┬─────────────────┘
         │
         │ 3. Upload File
         ▼
┌──────────────────────────┐
│ degree_works.py          │
│ (API Route)              │
└────────┬─────────────────┘
         │
         │ 4. Parse PDF
         ▼
┌──────────────────────────┐
│ DegreeWorksParser        │
│ (degree_works_parser.py) │
└────────┬─────────────────┘
         │
         │ 5. Save to File Storage
         ▼
┌──────────────────────────┐
│ FileStorage              │
│ data/users/{id}/         │
│   degree_works/          │
└────────┬─────────────────┘
         │
         │ 6. Return Analysis
         ▼
┌──────────────────────────┐
│ Frontend                 │
│ - Show Summary           │
│ - Display Badge          │
│ - Refresh Context        │
└──────────────────────────┘

┌─────────────────────────┐
│ Chat Message Sent       │
└────────┬────────────────┘
         │
         │ 7. User Asks Question
         ▼
┌──────────────────────────┐
│ chat.py                  │
│ POST /api/chat/message   │
└────────┬─────────────────┘
         │
         │ 8. Get Degree Works Context
         ▼
┌──────────────────────────┐
│ openai_service.py        │
│ _get_degree_works_       │
│        context()         │
└────────┬─────────────────┘
         │
         │ 9. Load from File Storage
         ▼
┌──────────────────────────┐
│ FileStorage              │
│ get_user_degree_works_   │
│        files()           │
└────────┬─────────────────┘
         │
         │ 10. Format for Chatbot
         ▼
┌──────────────────────────┐
│ DegreeWorksParser        │
│ format_for_chatbot()     │
└────────┬─────────────────┘
         │
         │ 11. Inject as System Context
         ▼
┌──────────────────────────┐
│ GPT-4 API                │
│ (with Degree Works       │
│  context in messages)    │
└────────┬─────────────────┘
         │
         │ 12. Generate Response
         ▼
┌──────────────────────────┐
│ Frontend Chat UI         │
│ Display Answer           │
└──────────────────────────┘
```

---

## 🐛 Bug Fixes Implemented

### Issue: "Chatbot says user hasn't taken a class even though Degree Works shows it as completed"

**Root Cause:**
- Parser categorizing completed courses as "remaining" due to fuzzy pattern matching
- Chat context not being properly formatted
- Chatbot not strictly checking completed list before answering

**Solution:**
1. **Enhanced Parser Logic** (9-tier status determination):
   - Explicit grade checks (A-F, P, S = completed)
   - IP/Registered status = in-progress
   - Current semester detection = in-progress
   - Everything else = remaining

2. **Improved Context Formatting**:
   - Clear section headers (COMPLETED / IN-PROGRESS / REMAINING)
   - Explicit course codes and names in each list
   - Grades and terms included for completed courses

3. **Strengthened System Prompt**:
   ```
   "DEGREE WORKS TRANSCRIPT ANALYSIS:
   - For questions like 'Did I take COSC 111?', check the COMPLETED COURSES list
   - If asked about courses not in transcript, clearly state 'According to your 
     Degree Works transcript, you have not taken [course name] yet'
   - NEVER contradict completed courses shown in the degree audit"
   ```

4. **Validation**:
   - Automated test script verifies chatbot answers match parsed data
   - Manual test checklist includes bug regression tests

---

## 🔐 Security & Privacy

- All data scoped to authenticated user (`user_id` from JWT)
- File storage isolated per user in `data/users/{user_id}/`
- No cross-user data access possible
- Uploaded PDFs encrypted at rest (file system permissions)
- API endpoints require valid JWT token
- Delete operations cascade to remove all associated data

---

## 📈 Future Enhancements

1. **Advanced Recommendations**:
   - Prerequisite chain analysis
   - Course scheduling conflict detection
   - Four-year graduation plan generation

2. **Progress Tracking**:
   - Semester-by-semester progress visualization
   - GPA trend analysis across versions
   - Completion percentage by requirement category

3. **Integration**:
   - Direct Degree Works API integration (no PDF upload)
   - Automatic semester updates via web scraping
   - Real-time course availability checking

4. **Analytics**:
   - Department-wide aggregated statistics
   - Popular course sequences
   - Average time-to-degree by classification

---

## 🎓 Conclusion

The Degree Works feature is **fully functional** with:
- ✅ No TODO items remaining
- ✅ Complete upload, parsing, and storage pipeline
- ✅ Seamless chat integration with context injection
- ✅ Persistent data across restarts
- ✅ User-friendly UI with quick actions
- ✅ Robust error handling and validation
- ✅ Bug fixes for completion status detection
- ✅ Comprehensive testing coverage

Students can now upload their transcript once and receive accurate, personalized academic guidance from the Morgan AI chatbot.
