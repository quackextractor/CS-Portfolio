USE HotelManagement;
GO

-- RoomTypes
IF OBJECT_ID('RoomTypes', 'U') IS NULL
BEGIN
    CREATE TABLE RoomTypes (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(50) NOT NULL,
        BasePrice DECIMAL(18,2) NOT NULL,
        Description NVARCHAR(200)
    );
END
GO

-- Rooms
IF OBJECT_ID('Rooms', 'U') IS NULL
BEGIN
    CREATE TABLE Rooms (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        RoomNumber NVARCHAR(20) NOT NULL UNIQUE,
        RoomTypeId INT NOT NULL FOREIGN KEY REFERENCES RoomTypes(Id),
        IsClean BIT NOT NULL DEFAULT 1,
        LastMaintenance DATE
    );
END
GO

-- Services
IF OBJECT_ID('Services', 'U') IS NULL
BEGIN
    CREATE TABLE Services (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Price DECIMAL(18,2) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1
    );
END
GO

-- Bookings
IF OBJECT_ID('Bookings', 'U') IS NULL
BEGIN
    CREATE TABLE Bookings (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        GuestId INT NOT NULL FOREIGN KEY REFERENCES Guests(Id),
        RoomId INT NOT NULL FOREIGN KEY REFERENCES Rooms(Id),
        CheckIn DATE NOT NULL,
        CheckOut DATE NOT NULL,
        TotalPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        Status INT NOT NULL DEFAULT 0, -- 0: Pending, 1: Confirmed, 2: Cancelled, 3: Completed
        CreatedAt DATETIME NOT NULL DEFAULT GETDATE()
    );
END
GO

-- BookingServices (M:N)
IF OBJECT_ID('BookingServices', 'U') IS NULL
BEGIN
    CREATE TABLE BookingServices (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        BookingId INT NOT NULL FOREIGN KEY REFERENCES Bookings(Id),
        ServiceId INT NOT NULL FOREIGN KEY REFERENCES Services(Id),
        SubTotal DECIMAL(18,2) NOT NULL,
        ServiceDate DATE NOT NULL
    );
END
GO

-- Views
GO
CREATE OR ALTER VIEW v_GuestBookings AS
SELECT 
    b.Id AS BookingId,
    g.FirstName,
    g.LastName,
    g.Email,
    r.RoomNumber,
    b.CheckIn,
    b.CheckOut,
    b.Status
FROM Bookings b
JOIN Guests g ON b.GuestId = g.Id
JOIN Rooms r ON b.RoomId = r.Id;
GO

CREATE OR ALTER VIEW v_RoomAvailability AS
SELECT 
    r.Id AS RoomId,
    r.RoomNumber,
    rt.Name AS RoomType,
    rt.BasePrice
FROM Rooms r
JOIN RoomTypes rt ON r.RoomTypeId = rt.Id
WHERE r.IsClean = 1; -- Simplified availability logic for view
GO

-- Seed Data
IF NOT EXISTS (SELECT * FROM RoomTypes)
BEGIN
    INSERT INTO RoomTypes (Name, BasePrice, Description) VALUES 
    ('Single', 100.00, 'Standard Single Room'),
    ('Double', 150.00, 'Standard Double Room'),
    ('Suite', 300.00, 'Luxury Suite');
END

IF NOT EXISTS (SELECT * FROM Rooms)
BEGIN
    INSERT INTO Rooms (RoomNumber, RoomTypeId) VALUES 
    ('101', 1), ('102', 1),
    ('201', 2), ('202', 2),
    ('301', 3);
END

IF NOT EXISTS (SELECT * FROM Services)
BEGIN
    INSERT INTO Services (Name, Price) VALUES 
    ('Breakfast', 15.00),
    ('Airport Shuttle', 50.00),
    ('Late Check-out', 30.00);
END
GO
