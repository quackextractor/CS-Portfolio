
# ChronoLog
Parallel log analyzer for large log files with live and batch processing modes, metrics tracking, and web-based visualization.

## Cloning the Repository

To get started with ChronoLog, clone the repository from GitHub:

```bash
git clone https://github.com/quackextractor/CS-Portfolio.git
cd CS-Portfolio/ChronoLog
```

## Overview
ChronoLog is a high-performance log analyzer designed to efficiently process large logs. 
It can detect errors, warnings, custom metrics, and latency events over time, producing JSON outputs for timelines, summaries, and message templates. 
A lightweight frontend dashboard allows visual exploration of logs and metrics.

## Features
- Parallel processing using multiple worker processes
- Incremental (live) or batch processing modes
- Automatic detection of key-value metrics in logs
- Aggregated outputs: timeline, summary, and message templates
- Modern Web Interface (React + TypeScript) for real-time visualization

## Docs
Recommended programs for markdown:
- Visual Studio Code
- Jetbrains PyCharm or similar
- Obsidian

Read the docs at `/docs/ChronoDocs.md`
pUML diagram: `/docs/diagram.puml`

## Requirements

- Python 3.9+ installed and added to system PATH

  - Official Python download: [https://www.python.org/downloads/](https://www.python.org/downloads/)
  - Adding Python to PATH: [https://www.geeksforgeeks.org/python/how-to-add-python-to-windows-path/](https://www.geeksforgeeks.org/python/how-to-add-python-to-windows-path/)
- Git installed and available in system PATH

  - Git download: [https://git-scm.com/install/](https://git-scm.com/install/)

### Installing dependencies
```commandline
pip install -r requirements.txt
```

## Configuration

ChronoLog can be customized via environment variables (see `.env.example`).

### Database Setup
1. Ensure Microsoft SQL Server is running.
2. Run the SQL scripts in `database/` to create the schema and stored procedures.
3. Configure `DB_CONNECTION_STRING` in your `.env` file.


## CLI Management Tool

The project includes a `cli.py` CLI tool to help with common tasks.

### Commands

*   `check`: Run system checks (environment, database, input files).
*   `setup`: Run database setup scripts.
*   `generate-logs`: Generate sample log files.
*   `run-processor`: Run the log processor.
*   `run-api`: Run the API server.
*   `auto`: Automate setup and run the processor.

### Usage Examples

Check system status:
```bash
python cli.py check
```

Automated setup and run:
```bash
python cli.py auto
```

## Running Unit Tests

```commandline
set PYTHONPATH=%CD%\src
python -m unittest discover -s tests -v
```

or

```commandline
python tests/run_all_tests.py
```

## Running the project

### 1. Generating a sample log

```commandline
python bin/generate_sample_log.py
```

### 2. Analyzing using ChronoLog

#### Processing Modes

* `batch` (default): reads current log file and exits
* `live`: tails the log file and processes new entries continuously

You can switch modes using:

```commandline
python src/main.py --mode live
```

```commandline
python src/main.py
```

### 3. Running the API

The project now exposes data via a Flask API.

```commandline
python src/api.py
```

The API will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).
Swagger documentation is available at [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs).

### 4. Running the Web Interface

The project includes a modern React-based frontend in the `web/` directory.

To start the development server:

```bash
cd web
npm install
npm run dev
```

The web interface will typically be available at [http://localhost:5173](http://localhost:5173) (check console output).

## Data Storage

ChronoLog stores results in a Microsoft SQL Server database.
The schema includes tables for:
* `TimelineEvents`: Individual log events
* `Messages`: Unique message templates
* `Summary`: Aggregated statistics

## Cleanup

```commandline
python bin/util_clear_dirs.py
```

## Performance Tips

* Adjust `CHUNK_SIZE` and `NUM_PROCESSES` for large log files to optimize throughput
* `QUEUE_MAX_SIZE` can be tuned to prevent memory spikes

## License

MIT License. See `LICENSE` for details.

## Contributing

Feel free to fork the project, submit pull requests, or report issues. Ensure tests pass before submitting changes.
