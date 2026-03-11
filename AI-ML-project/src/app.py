import os
import cv2
import numpy as np
import tensorflow as tf
import yaml
import logging


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_grad_model(model, last_conv_layer_name=None):
    """
    Pre-builds a multi-output model for gradient calculation.
    """
    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if "Conv2D" in layer.__class__.__name__:
                last_conv_layer_name = layer.name
                break

    if last_conv_layer_name is None:
        return None

    # Use layer references to avoid Sequential API missing attribute errors
    return tf.keras.Model(
        inputs=model.layers[0].input, 
        outputs=[model.get_layer(last_conv_layer_name).output, model.layers[-1].output]
    )


@tf.function
def compute_heatmap(img_tensor, grad_model, pred_index=None):
    """
    Optimized heatmap calculation using static graph.
    """
    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_tensor)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Normalization (Min-Max scaling for peak normalization)
    heatmap_min = tf.reduce_min(heatmap)
    heatmap_max = tf.reduce_max(heatmap)
    heatmap = (heatmap - heatmap_min) / (heatmap_max - heatmap_min + 1e-8)

    # Non-linear power transformation (gamma correction)
    heatmap = tf.pow(heatmap, 0.6)
    return heatmap


def make_gradcam_heatmap(img_array, grad_model, pred_index=None):
    """
    Wrapper for compute_heatmap to handle numpy conversion.
    """
    if grad_model is None:
        return np.zeros((img_array.shape[1], img_array.shape[2]))

    img_tensor = tf.cast(img_array, tf.float32)
    heatmap = compute_heatmap(img_tensor, grad_model, pred_index)
    return heatmap.numpy()


def display_gradcam(frame, heatmap, bbox, alpha=0.6, sensitivity=1.0):
    """
    Overlays the Grad-CAM heatmap on the detected face in the frame.
    """
    x, y, w, h = bbox

    # Apply sensitivity multiplier
    heatmap = np.clip(heatmap * sensitivity, 0.0, 1.0)

    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # Use jet colormap to colorize heatmap
    jet = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Resize heatmap to match the bounding box size
    jet = cv2.resize(jet, (w, h))

    # Create an overlay by combining the original ROI and the colorized heatmap
    roi = frame[y: y + h, x: x + w]
    overlay = cv2.addWeighted(roi, 1 - alpha, jet, alpha, 0)

    # Replace the ROI in the original frame
    frame[y: y + h, x: x + w] = overlay
    return frame


def _build_face_detector(model_path: str, running_mode=None, result_callback=None):
    """
    Construct a MediaPipe Tasks FaceDetector.
    """
    try:
        import mediapipe as mp
    except ImportError as err:
        raise ImportError(
            "mediapipe is not installed. Run: pip install -r requirements.txt"
        ) from err

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Face detector model not found at '{model_path}'.")

    try:
        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        if running_mode is None:
            running_mode = VisionRunningMode.IMAGE

        is_live = running_mode == VisionRunningMode.LIVE_STREAM
        options = FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=running_mode,
            min_detection_confidence=0.5,
            result_callback=result_callback if is_live else None
        )
        return FaceDetector.create_from_options(options)
    except Exception as e:
        raise RuntimeError(f"Failed to initialise MediaPipe FaceDetector: {e}") from e


def main(
    video_path: str = None,
    screen: bool = False,
    use_gradcam: bool = False,
    heatmap_sensitivity: float = 5.0,
):
    import mediapipe as mp
    import mss
    import time

    config = load_config()
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]
    camera_index = config["camera"]["index"]
    threshold = config["model"].get("threshold", 0.5)
    face_model_path = config["model"].get(
        "face_detector_model_path", "models/blaze_face_short_range.task"
    )

    if not str(model_path).endswith(".keras"):
        logging.error(f"Error: Model file must be in .keras format. Received: {model_path}")
        return

    if not os.path.exists(model_path):
        logging.error(f"Error: Model file not found at {model_path}. Please train first.")
        return

    try:
        model = tf.keras.models.load_model(model_path)
        grad_model = get_grad_model(model)
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return

    latest_result = None

    def live_stream_callback(result, output_image, timestamp_ms):
        nonlocal latest_result
        latest_result = result

    VisionRunningMode = mp.tasks.vision.RunningMode
    if screen or (not video_path and not screen):
        mode = VisionRunningMode.LIVE_STREAM
        face_detector = _build_face_detector(
            face_model_path, running_mode=mode, result_callback=live_stream_callback
        )
    elif video_path:
        mode = VisionRunningMode.VIDEO
        face_detector = _build_face_detector(face_model_path, running_mode=mode)
    else:
        mode = VisionRunningMode.IMAGE
        face_detector = _build_face_detector(face_model_path, running_mode=mode)

    sct = None
    monitor = None
    cap = None

    if screen:
        logging.info("Opening screen capture...")
        sct = mss.mss()
        monitor = sct.monitors[1]
    elif video_path:
        if not os.path.exists(video_path):
            logging.error(f"Error: Video file not found at {video_path}")
            face_detector.close()
            return
        logging.info(f"Opening video {video_path}...")
        cap = cv2.VideoCapture(video_path)
    else:
        logging.info(f"Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)

    if not screen and (cap is None or not cap.isOpened()):
        logging.error("Error: Could not open video source.")
        face_detector.close()
        return

    window_name = "Target Face Detector"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if video_path else 0
    paused = False
    force_read = False
    updating_trackbar = False
    gradcam_active = use_gradcam
    current_sensitivity = heatmap_sensitivity
    mirrored = False
    frame_count = 0
    cached_heatmap_data = {}  # {face_id: heatmap}

    if video_path and total_frames > 0:
        def on_trackbar(val):
            nonlocal force_read
            if not updating_trackbar:
                cap.set(cv2.CAP_PROP_POS_FRAMES, val)
                force_read = True
        cv2.createTrackbar("Progress", window_name, 0, total_frames, on_trackbar)
        logging.info("Controls: [Space] Pause, [a/d] Skip, [g] Grad-CAM, [m] Mirror, [q] Quit")

    while True:
        if not paused or force_read:
            if screen:
                sct_img = sct.grab(monitor)
                frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
                ret = True
            else:
                ret, frame = cap.read()

            if not ret:
                break

            force_read = False
            if mirrored:
                frame = cv2.flip(frame, 1)

            # Phase 1: Dynamic Frame Downscaling for detection
            ih, iw, _ = frame.shape
            scale_factor = 1.0
            if iw > 1280:
                scale_factor = 1280 / iw
                detection_frame = cv2.resize(frame, (1280, int(ih * scale_factor)))
            else:
                detection_frame = frame

            rgb_frame = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            timestamp_ms = int(time.time() * 1000)
            if mode == VisionRunningMode.LIVE_STREAM:
                face_detector.detect_async(mp_image, timestamp_ms)
                detection_result = latest_result
            elif mode == VisionRunningMode.VIDEO:
                v_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
                detection_result = face_detector.detect_for_video(mp_image, v_timestamp_ms)
            else:
                detection_result = face_detector.detect(mp_image)

            if detection_result and detection_result.detections:
                for face_idx, detection in enumerate(detection_result.detections):
                    bbox = detection.bounding_box
                    # Map back to original resolution
                    x = int(bbox.origin_x / scale_factor)
                    y = int(bbox.origin_y / scale_factor)
                    w = int(bbox.width / scale_factor)
                    h = int(bbox.height / scale_factor)

                    # Margin for cropping
                    margin_x, margin_y = int(w * 0.1), int(h * 0.1)
                    x_min, y_min = max(0, x - margin_x), max(0, y - margin_y)
                    x_max, y_max = min(iw, x + w + margin_x), min(ih, y + h + margin_y)

                    cropped_face = frame[y_min:y_max, x_min:x_max]
                    if cropped_face.size > 0:
                        resized_face = cv2.resize(cropped_face, (img_size, img_size))
                        rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
                        input_face = np.expand_dims(rgb_face / 255.0, axis=0)

                        prediction = model.predict(input_face, verbose=0)[0][0]
                        is_target = prediction >= threshold
                        label = f"{'Target' if is_target else 'Unknown'} ({prediction:.2f})"
                        color = (0, 255, 0) if is_target else (0, 0, 255)

                        if gradcam_active:
                            # Phase 2: Frame skipping and caching
                            if frame_count % 5 == 0 or face_idx not in cached_heatmap_data:
                                heatmap = make_gradcam_heatmap(input_face, grad_model)
                                cached_heatmap_data[face_idx] = heatmap
                            else:
                                heatmap = cached_heatmap_data[face_idx]

                            display_gradcam(
                                frame, heatmap, (x_min, y_min, x_max - x_min, y_max - y_min),
                                sensitivity=current_sensitivity
                            )

                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
                        cv2.putText(
                            frame, label, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2
                        )
                frame_count += 1

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
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, cap.get(cv2.CAP_PROP_POS_FRAMES) - 30))
            force_read = True
        elif key == ord("d") and video_path:
            new_pos = min(total_frames, cap.get(cv2.CAP_PROP_POS_FRAMES) + 30)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
            force_read = True
        elif key == ord("g"):
            gradcam_active = not gradcam_active
            logging.info(f"Grad-CAM: {'ON' if gradcam_active else 'OFF'}")
        elif key == ord("m"):
            mirrored = not mirrored
            logging.info(f"Mirror Mode: {'ON' if mirrored else 'OFF'}")
        elif key == ord("["):
            current_sensitivity = max(1.0, current_sensitivity - 1.0)
            logging.info(f"Heatmap Sensitivity: {current_sensitivity:.1f}x")
        elif key == ord("]"):
            current_sensitivity = min(20.0, current_sensitivity + 1.0)
            logging.info(f"Heatmap Sensitivity: {current_sensitivity:.1f}x")

    if cap:
        cap.release()
    if sct:
        sct.close()
    face_detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
