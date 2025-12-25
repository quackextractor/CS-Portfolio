# Setup Scenario

## 1. Installation

### Requirements
- .NET 8 SDK
- Node.js (LTS version)
- Microsoft SQL Server

### Steps
1.  Clone the repository.
2.  Navigate to `RDBMS` directory.
3.  **Configuration**: 
    - Copy `config.json.example` to `config.json`.
    - Edit `config.json` and update the `DefaultConnection` string with your SQL Server details.
    
    *Example `config.json`:*
    ```json
    {
      "ConnectionStrings": {
        "DefaultConnection": "Server=(localdb)\\MSSQLLocalDB;Database=HotelManagement;..."
      },
      ...
    }
    ```

4.  **Automated Setup**:
    ```bash
    dotnet run --project Hotel.Setup setup
    ```
    This command will:
    - Update the Backend configuration from `config.json`.
    - Create the database (if missing) and run initialization scripts.
    - Install Frontend dependencies.

## 4. Launching

1.  Start Backend:
    ```bash
    dotnet run --project Hotel.Setup run-backend
    ```

2.  Start Frontend:
    ```bash
    dotnet run --project Hotel.Setup run-frontend
    ```
