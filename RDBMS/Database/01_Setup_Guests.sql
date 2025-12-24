IF NOT EXISTS(SELECT * FROM sys.databases WHERE name = 'HotelManagement')
BEGIN
    CREATE DATABASE HotelManagement;
END
GO
USE HotelManagement;
GO

IF OBJECT_ID('Guests', 'U') IS NULL
BEGIN
    CREATE TABLE Guests (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        FirstName NVARCHAR(100) NOT NULL,
        LastName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(200) NOT NULL,
        Phone NVARCHAR(50),
        DateOfBirth DATE NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1,
        Type INT NOT NULL DEFAULT 0, -- 0: Regular, 1: VIP, 2: Corporate
        LoyaltyPoints FLOAT NOT NULL DEFAULT 0
    );
END
GO
