-- =============================================
-- ChronoLog Database Schema - Views
-- MS SQL Server
-- =============================================

-- USE ChronoLog;
GO

-- =============================================
-- View: vw_TimelineWithMessages
-- Combines timeline events with message templates
-- for easier querying and API access
-- =============================================
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_TimelineWithMessages]'))
    DROP VIEW [dbo].[vw_TimelineWithMessages];
GO

CREATE VIEW [dbo].[vw_TimelineWithMessages]
AS
SELECT 
    te.[EventId],
    te.[EventTime] as [time],
    te.[EventType] as [event],
    te.[MessageId] as [msg_id],
    te.[MessageValues] as [msg_values],
    te.[Value] as [value],
    m.[Template] as [template],
    te.[CreatedAt]
FROM [dbo].[TimelineEvents] te
LEFT JOIN [dbo].[Messages] m ON te.[MessageId] = m.[MessageId];
GO

PRINT 'View vw_TimelineWithMessages created successfully.';
GO

-- =============================================
-- View: vw_EventSummary
-- Pre-aggregated summary statistics
-- High-performance read for dashboard summary
-- =============================================
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_EventSummary]'))
    DROP VIEW [dbo].[vw_EventSummary];
GO

CREATE VIEW [dbo].[vw_EventSummary]
AS
SELECT 
    (SELECT COUNT(*) FROM [dbo].[TimelineEvents] WHERE [EventType] = 'error') as [error_count],
    (SELECT COUNT(*) FROM [dbo].[TimelineEvents] WHERE [EventType] = 'warning') as [warning_count],
    (SELECT COUNT(*) FROM [dbo].[TimelineEvents]) as [timeline_count],
    (SELECT COUNT(*) FROM [dbo].[Messages]) as [unique_messages],
    (SELECT COUNT(*) FROM [dbo].[TimelineEvents] WHERE [EventType] = 'latency' AND [Value] IS NOT NULL) as [latency_count],
    (SELECT AVG([Value]) FROM [dbo].[TimelineEvents] WHERE [EventType] = 'latency' AND [Value] IS NOT NULL) as [latency_average];
GO

PRINT 'View vw_EventSummary created successfully.';
GO

-- =============================================
-- View: vw_LatestEvents
-- Shows the latest 1000 events with full details
-- Useful for monitoring and debugging
-- =============================================
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_LatestEvents]'))
    DROP VIEW [dbo].[vw_LatestEvents];
GO

CREATE VIEW [dbo].[vw_LatestEvents]
AS
SELECT TOP 1000
    te.[EventId],
    te.[EventTime],
    te.[EventType],
    te.[MessageId],
    m.[Template],
    te.[MessageValues],
    te.[Value],
    te.[CreatedAt]
FROM [dbo].[TimelineEvents] te
LEFT JOIN [dbo].[Messages] m ON te.[MessageId] = m.[MessageId]
ORDER BY te.[EventId] DESC;
GO

PRINT 'View vw_LatestEvents created successfully.';
GO

-- =============================================
-- View: vw_ErrorsAndWarnings
-- Filtered view showing only errors and warnings
-- =============================================
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_ErrorsAndWarnings]'))
    DROP VIEW [dbo].[vw_ErrorsAndWarnings];
GO

CREATE VIEW [dbo].[vw_ErrorsAndWarnings]
AS
SELECT 
    te.[EventId],
    te.[EventTime],
    te.[EventType],
    te.[MessageId],
    m.[Template],
    te.[MessageValues],
    te.[CreatedAt]
FROM [dbo].[TimelineEvents] te
LEFT JOIN [dbo].[Messages] m ON te.[MessageId] = m.[MessageId]
WHERE te.[EventType] IN ('error', 'warning');
GO

PRINT 'View vw_ErrorsAndWarnings created successfully.';
GO

-- =============================================
-- View: vw_LatencyMetrics
-- Filtered view showing only latency events
-- =============================================
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_LatencyMetrics]'))
    DROP VIEW [dbo].[vw_LatencyMetrics];
GO

CREATE VIEW [dbo].[vw_LatencyMetrics]
AS
SELECT 
    te.[EventId],
    te.[EventTime],
    te.[Value] as [Latency],
    te.[CreatedAt]
FROM [dbo].[TimelineEvents] te
WHERE te.[EventType] = 'latency' AND te.[Value] IS NOT NULL;
GO

PRINT 'View vw_LatencyMetrics created successfully.';
GO

PRINT 'All views created successfully.';
GO
