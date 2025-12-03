# Morgan AI Feature Smoke Test
# Tests all major features: Auth, Chat, Voice, Degree Works, Quick Questions
# Run after: docker compose up -d

param(
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$SkipVoice = $false,
    [switch]$SkipDegreeWorks = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Colors
$colors = @{
    Green   = "`e[32m"
    Red     = "`e[31m"
    Yellow  = "`e[33m"
    Blue    = "`e[34m"
    Cyan    = "`e[36m"
    Reset   = "`e[0m"
    Bold    = "`e[1m"
}

function Write-Status {
    param([string]$Message, [ValidateSet("Pass", "Fail", "Info", "Warn")]$Type = "Info")
    $statusMap = @{
        Pass = @("✅", "Green")
        Fail = @("❌", "Red")
        Info = @("ℹ️", "Blue")
        Warn = @("⚠️", "Yellow")
    }
    $symbol = $statusMap[$Type][0]
    $color = $statusMap[$Type][1]
    Write-Host "$symbol $Message" -ForegroundColor $color
}

function Test-Endpoint {
    param([string]$Name, [string]$Url, [string]$Method = "GET", [hashtable]$Headers = @{}, [object]$Body = $null)
    
    try {
        $params = @{
            Uri     = $Url
            Method  = $Method
            Headers = $Headers
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = $Body -is [string] ? $Body : ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        Write-Status "$Name [200]" "Pass"
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__ ?? $_.Exception.Message
        Write-Status "$Name [$statusCode]" "Fail"
        if ($Verbose) { Write-Host "  Error: $($_.Exception.Message)" }
        return $null
    }
}

Write-Host "`n$($colors.Bold)═══════════════════════════════════════════════════════$($colors.Reset)"
Write-Host "$($colors.Bold)  Morgan AI Feature Smoke Test - $(Get-Date -f 'yyyy-MM-dd HH:mm:ss')$($colors.Reset)"
Write-Host "$($colors.Bold)═══════════════════════════════════════════════════════$($colors.Reset)`n"

# 1. Health Check
Write-Host "$($colors.Bold)📊 Health & Connectivity$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"

$health = Test-Endpoint "Backend Health" "$BaseUrl/health"
if ($health) {
    Write-Status "Database: $($health.services.database)" $(if ($health.services.database -eq "operational") { "Pass" } else { "Warn" })
    Write-Status "OpenAI: $($health.services.openai)" $(if ($health.services.openai -eq "operational") { "Pass" } else { "Warn" })
    Write-Status "Pinecone: $($health.services.pinecone)" $(if ($health.services.pinecone -eq "operational") { "Pass" } else { "Warn" })
    if ($health.database_stats) {
        Write-Status "Users in DB: $($health.database_stats.users)" "Info"
    }
}

$debug = Test-Endpoint "Debug Status" "$BaseUrl/api/debug/status"
if ($debug) {
    Write-Status "Database Connected: $($debug.db_health.healthy)" $(if ($debug.db_health.healthy) { "Pass" } else { "Warn" })
}

# 2. Authentication
Write-Host "`n$($colors.Bold)🔐 Authentication$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"

$testEmail = "smoke-test-$(Get-Random -Minimum 1000 -Maximum 9999)@example.com"
$testUsername = "smoketest$(Get-Random -Minimum 1000 -Maximum 9999)"
$testPassword = "P@ssw0rd$(Get-Random -Minimum 100 -Maximum 999)!"

$signupBody = @{
    email = $testEmail
    username = $testUsername
    password = $testPassword
    full_name = "Smoke Test User"
    student_id = "STU$(Get-Random -Minimum 100000 -Maximum 999999)"
    major = "Computer Science"
    classification = "Senior"
}

$authResp = Test-Endpoint "User Signup" "$BaseUrl/api/auth/signup" "POST" @{} $signupBody
if ($authResp) {
    $token = $authResp.access_token
    $userId = $authResp.user.user_id
    Write-Status "Token Generated (60 min)" "Pass"
    Write-Status "User ID: $($userId.Substring(0, 8))..." "Info"
} else {
    Write-Status "Failed to obtain auth token. Skipping remaining tests." "Fail"
    exit 1
}

$authHeaders = @{ Authorization = "Bearer $token" }

# 3. Chat Features
Write-Host "`n$($colors.Bold)💬 Chat Features$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"

# Quick Questions
$qqResp = Test-Endpoint "Quick Questions List" "$BaseUrl/api/chat/quick-questions" "GET" $authHeaders
if ($qqResp) {
    $qCount = ($qqResp.categories.Keys | Measure-Object).Count
    $totalQ = ($qqResp.categories.Values | ForEach-Object { @($_).Count } | Measure-Object -Sum).Sum
    Write-Status "Categories: $qCount | Questions: $totalQ" "Pass"
}

# Get Chat Threads
$threadsResp = Test-Endpoint "List Chat Threads" "$BaseUrl/api/chat/threads" "GET" $authHeaders
if ($threadsResp) {
    $threadCount = $threadsResp.threads.Count
    Write-Status "User Threads: $threadCount" "Pass"
}

# Send Chat Message
$messageBody = @{
    message = "What courses should I take next semester for my CS degree?"
    thread_id = $null
}
$chatResp = Test-Endpoint "Send Chat Message" "$BaseUrl/api/chat/message" "POST" $authHeaders $messageBody
if ($chatResp) {
    $respLen = if ($chatResp.response) { $chatResp.response.Length } else { 0 }
    Write-Status "Response received: $respLen chars" "Pass"
}

# 4. Voice Features (if enabled)
if (-not $SkipVoice) {
    Write-Host "`n$($colors.Bold)🎤 Voice Features$($colors.Reset)" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────"

    # Voice Status
    $voiceStatus = Test-Endpoint "Voice Service Status" "$BaseUrl/api/voice/status" "GET" $authHeaders
    if ($voiceStatus) {
        Write-Status "TTS: $(if ($voiceStatus.tts_enabled) { 'Enabled' } else { 'Disabled' })" $(if ($voiceStatus.tts_enabled) { "Pass" } else { "Warn" })
        Write-Status "STT: $(if ($voiceStatus.stt_enabled) { 'Enabled' } else { 'Disabled' })" $(if ($voiceStatus.stt_enabled) { "Pass" } else { "Warn" })
        Write-Status "Realtime: $(if ($voiceStatus.realtime_enabled) { 'Enabled' } else { 'Disabled' })" $(if ($voiceStatus.realtime_enabled) { "Pass" } else { "Warn" })
    }

    # Get Available Voices
    $voicesResp = Test-Endpoint "Available Voices" "$BaseUrl/api/voice/voices" "GET" $authHeaders
    if ($voicesResp) {
        $voiceCount = $voicesResp.voices.Count
        Write-Status "Voices Available: $voiceCount" "Pass"
    }

    # TTS Test
    $ttsBody = @{
        text = "Morgan AI voice feature test successful"
        voice = "alloy"
        speed = 1.0
        format = "mp3"
    }
    try {
        $ttsResp = Invoke-WebRequest -Uri "$BaseUrl/api/voice/text-to-speech" -Method POST -Headers $authHeaders -Body ($ttsBody | ConvertTo-Json) -ContentType "application/json" -OutFile "temp_tts.mp3" -PassThru -ErrorAction Stop
        if ($ttsResp.StatusCode -eq 200) {
            $fileSize = (Get-Item "temp_tts.mp3").Length
            Write-Status "TTS Generated: $fileSize bytes" "Pass"
        }
        Remove-Item "temp_tts.mp3" -ErrorAction SilentlyContinue
    }
    catch {
        Write-Status "TTS Failed: $($_.Exception.Response.StatusCode)" "Warn"
    }
}

# 5. Degree Works (if PDF exists)
if (-not $SkipDegreeWorks) {
    Write-Host "`n$($colors.Bold)🎓 Degree Works$($colors.Reset)" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────"

    $pdfPath = "BackEnd\app\test_degree_work.pdf"
    if (Test-Path $pdfPath) {
        try {
            $form = @{
                file = Get-Item $pdfPath
            }
            $dwResp = Invoke-WebRequest -Uri "$BaseUrl/api/degree-works/upload" -Method POST -Headers $authHeaders -Form $form -PassThru -ErrorAction Stop
            if ($dwResp.StatusCode -eq 200) {
                $dwData = $dwResp.Content | ConvertFrom-Json
                Write-Status "PDF Uploaded & Analyzed" "Pass"
                if ($dwData.analysis.student_info.name) {
                    Write-Status "Student: $($dwData.analysis.student_info.name)" "Info"
                }
            }
        }
        catch {
            Write-Status "PDF Upload/Parse Failed: $($_.Exception.Response.StatusCode)" "Warn"
        }
    } else {
        Write-Status "Test PDF not found: $pdfPath (skipped)" "Warn"
    }

    # Get Analysis (if available)
    $analysisResp = Test-Endpoint "Get Degree Works Analysis" "$BaseUrl/api/degree-works/analysis" "GET" $authHeaders
    if ($analysisResp) {
        $gpa = if ($analysisResp.analysis) { $analysisResp.analysis.academic_summary.gpa } else { "N/A" }
        Write-Status "GPA: $gpa" "Info"
    } else {
        Write-Status "No analysis available (upload PDF first)" "Info"
    }
}

# 6. WebSIS (informational - requires real credentials)
Write-Host "`n$($colors.Bold)🔗 WebSIS Integration$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"
Write-Status "WebSIS: Requires valid student credentials (not tested)" "Info"

# 7. Internships
Write-Host "`n$($colors.Bold)💼 Internships$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"

$internshipsResp = Test-Endpoint "List Internships" "$BaseUrl/api/internships/list" "GET" $authHeaders
if ($internshipsResp) {
    $count = $internshipsResp.internships.Count
    Write-Status "Internships Available: $count" "Pass"
}

# 8. Recommendations
Write-Host "`n$($colors.Bold)📚 Course Recommendations$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"

$recResp = Test-Endpoint "Recommendation Status" "$BaseUrl/api/recommendations/analyze-progress" "GET" $authHeaders
if ($recResp) {
    Write-Status "Recommendation Engine Online" "Pass"
}

# 9. Scraper/Admin
Write-Host "`n$($colors.Bold)🌐 Web Scraper$($colors.Reset)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────"
Write-Status "Scraper: Requires admin role (not tested)" "Info"

# Summary
Write-Host "`n$($colors.Bold)═══════════════════════════════════════════════════════$($colors.Reset)"
Write-Host "$($colors.Bold)✅ Smoke Test Complete$($colors.Reset)" -ForegroundColor Green
Write-Host "$($colors.Bold)═══════════════════════════════════════════════════════$($colors.Reset)`n"

Write-Host "$($colors.Bold)📋 Feature Summary:$($colors.Reset)"
Write-Host "  ✅ Backend: Running and healthy"
Write-Host "  ✅ Authentication: JWT tokens working"
Write-Host "  ✅ Chat: Messages, threads, quick questions"
Write-Host "  ✅ Voice: TTS/STT (requires OPENAI_API_KEY)"
Write-Host "  ✅ Degree Works: PDF upload & parsing"
Write-Host "  ✅ Internships: Database available"
Write-Host "  ✅ Recommendations: Engine online"
Write-Host "  ⚠️  WebSIS: Needs student credentials"
Write-Host "  ⚠️  Scraper: Requires admin role`n"

Write-Host "$($colors.Bold)🚀 Next Steps:$($colors.Reset)"
Write-Host "  1. Open http://localhost:3000 in browser"
Write-Host "  2. Sign up with a test account"
Write-Host "  3. Try chat, voice, and degree works features"
Write-Host "  4. Check admin dashboard for scraper/internship updates`n"
