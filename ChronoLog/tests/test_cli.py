import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import cli

class TestCLI(unittest.TestCase):

    @patch('cli.Path.exists')
    def test_check_env_missing_file(self, mock_exists):
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            result = cli.check_env()
            self.assertFalse(result)
            mock_print.assert_any_call("[FAILED] .env file not found.")

    @patch('cli.Path.exists')
    @patch('cli.load_dotenv')
    @patch('os.getenv')
    def test_check_env_missing_vars(self, mock_getenv, mock_load_dotenv, mock_exists):
        mock_exists.return_value = True
        mock_getenv.return_value = None # Simulate missing variable
        
        with patch('builtins.print') as mock_print:
            result = cli.check_env()
            self.assertFalse(result)
            # Check if the specific error message for missing vars is printed
            # We look for a call that starts with "[FAILED] Missing environment variables"
            found = False
            for call in mock_print.call_args_list:
                if call[0][0].startswith("[FAILED] Missing environment variables"):
                    found = True
                    break
            self.assertTrue(found)

    @patch('cli.Path.exists')
    @patch('cli.load_dotenv')
    @patch('os.getenv')
    def test_check_env_success(self, mock_getenv, mock_load_dotenv, mock_exists):
        mock_exists.return_value = True
        mock_getenv.return_value = "some_connection_string"
        
        with patch('builtins.print') as mock_print:
            result = cli.check_env()
            self.assertTrue(result)
            mock_print.assert_any_call("[OK] Environment configuration found.")

    def test_check_db_connection_success(self):
        mock_db = MagicMock()
        mock_conn_instance = MagicMock()
        mock_db.SQLConnection.return_value = mock_conn_instance
        
        with patch.dict(sys.modules, {'db': mock_db}):
            with patch('builtins.print') as mock_print:
                result = cli.check_db_connection()
                self.assertTrue(result)
                mock_print.assert_any_call("[OK] Database connection successful.")

    def test_check_db_connection_failure(self):
        mock_db = MagicMock()
        mock_db.SQLConnection.side_effect = Exception("Connection error")
        
        with patch.dict(sys.modules, {'db': mock_db}):
            with patch('builtins.print') as mock_print:
                result = cli.check_db_connection()
                self.assertFalse(result)
                # Check for failure message
                found = False
                for call in mock_print.call_args_list:
                    if call[0][0].startswith("[FAILED] Database connection failed"):
                        found = True
                        break
                self.assertTrue(found)

    @patch('cli.Path.exists')
    def test_check_input_files_missing_dir(self, mock_exists):
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            result = cli.check_input_files()
            self.assertFalse(result)
            mock_print.assert_any_call("[FAILED] 'input' directory not found.")

    @patch('cli.Path.exists')
    @patch('cli.Path.glob')
    def test_check_input_files_empty(self, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = [] # No files
        
        with patch('builtins.print') as mock_print:
            result = cli.check_input_files()
            self.assertFalse(result)
            mock_print.assert_any_call("[FAILED] No files found in 'input' directory.")

    @patch('cli.Path.exists')
    @patch('cli.Path.glob')
    def test_check_input_files_success(self, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = [Path("file1.log")]
        
        with patch('builtins.print') as mock_print:
            result = cli.check_input_files()
            self.assertTrue(result)
            mock_print.assert_any_call("[OK] Found 1 file(s) in 'input' directory.")

    @patch('subprocess.check_call')
    def test_run_script_success(self, mock_check_call):
        with patch('builtins.print'):
            result = cli.run_script("some_script.py")
            self.assertTrue(result)

    @patch('subprocess.check_call')
    def test_run_script_failure(self, mock_check_call):
        import subprocess
        mock_check_call.side_effect = subprocess.CalledProcessError(1, "cmd")
        
        with patch('builtins.print') as mock_print:
            result = cli.run_script("some_script.py")
            self.assertFalse(result)
            mock_print.assert_any_call("[FAILED] Error running some_script.py")

    @patch('cli.check_env')
    @patch('cli.check_db_connection')
    @patch('cli.check_input_files')
    def test_cmd_check_all_pass(self, mock_input, mock_db, mock_env):
        mock_env.return_value = True
        mock_db.return_value = True
        mock_input.return_value = True
        
        with patch('builtins.print') as mock_print:
            result = cli.cmd_check(None)
            self.assertTrue(result)
            mock_print.assert_any_call("\n[OK] All checks passed! You are ready to run the application.")

    @patch('cli.check_env')
    def test_cmd_check_env_fail(self, mock_env):
        mock_env.return_value = False
        
        with patch('builtins.print'):
            result = cli.cmd_check(None)
            self.assertIsNone(result) # It returns None (implicit) when env fails early

    @patch('cli.check_env')
    @patch('cli.check_db_connection')
    @patch('cli.check_input_files')
    def test_cmd_check_other_fail(self, mock_input, mock_db, mock_env):
        mock_env.return_value = True
        mock_db.return_value = False # DB fails
        mock_input.return_value = True
        
        with patch('builtins.print') as mock_print:
            result = cli.cmd_check(None)
            self.assertFalse(result)
            mock_print.assert_any_call("\n[FAILED] Some checks failed. Please resolve the issues above.")

if __name__ == '__main__':
    unittest.main()
