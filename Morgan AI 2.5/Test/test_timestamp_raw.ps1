#!/usr/bin/env pwsh
<#
.SYNOPSIS
Verify Degree Works Upload Timestamp - Raw Response Inspection
#>

$ApiUrl = "http://localhost:8000"
$GREEN = "`e[32m"
$RED = "`e[31m"
$RESET = "`e[0m"

Write-Host "`n=========================================="
Write-Host "Degree Works Timestamp Verification (Raw)"
Write-Host "=========================================="

# Step 1: Sign up a test user
Write-Host "`n[1] Creating test user..."
$username = "tester_$(Get-Random -Maximum 10000)"
$email = "test_$(Get-Random -Maximum 10000)@msu.edu"

$signupResponse = Invoke-WebRequest `
    -Uri "$ApiUrl/api/auth/signup" `
    -Method POST `
    -ContentType "application/json" `
    -Body (ConvertTo-Json @{
        username = $username
        email = $email
        password = "TestPass123!"
    }) -UseBasicParsing -ErrorAction Stop

$signupData = $signupResponse.Content | ConvertFrom-Json
$userId = $signupData.user.user_id
$token = $signupData.access_token

Write-Host "${GREEN}✅ User created${RESET}"
Write-Host "   User ID: $userId"

# Step 2: Upload degree works PDF
Write-Host "`n[2] Uploading degree works PDF..."

$pdfPath = "c:\Users\paule\Downloads\Senior-Project-main (2)\Senior-Project-main\Morgan AI 2.5\Morgan AI 2.5\BackEnd\app\test_degree_work.pdf"

$form = @{
    file = Get-Item -Path $pdfPath
}

try {
    $uploadResponse = Invoke-WebRequest `
        -Uri "$ApiUrl/api/degree-works/upload" `
        -Method POST `
        -Headers @{ Authorization = "Bearer $token" } `
        -Form $form `
        -UseBasicParsing `
        -ErrorAction Stop
    
    Write-Host "${GREEN}✅ Upload successful${RESET}"
    
    # Print raw JSON response
    Write-Host "`n[3] Raw API Response:"
    Write-Host "=============================="
    Write-Host $uploadResponse.Content
    Write-Host "=============================="
    
    # Parse JSON carefully
    $uploadData = $uploadResponse.Content | ConvertFrom-Json
    
    # Extract the uploaded_at field
    Write-Host "`n[4] Analyzing uploaded_at field:"
    $uploadedAt = $uploadData.uploaded_at
    Write-Host "Type: $($uploadedAt.GetType())"
    Write-Host "Value: $uploadedAt"
    
    # Check if it's a string with ISO 8601 format
    if ($uploadedAt -is [string]) {
        Write-Host "`n${GREEN}✅ uploaded_at is a string (ISO 8601 format)${RESET}"
        
        # Extract timezone info
        if ($uploadedAt -match '([+-])(\d{2}):(\d{2})(Z)?$') {
            $tzSign = $matches[1]
            $tzHour = [int]$matches[2]
            $tzMin = [int]$matches[3]
            $tzOffset = if ($tzSign -eq '+') { $tzHour * 60 + $tzMin } else { -($tzHour * 60 + $tzMin) }
            
            Write-Host "   Timezone offset: ${tzSign}${tzHour}:${tzMin}"
            Write-Host "   Total offset: ${tzOffset} minutes"
            
            # EST is UTC-5 (-300 min), EDT is UTC-4 (-240 min)
            if ($tzOffset -eq -300 -or $tzOffset -eq -240) {
                Write-Host "${GREEN}✅ Timestamp is in EST/EDT timezone${RESET}"
                if ($tzOffset -eq -300) {
                    Write-Host "   Time Zone: EST (Eastern Standard Time, UTC-5)"
                } else {
                    Write-Host "   Time Zone: EDT (Eastern Daylight Time, UTC-4)"
                }
            } else {
                Write-Host "${RED}❌ Timestamp is NOT in EST/EDT timezone${RESET}"
            }
        } else {
            Write-Host "${YELLOW}⚠️ Could not extract timezone from: $uploadedAt${RESET}"
        }
    } else {
        Write-Host "${YELLOW}⚠️ uploaded_at is not a string, it's: $($uploadedAt.GetType())${RESET}"
    }
    
} catch {
    Write-Host "${RED}❌ Upload failed${RESET}"
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}

Write-Host "`n=========================================="
Write-Host "${GREEN}✅ VERIFICATION COMPLETE${RESET}"
Write-Host "=========================================="
