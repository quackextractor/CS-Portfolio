import yaml
import pytest
from unittest.mock import patch
from src.app import main, load_config


@pytest.fixture
def dummy_app_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_data = {
        "data": {},
        "model": {
            "img_size": 128,
            "output_path": str(tmp_path / "dummy.keras"),
            "threshold": 0.75,
        },
        "camera": {"index": 2},
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    return str(config_file)


def test_load_app_config(dummy_app_config):
    config = load_config(dummy_app_config)
    assert config["model"]["threshold"] == 0.75
    assert config["camera"]["index"] == 2


@patch("src.app.os.path.exists")
@patch("src.app.load_config")
def test_main_missing_model_graceful_exit(mock_load_config, mock_exists, capsys):
    # Test that gracefully exits if model doesn't exist
    mock_load_config.return_value = {
        "model": {"output_path": "fake/path.keras", "img_size": 128, "threshold": 0.5},
        "camera": {"index": 0},
    }
    mock_exists.return_value = False

    main()

    captured = capsys.readouterr()
    assert "Error: Model file not found at fake/path.keras" in captured.out


@patch("src.app.cv2.VideoCapture")
@patch("src.app.os.path.exists")
@patch("src.app.load_config")
@patch("src.app.tf.keras.models.load_model")
@patch("src.app._build_face_detector")
def test_main_with_video_path(
    mock_build_face_detector,
    mock_load_model,
    mock_load_config,
    mock_exists,
    mock_VideoCapture,
    capsys,
):
    mock_load_config.return_value = {
        "model": {"output_path": "fake/path.keras", "img_size": 128, "threshold": 0.5},
        "camera": {"index": 0},
    }
    mock_exists.return_value = True

    mock_cap = mock_VideoCapture.return_value
    mock_cap.isOpened.return_value = False

    main(video_path="test_video.mp4")

    mock_VideoCapture.assert_called_with("test_video.mp4")
