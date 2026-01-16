# P2P Bank Node (Hacker Edition)

This project implements a decentralized Peer-to-Peer banking system where each node acts as an independent bank. It is part of the "Hacker Bank Node" assignment.

## Documentation

Full documentation is available in [docs/documentation.md](docs/documentation.md).

## Features

- **P2P Architecture**: Nodes communicate via TCP/IP.
- **Banking Operations**: Create accounts, Deposit, Withdraw, Balance check.
- **Proxying**: Requests can be forwarded to other nodes in the network.
- **Robbery Plan (RP)**: Advanced algorithm to calculate optimal robbery strategy.
- **Persistence**: Accounts are stored in `accounts.json` (NDJSON format).
- **Logging**: Requests and errors are logged to console and `node.log`.
- **Internationalization (i18n)**: Support for multiple languages (EN/CS) via JSON configuration.

## Configuration

The application is configured via `config.json` placed in the executable directory (see `config.json.example`).

```json
{
  "Port": 65525,
  "Timeout": 5000,
  "NodeIp": "127.0.0.1",
  "Language": "en"
}
```

- **Port**: Listening port (default 65525).
- **Timeout**: Network timeout in ms.
- **NodeIp**: IP address to advertise.
- **Language**: Language code (`en`, `cs`). Loads translations from `languages/<code >.json`.

If you need to change the target .NET framework (e.g., to use .NET 9.0 instead of 8.0), you can use the included script:

```bash
change_target_net_framework.bat
```

This will update the `TargetFramework` property in `src/Directory.Build.props`.

## Quick Start

1. **Build**:
   ```bash
   cd src
   dotnet build
   ```

2. **Run**:
   ```bash
   cd src/BankNode.App
   dotnet run -- --port 65525
   ```

3. **Connect**:
   Use Telnet or PuTTY to connect to `localhost` on port `65525`.
