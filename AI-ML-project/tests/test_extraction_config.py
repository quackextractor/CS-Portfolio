import os
import cv2
import numpy as np
import pytest
import json
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


def test_extract_frames_is_positive_false(temp_video, tmp_path):
    """Test that is_positive: false in config routes to negative directory."""
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
        
    # The default output_dir is "data/raw/positive". 
    # extract_frames should detect "is_positive": False and change it to "data/raw/negative".
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


def test_extract_frames_negative_true(temp_video, tmp_path):
    """Test that negative: true in config routes to negative directory (existing functionality)."""
    config_path = tmp_path / "config_neg.json"
    output_dir = tmp_path / "data" / "raw" / "positive"
    
    config_data = [
        {
            "video_path": temp_video,
            "frame_rate": 2,
            "negative": True
        }
    ]
    
    with open(config_path, "w") as f:
        json.dump(config_data, f)
        
    extract_frames(config_path=str(config_path), output_dir=str(output_dir))
    
    video_name = os.path.splitext(os.path.basename(temp_video))[0]
    negative_dir = str(output_dir).replace("positive", "negative")
    negative_subfolder = os.path.join(negative_dir, video_name)
    assert os.path.exists(negative_subfolder)
