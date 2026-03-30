import os
import cv2
import yaml
import logging
import base64
import requests
import numpy as np

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
    yield detection_frame, 0, 0
    mid_x, mid_y = w // 2, h // 2
    yield detection_frame[0:mid_y, 0:mid_x], 0, 0
    yield detection_frame[0:mid_y, mid_x:w], mid_x, 0
    yield detection_frame[mid_y:h, 0:mid_x], 0, mid_y
    yield detection_frame[mid_y:h, mid_x:w], mid_x, mid_y
    q_w, q_h = mid_x, mid_y
    c_x, c_y = w // 4, h // 4
    yield detection_frame[c_y:c_y+q_h, c_x:c_x+q_w], c_x, c_y

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
    server_url = config.get("server", {}).get("url", "http://127.0.0.1:5000/predict")
    config_url = server_url.replace("/predict", "/configure")
    
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]
    camera_index = config["camera"]["index"]
    face_model_path = config["model"].get("face_detector_model_path", "models/blaze_face_short_range.task")

    logging.info(f"Syncing configuration with remote server: requesting model '{model_path}'")
    try:
        response = requests.post(config_url, json={"model_path": model_path}, timeout=10.0)
        if response.status_code == 200:
            logging.info(f"Server synchronized successfully: {response.json().get('message')}")
        else:
            logging.error(f"Server refused configuration sync: {response.text}")
            return
    except Exception as e:
        logging.error(f"Could not reach server at {config_url} for initial configuration sync. Is it running?")
        return

    mining_defaults = config.get("defaults", {}).get("run", {}).get("mining", {})
    if mine_frame_rate is None:
        mine_frame_rate = mining_defaults.get("frame_rate", 10)
    mining_dir = os.path.join("data", "processed", "negative", "FALSE_POSITIVES")
    os.makedirs(mining_dir, exist_ok=True)
    
    is_mining = mine_enabled
    mine_counter = 0

    if threshold_override is not None:
        threshold = threshold_override
    elif "threshold" in config["model"]:
        threshold = float(config["model"]["threshold"])
    else:
        threshold = 0.5
        logging.info("Using default threshold: 0.5000")

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

    window_name = "Target Face Detector (Remote Client Mode)"
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
                        new_x = bbox.origin_x + x_offset
                        new_y = bbox.origin_y + y_offset
                        all_boxes.append([new_x, new_y, bbox.width, bbox.height])
                        all_scores.append(float(detection.categories[0].score))

            if all_boxes:
                all_boxes_arr = np.array(all_boxes)
                all_scores_arr = np.array(all_scores)
                indices = cv2.dnn.NMSBoxes(all_boxes_arr.tolist(), all_scores_arr.tolist(), 0.5, 0.4)
                
                final_boxes = []
                if len(indices) > 0:
                    for i in indices.flatten():
                        final_boxes.append(all_boxes[i])

                faces_batch_b64 = []
                face_coords = []
                raw_faces = []
                
                for box in final_boxes:
                    x, y, w, h = box
                    x, y, w, h = int(x / scale_factor), int(y / scale_factor), int(w / scale_factor), int(h / scale_factor)

                    margin_x, margin_y = int(w * 0.05), int(h * 0.05)
                    x_min, y_min = max(0, x - margin_x), max(0, y - margin_y)
                    x_max, y_max = min(iw, x + w + margin_x), min(ih, y + h + margin_y)

                    cropped_face = frame[y_min:y_max, x_min:x_max]
                    if cropped_face.size > 0:
                        _, buffer = cv2.imencode('.jpg', cropped_face)
                        b64_str = base64.b64encode(buffer).decode('utf-8')
                        faces_batch_b64.append(b64_str)
                        face_coords.append((x_min, y_min, x_max, y_max))
                        raw_faces.append(cv2.resize(cropped_face, (img_size, img_size)))

                if faces_batch_b64:
                    payload = {"faces": faces_batch_b64, "gradcam": gradcam_active and (frame_count % 15 == 0)}
                    try:
                        response = requests.post(server_url, json=payload, timeout=2.0)
                        if response.status_code == 200:
                            predictions = response.json().get("results", [])
                        else:
                            predictions = []
                            logging.warning(f"Server error: {response.status_code}")
                    except Exception:
                        predictions = []
                        logging.warning(f"Connection failed: Ensure server is running at {server_url}")

                    new_cached_heatmaps = {}
                   
                    for face_idx, (prediction_data, coords) in enumerate(zip(predictions, face_coords)):
                        prediction = prediction_data.get("prediction", 0.0)
                        is_target = prediction >= threshold
                        label = f"{'Target' if is_target else 'Unknown'} ({prediction:.2f})"
                        color = (0, 255, 0) if is_target else (0, 0, 255)
                       
                        x_min, y_min, x_max, y_max = coords

                        if gradcam_active:
                            if "heatmap" in prediction_data:
                                heatmap_bytes = base64.b64decode(prediction_data["heatmap"])
                                heatmap_arr = np.frombuffer(heatmap_bytes, np.uint8)
                                heatmap_img = cv2.imdecode(heatmap_arr, cv2.IMREAD_GRAYSCALE)
                                heatmap_float = heatmap_img.astype(np.float32) / 255.0
                                new_cached_heatmaps[face_idx] = heatmap_float
                                heatmap = heatmap_float
                            else:
                                heatmap = cached_heatmap_data.get(face_idx, np.zeros((126, 126)))
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

                        if is_mining and is_target and (mine_counter % mine_frame_rate == 0):
                            from datetime import datetime
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                            save_path = os.path.join(mining_dir, f"mined_fp_{timestamp}.jpg")
                            cv2.imwrite(save_path, raw_faces[face_idx])
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