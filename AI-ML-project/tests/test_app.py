import yaml
import pytest
from unittest.mock import patch
from src.app import main, load_config, make_gradcam_heatmap, display_gradcam
import numpy as np
import tensorflow as tf


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


@patch("src.app.load_config")
@patch("src.app.cv2.VideoCapture")
@patch("src.app._build_face_detector")
def test_main_missing_model_graceful_exit(mock_build, mock_cap, mock_load, caplog):
    # Mock config
    mock_load.return_value = {
        "model": {"output_path": "fake/path.keras", "img_size": 128},
        "camera": {"index": 0}
    }
    # Mock cap setup
    mock_cap.return_value.isOpened.return_value = True

    # Run main
    from src.app import main
    with caplog.at_level("ERROR"):
        main()

    # Assert that the error was logged
    assert "Model file not found at fake/path.keras" in caplog.text


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


@patch("mss.mss")
@patch("src.app.os.path.exists")
@patch("src.app.load_config")
@patch("src.app.tf.keras.models.load_model")
@patch("src.app._build_face_detector")
def test_main_with_screen(
    mock_build_face_detector,
    mock_load_model,
    mock_load_config,
    mock_exists,
    mock_mss,
    capsys,
):
    mock_load_config.return_value = {
        "model": {"output_path": "fake/path.keras", "img_size": 128, "threshold": 0.5},
        "camera": {"index": 0},
    }
    mock_exists.return_value = True

    # Simulate an exception or break so we don't loop forever.
    mock_sct = mock_mss.return_value
    # mock_sct.monitors will be accessed
    mock_sct.monitors = [{}, {}]  # at least 2 elements so monitors[1] works

    # The easiest way to break the endless while loop in test is to
    # intentionally break reading. Let's mock cv2.waitKey to return ord('q')
    dummy_frame = __import__("numpy").zeros((128, 128, 3), dtype=__import__("numpy").uint8)
    with patch("src.app.cv2.waitKey", return_value=ord("q")):
        with patch("src.app.cv2.imshow"):
            with patch("src.app.cv2.cvtColor", return_value=dummy_frame):
                main(screen=True)

    mock_mss.assert_called_once()


def test_make_gradcam_heatmap():
    # Create a simple model for testing
    inputs = tf.keras.Input(shape=(128, 128, 3))
    x = tf.keras.layers.Conv2D(32, (3, 3), name="conv2d_5")(inputs)
    outputs = tf.keras.layers.GlobalAveragePooling2D()(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(outputs)
    model = tf.keras.Model(inputs, outputs)

    dummy_img = np.random.random((1, 128, 128, 3)).astype("float32")
    heatmap = make_gradcam_heatmap(dummy_img, model, "conv2d_5")

    assert heatmap.shape == (126, 126)  # Output of 128x128 with 3x3 conv is 126x126
    assert np.min(heatmap) >= 0
    assert np.max(heatmap) <= 1.0


def test_display_gradcam():
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    heatmap = np.random.random((50, 50)).astype("float32")
    bbox = (50, 50, 100, 100)

    result_frame = display_gradcam(frame.copy(), heatmap, bbox)

    assert result_frame.shape == frame.shape
    # Check if the region has been modified
    assert not np.array_equal(result_frame[50:150, 50:150], frame[50:150, 50:150])
    # Check if outside region is still the same
    assert np.array_equal(result_frame[0:50, 0:50], frame[0:50, 0:50])
