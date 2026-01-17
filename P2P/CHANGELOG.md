# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.1] - 2026-01-17
### Fixed
- **Compiler Warnings**:
  - Fixed CS8618 (Uninitialized non-nullable field) in `AppConfig.cs`.
  - Fixed CS1998 (Async method lacks await) in `ConnectionPoolTests.cs`.

## [1.6.0] - 2026-01-17
### Added
- **Quality of Life**:
  - `HISTORY` command to view last 10 commands in session.
  - `EXECUTE <file>` command to run script files line-by-line.
- **Resource Management**:
  - `MaxConcurrentConnections` configuration (default 100).
  - `ClientIdleTimeout` configuration (default 5 minutes).
  - Connection Pool idle connection cleanup.
- **Validation**:
  - `MaxCommandLength` enforcement (1024 chars).

### Changed
- **Breaking Change**: Account numbers must now be strictly between 10000 and 99999.
- **Dependency**: Updated internal components to use `BankNode.Shared` consistently.

## [1.5.0] - 2026-01-17
### Added
- **Capabilities**:
  - **Connection Pooling**: Reuses TCP connections to reduce overhead.
  - **Rate Limiting**: Limits requests per IP (configurable via `RateLimit`).
  - **Metrics**: `HC` command now shows comprehensive node stats (requests, success rate).
  - **Disaster Recovery**: `BACKUP` and `RESTORE` commands.
  - **Interactive Logging**: Toggle log levels at runtime with `LOG` command.
- **Configuration**:
  - Added `RateLimit` setting to `config.json`.

## [1.4.0] - 2026-01-17
### Added
- **DevOps**:
  - Added `deployment.yaml` for Kubernetes support.
- **Documentation**:
  - Updated `README.md` and docs with K8s deployment instructions.

## [1.3.0] - 2026-01-17
### Added
- **Configuration**:
  - Hot Reload support for `config.json`.
- **Features**:
  - `HC` (Health Check) now includes CPU/RAM usage.
  - `RP` (Robbery Plan) now outputs a formatted table.
- **Testing**:
  - Added Concurrency Integration Tests.
- **DevOps**:
  - Added `Dockerfile`.

### Changed
- **Architecture**: 
  - **Async I/O**: Complete refactor of `IAccountRepository` and `AccountService` to use `async/await` and `SemaphoreSlim`, eliminating thread starvation issues.
- **Networking**:
  - Replaced unsafe `Task.WhenAny` timeouts with `CancellationTokenSource` in `NetworkClient`.

## [1.2.0] - 2026-01-17
### Added
- **Configurability**:
  - `RobberyConcurrency` is now configurable in `config.json`.
- **Security**:
  - `CommandParser` now sanitizes exception messages to prevent internal detail leaks (`ER Internal error...`).
- **Refactoring**:
  - Improved `RequestLoggingDecorator` dependency injection.

## [1.1.0] - 2026-01-17
### Added
- **Interactive CLI**:
  - Server now runs in background loop accepting `EXIT`, `BN` and `HELP` commands locally.
- **Data Integrity**:
  - `FileAccountRepository` now uses atomic writes (write-temp-move) to prevent corruption.
- **Documentation**:
  - Explicit algorithmic complexity explanation for `RP` command.
  - `LANG` command documentation.

## [1.0.0] - 2026-01-17
### Added
- **Command System**: Implemented flexible command processing using Strategy Pattern.
  - `BC`: Bank Code check.
  - `AC`: Account Create.
  - `AD`: Account Deposit.
  - `AW`: Account Withdraw.
  - `AB`: Account Balance.
  - `AR`: Account Remove.
  - `BA`: Bank Amount (Total).
  - `BN`: Bank Number (Client Count).
  - `RP`: Robbery Plan (Hacker feature).
  - `LANG`: Language switching.
  - `HELP`: Command assistance.
  - `HC`: Health Check.
- **Architecture**:
  - Clean Architecture separation (Core, Data, Network, App).
  - Dependency Injection using `Microsoft.Extensions.DependencyInjection`.
  - `ICommandStrategy` for modular command handling.
- **Networking**:
  - Raw TCP socket communication (`TcpListener`/`TcpClient`).
  - P2P Proxying support for remote accounts (`<acc>/<ip>:<port>`).
  - Robust IP detection and configuration.
- **Persistence**:
  - `FileAccountRepository` using NDJSON format in `accounts.json`.
- **Internationalization**:
  - Support for multiple languages (EN, CZ) via JSON files.
- **Quality of Life**:
  - "Did you mean?" command suggestions.
  - Configurable locking (Thread Safety).
  - Comprehensive Logging.

### Changed
- **Performance**:
  - Optimized `RP` (Robbery Plan) command to use parallel network scanning with `SemaphoreSlim`.
  - Upgraded `AccountService` to use `ReaderWriterLockSlim` for better read concurrency.
- **Robustness**:
  - Improved `CommandParser` to handle multiple spaces in commands.

## [0.5.0] - 2026-01-16
### Added
- **Internationalization**:
  - Initial integration of translation strategy for error messages.
  - JSON-based translation system.
- **Configuration**:
  - Refined `config.json` structure.

## [0.4.0] - 2026-01-16
### Added
- **Networking**:
  - Support for account addresses with custom ports (`<acc>/<ip>:<port>`).
  - IP override support and improved IP selection for BankNode.
- **CLI**:
  - Added `HELP` command foundation.
  - Initial `config.json.example`.

## [0.3.0] - 2026-01-16
### Added
- **Persistence**:
  - `FileAccountRepository` implementation with NDJSON support.
- **Testing**:
  - Added integration tests for persistence and proxying.
- **Documentation**:
  - Added testing guide (`docs/testing_guide.md`).

## [0.2.0] - 2026-01-16
### Added
- **Architecture**:
  - Refactored BankNode with Dependency Injection (DI) and network strategies.
- **Logging**:
  - Added file-based logging and request logging decorator.
- **Networking**:
  - Introduced `INetworkClient` interface.

## [0.1.0] - 2026-01-16
### Added
- **Project Structure**:
  - Initial solution setup with Core, Data, Network, and App projects.
  - `zadani.md` assignment documentation.
