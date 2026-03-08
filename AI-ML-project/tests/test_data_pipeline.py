import os
import cv2
import yaml
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.build_dataset import process_images, load_config, _build_face_detector


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
        "model": {
            "img_size": 128,
            "threshold": 0.65,
            "face_detector_model_path": "models/blaze_face_short_range.task",
        },
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
    assert "face_detector_model_path" in config["model"]


# ---------------------------------------------------------------------------
# Tests for _build_face_detector error paths
# ---------------------------------------------------------------------------

def test_build_face_detector_missing_model_raises(tmp_path):
    """FileNotFoundError is raised when the model file does not exist."""
    with pytest.raises(FileNotFoundError, match="Face detector model not found"):
        _build_face_detector(str(tmp_path / "nonexistent.task"))


# ---------------------------------------------------------------------------
# Tests for process_images  - detector is mocked so no real model needed.
# ---------------------------------------------------------------------------

def _make_mock_detector(detections=None, init_raises=None):
    """Return a mock FaceDetector with controlled detect() output."""
    mock_detector = MagicMock()
    if init_raises is not None:
        mock_detector.detect.side_effect = init_raises
        return mock_detector
    mock_result = MagicMock()
    mock_result.detections = detections
    mock_detector.detect.return_value = mock_result
    return mock_detector


_BUILD_DETECTOR = "src.build_dataset._build_face_detector"


@patch(_BUILD_DETECTOR)
def test_process_images_empty_dir(mock_build, tmp_path):
    """process_images returns empty list when input directory has no images."""
    mock_build.return_value = _make_mock_detector(detections=None)
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    records = process_images(str(input_dir), str(output_dir), label=1, img_size=128)
    assert len(records) == 0


@patch(_BUILD_DETECTOR)
def test_process_images_no_face(mock_build, tmp_path):
    """Images where face detection returns no detections are discarded."""
    mock_build.return_value = _make_mock_detector(detections=None)

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "test_no_face.jpg"), img)

    records = process_images(str(input_dir), str(output_dir), label=0, img_size=128)
    assert len(records) == 0
    assert not os.path.exists(str(output_dir / "test_no_face.jpg"))


@patch(_BUILD_DETECTOR)
def test_process_images_multiple_faces_discarded(mock_build, tmp_path):
    """Images with more than one detected face are discarded (strict single-face rule)."""
    mock_build.return_value = _make_mock_detector(
        detections=[MagicMock(), MagicMock()]
    )

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "two_faces.jpg"), img)

    records = process_images(str(input_dir), str(output_dir), label=1, img_size=128)
    assert len(records) == 0


@patch(_BUILD_DETECTOR)
def test_face_detection_init_failure_raises_runtime_error(mock_build, tmp_path):
    """If _build_face_detector raises RuntimeError it propagates correctly."""
    mock_build.side_effect = RuntimeError("init failed: MediaPipe FaceDetection error")

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    os.makedirs(input_dir)

    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(input_dir / "img.jpg"), img)

    with pytest.raises(RuntimeError, match="MediaPipe FaceDetection"):
        process_images(str(input_dir), str(output_dir), label=1, img_size=128)
