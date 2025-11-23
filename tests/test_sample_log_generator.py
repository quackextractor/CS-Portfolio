import os
import tempfile

from bin.generate_sample_log import generate_log_line


def test_generate_log_line():
    """Test that log lines are generated with expected format"""
    timestamp = "2024-01-01 00:00:00"
    line = generate_log_line(timestamp)

    # Should contain timestamp and log level
    assert timestamp in line
    assert any(level in line for level in ["ERROR", "WARNING", "INFO"])


def test_log_generator_creates_file():
    """Test that main function creates log file"""
    original_num_lines = 1000  # Use smaller number for test
    import bin.generate_sample_log as gen_module

    # Temporarily modify constants for testing
    original_num_lines = gen_module.NUM_LINES
    gen_module.NUM_LINES = 10

    with tempfile.TemporaryDirectory() as temp_dir:
        # Modify output path for test
        original_path = gen_module.OUTPUT_PATH
        gen_module.OUTPUT_PATH = os.path.join(temp_dir, "test_sample.log")

        try:
            # Run generator
            gen_module.main()

            # Check file was created
            assert os.path.exists(gen_module.OUTPUT_PATH)

            # Check file has expected number of lines
            with open(gen_module.OUTPUT_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                assert len(lines) == 10
        finally:
            # Restore original values
            gen_module.OUTPUT_PATH = original_path
            gen_module.NUM_LINES = original_num_lines