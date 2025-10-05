# Final test with all fixes applied

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "TESTING SUPER SMART AGENT" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Login
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "sneha.patel@bharatace.edu.in"
    password = "password123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json"

Write-Host "  Login successful!" -ForegroundColor Green
Write-Host "  Student: $($loginResponse.user.student_data.full_name)" -ForegroundColor White
Write-Host "  Student ID: $($loginResponse.user.id)" -ForegroundColor White
Write-Host "  CGPA (from login): $($loginResponse.user.student_data.cgpa)" -ForegroundColor White

# Get token
$token = $loginResponse.access_token

# Test CGPA query
Write-Host "`nStep 2: Asking AI Agent for CGPA..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

$questionBody = @{
    query = "What is my current CGPA?"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ask" `
    -Method POST `
    -Body $questionBody `
    -Headers $headers `
    -ContentType "application/json"

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "AGENT RESPONSE:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host $response.answer -ForegroundColor White
Write-Host "`n================================`n" -ForegroundColor Cyan
