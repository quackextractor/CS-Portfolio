import argparse
import os
import sys
import unittest
from pathlib import Path
from dotenv import load_dotenv

# Add src to path so we can import modules
sys.path.append(str(Path(__file__).parent / "src"))

def check_env():
    """Check if .env file exists and has required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("[FAILED] .env file not found.")
        print("   Please copy .env.example to .env and configure it.")
        return False
    
    load_dotenv()
    required_vars = ["DB_CONNECTION_STRING"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"[FAILED] Missing environment variables: {', '.join(missing)}")
        return False
    
    print("[OK] Environment configuration found.")
    return True

def check_db_connection():
    """Check database connection."""
    try:
        from db import SQLConnection, DatabaseConnectionError
        print("   Attempting to connect to database...")
        # This will also try to create the DB if it doesn't exist (based on src/db.py logic)
        conn = SQLConnection()
        conn.get_connection()
        print("[OK] Database connection successful.")
        return True
    except Exception as e:
        print(f"[FAILED] Database connection failed: {e}")
        print("   Please check your connection string in .env.")
        return False

def check_input_files():
    """Check if input files exist."""
    input_dir = Path("input")
    if not input_dir.exists():
        print("[FAILED] 'input' directory not found.")
        return False
    
    files = list(input_dir.glob("*"))
    if not files:
        print("[FAILED] No files found in 'input' directory.")
        print("   Run 'python cli.py generate-logs' to create sample data.")
        return False
    
    print(f"[OK] Found {len(files)} file(s) in 'input' directory.")
    return True

def check_db_initialized():
    """Check if database schema is initialized."""
    try:
        from db import SQLConnection
        conn = SQLConnection()
        # Try to select from a table that should exist
        conn.execute_query("SELECT TOP 1 * FROM Messages")
        return True
    except Exception:
        return False

def cmd_check(args):
    """Run all checks."""
    print("Running system checks...\n")
    env_ok = check_env()
    if not env_ok:
        return # Stop if env is missing
    
    db_ok = check_db_connection()
    if db_ok:
        if check_db_initialized():
            print("[OK] Database schema is initialized.")
        else:
            print("[WARNING] Database connected but schema appears missing.")
            print("   Run 'python cli.py setup' to initialize, or 'python cli.py auto' to automate everything.")
            
    input_ok = check_input_files()
    
    if env_ok and db_ok and input_ok:
        print("\n[OK] All checks passed! You are ready to run the application.")
        return True
    else:
        print("\n[FAILED] Some checks failed. Please resolve the issues above.")
        return False

def run_script(script_path, args=None):
    """Run a python script using subprocess."""
    import subprocess
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        print(f"[FAILED] Error running {script_path}")
        return False

def cmd_setup(args):
    """Run database setup."""
    print("Setting up database...")
    script = Path("bin/setup_db.py")
    run_script(script)

def cmd_generate_logs(args):
    """Generate sample logs."""
    print("Generating sample logs...")
    script = Path("bin/generate_sample_log.py")
    run_script(script)

def cmd_run_processor(args):
    """Run the log processor."""
    print("Starting log processor...")
    script = Path("src/main.py")
    # Pass through any extra arguments if we had them, but for now just run it
    # We could add specific args to the CLI if needed
    if args and getattr(args, 'live', False):
        # Add --mode live if requested
        # We need to construct the args list for the subprocess
        script_args = ["--mode", "live"]
        run_script(script, script_args)
    else:
        run_script(script)

def cmd_run_api(args):
    """Run the API server."""
    print("Starting API server...")
    script = Path("src/api.py")
    run_script(script)

def cmd_test(args):
    """Run all tests."""
    print("Running all tests...")
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "tests"
    suite = loader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print("\n[FAILED] Some tests failed.")
        sys.exit(1)
    print("\n[OK] All tests passed.")

def cmd_auto(args):
    """Automate setup and run."""
    print("Starting automated setup and run...\n")
    
    # 1. Check Env
    if not check_env():
        return
    
    # 2. Check DB Connection
    if not check_db_connection():
        print("[FAILED] Could not connect to database. Aborting.")
        return

    # 3. Check DB Schema
    if not check_db_initialized():
        print("Database schema not found. Running setup...")
        cmd_setup(None)
        if not check_db_initialized():
            print("[FAILED] Database setup failed. Aborting.")
            return
        print("[OK] Database schema initialized.")
    else:
        print("[OK] Database schema already initialized.")

    # 4. Check Input
    if not check_input_files():
        print("Attempting to generate sample logs...")
        cmd_generate_logs(None)
        if not check_input_files():
            print("[FAILED] Failed to generate input files. Aborting.")
            return

    # 5. Run Processor
    print("\n[OK] Setup complete. Launching Log Processor...")
    cmd_run_processor(None)

def main():
    parser = argparse.ArgumentParser(description="ChronoLog Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check command
    subparsers.add_parser("check", help="Run system checks")
    
    # Setup command
    subparsers.add_parser("setup", help="Run database setup")
    
    # Generate logs command
    subparsers.add_parser("generate-logs", help="Generate sample logs")
    
    # Run processor command
    rp_parser = subparsers.add_parser("run-processor", help="Run the log processor")
    rp_parser.add_argument("--live", action="store_true", help="Run in live mode (tail log file)")
    
    # Run API command
    subparsers.add_parser("run-api", help="Run the API server")

    # Test command
    subparsers.add_parser("test", help="Run all tests")
    
    # Auto command
    subparsers.add_parser("auto", help="Automate setup and run processor")
    
    args = parser.parse_args()
    
    if args.command == "check":
        cmd_check(args)
    elif args.command == "setup":
        cmd_setup(args)
    elif args.command == "generate-logs":
        cmd_generate_logs(args)
    elif args.command == "run-processor":
        cmd_run_processor(args)
    elif args.command == "run-api":
        cmd_run_api(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "auto":
        cmd_auto(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
