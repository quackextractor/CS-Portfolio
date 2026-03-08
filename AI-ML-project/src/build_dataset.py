import os
import cv2
import yaml
import glob
import pandas as pd
import argparse
from sklearn.model_selection import train_test_split


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def is_blurry(image, threshold: float = 100.0) -> bool:
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
    blur_threshold: float = 100.0,
) -> list:
    """
    Processes images in a directory: detects faces, crops, resizes, and saves them.
    Returns a list of dictionaries with metadata for the CSV.
    """
    import mediapipe as mp

    records = []

    face_detector = _build_face_detector(model_path)

    os.makedirs(output_dir, exist_ok=True)

    image_paths = glob.glob(os.path.join(input_dir, "*.[jp][pn]g")) + glob.glob(
        os.path.join(input_dir, "*.jpeg")
    )

    processed_count = 0
    discarded_count = 0

    for img_path in image_paths:
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            discarded_count += 1
            print(f"Failed to read image: {img_path}")
            continue

        # Tasks API requires an mp.Image in RGB format
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        detection_result = face_detector.detect(mp_image)

        # We strictly require exactly one face
        if not detection_result.detections or len(detection_result.detections) != 1:
            discarded_count += 1
            continue

        detection = detection_result.detections[0]
        # BoundingBox is now absolute pixels in the Tasks API
        bbox = detection.bounding_box
        x = bbox.origin_x
        y = bbox.origin_y
        w = bbox.width
        h = bbox.height

        ih, iw, _ = img_bgr.shape

        # Add a slight margin (helps CNN generalise)
        margin_x = int(w * 0.1)
        margin_y = int(h * 0.1)

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

        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
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


def build_dataset(skip_blurry: bool = True, blur_threshold: float = 100.0) -> None:
    config = load_config()
    raw_positive_dir = config["data"]["raw_positive_dir"]
    raw_negative_dir = config["data"]["raw_negative_dir"]
    processed_dir = config["data"]["processed_dir"]
    dataset_csv = config["data"]["dataset_csv"]
    test_split_size = config["data"].get("test_split_size", 0.2)
    random_seed = config["data"].get("random_seed", 42)
    img_size = config["model"]["img_size"]
    model_path = config["model"].get(
        "face_detector_model_path", "models/blaze_face_short_range.task"
    )

    proc_pos_dir = os.path.join(processed_dir, "positive")
    proc_neg_dir = os.path.join(processed_dir, "negative")

    print("Processing positive class (Miro)...")
    pos_records = process_images(
        raw_positive_dir,
        proc_pos_dir,
        label=1,
        img_size=img_size,
        model_path=model_path,
        skip_blurry=skip_blurry,
        blur_threshold=blur_threshold,
    )

    print("Processing negative class (Random)...")
    neg_records = process_images(
        raw_negative_dir,
        proc_neg_dir,
        label=0,
        img_size=img_size,
        model_path=model_path,
        skip_blurry=skip_blurry,
        blur_threshold=blur_threshold,
    )

    all_records = pos_records + neg_records

    if not all_records:
        print("No faces processed. Please check raw data.")
        return

    df = pd.DataFrame(all_records)

    # Stratified split to maintain positive/negative ratios in both sets
    train_df, test_df = train_test_split(
        df, test_size=test_split_size, stratify=df["label"], random_state=random_seed
    )

    train_df["split"] = "train"
    test_df["split"] = "test"

    final_df = pd.concat([train_df, test_df]).sort_index()

    os.makedirs(os.path.dirname(dataset_csv), exist_ok=True)
    final_df.to_csv(dataset_csv, index=False)

    print(f"Dataset successfully built with {len(final_df)} records.")
    print(f"Training samples: {len(train_df)}")
    print(f"Testing samples: {len(test_df)}")
    print(f"CSV saved to {dataset_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean, crop, and normalize raw images using MediaPipe."
    )
    parser.add_argument(
        "--no_skip_blurry",
        action="store_false",
        dest="skip_blurry",
        help="Do not skip blurry faces",
    )
    parser.add_argument(
        "--blur_threshold",
        type=float,
        default=100.0,
        help="Variance of Laplacian threshold for blur detection",
    )
    args = parser.parse_args()
    build_dataset(args.skip_blurry, args.blur_threshold)
