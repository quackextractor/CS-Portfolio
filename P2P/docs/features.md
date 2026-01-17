# P2P Bank Node - Extended Features Documentation

## Overview

This document details all additional features implemented in the P2P Bank Node (Hacker Edition) that extend beyond the explicit requirements specified in `zadani.md`. These enhancements demonstrate advanced architectural patterns, production-ready capabilities, and quality-of-life improvements.

## 1. Advanced Architectural Features

### 1.1 Clean Architecture Implementation

The solution enforces a strict separation of concerns to ensure maintainability and testability.

* **Multi-layer separation**: The solution is split into distinct projects: `Core` (Domain), `Data` (Persistence), `Network` (Communication), `Translation`, `Shared`, and `App` (Entry Point).


* **Dependency Inversion**: High-level modules (e.g., `AccountService`) depend on abstractions (`IAccountRepository`), not concrete implementations.


* **Interface-based design**: Major components are defined through interfaces, such as `IAccountService` , `IAccountRepository` , and `ICommandStrategy`.



### 1.2 Design Pattern Integration

* **Strategy Pattern**: Used for modular command processing (`ICommandStrategy`) and internationalization (`ITranslationStrategy`).


* **Repository Pattern**: Abstracts the data access layer, allowing the storage mechanism (currently File System/NDJSON) to change without affecting business logic.


* **Decorator Pattern**: The `RequestLoggingDecorator` wraps the command processor to inject logging logic transparently without modifying the core parser.


* **Dependency Injection**: A full DI container is implemented using `Microsoft.Extensions.DependencyInjection` to manage object lifecycles.



## 2. Extended Command System

### 2.1 Health Check Command (`HC`)

* **Real-time monitoring**: Returns a JSON-formatted object containing uptime, memory usage, account count, and total balance.


* **Resource metrics**: Specifically includes process memory usage (`WorkingSet64`), offering insights into the node's resource consumption.


* **Structured output**: The output is machine-readable JSON, suitable for integration with external monitoring dashboards.



### 2.2 Language Switching Command (`LANG`)

* **Runtime language switching**: Users can switch the interface language (e.g., `LANG cz`) while the server is running.


* **Language listing**: Running `LANG` without arguments lists all available language files found in the `languages/` directory.


* **Persistent configuration**: The selected language is saved to `config.json` and persists across server restarts.



### 2.3 Help Command (`HELP`)

* **Contextual assistance**: A dedicated strategy provides a list of commands and their descriptions via the network.


* **Multi-language support**: The help text is fully localized, pulling descriptions from the loaded translation strategy.



### 2.4 Interactive Server Console

* **Local management interface**: The server runs a background loop accepting local commands (`EXIT`, `BN`, `HELP`) directly in the terminal window.


* **Graceful shutdown**: The `EXIT` command triggers a `CancellationTokenSource` to stop the server cleanly.



## 3. Enhanced Robbery Plan (`RP`) Implementation

### 3.1 Advanced Algorithm

* **Density-based heuristic**: The algorithm sorts targets by "value density" (`TotalAmount / ClientCount`) to maximize loot while minimizing the number of victims.


* **Formatted output**: Returns a detailed table listing the specific IP addresses, loot amounts, and client counts for the robbery targets.



### 3.2 Parallel Network Scanning

* **Configurable concurrency**: The `RobberyConcurrency` setting in `config.json` controls how many nodes are scanned simultaneously.


* **Semaphore-based throttling**: A `SemaphoreSlim` is used to limit the number of concurrent network tasks, preventing the node from exhausting sockets or flooding the network.



### 3.3 Network Discovery

* **Subnet scanning**: The strategy attempts to detect the local subnet based on the node's own IP and scans that range (e.g., `192.168.1.x`).


* **Self-exclusion**: The scanner explicitly skips its own IP address to avoid self-robbery calculations.



## 4. Production-Grade Features

### 4.1 Hot Configuration Reload

* **File system watcher**: An instance of `FileSystemWatcher` monitors `config.json` for changes.


* **Debounced reloading**: A time check prevents multiple rapid reloads from firing immediately after a write.


* **Selective updates**: Runtime-safe properties like `Timeout` and `RobberyConcurrency` are updated immediately without requiring a restart.



### 4.2 Comprehensive Logging System

* **Dual output**: Logs are dispatched to both the Console and a persistent `node.log` file.


* **Request/response logging**: The `RequestLoggingDecorator` captures the incoming command, the response, and the execution time in milliseconds.



### 4.3 Advanced Error Handling

* **Exception sanitization**: The `CommandParser` catches exceptions and returns generic `ER` messages to the client to prevent leaking internal stack traces.


* **"Did you mean?" suggestions**: If a user types an unknown command, the system uses the Levenshtein Distance algorithm to suggest the closest valid command.



### 4.4 Data Integrity Guarantees

* **Atomic file writes**: The `FileAccountRepository` writes data to a `.tmp` file first, then performs a `File.Move` to replace the actual database. This prevents data corruption if the process crashes during a write.


* **Concurrent access safety**: A `SemaphoreSlim` ensures that only one operation can modify the account list or file at a time, ensuring thread safety.



## 5. Network Enhancements

### 5.1 Extended Address Format

* **Port specification support**: The system supports addresses in the format `<acc>/<ip>:<port>`, allowing communication with nodes running on non-standard ports.


* **Network interface enumeration**: On startup, the application lists all valid network interfaces and IPs to help the user identify their address.



### 5.2 Improved Timeout Management

* **Cancellation tokens**: The `NetworkClient` uses `CancellationTokenSource` for timeouts instead of the unsafe `Task.WhenAny` pattern, ensuring tasks are properly cancelled.


* **Layered timeouts**: Distinct timeouts are applied to the connection attempt , the welcome message read , and the command response.



## 6. Code Reuse and Generic Components

### 6.1 Request Logging Decorator

* **Adapted from RDBMS**: This component adapts the "Middleware pattern" used in ASP.NET projects (from the author's previous RDBMS project) to a raw TCP server context.



### 6.2 File Chunk Iterator

* **Ported from ChronoLog**: A Python-based memory-efficient file reader was ported to C# (`FileChunkIterator`), allowing the system to process large account files line-by-line using `yield return`.



### 6.3 Generic Logging Infrastructure

* **File logger provider**: A custom implementation of `ILoggerProvider` allows for file-based logging without external dependencies.



## 7. Deployment and Operations

### 7.1 Containerization Support

* **Dockerfile**: A multi-stage `Dockerfile` is included to build and publish the application as a lightweight container image.



### 7.2 Kubernetes Deployment

* **Deployment manifest**: A `deployment.yaml` file is provided for orchestration, defining the deployment replicas and a `NodePort` service for external access.



### 7.3 Build System Enhancements

* **Target framework script**: A batch script (`change_target_net_framework.bat`) allows users to easily switch the target .NET version in `Directory.Build.props`.



## 8. Testing and Quality Assurance

### 8.1 Comprehensive Test Suite

* **Unit tests**: Isolated tests for `AccountService`, `CommandParser`, and `RobberyCommandStrategy` using mocks.


* **Integration tests**: Tests covering persistence (server restarts) and proxy functionality.


* **Concurrency tests**: Specific tests verify that concurrent deposits and read/write operations do not corrupt data.



## 9. Internationalization System

### 9.1 Dynamic Language Switching

* **JSON-based translations**: Translation strings are stored in external JSON files (`languages/en.json`, `languages/cz.json`), allowing updates without recompilation.


* **Fallback mechanism**: If a configured language is missing, the system gracefully falls back to English and logs a warning.



### 9.2 Complete Interface Translation

* **Error messages**: All protocol error messages (`ER ...`) are localized.


* **Help text**: The help output adapts entirely to the selected language.



## 10. Configuration Management

### 10.1 Extended Configuration Options

* **Validations**: The system supports configuration for `RobberyConcurrency`, `NodeIp`, and `Language`.


* **Automatic IP Detection**: If `NodeIp` is left as default, the system attempts to auto-detect the LAN IP.