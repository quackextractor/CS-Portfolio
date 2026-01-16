@echo off
setlocal

:: Default to net8.0 if no argument is provided
set "CURRENT_VERSION=net8.0"

echo Current target framework is set in src\Directory.Build.props.
echo Enter the new target framework (e.g., net8.0, net9.0).
echo Press Enter to use default [%CURRENT_VERSION%]: 

set /p NEW_VERSION=

if "%NEW_VERSION%"=="" set NEW_VERSION=%CURRENT_VERSION%

echo Updating target framework to %NEW_VERSION%...

(
echo ^<Project^>
echo   ^<PropertyGroup^>
echo     ^<TargetFramework^>%NEW_VERSION%^</TargetFramework^>
echo   ^</PropertyGroup^>
echo ^</Project^>
) > src\Directory.Build.props

echo Done. verify by running 'dotnet build src'
pause
