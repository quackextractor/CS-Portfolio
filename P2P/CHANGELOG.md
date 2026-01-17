# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
