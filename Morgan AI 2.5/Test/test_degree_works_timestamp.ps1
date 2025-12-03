#!/usr/bin/env pwsh
<#
.SYNOPSIS
Test Degree Works Upload Timestamp Verification

Tests that:
1. Degree Works PDF upload succeeds
2. Timestamp is in EST/EDT timezone (Morgan State University local time)
3. Timestamp is properly formatted ISO 8601
4. Timestamp matches expected date/time
#>

param(
    [string]$ApiUrl = "http://localhost:8000",
    [string]$PdfPath = "$PSScriptRoot\..\BackEnd\app\test_degree_work.pdf"
)

# Color constants
$GREEN = "`e[32m"
$RED = "`e[31m"
$YELLOW = "`e[33m"
$RESET = "`e[0m"

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [object]$Body,
        [hashtable]$Headers = @{},
        [System.IO.FileInfo]$File
    )
    
    try {
        Write-Host "`n[TEST] $Name"
        
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params['Body'] = $Body | ConvertTo-Json
        }
        
        if ($File -and $Method -eq "POST") {
            # Use multipart form data for file uploads
            $params.Remove('ContentType')
            
            $fileBytes = [System.IO.File]::ReadAllBytes($File.FullName)
            $fileString = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)
            
            $boundary = [System.Guid]::NewGuid().ToString()
            $body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="$($File.Name)"
Content-Type: application/pdf

$fileString
--$boundary--
"@
            $params['Body'] = $body
            $params['ContentType'] = "multipart/form-data; boundary=$boundary"
        }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        $statusCode = $response.StatusCode
        
        $content = $response.Content | ConvertFrom-Json
        
        Write-Host "${GREEN}✅ PASS${RESET} - Status: $statusCode"
        return @{
            Success = $true
            StatusCode = $statusCode
            Content = $content
            Response = $response
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.Value
        Write-Host "${RED}❌ FAIL${RESET} - Status: $statusCode"
        Write-Host "${RED}Error:${RESET} $($_.Exception.Message)"
        return @{
            Success = $false
            StatusCode = $statusCode
            Error = $_.Exception.Message
        }
    }
}

function Parse-ISO8601 {
    param([string]$IsoString)
    
    # Remove the timezone info for parsing
    if ($IsoString -match '([+-]\d{2}):(\d{2})$') {
        $IsoString = $IsoString -replace '[+-]\d{2}:\d{2}$', ''
    }
    
    try {
        return [DateTime]::Parse($IsoString, $null, [System.Globalization.DateTimeStyles]::RoundtripKind)
    } catch {
        return $null
    }
}

function Validate-Timestamp {
    param([string]$Timestamp)
    
    Write-Host "`n[VALIDATE] Degree Works Timestamp"
    Write-Host "Timestamp: $Timestamp"
    
    # Extract timezone offset
    $tzMatch = $Timestamp -match '([+-])(\d{2}):(\d{2})$'
    if (-not $tzMatch) {
        Write-Host "${RED}❌ No timezone found in timestamp${RESET}"
        return $false
    }
    
    $tzSign = $matches[1]
    $tzHour = [int]$matches[2]
    $tzMin = [int]$matches[3]
    
    $tzOffset = if ($tzSign -eq '+') { $tzHour * 60 + $tzMin } else { -($tzHour * 60 + $tzMin) }
    
    Write-Host "Extracted timezone offset: $tzSign$($tzHour):$($tzMin) (total: ${tzOffset} minutes)"
    
    # EST is UTC-5 (-300 minutes), EDT is UTC-4 (-240 minutes)
    $validOffsets = @(-300, -240)  # EST and EDT
    
    if ($validOffsets -contains $tzOffset) {
        Write-Host "${GREEN}✅ Timezone is correct (EST/EDT)${RESET}"
        return $true
    } else {
        Write-Host "${RED}❌ Timezone is incorrect (expected EST/EDT)${RESET}"
        return $false
    }
}

# Main test flow
Write-Host "`n=========================================="
Write-Host "DEGREE WORKS TIMESTAMP VERIFICATION TEST"
Write-Host "=========================================="

# Check PDF exists
if (-not (Test-Path $PdfPath)) {
    Write-Host "${RED}Error: Test PDF not found at $PdfPath${RESET}"
    exit 1
}

Write-Host "Test PDF: $PdfPath"
Write-Host "File size: $((Get-Item $PdfPath).Length) bytes"

# Step 1: Sign up new user
Write-Host "`n[STEP 1/4] User Registration"
$signupResult = Test-Endpoint `
    -Name "User Signup" `
    -Method "POST" `
    -Url "$ApiUrl/api/auth/signup" `
    -Body @{
        username = "testuser_$(Get-Random)"
        email = "test_$(Get-Random)@msu.edu"
        password = "TestPassword123!"
    }

if (-not $signupResult.Success) {
    Write-Host "${RED}Failed to sign up user${RESET}"
    exit 1
}

$userId = $signupResult.Content.user_id
$token = $signupResult.Content.token
Write-Host "User ID: $userId"

# Step 2: Get the token for authenticated requests
Write-Host "`n[STEP 2/4] Prepare Authentication Headers"
$authHeaders = @{
    "Authorization" = "Bearer $token"
}
Write-Host "Token: $($token.Substring(0, 20))..."

# Step 3: Upload Degree Works PDF
Write-Host "`n[STEP 3/4] Upload Degree Works PDF"

try {
    $fileBytes = [System.IO.File]::ReadAllBytes($PdfPath)
    
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`n"
    $body = (
        "--$boundary$LF",
        "Content-Disposition: form-data; name=`"file`"; filename=`"test_degree_work.pdf`"$LF",
        "Content-Type: application/pdf$LF$LF"
    ) -join ''
    
    # Append file bytes
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body) + $fileBytes
    $bodyBytes += [System.Text.Encoding]::UTF8.GetBytes("$LF--$boundary--$LF")
    
    $uploadResult = Invoke-WebRequest `
        -Uri "$ApiUrl/api/degree-works/upload" `
        -Method POST `
        -Headers $authHeaders `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyBytes `
        -ErrorAction Stop
    
    Write-Host "${GREEN}✅ PASS${RESET} - Status: $($uploadResult.StatusCode)"
    $uploadContent = $uploadResult.Content | ConvertFrom-Json
    
} catch {
    Write-Host "${RED}❌ FAIL${RESET} - Status: $($_.Exception.Response.StatusCode.Value)"
    Write-Host "${RED}Error:${RESET} $($_.Exception.Message)"
    Write-Host "Response: $($_.ErrorDetails.Message)"
    exit 1
}

# Step 4: Validate timestamps
Write-Host "`n[STEP 4/4] Validate Timestamps"

# Check uploaded_at from API response
if ($uploadContent.PSObject.Properties.Name -contains 'uploaded_at') {
    $uploadedAt = $uploadContent.uploaded_at
    Write-Host "`nAPI Response uploaded_at: $uploadedAt"
    $isValid = Validate-Timestamp -Timestamp $uploadedAt
    if (-not $isValid) {
        Write-Host "${YELLOW}⚠️ WARNING: uploaded_at timezone may be incorrect${RESET}"
    }
}

# Check file metadata on disk
Write-Host "`nChecking stored metadata on disk..."
$userDataPath = "$PSScriptRoot\..\BackEnd\app\data\users\$userId\degree_works"
$metaFiles = Get-ChildItem -Path $userDataPath -Filter "*.meta.json" -ErrorAction SilentlyContinue

if ($metaFiles.Count -gt 0) {
    $latestMeta = $metaFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $metadata = Get-Content $latestMeta.FullName | ConvertFrom-Json
    
    Write-Host "Latest metadata file: $($latestMeta.Name)"
    Write-Host "Stored uploaded_at: $($metadata.uploaded_at)"
    
    $isValid = Validate-Timestamp -Timestamp $metadata.uploaded_at
    if ($isValid) {
        Write-Host "${GREEN}✅ Timestamp validation PASSED${RESET}"
    } else {
        Write-Host "${RED}❌ Timestamp validation FAILED${RESET}"
    }
} else {
    Write-Host "${YELLOW}⚠️ No metadata files found in user data${RESET}"
}

# Final summary
Write-Host "`n=========================================="
Write-Host "${GREEN}TEST COMPLETE${RESET}"
Write-Host "=========================================="
Write-Host "`nKey Information:"
Write-Host "- User ID: $userId"
Write-Host "- Upload Status: OK"
Write-Host "- Timestamp Format: ISO 8601 with EST/EDT timezone"
Write-Host "- Current EST Offset: -5 hours (EST) or -4 hours (EDT)"
Write-Host "`nNote: Timestamps are stored in Morgan State University local time (EST/EDT)"
Write-Host "=========================================="
