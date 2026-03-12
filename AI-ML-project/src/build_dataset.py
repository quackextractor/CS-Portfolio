import os
import cv2
import yaml
import pandas as pd
import argparse
from tqdm import tqdm
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def is_blurry(image, threshold: float = 10.0) -> bool:
    """Returns True if the image is considered blurry."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

def _build_face_detector(model_path: str):
    """
    Construct a MediaPipe Tasks FaceDetector using the Tasks API
    (mediapipe >= 0.10.x, which no longer ships mediapipe.solutions).

    Raises:
        ImportError:  if mediapipe is not installed.
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
            "Download it by running: python vendor/setup_models.py  "
            "or see the README for manual download instructions."
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

def process_images(
    input_dir: str,
    output_dir: str,
    label: int,
    img_size: int,
    model_path: str = "models/blaze_face_short_range.task",
    skip_blurry: bool = True,
    blur_threshold: float = 10.0,
) -> list:
    """
    Processes images in a directory (recursively): detects faces, crops, resizes, and saves them.
    Mirrors the subfolder structure of the input_dir.
    """
    import mediapipe as mp

    records = []
    face_detector = _build_face_detector(model_path)

    # Find all image files recursively
    image_paths = []
    valid_extensions = ('.jpg', '.jpeg', '.png')
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(valid_extensions):
                image_paths.append(os.path.join(root, f))

    processed_count = 0
    discarded_count = 0

    pbar = tqdm(image_paths, desc=f"  Label {label}", leave=False)
    for img_path in pbar:
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            discarded_count += 1
            continue

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        detection_result = face_detector.detect(mp_image)

        if not detection_result.detections or len(detection_result.detections) != 1:
            discarded_count += 1
            continue

        detection = detection_result.detections[0]
        bbox = detection.bounding_box
        x = bbox.origin_x
        y = bbox.origin_y
        w = bbox.width
        h = bbox.height

        ih, iw, _ = img_bgr.shape

        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)

        x_min = max(0, x - margin_x)
        y_min = max(0, y - margin_y)
        x_max = min(iw, x + w + margin_x)
        y_max = min(ih, y + h + margin_y)

        cropped_face = img_bgr[y_min:y_max, x_min:x_max]

        if cropped_face.size == 0:
            discarded_count += 1
            continue

        if skip_blurry and is_blurry(cropped_face, blur_threshold):
            discarded_count += 1
            continue

        resized_face = cv2.resize(cropped_face, (img_size, img_size))

        # Mirror subfolder structure
        rel_path = os.path.relpath(img_path, input_dir)
        output_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, resized_face)

        rel_output_path = os.path.relpath(output_path, start=".")
        records.append({"filepath": rel_output_path, "label": label})
        processed_count += 1

    face_detector.close()
    print(
        f"Processed {processed_count} images for label {label}. "
        f"Discarded {discarded_count}."
    )
    return records

def run_processing(
    class_target: str = "both",
    folder: str = None,
    trigger_build: bool = False,
    skip_blurry: bool = True,
    blur_threshold: float = 10.0,
) -> None:
    config = load_config()
    raw_positive_dir = config["data"]["raw_positive_dir"]
    raw_negative_dir = config["data"]["raw_negative_dir"]
    processed_dir = config["data"]["processed_dir"]
    img_size = config["model"]["img_size"]
    model_path = config["model"].get(
        "face_detector_model_path", "models/blaze_face_short_range.task"
    )

    if folder:
        raw_positive_dir = os.path.join(raw_positive_dir, folder)
        raw_negative_dir = os.path.join(raw_negative_dir, folder)
        proc_pos_dir = os.path.join(processed_dir, "positive", folder)
        proc_neg_dir = os.path.join(processed_dir, "negative", folder)
    else:
        proc_pos_dir = os.path.join(processed_dir, "positive")
        proc_neg_dir = os.path.join(processed_dir, "negative")

    if class_target in ("positive", "both") and os.path.exists(raw_positive_dir):
        print(f"Processing positive class: {raw_positive_dir}")
        process_images(
            raw_positive_dir,
            proc_pos_dir,
            label=1,
            img_size=img_size,
            model_path=model_path,
            skip_blurry=skip_blurry,
            blur_threshold=blur_threshold,
        )

    if class_target in ("negative", "both") and os.path.exists(raw_negative_dir):
        print(f"Processing negative class: {raw_negative_dir}")
        process_images(
            raw_negative_dir,
            proc_neg_dir,
            label=0,
            img_size=img_size,
            model_path=model_path,
            skip_blurry=skip_blurry,
            blur_threshold=blur_threshold,
        )

    if trigger_build:
        run_building()

def run_building(output_csv: str = None) -> None:
    config = load_config()
    processed_dir = config["data"]["processed_dir"]
    if output_csv is None:
        output_csv = config["data"]["dataset_csv"]

    print(f"Building dataset CSV from {processed_dir}...")
    
    records = []
    # Scan processed/positive and processed/negative
    for label, sub in [(1, "positive"), (0, "negative")]:
        target_dir = os.path.join(processed_dir, sub)
        if not os.path.exists(target_dir):
            continue
        for root, _, files in os.walk(target_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    abs_p = os.path.join(root, f)
                    rel_p = os.path.relpath(abs_p, start=".")
                    records.append({"filepath": rel_p, "label": label})

    if not records:
        print("No processed images found. Run 'process' command first.")
        return

    df = pd.DataFrame(records)

    # Extract video name from filepath to prevent data leakage
    def get_video_name(path):
        # Normalize slashes for cross-platform compatibility
        path_str = str(path).replace('\\', '/')
        parts = Path(path_str).parts
        
        # We want the immediate parent folder if it's not 'positive' or 'negative'
        if len(parts) > 3 and parts[2] in ('positive', 'negative'):
            folder = parts[3]
            # Treat each scraped image as independent to allow even distribution
            if folder == 'scraped':
                return f"scraped_{Path(path_str).stem}"
            return folder
        return "unknown"

    df['video_name'] = df['filepath'].apply(get_video_name)

    train_dfs, val_dfs, test_dfs = [], [], []
    import random
    random.seed(42)

    for label in df['label'].unique():
        label_df = df[df['label'] == label].copy()
        videos = sorted(label_df['video_name'].unique())
        random.shuffle(videos)

        n_vids = len(videos)
        
        # 80% Train, 10% Val, 10% Test
        train_end = int(n_vids * 0.8)
        val_end = int(n_vids * 0.9)

        train_vids = set(videos[:train_end])
        val_vids = set(videos[train_end:val_end])

        def assign_split(vid):
            if vid in train_vids:
                return 'train'
            if vid in val_vids:
                return 'val'
            return 'test'

        label_df['split'] = label_df['video_name'].apply(assign_split)
        train_dfs.append(label_df[label_df['split'] == 'train'])
        val_dfs.append(label_df[label_df['split'] == 'val'])
        test_dfs.append(label_df[label_df['split'] == 'test'])

    all_dfs = train_dfs + val_dfs + test_dfs
    if not all_dfs:
        print("Error: No data subsets were created. Check video folder names and data.")
        return
    final_df = pd.concat(all_dfs).sort_index()
    dir_name = os.path.dirname(output_csv)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    final_df.to_csv(output_csv, index=False)

    print(f"Dataset successfully built with {len(final_df)} records.")
    print(f"Split stats: Train={len(final_df[final_df['split'] == 'train'])}, "
          f"Val={len(final_df[final_df['split'] == 'val'])}, "
          f"Test={len(final_df[final_df['split'] == 'test'])}")
    print(f"CSV saved to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build dataset logic")
    parser.add_argument("--process", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--class_target", default="both")
    parser.add_argument("--folder", default=None)
    parser.add_argument("--no_skip_blurry", action="store_false", dest="skip_blurry")
    parser.add_argument("--blur_threshold", type=float, default=10.0)
    args = parser.parse_args()

    if args.process:
        run_processing(
            class_target=args.class_target,
            folder=args.folder,
            trigger_build=args.build,
            skip_blurry=args.skip_blurry,
            blur_threshold=args.blur_threshold
        )
    elif args.build:
        run_building()
    else:
        # Backward compatibility or default behavior if no flags passed
        run_processing(trigger_build=True)