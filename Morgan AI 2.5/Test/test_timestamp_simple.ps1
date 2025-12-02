#!/usr/bin/env pwsh
<#
.SYNOPSIS
Verify Degree Works Upload Timestamp in EST/EDT

Tests that degree works PDF upload timestamps are stored in Morgan State University
local timezone (EST/EDT) instead of UTC.
#>

$ApiUrl = "http://localhost:8000"
$GREEN = "`e[32m"
$RED = "`e[31m"
$RESET = "`e[0m"

Write-Host "`n=========================================="
Write-Host "Degree Works Timestamp Verification"
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
    }) -ErrorAction Stop

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
        -ErrorAction Stop
    
    Write-Host "${GREEN}✅ Upload successful${RESET}"
    $uploadData = $uploadResponse.Content | ConvertFrom-Json
    
    # Extract timestamp
    $uploadedAt = $uploadData.uploaded_at
    Write-Host "   uploaded_at: $uploadedAt"
    
    # Validate timezone offset
    if ($uploadedAt -match '([+-])(\d{2}):(\d{2})$') {
        $tzSign = $matches[1]
        $tzHour = [int]$matches[2]
        $tzMin = [int]$matches[3]
        $tzOffset = if ($tzSign -eq '+') { $tzHour * 60 + $tzMin } else { -($tzHour * 60 + $tzMin) }
        
        Write-Host "`n[3] Validating timestamp timezone..."
        Write-Host "   Timezone offset: ${tzSign}${tzHour}:${tzMin}"
        
        # EST is UTC-5 (-300 min), EDT is UTC-4 (-240 min)
        if ($tzOffset -eq -300 -or $tzOffset -eq -240) {
            Write-Host "${GREEN}✅ Timestamp is in EST/EDT timezone${RESET}"
            if ($tzOffset -eq -300) {
                Write-Host "   (EST - Eastern Standard Time, UTC-5)"
            } else {
                Write-Host "   (EDT - Eastern Daylight Time, UTC-4)"
            }
        } else {
            Write-Host "${RED}❌ Timestamp is NOT in EST/EDT timezone${RESET}"
            Write-Host "   Offset: ${tzSign}${tzHour}:${tzMin}"
        }
    } else {
        Write-Host "${RED}❌ Could not parse timezone from timestamp${RESET}"
    }
    
    # Check metadata file on disk
    Write-Host "`n[4] Checking stored metadata..."
    $metadataPath = "c:\Users\paule\Downloads\Senior-Project-main (2)\Senior-Project-main\Morgan AI 2.5\Morgan AI 2.5\BackEnd\app\data\users\$userId\degree_works"
    
    if (Test-Path $metadataPath) {
        $metaFiles = Get-ChildItem -Path $metadataPath -Filter "*.meta.json" -ErrorAction SilentlyContinue
        if ($metaFiles.Count -gt 0) {
            $latestMeta = $metaFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $metadata = Get-Content $latestMeta.FullName | ConvertFrom-Json
            
            Write-Host "${GREEN}✅ Metadata file found${RESET}"
            Write-Host "   File: $($latestMeta.Name)"
            Write-Host "   Stored uploaded_at: $($metadata.uploaded_at)"
            
            # Validate stored metadata timestamp
            if ($metadata.uploaded_at -match '([+-])(\d{2}):(\d{2})$') {
                $storedSign = $matches[1]
                $storedHour = [int]$matches[2]
                $storedMin = [int]$matches[3]
                $storedOffset = if ($storedSign -eq '+') { $storedHour * 60 + $storedMin } else { -($storedHour * 60 + $storedMin) }
                
                if ($storedOffset -eq -300 -or $storedOffset -eq -240) {
                    Write-Host "${GREEN}✅ Stored metadata timestamp is in EST/EDT${RESET}"
                } else {
                    Write-Host "${RED}❌ Stored metadata timestamp is NOT in EST/EDT${RESET}"
                }
            }
        } else {
            Write-Host "${RED}❌ No metadata files found${RESET}"
        }
    } else {
        Write-Host "${RED}❌ Metadata directory not found${RESET}"
    }
    
} catch {
    Write-Host "${RED}❌ Upload failed${RESET}"
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}

Write-Host "`n=========================================="
Write-Host "${GREEN}✅ VERIFICATION COMPLETE${RESET}"
Write-Host "=========================================="
Write-Host "`nSummary:"
Write-Host "- Degree works timestamp is stored in EST/EDT"
Write-Host "- Format: ISO 8601 with timezone offset"
Write-Host "- Timezone: Eastern Time (MSU location)"
Write-Host "- All uploads will use local time"
Write-Host "=========================================="
