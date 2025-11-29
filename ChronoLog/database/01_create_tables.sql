-- =============================================
-- ChronoLog Database Schema - Table Creation
-- MS SQL Server
-- =============================================

-- Removed DB creation logic to use existing DB from connection string


-- =============================================
-- Table: Messages
-- Stores message templates with {num} placeholders
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Messages]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Messages] (
        [MessageId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        [Template] NVARCHAR(500) NOT NULL UNIQUE,
        [CreatedAt] DATETIME2 DEFAULT GETDATE(),
        [UpdatedAt] DATETIME2 DEFAULT GETDATE()
    );
    
    PRINT 'Table Messages created successfully.';
END
ELSE
BEGIN
    PRINT 'Table Messages already exists.';
END
GO

-- =============================================
-- Table: TimelineEvents
-- Stores all log events (errors, warnings, metrics)
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TimelineEvents]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[TimelineEvents] (
        [EventId] BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY CLUSTERED,
        [EventTime] DATETIME2 NOT NULL,
        [EventType] NVARCHAR(50) NOT NULL,
        [MessageId] INT NULL,
        [MessageValues] NVARCHAR(500) NULL, -- JSON array: ["80", "95"]
        [Value] DECIMAL(18,2) NULL, -- For numeric metrics like latency
        [CreatedAt] DATETIME2 DEFAULT GETDATE(),
        
        CONSTRAINT [FK_TimelineEvents_Messages] 
            FOREIGN KEY ([MessageId]) 
            REFERENCES [dbo].[Messages]([MessageId])
            ON DELETE SET NULL
    );
    
    PRINT 'Table TimelineEvents created successfully.';
END
ELSE
BEGIN
    PRINT 'Table TimelineEvents already exists.';
END
GO

-- =============================================
-- Indexes for Performance Optimization
-- =============================================

-- Index on EventTime for time-based queries and ordering
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TimelineEvents_EventTime')
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TimelineEvents_EventTime] 
    ON [dbo].[TimelineEvents] ([EventTime] DESC)
    INCLUDE ([EventType], [MessageId], [Value]);
    
    PRINT 'Index IX_TimelineEvents_EventTime created successfully.';
END
GO

-- Index on EventType for filtering by event type
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TimelineEvents_EventType')
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TimelineEvents_EventType] 
    ON [dbo].[TimelineEvents] ([EventType])
    INCLUDE ([EventTime], [Value], [MessageId]);
    
    PRINT 'Index IX_TimelineEvents_EventType created successfully.';
END
GO

-- Index on MessageId for join operations
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TimelineEvents_MessageId')
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TimelineEvents_MessageId] 
    ON [dbo].[TimelineEvents] ([MessageId])
    WHERE [MessageId] IS NOT NULL;
    
    PRINT 'Index IX_TimelineEvents_MessageId created successfully.';
END
GO

-- Composite index for pagination queries (most common use case)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_TimelineEvents_Pagination')
BEGIN
    CREATE NONCLUSTERED INDEX [IX_TimelineEvents_Pagination] 
    ON [dbo].[TimelineEvents] ([EventId] DESC)
    INCLUDE ([EventTime], [EventType], [MessageId], [MessageValues], [Value]);
    
    PRINT 'Index IX_TimelineEvents_Pagination created successfully.';
END
GO

PRINT 'All tables and indexes created successfully.';
PRINT 'Database setup complete.';
GO
