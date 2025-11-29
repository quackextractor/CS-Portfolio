-- =============================================
-- ChronoLog Database Schema - Sample Data
-- MS SQL Server
-- =============================================

-- USE ChronoLog;
GO

PRINT 'Inserting sample data...';
GO

-- =============================================
-- Insert sample message templates
-- =============================================
-- =============================================
-- Insert sample message templates
-- =============================================
SET IDENTITY_INSERT [dbo].[Messages] ON;

INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (0, 'WARNING CPU usage > {num}%');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (1, 'ERROR Timeout on API call');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (2, 'WARNING Slow query detected');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (3, 'WARNING Cache miss rate high');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (4, 'ERROR Database connection failed');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (5, 'ERROR Disk write error');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (6, 'ERROR User authentication failed');
INSERT INTO [dbo].[Messages] ([MessageId], [Template]) VALUES (7, 'WARNING Memory usage high');

SET IDENTITY_INSERT [dbo].[Messages] OFF;

PRINT 'Message templates inserted.';
GO

-- =============================================
-- Insert sample timeline events
-- =============================================

-- Latency events
EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T04:59:56', 
    @EventType = 'latency', 
    @Value = 88;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:01:56', 
    @EventType = 'latency', 
    @Value = 198;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:03:26', 
    @EventType = 'latency', 
    @Value = 55;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:05:56', 
    @EventType = 'latency', 
    @Value = 329;

-- Warning events with message references
EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:00:56', 
    @EventType = 'warning', 
    @MessageId = 0,
    @MessageValues = '["80"]';

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:02:26', 
    @EventType = 'warning', 
    @MessageId = 0,
    @MessageValues = '["80"]';

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:03:56', 
    @EventType = 'warning', 
    @MessageId = 2;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:04:26', 
    @EventType = 'warning', 
    @MessageId = 3;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:04:56', 
    @EventType = 'warning', 
    @MessageId = 3;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:06:56', 
    @EventType = 'warning', 
    @MessageId = 0,
    @MessageValues = '["80"]';

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:07:56', 
    @EventType = 'warning', 
    @MessageId = 2;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:08:56', 
    @EventType = 'warning', 
    @MessageId = 0,
    @MessageValues = '["80"]';

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:09:56', 
    @EventType = 'warning', 
    @MessageId = 2;

-- Error events
EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:02:56', 
    @EventType = 'error', 
    @MessageId = 1;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:05:26', 
    @EventType = 'error', 
    @MessageId = 4;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:06:26', 
    @EventType = 'error', 
    @MessageId = 5;

EXEC [dbo].[sp_InsertTimelineEvent] 
    @EventTime = '2025-12-01T05:08:26', 
    @EventType = 'error', 
    @MessageId = 6;

PRINT 'Sample timeline events inserted.';
GO

-- =============================================
-- Verify sample data
-- =============================================
PRINT 'Verification:';
PRINT '-----------------';

DECLARE @MessageCount INT, @EventCount BIGINT;

SELECT @MessageCount = COUNT(*) FROM [dbo].[Messages];
SELECT @EventCount = COUNT(*) FROM [dbo].[TimelineEvents];

PRINT 'Messages: ' + CAST(@MessageCount AS NVARCHAR(10));
PRINT 'Timeline Events: ' + CAST(@EventCount AS NVARCHAR(10));

PRINT '';
PRINT 'Sample data insertion complete.';
PRINT 'You can now test the stored procedures:';
PRINT '  EXEC sp_GetTimelinePage @PageNumber = 1, @EntriesPerPage = 30;';
PRINT '  EXEC sp_GetSummary;';
PRINT '  EXEC sp_GetTimeseries @Metric = ''latency'', @Limit = 500;';
GO
