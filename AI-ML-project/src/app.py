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
    Splits the model into a feature extractor and a classifier
    to guarantee explicit gradient tracking.
    """
    if last_conv_layer_name is None:
        # First try to find the explicitly named optimal layer
        for layer in model.layers:
            if layer.name == "target_conv_layer":
                last_conv_layer_name = layer.name
                break
        
        # Fallback to the last convolutional layer found
        if last_conv_layer_name is None:
            for layer in reversed(model.layers):
                if "Conv2D" in layer.__class__.__name__:
                    last_conv_layer_name = layer.name
                    break

    if last_conv_layer_name is None:
        return None, None

    last_conv_layer = model.get_layer(last_conv_layer_name)
    feature_extractor = tf.keras.Model(
        inputs=model.layers[0].input, 
        outputs=last_conv_layer.output
    )

    classifier_input = tf.keras.Input(shape=last_conv_layer.output.shape[1:])
    x = classifier_input
    
    layer_idx = model.layers.index(last_conv_layer)
    for layer in model.layers[layer_idx + 1:]:
        x = layer(x)
        
    classifier = tf.keras.Model(inputs=classifier_input, outputs=x)
    return feature_extractor, classifier

@tf.function(reduce_retracing=True)
def _compute_heatmap_graph(img_tensor, feature_extractor, classifier):
    with tf.GradientTape() as tape:
        last_conv_layer_output = feature_extractor(img_tensor, training=False)
        tape.watch(last_conv_layer_output)
        
        preds = classifier(last_conv_layer_output, training=False)
        # For Binary (1 output), we take the gradient of the raw score
        class_channel = preds[:, 0] 

    grads = tape.gradient(class_channel, last_conv_layer_output)
    
    if grads is None:
        return tf.zeros(last_conv_layer_output.shape[1:3])
        
    # Standard Grad-CAM: Weight channels by the mean gradient
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # ReLU: We only care about positive influence
    heatmap = tf.maximum(heatmap, 0.0)

    # Robust Normalization: Avoid division by zero and handle low-signal frames
    heatmap_max = tf.reduce_max(heatmap)
    if heatmap_max > 0:
        heatmap = heatmap / heatmap_max
    
    return heatmap

def compute_heatmap(img_tensor, grad_models, pred_index=None):
    feature_extractor, classifier = grad_models
    if feature_extractor is None or classifier is None:
        return tf.zeros((img_tensor.shape[1], img_tensor.shape[2]))
    return _compute_heatmap_graph(img_tensor, feature_extractor, classifier)

def make_gradcam_heatmap(img_array, grad_model, pred_index=None):
    if grad_model is None:
        return np.zeros((img_array.shape[1], img_array.shape[2]))
    img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
    heatmap = compute_heatmap(img_tensor, grad_model, pred_index)
    return heatmap.numpy()

def display_gradcam(frame, heatmap, bbox, alpha=0.5, sensitivity=2.0):
    x, y, w, h = bbox

    # 1. Boost the heatmap intensity using sensitivity
    heatmap = heatmap * sensitivity
    
    # 2. Use a different power law to make 'hot' spots broader
    # Gamma < 1 makes the peaks larger; Gamma > 1 makes them sharper
    heatmap = np.power(heatmap, 0.5) 
    
    heatmap = np.clip(heatmap, 0, 1)
    heatmap = (heatmap * 255).astype(np.uint8)

    # 3. Apply color map
    heatmap_img = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap_img = cv2.resize(heatmap_img, (w, h))

    # 4. Blend
    roi = frame[y:y+h, x:x+w]
    # Increase alpha slightly to see the 'glow' better
    overlay = cv2.addWeighted(roi, 1.0 - alpha, heatmap_img, alpha, 0)
    frame[y:y+h, x:x+w] = overlay
    return frame

def _build_face_detector(model_path: str, running_mode=None, result_callback=None):
    try:
        import mediapipe as mp
    except ImportError as err:
        raise ImportError("mediapipe is not installed. Run: pip install -r requirements.txt") from err

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Face detector model not found at '{model_path}'.")

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
    face_model_path = config["model"].get("face_detector_model_path", "models/blaze_face_short_range.task")

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
        face_detector = _build_face_detector(face_model_path, running_mode=mode, result_callback=live_stream_callback)
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
    cached_heatmap_data = {}

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
                if video_path:
                    paused = True
                    current_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, current_pos - 1))
                    force_read = True
                    continue
                else:
                    break

            force_read = False
            if mirrored:
                frame = cv2.flip(frame, 1)

            ih, iw, _ = frame.shape
            scale_factor = 1.0
            if iw > 1280:
                scale_factor = 1280 / iw
                detection_frame = cv2.resize(frame, (1280, int(ih * scale_factor)))
            else:
                detection_frame = frame

            rgb_frame = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            if mode == VisionRunningMode.LIVE_STREAM:
                timestamp_ms = int(time.time() * 1000)
                face_detector.detect_async(mp_image, timestamp_ms)
                detection_result = latest_result
            else:
                detection_result = face_detector.detect(mp_image)

            if detection_result and detection_result.detections:
                for face_idx, detection in enumerate(detection_result.detections):
                    bbox = detection.bounding_box
                    x = int(bbox.origin_x / scale_factor)
                    y = int(bbox.origin_y / scale_factor)
                    w = int(bbox.width / scale_factor)
                    h = int(bbox.height / scale_factor)

                    margin_x, margin_y = int(w * 0.1), int(h * 0.1)
                    x_min, y_min = max(0, x - margin_x), max(0, y - margin_y)
                    x_max, y_max = min(iw, x + w + margin_x), min(ih, y + h + margin_y)

                    cropped_face = frame[y_min:y_max, x_min:x_max]
                    if cropped_face.size > 0:
                        resized_face = cv2.resize(cropped_face, (img_size, img_size))
                        rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
                        input_face = np.expand_dims(rgb_face / 255.0, axis=0)

                        prediction = model(input_face, training=False)[0][0].numpy()
                        is_target = prediction >= threshold
                        label = f"{'Target' if is_target else 'Unknown'} ({prediction:.2f})"
                        color = (0, 255, 0) if is_target else (0, 0, 255)

                        if gradcam_active:
                            if frame_count % 15 == 0 or face_idx not in cached_heatmap_data:
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