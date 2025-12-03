# Degree Works AI Integration - Complete Guide

## Overview

The Morgan AI chatbot **automatically accesses uploaded Degree Works transcripts** to answer personalized student questions. When a student uploads their Degree Works PDF, the AI can analyze it to answer questions like:

- "Did I take COSC 111?"
- "What courses am I taking this semester?"
- "How many credits do I have left?"
- "What's my GPA?"
- "Have I completed Data Structures?"

## How It Works

### 1. **Student Uploads Degree Works PDF**
- Student logs into the web UI
- Navigates to Degree Works section
- Uploads their Degree Works PDF transcript
- System automatically parses and stores the data in PostgreSQL database

### 2. **AI Automatically Retrieves Transcript Data**
When a student asks a question, the AI:
1. Checks if the user has an uploaded Degree Works file in the database
2. Retrieves the most recent parsed transcript data
3. Includes it in the AI context as "Student's Academic Record"
4. AI analyzes the data to answer the question

### 3. **AI Responds with Personalized Information**
The AI can reference:
- **Completed Courses**: Courses student has already taken with grades
- **In-Progress Courses**: Currently enrolled courses
- **Remaining Courses**: Required courses not yet taken
- **Academic Stats**: GPA, credits completed, classification

## Database Integration

### Storage Location
```
PostgreSQL Database: degree_works_files table
├── id (UUID)
├── user_id (Foreign key to users)
├── filename (Original PDF name)
├── file_path (Storage location)
├── parsed_data (JSON with all extracted info)
├── is_processed (Boolean)
└── uploaded_at (Timestamp)
```

### Parsed Data Structure
```json
{
  "success": true,
  "student_info": {
    "name": "John Doe",
    "student_id": "123456",
    "major": "Computer Science"
  },
  "academic_summary": {
    "gpa": 3.5,
    "completed_credits": 90,
    "in_progress_credits": 12,
    "total_credits_required": 120,
    "remaining_credits": 18,
    "classification": "Senior"
  },
  "courses": {
    "completed": [
      {
        "course_code": "COSC 111",
        "course_name": "Programming I",
        "credits": 4,
        "grade": "A",
        "semester": "Fall 2022",
        "category": "Core CS"
      }
    ],
    "in_progress": [
      {
        "course_code": "COSC 340",
        "course_name": "Artificial Intelligence",
        "credits": 3,
        "semester": "Fall 2025",
        "category": "Core CS"
      }
    ],
    "remaining": [
      {
        "course_code": "COSC 400",
        "course_name": "Senior Capstone",
        "credits": 3,
        "category": "Core CS"
      }
    ]
  }
}
```

## System Prompt Instructions

The AI has been instructed to:

```
DEGREE WORKS TRANSCRIPT ANALYSIS:
- When a student's Degree Works data is provided, use it to answer personalized questions
- For "Did I take COSC 111?" → Check COMPLETED COURSES list
- For "What am I taking now?" → Check IN-PROGRESS COURSES list
- For "What do I still need?" → Check REMAINING REQUIRED COURSES list
- Always reference specific course codes, names, and grades
- If course not in transcript: "According to your Degree Works, you have not taken [course] yet"
- Use actual GPA, credits, classification from transcript
- If no Degree Works: Suggest uploading transcript for personalized guidance
```

## Code Implementation

### OpenAI Service - Degree Works Retrieval
```python
async def _get_degree_works_context(self, user_id: str) -> Optional[str]:
    """Retrieve Degree Works context from database"""
    from app.core.database import get_db
    from app.core.db_operations import get_latest_degree_works
    from app.services.degree_works_parser import DegreeWorksParser
    
    async for db in get_db():
        # Get latest file from database
        degree_works_file = await get_latest_degree_works(db, user_id)
        
        if not degree_works_file or not degree_works_file.parsed_data:
            return None
        
        # Format for chatbot
        parser = DegreeWorksParser()
        context = parser.format_for_chatbot(degree_works_file.parsed_data)
        return context
```

### Chat Response Generation
```python
# Get Degree Works context if available
if user_id:
    degree_works_context = await self._get_degree_works_context(user_id)
    if degree_works_context:
        messages.append({
            "role": "system",
            "content": f"Student's Academic Record:\n{degree_works_context}"
        })
```

## Example Conversations

### Example 1: Course Completion Check
**Student**: "Did I take COSC 111?"

**AI**: "Yes, according to your Degree Works transcript, you completed COSC 111: Programming I in Fall 2022 with a grade of A. This is a 4-credit core CS requirement."

### Example 2: Current Enrollment
**Student**: "What courses am I taking this semester?"

**AI**: "Based on your Degree Works, you are currently enrolled in:
1. COSC 340: Artificial Intelligence (3 credits)
2. COSC 360: Cybersecurity Fundamentals (3 credits)
3. COSC 400: Senior Capstone I (3 credits)

Total: 9 credits in progress for Fall 2025."

### Example 3: Remaining Requirements
**Student**: "What CS courses do I still need to graduate?"

**AI**: "According to your Degree Works, you still need to complete:
1. COSC 401: Senior Capstone II (3 credits)
2. CS Elective (3 credits)

You have 18 credits remaining total, with 6 being core CS requirements."

### Example 4: Academic Progress
**Student**: "How many credits have I completed and what's my GPA?"

**AI**: "Based on your Degree Works transcript:
- Credits Completed: 90 credits
- Current GPA: 3.50
- Classification: Senior
- Credits Remaining: 18 credits (you need 120 total)

You're on track to graduate after completing your remaining courses!"

### Example 5: Course Not Taken
**Student**: "Have I taken Quantum Computing?"

**AI**: "According to your Degree Works transcript, you have not taken Quantum Computing yet. This would typically be an advanced elective course. Would you like to know the prerequisites or when it's offered?"

## Testing

### Using the Test Script
```powershell
# Run the automated test
.\Test\test_degree_works_chatbot.ps1
```

### Manual Testing Steps
1. **Upload Degree Works**:
   - Login to UI: http://localhost
   - Navigate to Degree Works section
   - Upload your PDF transcript

2. **Ask Questions**:
   - "Did I take Data Structures?"
   - "What's my GPA?"
   - "What courses am I taking now?"
   - "How many credits do I have left?"

3. **Verify Backend Logs**:
   ```powershell
   docker-compose logs backend --tail 50 | Select-String "Degree Works"
   ```

## Benefits

✅ **Personalized Responses**: AI knows each student's exact academic history
✅ **Accurate Information**: Data comes directly from official Degree Works transcript
✅ **Automatic Updates**: Upload new transcript anytime for updated information
✅ **Privacy**: Each student only sees their own data
✅ **Comprehensive**: AI can answer complex questions combining transcript + knowledge base
✅ **Database Persistence**: Data survives container restarts

## Troubleshooting

### "No Degree Works data found"
**Solution**: Student needs to upload their Degree Works PDF via the UI

### AI not using transcript data
**Check**:
```powershell
# Verify file in database
docker-compose exec postgres psql -U postgres -d morganai_db -c "SELECT id, user_id, filename, is_processed FROM degree_works_files;"

# Check backend logs
docker-compose logs backend | Select-String "Degree Works context"
```

### Parsed data empty
**Solution**: Re-upload the PDF - parser may have failed on first attempt

## Future Enhancements

- [ ] Auto-refresh from WebSIS integration
- [ ] Multi-semester comparison
- [ ] Graduation timeline predictions
- [ ] Course sequence recommendations
- [ ] Prerequisite violation warnings
- [ ] GPA projection based on current grades

## Technical Details

- **Parser**: PyPDF2-based extraction with regex pattern matching
- **Storage**: PostgreSQL with JSON column for parsed_data
- **Context Size**: ~2000-5000 chars per transcript
- **Retrieval**: Async database query per chat request
- **Caching**: None (queries database each time for accuracy)
- **Format**: Natural language summary for AI consumption
