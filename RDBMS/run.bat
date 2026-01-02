@echo off
echo Starting Hotel Management System...

echo Launching Backend...
start "Hotel Backend" cmd /k "cd Hotel.Backend && dotnet run"

echo Launching Frontend...
start "Hotel Frontend" cmd /k "cd Hotel.Frontend && npm run dev"

echo System is starting up in two new windows.
