Write-Host "Starting Hotel Management System..."

# Start Backend
Write-Host "Launching Backend..."
Start-Process dotnet -ArgumentList "run" -WorkingDirectory .\Hotel.Backend

# Start Frontend
Write-Host "Launching Frontend..."
Start-Process npm -ArgumentList "run dev" -WorkingDirectory .\Hotel.Frontend

Write-Host "System is starting up. Check the new windows for logs."
