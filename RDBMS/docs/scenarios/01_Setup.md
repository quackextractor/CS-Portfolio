# Setup Scenario (Scenario 1)

## 1. Prerequisites
- **Operating System**: Windows 10/11
- **Database**: Microsoft SQL Server (LocalDB or Full Instance)
- **Backend SDK**: .NET 8.0 SDK
- **Frontend Runtime**: Node.js (v18+)

## 2. Configuration

1. Open a terminal in the `RDBMS/` root directory.
2. Search for `config.json`. If it doesn't exist, copy `config.json.example` to `config.json`.
3. Open `config.json` and ensure the `DefaultConnection` string matches your SQL Server instance.
   *   **LocalDB Example**: `"Server=(localdb)\\mssqllocaldb;Database=HotelManagement;Trusted_Connection=True;MultipleActiveResultSets=true"`
   *   **Remote/Auth Example**: `"Server=YOUR_SERVER_IP;Database=YOUR_DB;User Id=YOUR_USER;Password=YOUR_PASSWORD;TrustServerCertificate=True"`

## 3. Automated Setup

The system includes a setup tool that initializes the database and installs frontend dependencies.

1. Navigate to the Backend directory:
   ```powershell
   cd Hotel.Backend
   ```
2. Run the setup command:
   ```powershell
   dotnet run -- --setup
   ```
   *   This will:
        *   Create the database if it doesn't exist.
        *   Execute all SQL scripts found in `RDBMS/Database`.
        *   Run `npm install` in `RDBMS/Hotel.Frontend`.

## 4. Running the System

To start the full system (Backend + Frontend), simply run the helper script from the `RDBMS/` root:

```powershell
.\run.ps1
```

This will open two new terminal windows:
1.  **Backend**: Listens on `http://localhost:5106`.
2.  **Frontend**: Listens on `http://localhost:5173`.

Once started, open your browser to [http://localhost:5173](http://localhost:5173).

## 5. Verification
- You should see the "Hotel Manager" application.
- Navigate to "Guests", "Book Room", "Reports" using the top navigation bar to ensure data is accessible (database connection works).
