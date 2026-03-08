import os
import cv2
import numpy as np
import tensorflow as tf
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """
    Computes a Grad-CAM heatmap for a given image and model.
    """
    # Ensure input is a tensor
    img_tensor = tf.cast(img_array, tf.float32)

    with tf.GradientTape() as tape:
        tape.watch(img_tensor)
        x = img_tensor
        last_conv_layer_output = None
        for layer in model.layers:
            # Skip InputLayer which is not callable and redundant here
            if "InputLayer" in layer.__class__.__name__:
                continue
            x = layer(x)
            if layer.name == last_conv_layer_name:
                last_conv_layer_output = x
        
        preds = x
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    # Safety check if layer was not found or gradients are disconnected
    if last_conv_layer_output is None:
        return np.zeros((img_array.shape[1], img_array.shape[2]))

    # This is the gradient of the output neuron (top predicted or chosen)
    # with regard to the output feature map of the last conv layer
    grads = tape.gradient(class_channel, last_conv_layer_output)

    if grads is None:
        return np.zeros((img_array.shape[1], img_array.shape[2]))

    # This is a vector where each entry is the mean intensity of the gradient
    # over a specific feature map channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # We multiply each channel in the feature map array
    # by "how important this channel is" with regard to the top predicted class
    # then sum all the channels to obtain the heatmap class activation
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # For visualization purpose, we will also normalize the heatmap between 0 & 1
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()


def display_gradcam(frame, heatmap, bbox, alpha=0.4):
    """
    Overlays the Grad-CAM heatmap on the detected face in the frame.
    """
    x, y, w, h = bbox

    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # Use jet colormap to colorize heatmap
    jet = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Resize heatmap to match the bounding box size
    jet = cv2.resize(jet, (w, h))

    # Create an overlay by combining the original ROI and the colorized heatmap
    roi = frame[y : y + h, x : x + w]
    overlay = cv2.addWeighted(roi, 1 - alpha, jet, alpha, 0)

    # Replace the ROI in the original frame
    frame[y : y + h, x : x + w] = overlay
    return frame


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


def main(video_path: str = None, screen: bool = False, use_gradcam: bool = False):
    import mediapipe as mp
    import mss

    config = load_config()
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]
    camera_index = config["camera"]["index"]
    threshold = config["model"].get("threshold", 0.5)
    face_model_path = config["model"].get(
        "face_detector_model_path", "models/blaze_face_short_range.task"
    )

    print(f"Loading model from {model_path}...")
    if not model_path.endswith(".keras"):
        print(f"Error: Model file must be in .keras format. Received: {model_path}")
        return

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

    sct = None
    monitor = None
    cap = None

    if screen:
        print("Opening screen capture...")
        sct = mss.mss()
        monitor = sct.monitors[1]  # primary monitor
    elif video_path:
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            face_detector.close()
            return
        print(f"Opening video {video_path}...")
        cap = cv2.VideoCapture(video_path)
    else:
        print(f"Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)

    if not screen and (cap is None or not cap.isOpened()):
        print("Error: Could not open video source.")
        face_detector.close()
        return

    window_name = "Miro Face Detector"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if video_path else 0
    paused = False
    force_read = False
    updating_trackbar = False
    gradcam_active = use_gradcam

    if video_path and total_frames > 0:
        def on_trackbar(val):
            nonlocal force_read
            if not updating_trackbar:
                cap.set(cv2.CAP_PROP_POS_FRAMES, val)
                force_read = True

        cv2.createTrackbar("Progress", window_name, 0, total_frames, on_trackbar)
        print("Video opened successfully. Controls:")
        print("  [Space] Pause/Resume")
        print("  [a] / [d] Skip 30 frames backward/forward")
        print("  [g] Toggle Grad-CAM heatmap")
        print("  [q] or [ESC] to quit")
    elif screen:
        print("Screen capture started. Press 'q' to quit.")
    else:
        print("Camera opened successfully. Controls:")
        print("  [g] Toggle Grad-CAM heatmap")
        print("  [q] or [ESC] to quit")

    frame_index = 0

    while True:
        if not paused or force_read:
            if screen:
                sct_img = sct.grab(monitor)
                frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
                ret = True
            else:
                ret, frame = cap.read()

            if not ret:
                if video_path:
                    print("End of video reached.")
                else:
                    print("Failed to grab frame")
                break

            force_read = False

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

                        if gradcam_active:
                            heatmap = make_gradcam_heatmap(input_face, model, "conv2d_5")
                            display_gradcam(
                                frame, heatmap, (x_min, y_min, x_max - x_min, y_max - y_min)
                            )

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

            if video_path and total_frames > 0:
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                updating_trackbar = True
                cv2.setTrackbarPos("Progress", window_name, current_frame)
                updating_trackbar = False

            cv2.imshow(window_name, frame)

        key = cv2.waitKey(1 if not paused else 30) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord(" ") and video_path:
            paused = not paused
        elif key == ord("a") and video_path:
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, current_frame - 30))
            force_read = True
        elif key == ord("d") and video_path:
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(total_frames, current_frame + 30))
            force_read = True
        elif key == ord("g"):
            gradcam_active = not gradcam_active
            print(f"Grad-CAM: {'ON' if gradcam_active else 'OFF'}")

    if cap:
        cap.release()
    if sct:
        sct.close()
    face_detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
