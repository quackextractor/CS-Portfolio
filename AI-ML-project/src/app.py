import os
import cv2
import yaml
import logging
import numpy as np
import tensorflow as tf

try:
    import mediapipe as mp
except ImportError as err:
    raise ImportError("mediapipe is not installed. Run: pip install mediapipe") from err

try:
    import mss
except ImportError:
    mss = None


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def generate_tiles(detection_frame):
    h, w = detection_frame.shape[:2]
    
    # Yield 1: Full frame
    yield detection_frame, 0, 0

    # Yield 2 to 5: Quadrants
    mid_x, mid_y = w // 2, h // 2
    yield detection_frame[0:mid_y, 0:mid_x], 0, 0
    yield detection_frame[0:mid_y, mid_x:w], mid_x, 0
    yield detection_frame[mid_y:h, 0:mid_x], 0, mid_y
    yield detection_frame[mid_y:h, mid_x:w], mid_x, mid_y

    # Yield 6: Center Crop
    q_w, q_h = mid_x, mid_y
    c_x, c_y = w // 4, h // 4
    yield detection_frame[c_y:c_y+q_h, c_x:c_x+q_w], c_x, c_y


def get_grad_model(model, last_conv_layer_name=None):
    """
    Splits the model into a feature extractor and a classifier
    by functionally rebuilding the layers to avoid Keras 3 input graph bugs.
    """
    
    # If the loaded model is a wrapper, extract the inner base model
    if len(model.layers) >= 2 and isinstance(model.layers[6], tf.keras.Model):
        model = model.layers[6] 

    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if "Conv2D" in layer.__class__.__name__:
                last_conv_layer_name = layer.name
                break

    if last_conv_layer_name is None:
        return None, None

    # 1. Safely determine the input shape
    try:
        input_shape = model.input_shape[1:]
    except AttributeError:
        input_shape = (128, 128, 3)

    # 2. Rebuild the Feature Extractor functionally
    feature_input = tf.keras.Input(shape=input_shape)
    x = feature_input
    
    last_conv_layer = None
    for layer in model.layers:
        # Skip InputLayer to avoid "object is not callable" errors
        if isinstance(layer, tf.keras.layers.InputLayer):
            continue
            
        x = layer(x)
        if layer.name == last_conv_layer_name:
            last_conv_layer = layer
            break

    if last_conv_layer is None:
        return None, None
        
    feature_extractor = tf.keras.Model(inputs=feature_input, outputs=x)

    # 3. Rebuild the Classifier functionally
    classifier_input = tf.keras.Input(shape=x.shape[1:])
    y = classifier_input
    
    layer_idx = model.layers.index(last_conv_layer)
    for layer in model.layers[layer_idx + 1:]:
        y = layer(y)
        
    classifier = tf.keras.Model(inputs=classifier_input, outputs=y)
    
    return feature_extractor, classifier


@tf.function(reduce_retracing=True)
def _compute_heatmap_graph(img_tensor, feature_extractor, classifier):
    with tf.GradientTape() as tape:
        last_conv_layer_output = feature_extractor(img_tensor, training=False)
        tape.watch(last_conv_layer_output)
        
        preds = classifier(last_conv_layer_output, training=False)
        class_channel = preds[:, 0] 

    grads = tape.gradient(class_channel, last_conv_layer_output)
    
    if grads is None:
        return tf.zeros(last_conv_layer_output.shape[1:3])
        
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    heatmap = tf.maximum(heatmap, 0.0)

    heatmap_max = tf.reduce_max(heatmap)
    # Use divide_no_nan to safely handle the division without needing an 'if' statement
    heatmap = tf.math.divide_no_nan(heatmap, heatmap_max)
    
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

    heatmap = heatmap * sensitivity
    heatmap = np.power(heatmap, 0.5) 
    
    heatmap = np.clip(heatmap, 0, 1)
    heatmap = (heatmap * 255).astype(np.uint8)

    heatmap_img = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap_img = cv2.resize(heatmap_img, (w, h))

    roi = frame[y:y+h, x:x+w]
    overlay = cv2.addWeighted(roi, 1.0 - alpha, heatmap_img, alpha, 0)
    frame[y:y+h, x:x+w] = overlay
    return frame


def _build_face_detector(model_path: str):
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Face detector model not found at '{model_path}'.")

    BaseOptions = mp.tasks.BaseOptions
    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE,
        min_detection_confidence=0.5
    )
    return FaceDetector.create_from_options(options)


def main(
    video_path: str = None,
    screen: bool = False,
    use_gradcam: bool = False,
    heatmap_sensitivity: float = 5.0,
    threshold_override: float = None,
    mine_enabled: bool = False,
    mine_frame_rate: int = None,
):
    config = load_config()
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]
    camera_index = config["camera"]["index"]
    face_model_path = config["model"].get("face_detector_model_path", "models/blaze_face_short_range.task")

    # Setup Mining Configuration & Directories
    mining_defaults = config.get("defaults", {}).get("run", {}).get("mining", {})
    if mine_frame_rate is None:
        mine_frame_rate = mining_defaults.get("frame_rate", 10)
    
    mining_dir = os.path.join("data", "processed", "negative", "FALSE_POSITIVES")
    os.makedirs(mining_dir, exist_ok=True)
    
    is_mining = mine_enabled
    mine_counter = 0

    if not str(model_path).endswith(".keras"):
        logging.error(f"Error: Model file must be in .keras format. Received: {model_path}")
        return

    if not os.path.exists(model_path):
        logging.error(
            f"Error: Model file not found at {model_path}. Please train first."
        )
        return

    try:
        # Added compile=False to bypass optimizer shape warnings
        model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
        grad_model = get_grad_model(model)
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return

    # Extract the baked-in threshold from the model name
    baked_threshold = 0.5
    if model.name and "thresh_" in model.name:
        try:
            thresh_str = model.name.split("thresh_")[-1].replace("p", ".")
            baked_threshold = float(thresh_str)
        except ValueError:
            pass

    # Determine the final threshold to use
    if threshold_override is not None:
        threshold = threshold_override
    elif "threshold" in config["model"]:
        threshold = float(config["model"]["threshold"])
    else:
        threshold = baked_threshold
        logging.info(f"No threshold found in config. Using model baked-in threshold: {threshold:.4f}")

    face_detector = _build_face_detector(face_model_path)

    sct_obj = None
    monitor = None
    cap = None

    if screen:
        if mss is None:
            logging.error("mss is required for screen capture. Run: pip install mss")
            return
        logging.info("Opening screen capture...")
        sct_obj = mss.mss()
        monitor = sct_obj.monitors[1]
    elif video_path:
        if not os.path.exists(video_path):
            logging.error(f"Error: Video file not found at {video_path}")
            return
        logging.info(f"Opening video {video_path}...")
        cap = cv2.VideoCapture(video_path)
    else:
        logging.info(f"Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)

    if not screen and (cap is None or not cap.isOpened()):
        logging.error("Error: Could not open video source.")
        return

    window_name = "Target Face Detector"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if video_path else 0
    paused = False
    force_read = False
    updating_trackbar = False
    gradcam_active = use_gradcam
    grid_mode_active = False
    current_sensitivity = heatmap_sensitivity
    mirrored = False
    frame_count = 0
    cached_heatmap_data = {}
    
    scale_factor = None
    iw, ih = None, None

    if video_path and total_frames > 0:
        def on_trackbar(val):
            nonlocal force_read
            if not updating_trackbar:
                cap.set(cv2.CAP_PROP_POS_FRAMES, val)
                force_read = True
        cv2.createTrackbar("Progress", window_name, 0, total_frames, on_trackbar)
        logging.info("Controls: [Space] Pause, [a/d] Skip, [g] Grad-CAM, [m] Mirror, [t] Grid Mode, [-/+] Threshold, [q] Quit")
    else:
        logging.info("Controls: [g] Grad-CAM, [m] Mirror, [t] Grid Mode, [-/+] Threshold, [n] Toggle Mining, [ { / } ] Mine FR, [q] Quit")

    while True:
        if not paused or force_read:
            if screen:
                sct_img = sct_obj.grab(monitor)
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

            if scale_factor is None:
                ih, iw, _ = frame.shape
                scale_factor = 1280 / iw if iw > 1280 else 1.0

            if scale_factor != 1.0:
                detection_frame = cv2.resize(frame, (1280, int(ih * scale_factor)))
            else:
                detection_frame = frame

            all_boxes = []
            all_scores = []

            for tile, x_offset, y_offset in generate_tiles(detection_frame):
                rgb_tile = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_tile)
                detection_result = face_detector.detect(mp_image)

                if detection_result and detection_result.detections:
                    for detection in detection_result.detections:
                        bbox = detection.bounding_box
                        origin_x = bbox.origin_x
                        origin_y = bbox.origin_y
                        width = bbox.width
                        height = bbox.height

                        new_x = origin_x + x_offset
                        new_y = origin_y + y_offset

                        all_boxes.append([new_x, new_y, width, height])
                        all_scores.append(float(detection.categories[0].score))

            if all_boxes:
                all_boxes_arr = np.array(all_boxes)
                all_scores_arr = np.array(all_scores)
                
                indices = cv2.dnn.NMSBoxes(all_boxes_arr.tolist(), all_scores_arr.tolist(), 0.5, 0.4)
                
                final_boxes = []
                if len(indices) > 0:
                    for i in indices.flatten():
                        final_boxes.append(all_boxes[i])

                faces_batch = []
                face_coords = []
                
                for box in final_boxes:
                    x, y, w, h = box
                    x = int(x / scale_factor)
                    y = int(y / scale_factor)
                    w = int(w / scale_factor)
                    h = int(h / scale_factor)

                    margin_x, margin_y = int(w * 0.05), int(h * 0.05)
                    x_min, y_min = max(0, x - margin_x), max(0, y - margin_y)
                    x_max, y_max = min(iw, x + w + margin_x), min(ih, y + h + margin_y)

                    cropped_face = frame[y_min:y_max, x_min:x_max]
                    if cropped_face.size > 0:
                        resized_face = cv2.resize(cropped_face, (img_size, img_size))
                        rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
                        normalized_face = rgb_face / 255.0
                       
                        faces_batch.append(normalized_face)
                        face_coords.append((x_min, y_min, x_max, y_max))

                if faces_batch:
                    batch_tensor = np.array(faces_batch)
                    predictions = model(batch_tensor, training=False)
                   
                    new_cached_heatmaps = {}
                   
                    for face_idx, (prediction_tensor, coords) in enumerate(zip(predictions, face_coords)):
                        prediction = prediction_tensor[0].numpy()
                        is_target = prediction >= threshold
                        label = f"{'Target' if is_target else 'Unknown'} ({prediction:.2f})"
                        color = (0, 255, 0) if is_target else (0, 0, 255)
                       
                        x_min, y_min, x_max, y_max = coords

                        if gradcam_active:
                            input_face = np.expand_dims(faces_batch[face_idx], axis=0)
                           
                            if frame_count % 15 == 0 or face_idx not in cached_heatmap_data:
                                heatmap = make_gradcam_heatmap(input_face, grad_model)
                                new_cached_heatmaps[face_idx] = heatmap
                            else:
                                heatmap = cached_heatmap_data[face_idx]
                                new_cached_heatmaps[face_idx] = heatmap

                            display_gradcam(
                                frame, heatmap, (x_min, y_min, x_max - x_min, y_max - y_min),
                                sensitivity=current_sensitivity
                            )

                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
                        cv2.putText(
                            frame, label, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2
                        )

                        # Mining Extraction Logic
                        if is_mining and is_target and (mine_counter % mine_frame_rate == 0):
                            from datetime import datetime
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                            save_path = os.path.join(mining_dir, f"mined_fp_{timestamp}.jpg")
                            
                            # Save the un-normalized 128x128 crop
                            cv2.imwrite(save_path, resized_face)
                            logging.info(f"Saved false positive: {save_path}")
                    
                    if gradcam_active:
                        cached_heatmap_data = new_cached_heatmaps

            if grid_mode_active:
                f_h, f_w = frame.shape[:2]
                mid_x, mid_y = f_w // 2, f_h // 2
                
                cv2.line(frame, (mid_x, 0), (mid_x, f_h), (0, 255, 255), 2)
                cv2.line(frame, (0, mid_y), (f_w, mid_y), (0, 255, 255), 2)
                
                c_w, c_h = mid_x, mid_y
                c_x, c_y = f_w // 4, f_h // 4
                cv2.rectangle(frame, (c_x, c_y), (c_x + c_w, c_y + c_h), (0, 255, 255), 2)

            if is_mining:
                status_text = f"MINING ON (1/{mine_frame_rate})"
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            frame_count += 1
            mine_counter += 1

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
        elif key == ord("t"):
            grid_mode_active = not grid_mode_active
            logging.info(f"Grid Mode: {'ON' if grid_mode_active else 'OFF'}")
        elif key == ord("-"):
            threshold = max(0.0, threshold - 0.05)
            logging.info(f"Threshold adjusted: {threshold:.2f}")
        elif key == ord("=") or key == ord("+"):
            threshold = min(1.0, threshold + 0.05)
            logging.info(f"Threshold adjusted: {threshold:.2f}")
        elif key == ord("["):
            current_sensitivity = max(1.0, current_sensitivity - 1.0)
            logging.info(f"Heatmap Sensitivity: {current_sensitivity:.1f}x")
        elif key == ord("]"):
            current_sensitivity = min(20.0, current_sensitivity + 1.0)
            logging.info(f"Heatmap Sensitivity: {current_sensitivity:.1f}x")
        elif key == ord("n"):
            is_mining = not is_mining
            logging.info(f"Mining toggled: {'ON' if is_mining else 'OFF'}")
        elif key == ord("{"):
            mine_frame_rate = max(1, mine_frame_rate - 1)
            logging.info(f"Mining frame rate decreased to: {mine_frame_rate}")
        elif key == ord("}"):
            mine_frame_rate += 1
            logging.info(f"Mining frame rate increased to: {mine_frame_rate}")

    if cap:
        cap.release()
    if sct_obj:
        sct_obj.close()
    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()