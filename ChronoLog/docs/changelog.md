# Changelog

## [V2] - 2025-12-01
Next review: 2025-12-02

### Changed
- **Storage Backend**: Migrated from file-based storage (JSON/JSONL) to a Microsoft SQL Server (MSSQL) database.
    - Previous versions relied on `messages.json` for templates and `timeline.jsonl` for event data.
    - The new implementation uses a relational schema with stored procedures for efficient data access and manipulation.

### Techn Stuff

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
    - `LogProcessor` uses a `multiprocessing.Pool` of worker processes.
    - Large log files are read in chunks, and each chunk is dispatched to a worker in the pool for parsing. This allows the CPU-intensive parsing task to be distributed across multiple cores.

2.  **Dedicated Writer Process**:
    - A separate `multiprocessing.Process` runs the `WriterProcess`.
    - This process listens to a `multiprocessing.Queue` for parsed data.
    - It batches incoming events and performs efficient bulk inserts (`sp_BulkInsertTimelineEvents`) to the MSSQL database, minimizing network round-trips and transaction overhead.

3.  **Data Flow**:
    - `FileChunkReader` -> `LogProcessor` (Main Process) -> `Pool Workers` (Parsing) -> `Queue` -> `WriterProcess` (Database Insertion).

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