import os
import cv2
import numpy as np
import tensorflow as tf
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _build_face_detector(model_path: str):
    """
    Construct a MediaPipe Tasks FaceDetector for live-stream inference.

    Raises:
        ImportError: if mediapipe is not installed.
        FileNotFoundError: if the model file does not exist.
        RuntimeError: if the detector cannot be initialised.
    """
    try:
        import mediapipe as mp
    except ImportError as err:
        raise ImportError(
            "mediapipe is not installed or is incompatible. "
            "Run: pip install -r requirements.txt"
        ) from err

    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Face detector model not found at '{model_path}'. "
            "See the README for download instructions."
        )

    try:
        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            min_detection_confidence=0.5,
        )
        return FaceDetector.create_from_options(options)
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialise MediaPipe FaceDetector: {e}\n"
            "Ensure mediapipe >= 0.10.9 is installed and the model file is valid."
        ) from e


def main():
    import mediapipe as mp

    config = load_config()
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]
    camera_index = config["camera"]["index"]
    threshold = config["model"].get("threshold", 0.5)
    face_model_path = config["model"].get(
        "face_detector_model_path", "models/blaze_face_short_range.task"
    )

    print(f"Loading model from {model_path}...")
    if not os.path.exists(model_path):
        print(
            f"Error: Model file not found at {model_path}. "
            "Please train the model first."
        )
        return

    try:
        model = tf.keras.models.load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    face_detector = _build_face_detector(face_model_path)

    print(f"Opening camera {camera_index}...")
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        face_detector.close()
        return

    print("Camera opened successfully. Press 'q' to quit.")
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert BGR frame to RGB mp.Image for the Tasks API
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        detection_result = face_detector.detect(mp_image)
        frame_index += 1

        if detection_result.detections:
            ih, iw, _ = frame.shape
            for detection in detection_result.detections:
                # BoundingBox is absolute pixels in the Tasks API
                bbox = detection.bounding_box
                x = bbox.origin_x
                y = bbox.origin_y
                w = bbox.width
                h = bbox.height

                # Margin for cropping
                margin_x = int(w * 0.1)
                margin_y = int(h * 0.1)

                x_min = max(0, x - margin_x)
                y_min = max(0, y - margin_y)
                x_max = min(iw, x + w + margin_x)
                y_max = min(ih, y + h + margin_y)

                cropped_face = frame[y_min:y_max, x_min:x_max]

                if cropped_face.size > 0:
                    # Preprocess for classifier model
                    resized_face = cv2.resize(cropped_face, (img_size, img_size))
                    rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
                    normalized_face = rgb_face / 255.0
                    input_face = np.expand_dims(normalized_face, axis=0)

                    prediction = model.predict(input_face, verbose=0)[0][0]

                    if prediction >= threshold:
                        label = f"Miro ({prediction:.2f})"
                        color = (0, 255, 0)  # Green
                    else:
                        label = f"Unknown ({prediction:.2f})"
                        color = (0, 0, 255)  # Red

                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
                    cv2.putText(
                        frame,
                        label,
                        (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        color,
                        2,
                    )

        cv2.imshow("Miro Face Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    face_detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
