import os
import pytest
import numpy as np
import cv2
import tensorflow as tf
from unittest.mock import patch, MagicMock
from src.app import main

@patch("src.app.cv2.VideoCapture")
@patch("src.app.os.path.exists")
@patch("src.app.load_config")
@patch("src.app.tf.keras.models.load_model")
@patch("src.app._build_face_detector")
@patch("src.app.cv2.imwrite")
@patch("src.app.os.makedirs")
def test_mining_logic(
    mock_makedirs,
    mock_imwrite,
    mock_build_face_detector,
    mock_load_model,
    mock_load_config,
    mock_exists,
    mock_VideoCapture
):
    # Setup mocks
    mock_load_config.return_value = {
        "model": {"output_path": "fake.keras", "img_size": 128, "threshold": 0.5},
        "camera": {"index": 0},
        "defaults": {"run": {"mining": {"enabled": False, "frame_rate": 10}}}
    }
    mock_exists.return_value = True
    
    mock_cap = mock_VideoCapture.return_value
    mock_cap.isOpened.return_value = True
    mock_cap.get.return_value = 100 # total frames
    
    # Simple 100x100 white frame
    dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    mock_cap.read.return_value = (True, dummy_frame)
    
    # Mock face detector to return one face
    mock_detector = mock_build_face_detector.return_value
    mock_detection = MagicMock()
    # Bounding box in detection_frame (1280 wide)
    mock_detection.bounding_box.origin_x = 100
    mock_detection.bounding_box.origin_y = 100
    mock_detection.bounding_box.width = 200
    mock_detection.bounding_box.height = 200
    mock_detection.categories = [MagicMock(score=0.9)]
    mock_detector.detect.return_value.detections = [mock_detection]
    
    # Mock model
    mock_model_obj = MagicMock()
    mock_load_model.return_value = mock_model_obj
    
    # mock_model_obj(batch_tensor) should return predictions
    # predictions should be iterable and each item should have [0].numpy()
    mock_prediction_tensor = MagicMock()
    mock_prediction_tensor.__getitem__.return_value.numpy.return_value = 0.9
    mock_model_obj.return_value = [mock_prediction_tensor]
    
    # Mock waitKey to exit immediately
    with patch("src.app.cv2.waitKey", return_value=ord('q')):
        with patch("src.app.cv2.imshow"):
             # Run main with mining enabled
             main(mine_enabled=True, mine_frame_rate=1)
    
    # Verify imwrite was called
    assert mock_imwrite.called
