# Architectural Decisions

This document records the significant architectural decisions made during the development of the P2P Bank Node.

## 1. Data Storage: NDJSON (Line Delimited JSON)
**Decision:** Store accounts in `accounts.json` using one JSON object per line (NDJSON).
**Reasoning:**
- **Simplicity:** It is easy to append to the file (though current simple implementation rewrites for safety) and easy to read/debug by humans.
- **Portability:** No external database dependencies (like SQL Server or SQLite) are required. This ensures the project runs on any machine (e.g., school PCs) without installation steps.
- **Assignment Compliance:** The assignment allows file storage, and this format is robust enough for the expected scale (thousands of accounts, not millions).

## 2. Network Communication: System.Net.Sockets (Raw TCP)
**Decision:** Use `TcpListener` and `TcpClient` directly instead of high-level frameworks like ASP.NET Core or WCF.
**Reasoning:**
- **Protocol Control:** The assignment requires a specific custom text-based protocol. Raw sockets provide exact control over the bytes sent and received.
- **Performance:** Avoids the overhead of HTTP/REST headers for this specific P2P "chat-like" protocol.
- **Educational Value:** Demonstrates understanding of core networking concepts as required by the "Hacker" difficulty.

## 3. Architecture: Clean Architecture + Strategy Pattern
**Decision:** Isolate Core logic and use Strategies for specific commands.
**Reasoning:**
- **Extensibility:** New commands (like `RP` - Robbery Plan) can be added by creating a new `ICommandStrategy` implementation without modifying the core `CommandParser` or `TcpServer` logic. This follows the Open/Closed Principle.
- **Testability:** The core business logic (`AccountService`, `BankNode.Core`) is decoupled from the network layer. This allows `AccountService` to be unit tested without spinning up a real TCP server.
- **Separation of Concerns:** `BankNode.Core` contains pure domain logic. `BankNode.Network` handles protocol details. `BankNode.Data` handles file I/O.

## 4. Internationalization: JSON-based Strategy
**Decision:** Use `I18nStrategy` loading from JSON files (`en.json`, `cz.json`).
**Reasoning:**
- **Flexibility:** Allows adding new languages without recompiling the code.
- **User Experience:** The node can switch languages dynamically based on configuration or command.

## 5. Network Scanning: Parallel Tasks with `SemaphoreSlim`
**Decision:** Use `Task.Run` with `SemaphoreSlim` for the `RP` (Robbery Plan) command's network scan.
**Reasoning:**
- **Performance:** Scanning 254 IPs sequentially is too slow. Parallelism drastically reduces wait time.
- **Stability:** A naive `Task.WhenAll` on 255 tasks might exhaust thread pool or sockets. `SemaphoreSlim` (set to 20) ensures the node behaves nicely on the network and respects OS limits.

## 6. Concurrency: ReaderWriterLockSlim
**Decision:** Use `ReaderWriterLockSlim` for `AccountService`.
**Reasoning:**
- **Throughput:** Allows multiple concurrent readers (e.g., users checking balances) while ensuring exclusive access for writers (deposits/withdrawals). This is superior to a simple `lock` (Monitor) which blocks all access.