import os
import cv2
import yaml
import pytest
import numpy as np
from src.build_dataset import process_images, load_config


@pytest.fixture
def dummy_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_data = {
        "data": {
            "raw_positive_dir": str(tmp_path / "raw_pos"),
            "raw_negative_dir": str(tmp_path / "raw_neg"),
            "processed_dir": str(tmp_path / "processed"),
            "dataset_csv": str(tmp_path / "processed" / "dataset.csv"),
            "test_split_size": 0.2,
            "random_seed": 42,
        },
        "model": {"img_size": 128, "threshold": 0.65},
        "camera": {"index": 0},
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    return str(config_file)


def test_load_config(dummy_config):
    config = load_config(dummy_config)
    assert "data" in config
    assert "model" in config
    assert config["model"]["img_size"] == 128
    assert config["data"]["test_split_size"] == 0.2
    assert config["data"]["random_seed"] == 42
    assert config["model"]["threshold"] == 0.65


from unittest.mock import patch, MagicMock

@patch("src.build_dataset.mp")
def test_process_images_empty_dir(mock_mp, tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    records = process_images(str(input_dir), str(output_dir), label=1, img_size=128)
    assert len(records) == 0


@patch("src.build_dataset.mp")
def test_process_images_no_face(mock_mp, tmp_path):
    # Setup mock face detection
    mock_solution = MagicMock()
    mock_mp.solutions.face_detection.FaceDetection.return_value = mock_solution
    
    # Process method returns result with detections=None
    mock_results = MagicMock()
    mock_results.detections = None
    mock_solution.process.return_value = mock_results

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    # Create an image with no face (just black)
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "test_no_face.jpg"), img)

    records = process_images(str(input_dir), str(output_dir), label=0, img_size=128)
    assert len(records) == 0
    # The image should be discarded, so no output
    assert not os.path.exists(str(output_dir / "test_no_face.jpg"))
