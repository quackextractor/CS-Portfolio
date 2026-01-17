# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  - Server now runs in background loop acceptin `EXIT`, `BN` and `HELP` commands locally.
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
- **Documentation**:
  - Added architectural decision records.
  - Added comprehensive testing guide.
