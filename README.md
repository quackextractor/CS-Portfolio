# ChronoLog
Parallel log analyzer

## Requirements
- Modern python installed and added to system PATH
  - [Official Python download](https://www.python.org/downloads/)
  - [Adding python to PATH - geeksforgeeks.org](https://www.geeksforgeeks.org/python/how-to-add-python-to-windows-path/)


### Installing dependencies (optional)
Needed for the frontend demo in `/vendor/`

```commandline
pip install -r requirements.txt
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
```commandline
python src/main.py
```

### 3. Running FrontEnd Demo
Dependencies need to be installed for this. [Guide Here](#installing-dependencies-optional)

TODO: ADD INSTRUCTIONS HERE!!!