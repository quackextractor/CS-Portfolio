import os
import cv2
import yaml
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
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


# ---------------------------------------------------------------------------
# Helper: create a mock mediapipe face_detection module
# We patch _get_mp_face_detection so mediapipe need not be installed.
# ---------------------------------------------------------------------------

def _make_mock_face_module(detections=None, init_raises=None):
    """Return a mock mediapipe face_detection module."""
    mock_module = MagicMock()
    if init_raises is not None:
        mock_module.FaceDetection.side_effect = init_raises
        return mock_module
    mock_detector = MagicMock()
    mock_results = MagicMock()
    mock_results.detections = detections
    mock_detector.process.return_value = mock_results
    mock_module.FaceDetection.return_value = mock_detector
    return mock_module


_LAZY_TARGET = "src.build_dataset._get_mp_face_detection"


@patch(_LAZY_TARGET)
def test_process_images_empty_dir(mock_get_mp, tmp_path):
    """process_images returns empty list when input directory has no images."""
    mock_get_mp.return_value = _make_mock_face_module(detections=None)
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    records = process_images(str(input_dir), str(output_dir), label=1, img_size=128)
    assert len(records) == 0


@patch(_LAZY_TARGET)
def test_process_images_no_face(mock_get_mp, tmp_path):
    """Images where face detection returns no detections are discarded."""
    mock_get_mp.return_value = _make_mock_face_module(detections=None)

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "test_no_face.jpg"), img)

    records = process_images(str(input_dir), str(output_dir), label=0, img_size=128)
    assert len(records) == 0
    assert not os.path.exists(str(output_dir / "test_no_face.jpg"))


@patch(_LAZY_TARGET)
def test_process_images_multiple_faces_discarded(mock_get_mp, tmp_path):
    """Images with more than one detected face are discarded (strict single-face rule)."""
    mock_get_mp.return_value = _make_mock_face_module(
        detections=[MagicMock(), MagicMock()]
    )

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "two_faces.jpg"), img)

    records = process_images(str(input_dir), str(output_dir), label=1, img_size=128)
    assert len(records) == 0


@patch(_LAZY_TARGET)
def test_face_detection_init_failure_raises_runtime_error(mock_get_mp, tmp_path):
    """If FaceDetection() raises, a RuntimeError with a helpful message is raised."""
    mock_get_mp.return_value = _make_mock_face_module(
        init_raises=Exception("init failed")
    )

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "img.jpg"), img)

    with pytest.raises(RuntimeError, match="MediaPipe FaceDetection"):
        process_images(str(input_dir), str(output_dir), label=1, img_size=128)
