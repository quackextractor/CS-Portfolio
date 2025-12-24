# Setup Scenario

## 1. Installation

### Requirements
- .NET 8 SDK
- Node.js (LTS version)
- Microsoft SQL Server (LocalDB or User instance)

### Steps
1.  Clone the repository.
2.  Navigate to `RDBMS` directory.
3.  Restore Backend dependencies:
    ```bash
    cd Hotel.Backend
    dotnet restore
    ```
4.  Restore Frontend dependencies:
    ```bash
    cd ../Hotel.Frontend
    npm install
    ```

## 2. Configuration

1.  Open `RDBMS/Hotel.Backend/appsettings.json`.
2.  Update the `DefaultConnection` string to point to your SQL Server instance.
    *   Example for LocalDB:
        `"Server=(localdb)\\mssqllocaldb;Database=HotelManagement;Trusted_Connection=True;MultipleActiveResultSets=true"`
    *   Example for School Server:
        `"DRIVER={ODBC Driver 17 for SQL Server};SERVER=193.85.203.188;DATABASE=schoolusername;UID=schoolusername;PWD=password;TrustServerCertificate=yes"`

## 3. Database Setup

1.  Open your SQL Management tool (SSMS or Azure Data Studio).
2.  Connect to the target server.
3.  Run `RDBMS/Database/01_Setup_Guests.sql` first.
4.  Run `RDBMS/Database/02_Setup_Rest.sql` second.
    *   This will create the database `HotelManagement`, all tables, views, and seed initial data.

## 4. Launching

1.  Start Backend:
    ```bash
    cd Hotel.Backend
    dotnet run
    ```
    *   Verify API is running at `http://localhost:5106/swagger`.

2.  Start Frontend:
    ```bash
    cd Hotel.Frontend
    npm run dev
    ```
    *   Open `http://localhost:5173` in your browser.
