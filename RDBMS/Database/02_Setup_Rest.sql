

-- RoomTypes
IF OBJECT_ID('RoomTypes', 'U') IS NULL
BEGIN
    CREATE TABLE RoomTypes (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(50) NOT NULL,
        BasePrice DECIMAL(18,2) NOT NULL
    );
END
GO

-- Rooms
IF OBJECT_ID('Rooms', 'U') IS NULL
BEGIN
    CREATE TABLE Rooms (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        RoomNumber NVARCHAR(20) NOT NULL UNIQUE,
        RoomTypeId INT NOT NULL FOREIGN KEY REFERENCES RoomTypes(Id)
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
        TotalPrice DECIMAL(18,2) NOT NULL DEFAULT 0
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
    b.CheckOut
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
JOIN RoomTypes rt ON r.RoomTypeId = rt.Id;
GO

CREATE OR ALTER VIEW v_RevenueByRoomType AS
SELECT 
    rt.Name AS RoomTypeName,
    COUNT(b.Id) AS TotalBookings,
    ISNULL(SUM(b.TotalPrice), 0) AS TotalRevenue
FROM RoomTypes rt
JOIN Rooms r ON rt.Id = r.RoomTypeId
LEFT JOIN Bookings b ON r.Id = b.RoomId
GROUP BY rt.Name;
GO

-- Seed Data
IF NOT EXISTS (SELECT * FROM RoomTypes)
BEGIN
    INSERT INTO RoomTypes (Name, BasePrice) VALUES 
    ('Single', 100.00),
    ('Double', 150.00),
    ('Suite', 300.00);
END

IF NOT EXISTS (SELECT * FROM Rooms)
BEGIN
    INSERT INTO Rooms (RoomNumber, RoomTypeId) VALUES 
    ('101', 1), ('102', 1),
    ('201', 2), ('202', 2),
    ('301', 3);
END
GO

-- Seed Data: Bookings
IF NOT EXISTS (SELECT * FROM Bookings)
BEGIN
    -- Linking queries to get IDs ensures robustness, though identity INSERTs are standard 1-based usually.
    -- Assuming Guest IDs 1, 2 from previous script and Room IDs 1, 3 from this script.
    
    INSERT INTO Bookings (GuestId, RoomId, CheckIn, CheckOut, TotalPrice) VALUES 
    (1, 1, DATEADD(day, 1, GETDATE()), DATEADD(day, 5, GETDATE()), 400.00),  -- John Doe, Room 101 (Single)
    (2, 5, DATEADD(day, 10, GETDATE()), DATEADD(day, 15, GETDATE()), 1500.00); -- Jane Smith, Room 301 (Suite)
END
GO
