# Hotel Management System

A full-stack RDBMS assignment implementing a Hotel Management System using .NET Core 8 Web API and React + Vite.

## Prerequisites

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- [Node.js](https://nodejs.org/) (LTS version recommended)
- [Microsoft SQL Server](https://www.microsoft.com/sql-server/) (or LocalDB)

## Installation & Setup

### 1. Database Setup

1.  Locate the SQL scripts in the `Database` folder.
2.  Execute the scripts in the following order against your SQL Server instance:
    *   `01_Setup_Guests.sql`
    *   `02_Setup_Rest.sql`
3.  Configure the connection string in `Hotel.Backend/appsettings.json`:
    ```json
    "ConnectionStrings": {
      "DefaultConnection": "Server=(localdb)\\MSSQLLocalDB;Database=HotelManagement;Trusted_Connection=True;MultipleActiveResultSets=true;TrustServerCertificate=True"
    }
    ```
    *Update the `Server` value if you are using a different SQL Server instance (e.g., a remote server).*

### 2. Backend Setup

1.  Open a terminal and navigate to the `Hotel.Backend` directory:
    ```bash
    cd Hotel.Backend
    ```
2.  Run the application:
    ```bash
    dotnet run
    ```
    The backend will start (typically on `http://localhost:5069` or similar - check console output).

### 3. Frontend Setup

1.  Open a new terminal and navigate to the `Hotel.Frontend` directory:
    ```bash
    cd Hotel.Frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
4.  Open your browser and navigate to the URL shown in the console (usually `http://localhost:5173`).

## Project Structure

- `Hotel.Backend`: ASP.NET Core Web API implementing Custom Active Record pattern.
- `Hotel.Frontend`: React + Vite + TypeScript application with Tailwind CSS & shadcn/ui.
- `Database`: SQL scripts for database schema initialization.
- `docs`: Documentation and test scenarios.
