# Hotel Management System

A full-stack RDBMS assignment implementing a Hotel Management System using .NET Core 8 Web API and React + Vite.

## Prerequisites

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- [Node.js](https://nodejs.org/) (LTS version recommended)
- [Microsoft SQL Server](https://www.microsoft.com/sql-server/) (or LocalDB)

## Installation & Setup

### 1. Configuration

1.  Navigate to the `RDBMS` directory.
2.  Copy the example configuration:
    ```bash
    cp config.json.example config.json
    ```
    *(Or manually copy and rename)*
3.  Edit `config.json` and update the `DefaultConnection` string with your SQL Server connection details.

### 2. Automated Setup

Run the setup via the backend:

```bash
dotnet run --project Hotel.Backend -- --setup
```

This tool will:
*   Configure the Backend `appsettings.json` using your `config.json`.
*   Initialize the database using scripts in `Database/`.
*   Install Frontend `npm` dependencies.

### 3. Running the Application

You can use the helper script to run both backend and frontend:
```batch
.\run.bat
```

Or run them individually:

**Run Backend:**
```bash
dotnet run --project Hotel.Backend
```

**Run Frontend:**
```bash
cd Hotel.Frontend
npm run dev
```

## Project Structure

- `Hotel.Backend`: ASP.NET Core Web API implementing Custom Active Record pattern.
- `Hotel.Frontend`: React + Vite + TypeScript application with Tailwind CSS & shadcn/ui.
- `Database`: SQL scripts for database schema initialization.
- `docs`: Documentation and test scenarios.

## API Documentation

The backend API documentation is available via Swagger UI:
- **URL**: `http://localhost:5173/docs`
- **Note**: Ensure both backend and frontend are running. The frontend proxies requests to the backend.

## Changing .NET Version

The project is currently configured for **.NET 8**. If you need to use a different version (e.g., .NET 7 or .NET 6):

1.  Open `Hotel.Backend/Hotel.Backend.csproj`.
2.  Locate the `<TargetFramework>` tag:
    ```xml
    <TargetFramework>net8.0</TargetFramework>
    ```
3.  Change `net8.0` to your desired version (e.g., `net7.0`, `net6.0`).
4.  Ensure you have the corresponding SDK installed.

    To check which SDKs are installed on your machine, run:
    ```bash
    dotnet --list-sdks
    ```

