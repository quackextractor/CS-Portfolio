# Setup Scenario (Scenario 1)

## 1. Prerequisites
- **Operating System**: Windows 10/11
- **Database**: Microsoft SQL Server (LocalDB or Full Instance)
- **Backend SDK**: .NET 8.0 SDK
- **Frontend Runtime**: Node.js (v18+)

## 2. Database Setup

1. Open a terminal in `RDBMS/` directory.
2. Run the SQL setup scripts using `sqlcmd` (assuming LocalDB):
   ```powershell
   sqlcmd -S "(localdb)\MSSQLLocalDB" -i Database\01_Setup_Guests.sql
   sqlcmd -S "(localdb)\MSSQLLocalDB" -i Database\02_Setup_Rest.sql
   ```
   *Note: If using a different SQL Server instance, replace `(localdb)\MSSQLLocalDB` with your server address.*

3. Verify database `HotelManagement` is created.

## 3. Backend Setup

1. Navigate to `RDBMS/Hotel.Backend`.
2. check `appsettings.json` to ensure `ConnectionStrings:DefaultConnection` matches your SQL Server instance.
   Default is: `Server=(localdb)\\MSSQLLocalDB;Database=HotelManagement;Trusted_Connection=True;MultipleActiveResultSets=true;TrustServerCertificate=True`
3. Run the backend:
   ```powershell
   dotnet run
   ```
4. The API should be listening on `http://localhost:5106`.

## 4. Frontend Setup

1. Open a new terminal.
2. Navigate to `RDBMS/Hotel.Frontend`.
3. Install dependencies:
   ```powershell
   npm install
   ```
4. Start the development server:
   ```powershell
   npm run dev
   ```
5. Open your browser to `http://localhost:5173`.

## 5. Verification
- You should see the "Hotel Manager" application.
- Navigate to "Guests", "Book Room", "Reports" using the top navigation bar.
