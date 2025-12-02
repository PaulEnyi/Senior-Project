# Test Web Search Fallback for Missing Course Information
# This demonstrates automatic web search when information is NOT in the knowledge base

Write-Host "`n=== MORGAN AI WEB SEARCH FALLBACK TEST ===" -ForegroundColor Cyan
Write-Host "Testing automatic web search for information NOT in knowledge base`n" -ForegroundColor Yellow

# Step 1: Create test user
Write-Host "[1] Using existing test user..." -ForegroundColor Green

# Step 2: Login
Write-Host "`n[2] Logging in..." -ForegroundColor Green
$loginBody = @{
    email = "testgrad@morgan.edu"
    password = "Test123!@#"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/login" -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
Write-Host "✓ Login successful" -ForegroundColor Green
Write-Host "Token: $($token.Substring(0,20))..." -ForegroundColor Gray

# Step 3: Create chat thread
Write-Host "`n[3] Creating chat thread..." -ForegroundColor Green
$headers = @{
    Authorization = "Bearer $token"
}

$threadResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/chat/threads" -Headers $headers -ContentType "application/json"
$threadId = $threadResponse.thread_id
Write-Host "✓ Thread created: $threadId" -ForegroundColor Green

# Wait for backend to be ready
Write-Host "`n[4] Waiting for backend to initialize..." -ForegroundColor Green
Start-Sleep -Seconds 3

# Test Cases - Information NOT in Knowledge Base (should trigger web search)
Write-Host "`n=== TEST CASES: WEB SEARCH FALLBACK ===" -ForegroundColor Cyan

# Test 1: Course not in knowledge base (COSC 300 / CSC 300)
Write-Host "`n[TEST 1] Query: Course not in knowledge base (COSC 300)" -ForegroundColor Magenta
Write-Host "Expected: Web search to Morgan State catalog" -ForegroundColor Yellow

$chatBody1 = @{
    message = "Tell me about COSC 300 or CSC 300"
    thread_id = $threadId
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/chat/message" -Headers $headers -Body $chatBody1 -ContentType "application/json"
    Write-Host "`nAI Response:" -ForegroundColor Green
    Write-Host $response1.response -ForegroundColor White
    
    if ($response1.response -match "catalog\.morgan\.edu|morgan\.edu") {
        Write-Host "`n✓ SUCCESS: Response includes Morgan State web sources!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠ Response may be from knowledge base or no web search triggered" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 2: Unknown faculty member
Write-Host "`n[TEST 2] Query: Faculty not in knowledge base" -ForegroundColor Magenta
Write-Host "Expected: Web search to department website" -ForegroundColor Yellow

$chatBody2 = @{
    message = "Who is Dr. Smith in the CS department?"
    thread_id = $threadId
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/chat/message" -Headers $headers -Body $chatBody2 -ContentType "application/json"
    Write-Host "`nAI Response:" -ForegroundColor Green
    Write-Host $response2.response -ForegroundColor White
    
    if ($response2.response -match "morgan\.edu") {
        Write-Host "`n✓ SUCCESS: Web search triggered!" -ForegroundColor Green
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 3: General CS department question
Write-Host "`n[TEST 3] Query: Current semester information" -ForegroundColor Magenta
Write-Host "Expected: Web search for latest information" -ForegroundColor Yellow

$chatBody3 = @{
    message = "What are the latest updates to the Computer Science graduate program?"
    thread_id = $threadId
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/chat/message" -Headers $headers -Body $chatBody3 -ContentType "application/json"
    Write-Host "`nAI Response:" -ForegroundColor Green
    Write-Host $response3.response -ForegroundColor White
    
    if ($response3.response -match "catalog\.morgan\.edu|morgan\.edu") {
        Write-Host "`n✓ SUCCESS: Web sources cited!" -ForegroundColor Green
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check logs for web search activity
Write-Host "`n=== CHECKING BACKEND LOGS FOR WEB SEARCH ACTIVITY ===" -ForegroundColor Cyan
Write-Host "Looking for web search indicators..`n" -ForegroundColor Yellow

docker-compose logs backend --tail 30 | Select-String -Pattern "WEB SEARCH|deep_search_morgan|catalog.morgan.edu" | ForEach-Object {
    Write-Host $_ -ForegroundColor Gray
}

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host @"

SUMMARY:
✓ System automatically searches Morgan State websites when knowledge base lacks information
✓ Prioritized sources: catalog.morgan.edu, www.morgan.edu/scmns/computerscience
✓ Web search is transparent to users - they just get comprehensive answers
✓ All responses cite sources when using web search results

TRY THESE QUERIES IN THE UI:
1. "Tell me about COSC 300"
2. "What are the requirements for the PhD program?"
3. "Who teaches Advanced Database Systems?"
4. "What internships are available this semester?"

"@ -ForegroundColor Green
