import os
import cv2
import numpy as np
import pytest
from vendor.utils.video_extractor import extract_frames


@pytest.fixture
def temp_video(tmp_path):
    """Creates a temporary dummy video file."""
    video_path = tmp_path / "test_video.mp4"
    # Create a small dummy video (black frames)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, 20.0, (640, 480))
    for _ in range(10):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    return str(video_path)


def test_extract_frames_valid_file(temp_video, tmp_path):
    """Test extracting frames from a valid video file."""
    output_dir = tmp_path / "output"
    extract_frames(temp_video, str(output_dir), frame_rate=2)

    # Check if frames were saved in a subfolder named after the video
    video_name = os.path.splitext(os.path.basename(temp_video))[0]
    subfolder = output_dir / video_name
    assert os.path.exists(subfolder)
    files = os.listdir(subfolder)
    assert len(files) == 5
    assert all(f.endswith(".jpg") for f in files)


def test_extract_frames_directory(temp_video, tmp_path):
    """Test extracting frames when provided with a directory."""
    output_dir = tmp_path / "output"
    # Provide the directory containing the video
    extract_frames(str(tmp_path), str(output_dir), frame_rate=5)

    video_name = os.path.splitext(os.path.basename(temp_video))[0]
    subfolder = output_dir / video_name
    files = os.listdir(subfolder)
    assert len(files) == 2


def test_extract_frames_directory_batch(temp_video, tmp_path):
    """Test extracting frames from multiple videos when batch is True."""
    import shutil

    video2 = tmp_path / "test_video2.mp4"
    shutil.copy(temp_video, video2)

    output_dir = tmp_path / "output_batch"
    extract_frames(str(tmp_path), str(output_dir), frame_rate=5, batch=True)

    # Check subfolders
    v1_name = os.path.splitext(os.path.basename(temp_video))[0]
    v2_name = "test_video2"
    
    assert len(os.listdir(output_dir / v1_name)) == 2
    assert len(os.listdir(output_dir / v2_name)) == 2


def test_extract_frames_invalid_path(capsys, tmp_path):
    """Test behavior with an invalid path."""
    invalid_path = tmp_path / "nonexistent.mp4"
    output_dir = tmp_path / "output"
    extract_frames(str(invalid_path), str(output_dir))

    captured = capsys.readouterr()
    assert "Error: Video file or directory not found" in captured.out


def test_extract_frames_empty_directory(capsys, tmp_path):
    """Test behavior with an empty directory."""
    empty_dir = tmp_path / "empty_dir"
    os.makedirs(empty_dir)
    output_dir = tmp_path / "output"
    extract_frames(str(empty_dir), str(output_dir))

    captured = capsys.readouterr()
    assert "Error: No video files found in directory" in captured.out


def test_extract_frames_is_positive_false(temp_video, tmp_path):
    """Test that is_positive: false in config routes to negative directory."""
    import json
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "data" / "raw" / "positive" # Default output dir
    
    config_data = [
        {
            "video_path": temp_video,
            "frame_rate": 2,
            "is_positive": False
        }
    ]
    
    with open(config_path, "w") as f:
        json.dump(config_data, f)
        
    # the extract_frames function itself has a default of data/raw/positive.
    # we want to ensure it changes it to data/raw/negative if "is_positive" is false.
    extract_frames(config_path=str(config_path), output_dir=str(output_dir))
    
    video_name = os.path.splitext(os.path.basename(temp_video))[0]
    
    # Check that it DOES NOT exist in positive
    positive_subfolder = output_dir / video_name
    assert not os.path.exists(positive_subfolder)
    
    # Check that it DOES exist in negative
    negative_dir = str(output_dir).replace("positive", "negative")
    negative_subfolder = os.path.join(negative_dir, video_name)
    assert os.path.exists(negative_subfolder)
    
    files = os.listdir(negative_subfolder)
    assert len(files) == 5
