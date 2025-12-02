# Changelog

## [V2] - 2025-12-01
Next review: 2025-12-02

### Changed
- **Storage Backend**: Migrated from file-based storage (JSON/JSONL) to a Microsoft SQL Server (MSSQL) database.
    - Previous versions relied on `messages.json` for templates and `timeline.jsonl` for event data.
    - The new implementation uses a relational schema with stored procedures for efficient data access and manipulation.

### Technical Implementation Details

#### Design Patterns
The application utilizes several key design patterns to ensure modularity, scalability, and maintainability:

1.  **Facade Pattern**:
    - Implemented in `src/facade.py` as `ChronoLogFacade`.
    - **Purpose**: Provides a simplified, high-level interface for the application to interact with the database. It hides the complexity of raw SQL queries and stored procedure calls, exposing clean methods like `get_messages`, `insert_timeline_event`, and `get_timeseries`.

2.  **Singleton Pattern**:
    - Implemented in `src/db.py` as `SQLConnection`.
    - **Purpose**: Ensures that the database connection configuration is managed centrally. While it currently creates new connections per call (leveraging driver-level pooling), the class structure prevents multiple instances of the connection manager from being created.

3.  **Producer-Consumer Pattern**:
    - **Producer**: `LogProcessor` (in `src/log_processor.py`) reads log files, parses them, and pushes structured data into a queue.
    - **Consumer**: `WriterProcess` (in `src/writer_process.py`) reads from the queue and performs bulk inserts into the database.
    - **Purpose**: Decouples the log parsing logic from the database writing logic, allowing them to operate at different speeds and preventing the database write latency from blocking the log parsing.

#### Parallel Processing Architecture
The project is designed to handle high-throughput log processing using Python's `multiprocessing` module:

1.  **Parallel Parsing**:
    -   `LogProcessor` uses a `multiprocessing.Pool` of worker processes.
    -   Large log files are read in chunks, and each chunk is dispatched to a worker in the pool for parsing. This allows the CPU-intensive parsing task to be distributed across multiple cores.

2.  **Dedicated Writer Process**:
    -   A separate `multiprocessing.Process` runs the `WriterProcess`.
    -   This process listens to a `multiprocessing.Queue` for parsed data.
    -   It batches incoming events and performs efficient bulk inserts (`sp_BulkInsertTimelineEvents`) to the MSSQL database, minimizing network round-trips and transaction overhead.

3.  **Data Flow**:
    -   `FileChunkReader` -> `LogProcessor` (Main Process) -> `Pool Workers` (Parsing) -> `Queue` -> `WriterProcess` (Database Insertion).

#### Batch Processing Strategy
To handle high-volume log ingestion efficiently, the application implements a robust batch processing strategy:

-   **Queue-Based Buffering**: Parsed log events are pushed to a `multiprocessing.Queue`, acting as a buffer between the fast log parser and the database writer.
-   **Bulk Insertion**: The `WriterProcess` accumulates events from the queue and inserts them in batches using `sp_BulkInsertTimelineEvents`. This significantly reduces the overhead of individual network round-trips and transaction commits.
-   **Local Caching**: To minimize database lookups, the writer maintains a local cache (`self.msg_cache`) of message templates and their IDs. New templates are registered on-the-fly using `sp_GetOrInsertMessage`.

#### Database Architecture
The backend relies on a Microsoft SQL Server database designed for write-heavy workloads and efficient analytical queries.

**1. Schema Design**
-   **`Messages` Table**: Stores unique log message templates.
    -   Columns: `MessageId` (PK), `Template` (Unique), `CreatedAt`.
    -   Optimization: Normalizing templates reduces storage size and allows for efficient aggregation.
-   **`TimelineEvents` Table**: Stores individual log occurrences.
    -   Columns: `EventId` (PK), `EventTime`, `EventType`, `MessageId` (FK), `MessageValues` (JSON), `Value`.
    -   Indexes:
        -   `IX_TimelineEvents_EventTime`: For time-range queries.
        -   `IX_TimelineEvents_EventType`: For filtering by error/warning/latency.
        -   `IX_TimelineEvents_Pagination`: Composite index for efficient API pagination.

**2. Stored Procedures**
Encapsulate business logic and data access patterns:
-   **`sp_BulkInsertTimelineEvents`**: Accepts a JSON array of events and performs a high-performance bulk insert.
-   **`sp_GetTimelinePage`**: Returns a specific page of timeline events, joining with the `Messages` table to reconstruct full log lines.
-   **`sp_GetSummary`**: Calculates dashboard metrics (error counts, latency averages) in a single database round-trip.
-   **`sp_GetTimeseries`**: Generates time-series data points for latency or specific message occurrences.
-   **`sp_GetOrInsertMessage`**: Thread-safe idempotent registration of new message templates.

**3. Views**
Provide simplified interfaces for common query patterns:
-   **`vw_TimelineWithMessages`**: Denormalized view joining events with their templates.
-   **`vw_EventSummary`**: Pre-aggregated view for quick dashboard loading.
-   **`vw_LatestEvents`**: Returns the most recent 1000 events for real-time monitoring.
-   **`vw_ErrorsAndWarnings`**: Filtered view for quickly identifying system issues.

#### API Layer
The application exposes a RESTful API (built with Flask) to serve data to the frontend:

-   **`GET /api/summary`**: Returns high-level statistics (error counts, total events, latency metrics).
-   **`GET /api/timeline`**: Provides paginated access to the event timeline. Supports `page` and `per_page` parameters.
-   **`GET /api/timeseries`**: Retrieves timeseries data for specific metrics (e.g., latency). Requires a `metric` parameter.
-   **`GET /api/messages`**: Lists all unique message templates and their IDs.
-   **Swagger UI**: The API includes Swagger documentation (via `flasgger`) for easy exploration and testing.

### Future Improvements
- **User Experience**: Add a more user-friendly interface, potentially via the API, command line application, or a web interface.
- **Frontend**: Connect a proper React TypeScript frontend to the application.