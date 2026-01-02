@echo off
echo --- Starting Setup via Hotel.Backend ---

if not exist config.json (
    echo [WARNING] config.json not found! Please copy config.json.example to config.json.
    echo Usage: copy config.json.example config.json
    exit /b 1
)

dotnet run --project Hotel.Backend -- --setup
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Setup execution failed.
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] Setup execution finished.
pause
