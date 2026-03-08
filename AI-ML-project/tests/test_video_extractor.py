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

    # Check if frames were saved
    # 10 frames total, frame_rate=2 -> should be 5 frames (0, 2, 4, 6, 8)
    files = os.listdir(output_dir)
    assert len(files) == 5
    assert all(f.endswith(".jpg") for f in files)


def test_extract_frames_directory(temp_video, tmp_path):
    """Test extracting frames when provided with a directory."""
    output_dir = tmp_path / "output"
    # Provide the directory containing the video
    extract_frames(str(tmp_path), str(output_dir), frame_rate=5)

    # 10 frames total, frame_rate=5 -> should be 2 frames (0, 5)
    files = os.listdir(output_dir)
    assert len(files) == 2


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
