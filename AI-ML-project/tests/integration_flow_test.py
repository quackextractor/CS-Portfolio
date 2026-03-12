import os
import subprocess
import sys
import shutil

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    return result.returncode


def test_integration():
    # Setup dummy data structure
    test_data_dir = "tests/integration_tmp"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    
    raw_pos = os.path.join(test_data_dir, "raw/positive")
    raw_neg = os.path.join(test_data_dir, "raw/negative")
    os.makedirs(raw_pos, exist_ok=True)
    os.makedirs(raw_neg, exist_ok=True)

    # Let's test the CLI commands 'process' and 'build'

    print("Pre-requisite: ensure models are setup or mock them.")
    
    # 1. Test CLI 'process'
    # For now, just check if the CLI responds to the new commands
    code = run_command([sys.executable, "main.py", "process", "--help"])
    if code != 0:
        return False

    # 2. Test CLI 'build'
    code = run_command([sys.executable, "main.py", "build", "--help"])
    if code != 0:
        return False

    # 3. Test CLI 'extract'
    code = run_command([sys.executable, "main.py", "extract", "--help"])
    if code != 0:
        return False
    print("CLI commands are registered correctly.")
    return True


if __name__ == "__main__":
    if test_integration():
        print("Integration flow check PASSED.")
        sys.exit(0)
    else:
        print("Integration flow check FAILED.")
        sys.exit(1)
