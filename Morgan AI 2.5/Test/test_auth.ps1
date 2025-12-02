# Test authentication endpoints

# Test signup
Write-Host "Testing Signup Endpoint..." -ForegroundColor Cyan
$signupBody = @{
    email = "test@morgan.edu"
    username = "testuser"
    password = "TestPass123"
    full_name = "Test User"
    role = "student"
} | ConvertTo-Json

try {
    $signupResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/signup" -Method Post -Body $signupBody -ContentType "application/json"
    $token = $signupResponse.access_token
    Write-Host "✓ Signup successful!" -ForegroundColor Green
    Write-Host "Access Token (full): $token" -ForegroundColor Yellow
    Write-Host "Access Token (first 20): $($token.Substring(0,20))..." -ForegroundColor Gray
    Write-Host "User: $($signupResponse.user.email)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Signup failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host $_.Exception.Response.StatusCode.value__
    }
}

Write-Host ""

# Test login
Write-Host "Testing Login Endpoint..." -ForegroundColor Cyan
$loginBody = @{
    email = "test@morgan.edu"
    password = "TestPass123"
    role = "student"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "Access Token (full): $token" -ForegroundColor Yellow
    Write-Host "Access Token (first 20): $($token.Substring(0,20))..." -ForegroundColor Gray
    Write-Host "User: $($loginResponse.user.email)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Authentication tests complete!" -ForegroundColor Cyan
