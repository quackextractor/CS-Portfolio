

IF OBJECT_ID('Guests', 'U') IS NULL
BEGIN
    CREATE TABLE Guests (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        FirstName NVARCHAR(100) NOT NULL,
        LastName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(200) NOT NULL,
        Phone NVARCHAR(50),
        DateOfBirth DATE NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1
    );
END
GO

-- Seed Data
IF NOT EXISTS (SELECT * FROM Guests)
BEGIN
    INSERT INTO Guests (FirstName, LastName, Email, Phone, DateOfBirth, IsActive) VALUES 
    ('John', 'Doe', 'john.doe@example.com', '555-0101', '1985-06-15', 1), 
    ('Jane', 'Smith', 'jane.smith@example.com', '555-0102', '1990-11-20', 1), 
    ('Bob', 'Johnson', 'bob.j@example.com', '555-0103', '1978-03-12', 1); 
END
GO
