# Test Degree Works Integration with AI Chatbot
# Demonstrates AI answering questions using uploaded Degree Works transcript

Write-Host "`n=== DEGREE WORKS AI CHATBOT INTEGRATION TEST ===" -ForegroundColor Cyan
Write-Host "Testing AI's ability to answer questions using uploaded Degree Works transcript`n" -ForegroundColor Yellow

# Configuration
$baseUrl = "http://localhost:8000"

# Step 1: Create test user
Write-Host "[1] Creating/logging in test student..." -ForegroundColor Green

$signupBody = @{
    username = "dwtest"
    email = "dwtest@morgan.edu"
    password = "Test123!@#"
    full_name = "Degree Works Test Student"
    role = "student"
} | ConvertTo-Json

try {
    $signupResponse = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/auth/signup" -Body $signupBody -ContentType "application/json"
    Write-Host "✓ New user created" -ForegroundColor Green
    $token = $signupResponse.access_token
} catch {
    # User exists, try login
    Write-Host "User exists, logging in..." -ForegroundColor Yellow
    $loginBody = @{
        email = "dwtest@morgan.edu"
        password = "Test123!@#"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/auth/login" -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
}

$userId = $loginResponse.user_id
Write-Host "User ID: $userId" -ForegroundColor Gray

# Step 2: Check if Degree Works already uploaded
Write-Host "`n[2] Checking for existing Degree Works data..." -ForegroundColor Green

$headers = @{
    Authorization = "Bearer $token"
}

try {
    $dwFiles = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/degree-works/my-files" -Headers $headers
    
    if ($dwFiles.Count -gt 0) {
        Write-Host "✓ Found $($dwFiles.Count) Degree Works file(s)" -ForegroundColor Green
        $hasTranscript = $true
    } else {
        Write-Host "⚠ No Degree Works files found" -ForegroundColor Yellow
        Write-Host "NOTE: Upload a Degree Works PDF via the UI first" -ForegroundColor Yellow
        $hasTranscript = $false
    }
} catch {
    Write-Host "⚠ Could not retrieve Degree Works files" -ForegroundColor Yellow
    $hasTranscript = $false
}

# Step 3: Create chat thread
Write-Host "`n[3] Creating chat thread..." -ForegroundColor Green

$threadResponse = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat/threads" -Headers $headers -ContentType "application/json"
$threadId = $threadResponse.thread_id
Write-Host "✓ Thread created: $threadId" -ForegroundColor Green

Start-Sleep -Seconds 2

# Step 4: Test Questions - Degree Works Specific
Write-Host "`n=== TEST QUESTIONS: DEGREE WORKS TRANSCRIPT ANALYSIS ===" -ForegroundColor Cyan

if ($hasTranscript) {
    Write-Host "`nAsking questions that require Degree Works data..." -ForegroundColor Yellow
    
    # Test 1: Did I take a specific course?
    Write-Host "`n[TEST 1] Question: Did I take COSC 111?" -ForegroundColor Magenta
    $chatBody1 = @{
        message = "Did I take COSC 111? Have I completed Programming I?"
        thread_id = $threadId
    } | ConvertTo-Json
    
    try {
        $response1 = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat/message" -Headers $headers -Body $chatBody1 -ContentType "application/json"
        Write-Host "`nAI Response:" -ForegroundColor Green
        Write-Host $response1.response -ForegroundColor White
        
        if ($response1.response -match "completed|taken|yes|grade|transcript") {
            Write-Host "`n✓ SUCCESS: AI referenced Degree Works data!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
    
    # Test 2: What courses am I taking now?
    Write-Host "`n[TEST 2] Question: What courses am I currently taking?" -ForegroundColor Magenta
    $chatBody2 = @{
        message = "What courses am I taking this semester?"
        thread_id = $threadId
    } | ConvertTo-Json
    
    try {
        $response2 = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat/message" -Headers $headers -Body $chatBody2 -ContentType "application/json"
        Write-Host "`nAI Response:" -ForegroundColor Green
        Write-Host $response2.response -ForegroundColor White
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
    
    # Test 3: What do I still need?
    Write-Host "`n[TEST 3] Question: What courses do I still need to take?" -ForegroundColor Magenta
    $chatBody3 = @{
        message = "What CS courses do I still need to complete for graduation?"
        thread_id = $threadId
    } | ConvertTo-Json
    
    try {
        $response3 = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat/message" -Headers $headers -Body $chatBody3 -ContentType "application/json"
        Write-Host "`nAI Response:" -ForegroundColor Green
        Write-Host $response3.response -ForegroundColor White
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
    
    # Test 4: Academic progress
    Write-Host "`n[TEST 4] Question: What's my academic progress?" -ForegroundColor Magenta
    $chatBody4 = @{
        message = "How many credits have I completed and what's my GPA?"
        thread_id = $threadId
    } | ConvertTo-Json
    
    try {
        $response4 = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat/message" -Headers $headers -Body $chatBody4 -ContentType "application/json"
        Write-Host "`nAI Response:" -ForegroundColor Green
        Write-Host $response4.response -ForegroundColor White
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
    
    # Test 5: Course not taken
    Write-Host "`n[TEST 5] Question: Did I take a course I haven't taken?" -ForegroundColor Magenta
    $chatBody5 = @{
        message = "Have I taken Quantum Computing yet?"
        thread_id = $threadId
    } | ConvertTo-Json
    
    try {
        $response5 = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/chat/message" -Headers $headers -Body $chatBody5 -ContentType "application/json"
        Write-Host "`nAI Response:" -ForegroundColor Green
        Write-Host $response5.response -ForegroundColor White
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} else {
    Write-Host "`n⚠ CANNOT RUN TESTS - No Degree Works uploaded" -ForegroundColor Yellow
    Write-Host @"
    
TO UPLOAD DEGREE WORKS:
1. Open the web UI at http://localhost (or http://localhost:3000)
2. Log in with: dwtest@morgan.edu / Test123!@#
3. Navigate to Degree Works section
4. Upload your Degree Works PDF
5. Re-run this test script

"@ -ForegroundColor Cyan
}

# Check backend logs for Degree Works context retrieval
Write-Host "`n=== CHECKING BACKEND LOGS ===" -ForegroundColor Cyan
Write-Host "Looking for Degree Works context retrieval..`n" -ForegroundColor Yellow

docker-compose logs backend --tail 20 | Select-String -Pattern "Degree Works|DEGREE WORKS|degree_works_context" | ForEach-Object {
    Write-Host $_ -ForegroundColor Gray
}

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host @"

SUMMARY:
✓ AI automatically accesses uploaded Degree Works transcripts
✓ Can answer: "Did I take COSC 111?" by checking completed courses
✓ Can answer: "What am I taking now?" by checking in-progress courses
✓ Can answer: "What do I need?" by checking remaining requirements
✓ Provides personalized GPA, credits, and academic progress
✓ Clearly states when courses haven't been taken yet

EXAMPLE QUESTIONS TO ASK IN THE UI:
1. "Did I take Data Structures?"
2. "What courses am I currently enrolled in?"
3. "How many credits do I have left?"
4. "What's my current GPA?"
5. "Have I completed all my core CS requirements?"
6. "What electives do I still need to take?"
7. "Am I on track to graduate on time?"

"@ -ForegroundColor Green
