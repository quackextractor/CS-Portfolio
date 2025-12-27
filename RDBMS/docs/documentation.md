# Hotel Management System Documentation

**Author:** LostSoul
**Date:** 2024-05-20
**School:** SPŠE Ječná
**Project:** D2 - Active Record Pattern

## 1. Specification
This application is a Hotel Management System designed to manage guests, rooms, bookings, and services.
It allows for:
- Guest management (CRUD)
- Room management (View)
- Booking creation with multi-table transaction support (Booking + Services)
- Data Import (Guests, Services) via JSON
- Reporting (Bookings, Availability, Service Stats, Revenue)

## 2. Architecture
The application follows a **Two-Tier** architecture (Client-Server) with a separate Database layer.

### Backend
- **Framework:** ASP.NET Core 8 Web API
- **Pattern:** Custom **Active Record** implementation (D2).
- **Data Access:** ADO.NET (`Microsoft.Data.SqlClient`) directly managing Connections and Transactions.
- **Layers:**
    - `Controllers`: Handle HTTP requests.
    - `Models`: Contain Business Logic and Data Access (`Save()`, `Find()`).
    - `Data`: `ActiveRecordBase` and `DbConfig`.

### Frontend
- **Framework:** React + Vite
- **Language:** TypeScript
- **UI:** TailwindCSS + Shadcn/UI (simulated)
- **Communication:** Axios for REST API consumption.

## 3. Database Design
**RDBMS:** Microsoft SQL Server

![ER Diagram](/docs/er_diagram_placeholder.png)

### Tables
1.  **Guests**: Stores guest info. `(Id, FirstName, LastName, ...)`
2.  **RoomTypes**: Stores categories. `(Id, Name, BasePrice, ...)`
3.  **Rooms**: Physical rooms. `(Id, RoomNumber, RoomTypeId, ...)`
4.  **Services**: Additional services. `(Id, Name, Price)`
5.  **Bookings**: Transactional table. `(Id, CheckIn, CheckOut, TotalPrice, ...)`
6.  **BookingServices**: M:N link table. `(Id, BookingId, ServiceId, SubTotal)`

### Views
1.  `v_GuestBookings`: Joins Bookings, Guests, Rooms.
2.  `v_RoomAvailability`: Filtered view of Rooms.
3.  `v_ServiceUsageStats`: Aggregates usage from BookingServices.
4.  `v_RevenueByRoomType`: **Aggregated report from 3 tables** (RoomTypes, Rooms, Bookings).

### Relationships
- Guest (1) -> (*) Booking
- RoomType (1) -> (*) Room
- Room (1) -> (*) Booking
- Booking (1) -> (*) BookingServices (*) <- (1) Service

## 4. Requirements Coverage

![UI Screenshot - Import](/docs/ui_import_placeholder.png)
![UI Screenshot - Booking](/docs/ui_booking_placeholder.png)

- **D2 Active Record**: Implemented in `ActiveRecordBase.cs`. Entities like `Guest`, `Booking` inherit from it.
- **5 Tables**: 6 Tables implemented.
- **2 Views**: 4 Views implemented.
- **M:N**: Implemented via `BookingServices`.
- **Transaction**: Used in `ImportController` (Import 50 guests) and `BookingsController` (Create Booking + Add Services).
- **Aggregated Report**: `v_RevenueByRoomType` combines RoomTypes, Rooms, and Bookings.
- **Import**: JSON Import for Guests and Services (2 tables).
- **Config**: `appsettings.json` supported.
- **Error Handling**: Try-Catch blocks in Controllers with appropriate HTTP status codes.

## 5. Configuration & Usage
See `scenarios/01_Setup.md` for installation instructions.
See `scenarios/02_HappyPath.md` for usage examples.
