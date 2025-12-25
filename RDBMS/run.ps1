Write-Host "Starting Hotel Management System..."

$backendPath = Resolve-Path ".\Hotel.Backend"
$frontendPath = Resolve-Path ".\Hotel.Frontend"

# Start Backend
Write-Host "Launching Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; dotnet run"

# Start Frontend
Write-Host "Launching Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host "System is starting up in two new windows."
