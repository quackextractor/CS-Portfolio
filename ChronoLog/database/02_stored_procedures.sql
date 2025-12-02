-- =============================================
-- ChronoLog Database Schema - Stored Procedures
-- MS SQL Server
-- =============================================


GO

-- =============================================
-- Stored Procedure: sp_GetTimelinePage
-- Retrieves paginated timeline events
-- Parameters:
--   @PageNumber: Page number (1-based)
--   @EntriesPerPage: Number of entries per page
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GetTimelinePage]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_GetTimelinePage];
GO

CREATE PROCEDURE [dbo].[sp_GetTimelinePage]
    @PageNumber INT = 1,
    @EntriesPerPage INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Validate parameters
    IF @PageNumber < 1 SET @PageNumber = 1;
    IF @EntriesPerPage < 1 SET @EntriesPerPage = 30;
    IF @EntriesPerPage > 1000 SET @EntriesPerPage = 1000; -- Max limit
    
    DECLARE @Offset INT = (@PageNumber - 1) * @EntriesPerPage;
    DECLARE @TotalCount BIGINT;
    
    -- Get total count (cached for performance)
    SELECT @TotalCount = COUNT(*) FROM [dbo].[TimelineEvents];
    
    -- Return paginated results with message templates
    SELECT 
        te.[EventId],
        te.[EventTime] as [time],
        te.[EventType] as [event],
        te.[MessageId] as [msg_id],
        te.[MessageValues] as [msg_values],
        te.[Value] as [value],
        m.[Template] as [template],
        @TotalCount as [TotalCount]
    FROM [dbo].[TimelineEvents] te WITH (NOLOCK)
    LEFT JOIN [dbo].[Messages] m WITH (NOLOCK) ON te.[MessageId] = m.[MessageId]
    ORDER BY te.[EventId] DESC
    OFFSET @Offset ROWS
    FETCH NEXT @EntriesPerPage ROWS ONLY;
END
GO

PRINT 'Stored procedure sp_GetTimelinePage created successfully.';
GO

-- =============================================
-- Stored Procedure: sp_GetSummary
-- Returns summary statistics for the dashboard
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GetSummary]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_GetSummary];
GO

CREATE PROCEDURE [dbo].[sp_GetSummary]
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @ErrorCount INT;
    DECLARE @WarningCount INT;
    DECLARE @TimelineCount BIGINT;
    DECLARE @UniqueMessages INT;
    DECLARE @LatencyCount INT;
    DECLARE @LatencyAvg DECIMAL(18,2);
    
    -- Count errors
    SELECT @ErrorCount = COUNT(*) 
    FROM [dbo].[TimelineEvents] WITH (NOLOCK)
    WHERE [EventType] = 'error';
    
    -- Count warnings
    SELECT @WarningCount = COUNT(*) 
    FROM [dbo].[TimelineEvents] WITH (NOLOCK)
    WHERE [EventType] = 'warning';
    
    -- Total timeline count
    SELECT @TimelineCount = COUNT(*) 
    FROM [dbo].[TimelineEvents] WITH (NOLOCK);
    
    -- Unique messages count
    SELECT @UniqueMessages = COUNT(*) 
    FROM [dbo].[Messages] WITH (NOLOCK);
    
    -- Latency metrics
    SELECT 
        @LatencyCount = COUNT(*),
        @LatencyAvg = AVG([Value])
    FROM [dbo].[TimelineEvents] WITH (NOLOCK)
    WHERE [EventType] = 'latency' AND [Value] IS NOT NULL;
    
    -- Return summary in JSON-like format
    SELECT 
        @ErrorCount as [error_count],
        @WarningCount as [warning_count],
        @TimelineCount as [timeline_count],
        @UniqueMessages as [unique_messages],
        @LatencyCount as [latency_count],
        @LatencyAvg as [latency_average];
END
GO

PRINT 'Stored procedure sp_GetSummary created successfully.';
GO

-- =============================================
-- Stored Procedure: sp_GetTimeseries
-- Returns timeseries data for a specific metric
-- Parameters:
--   @Metric: Metric name ('latency', 'msg_0', 'msg_1', etc.)
--   @Limit: Maximum number of points to return
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GetTimeseries]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_GetTimeseries];
GO

CREATE PROCEDURE [dbo].[sp_GetTimeseries]
    @Metric NVARCHAR(50) = 'latency',
    @Limit INT = 500
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Validate limit
    IF @Limit < 1 SET @Limit = 500;
    IF @Limit > 5000 SET @Limit = 5000;
    
    DECLARE @MessageId INT = NULL;
    
    -- Check if metric is msg_{id} pattern
    IF @Metric LIKE 'msg[_]%'
    BEGIN
        DECLARE @IdString NVARCHAR(50) = SUBSTRING(@Metric, 5, LEN(@Metric) - 4);
        IF ISNUMERIC(@IdString) = 1
            SET @MessageId = CAST(@IdString AS INT);
    END
    
    -- If it's a latency metric
    IF LOWER(@Metric) = 'latency'
    BEGIN
        SELECT TOP (@Limit)
            [EventTime] as [time],
            [Value] as [value]
        FROM [dbo].[TimelineEvents] WITH (NOLOCK)
        WHERE [EventType] = 'latency' AND [Value] IS NOT NULL
        ORDER BY [EventId] DESC;
        RETURN;
    END
    
    -- If it's a message metric (msg_X)
    IF @MessageId IS NOT NULL
    BEGIN
        SELECT TOP (@Limit)
            te.[EventTime] as [time],
            CAST(JSON_VALUE(te.[MessageValues], '$[0]') AS DECIMAL(18,2)) as [value]
        FROM [dbo].[TimelineEvents] te WITH (NOLOCK)
        WHERE te.[MessageId] = @MessageId 
            AND te.[MessageValues] IS NOT NULL
            AND JSON_VALUE(te.[MessageValues], '$[0]') IS NOT NULL
        ORDER BY te.[EventId] DESC;
        RETURN;
    END
    
    -- Otherwise match by event type, return Value field
    SELECT TOP (@Limit)
        [EventTime] as [time],
        [Value] as [value]
    FROM [dbo].[TimelineEvents] WITH (NOLOCK)
    WHERE [EventType] = @Metric AND [Value] IS NOT NULL
    ORDER BY [EventId] DESC;
END
GO

PRINT 'Stored procedure sp_GetTimeseries created successfully.';
GO

-- =============================================
-- Stored Procedure: sp_InsertTimelineEvent
-- Inserts a new timeline event
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_InsertTimelineEvent]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_InsertTimelineEvent];
GO

CREATE PROCEDURE [dbo].[sp_InsertTimelineEvent]
    @EventTime DATETIME2,
    @EventType NVARCHAR(50),
    @MessageId INT = NULL,
    @MessageValues NVARCHAR(500) = NULL,
    @Value DECIMAL(18,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO [dbo].[TimelineEvents] 
        ([EventTime], [EventType], [MessageId], [MessageValues], [Value])
    VALUES 
        (@EventTime, @EventType, @MessageId, @MessageValues, @Value);
    
    -- Return the new EventId
    SELECT SCOPE_IDENTITY() as [NewEventId];
END
GO

PRINT 'Stored procedure sp_InsertTimelineEvent created successfully.';
GO

-- =============================================
-- Stored Procedure: sp_UpsertMessage
-- Insert or update a message template
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GetOrInsertMessage]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_GetOrInsertMessage];
GO

CREATE PROCEDURE [dbo].[sp_GetOrInsertMessage]
    @Template NVARCHAR(500)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @MessageId INT;
    
    -- Try to find existing
    SELECT @MessageId = [MessageId] FROM [dbo].[Messages] WHERE [Template] = @Template;
    
    IF @MessageId IS NOT NULL
    BEGIN
        SELECT @MessageId as [MessageId];
        RETURN;
    END
    
    -- Insert new
    BEGIN TRY
        INSERT INTO [dbo].[Messages] ([Template]) VALUES (@Template);
        SELECT SCOPE_IDENTITY() as [MessageId];
    END TRY
    BEGIN CATCH
        -- If race condition (inserted by another process), select again
        SELECT [MessageId] FROM [dbo].[Messages] WHERE [Template] = @Template;
    END CATCH
END
GO

PRINT 'Stored procedure sp_GetOrInsertMessage created successfully.';
GO

-- =============================================
-- Stored Procedure: sp_BulkInsertTimelineEvents
-- Bulk insert multiple timeline events (for migration)
-- =============================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_BulkInsertTimelineEvents]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_BulkInsertTimelineEvents];
GO

CREATE PROCEDURE [dbo].[sp_BulkInsertTimelineEvents]
    @EventsJson NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Parse JSON and insert
    INSERT INTO [dbo].[TimelineEvents] 
        ([EventTime], [EventType], [MessageId], [MessageValues], [Value])
    SELECT 
        CAST([time] AS DATETIME2),
        [event],
        [msg_id],
        [msg_values],
        CAST([value] AS DECIMAL(18,2))
    FROM OPENJSON(@EventsJson)
    WITH (
        [time] NVARCHAR(50),
        [event] NVARCHAR(50),
        [msg_id] INT,
        [msg_values] NVARCHAR(500),
        [value] NVARCHAR(50)
    );
    
    SELECT @@ROWCOUNT as [InsertedCount];
END
GO

PRINT 'Stored procedure sp_BulkInsertTimelineEvents created successfully.';
GO

PRINT 'All stored procedures created successfully.';
GO
