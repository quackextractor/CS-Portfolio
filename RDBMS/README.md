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

Run the setup tool to configure the system:

```bash
dotnet run --project Hotel.Setup setup
```

This tool will:
*   Configure the Backend `appsettings.json` using your `config.json`.
*   Initialize the database using scripts in `Database/`.
*   Install Frontend `npm` dependencies.

### 3. Running the Application

**Run Backend:**
```bash
dotnet run --project Hotel.Setup run-backend
```

**Run Frontend:**
```bash
dotnet run --project Hotel.Setup run-frontend
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
