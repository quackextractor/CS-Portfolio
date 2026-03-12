import os
import pytest
from src.dataset_status import get_dir_stats, get_source_name, print_status


def test_get_dir_stats(tmp_path):
    """Test recursive directory stats calculation."""
    data_dir = tmp_path / "data"
    sub_dir = data_dir / "folder"
    sub_dir.mkdir(parents=True)
    
    (data_dir / "file1.txt").write_text("hello")
    (sub_dir / "file2.jpg").write_text("world")
    
    count, size, files = get_dir_stats(str(data_dir))
    assert count == 2
    assert len(files) == 2
    assert any("file1.txt" in f for f in files)
    assert any("file2.jpg" in f for f in files)


def test_get_source_name_subfolder(tmp_path):
    """Test source name extraction from subfolder."""
    base_dir = tmp_path / "raw"
    file_path = base_dir / "video_folder" / "frame_0001.jpg"
    
    source = get_source_name(str(file_path), str(base_dir))
    assert source == "video_folder"


def test_get_source_name_filename(tmp_path):
    """Test source name extraction from filename fallback."""
    base_dir = tmp_path / "raw"
    file_path = base_dir / "my_video_frame_0001.jpg"
    
    source = get_source_name(str(file_path), str(base_dir))
    assert source == "my_video"


def test_get_source_name_unknown(tmp_path):
    """Test source name extraction fallback to root."""
    base_dir = tmp_path / "raw"
    file_path = base_dir / "random_image.png"
    
    source = get_source_name(str(file_path), str(base_dir))
    assert source == "root"


def test_print_status_no_data(capsys):
    """Test print_status with empty config/directories."""
    config = {
        "data": {
            "raw_positive_dir": "nonexistent_pos",
            "raw_negative_dir": "nonexistent_neg",
            "processed_dir": "nonexistent_proc"
        }
    }
    print_status(config)
    captured = capsys.readouterr()
    assert "TARGET DATASET STATUS REPORT" in captured.out
    assert "Positive:      0 frames" in captured.out
