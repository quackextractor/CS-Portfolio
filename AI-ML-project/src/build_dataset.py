import os
import cv2
import yaml
import glob
import pandas as pd
import numpy as np
import mediapipe as mp
import argparse
from pathlib import Path
from sklearn.model_selection import train_test_split


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def process_images(input_dir: str, output_dir: str, label: int, img_size: int, split_mapping: dict = None) -> list:
    """
    Processes images in a directory: detects faces, crops, resizes, and saves them.
    Returns a list of dictionaries with metadata for the CSV.
    """
    records = []
    
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    
    os.makedirs(output_dir, exist_ok=True)
    
    image_paths = glob.glob(os.path.join(input_dir, "*.[jp][pn]g")) + glob.glob(os.path.join(input_dir, "*.jpeg"))
    
    processed_count = 0
    discarded_count = 0
    
    for img_path in image_paths:
        img = cv2.imread(img_path)
        if img is None:
            discarded_count += 1
            print(f"Failed to read image: {img_path}")
            continue
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)
        
        # We strictly require exactly one face
        if not results.detections or len(results.detections) != 1:
            discarded_count += 1
            continue
            
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        
        ih, iw, _ = img.shape
        x = int(bboxC.xmin * iw)
        y = int(bboxC.ymin * ih)
        w = int(bboxC.width * iw)
        h = int(bboxC.height * ih)
        
        # Add a slight margin (optional but helps CNN)
        margin_x = int(w * 0.1)
        margin_y = int(h * 0.1)
        
        x_min = max(0, x - margin_x)
        y_min = max(0, y - margin_y)
        x_max = min(iw, x + w + margin_x)
        y_max = min(ih, y + h + margin_y)
        
        cropped_face = img[y_min:y_max, x_min:x_max]
        
        if cropped_face.size == 0:
            discarded_count += 1
            continue
            
        resized_face = cv2.resize(cropped_face, (img_size, img_size))
        
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, resized_face)
        
        # Create record
        # Note: dataset path should be relative to project root ideally
        rel_output_path = os.path.relpath(output_path, start=".")
        records.append({
            "filepath": rel_output_path,
            "label": label
        })
        processed_count += 1

    face_detection.close()
    print(f"Processed {processed_count} images for label {label}. Discarded {discarded_count}.")
    return records


def build_dataset() -> None:
    config = load_config()
    raw_positive_dir = config["data"]["raw_positive_dir"]
    raw_negative_dir = config["data"]["raw_negative_dir"]
    processed_dir = config["data"]["processed_dir"]
    dataset_csv = config["data"]["dataset_csv"]
    img_size = config["model"]["img_size"]
    
    proc_pos_dir = os.path.join(processed_dir, "positive")
    proc_neg_dir = os.path.join(processed_dir, "negative")
    
    print("Processing positive class (Miro)...")
    pos_records = process_images(raw_positive_dir, proc_pos_dir, label=1, img_size=img_size)
    
    print("Processing negative class (Random)...")
    neg_records = process_images(raw_negative_dir, proc_neg_dir, label=0, img_size=img_size)
    
    all_records = pos_records + neg_records
    
    if not all_records:
        print("No faces processed. Please check raw data.")
        return
        
    df = pd.DataFrame(all_records)
    
    # Stratified split to maintain positive/negative ratios in both sets
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    
    train_df['split'] = 'train'
    test_df['split'] = 'test'
    
    final_df = pd.concat([train_df, test_df]).sort_index()
    
    os.makedirs(os.path.dirname(dataset_csv), exist_ok=True)
    final_df.to_csv(dataset_csv, index=False)
    
    print(f"Dataset successfully built with {len(final_df)} records.")
    print(f"Training samples: {len(train_df)}")
    print(f"Testing samples: {len(test_df)}")
    print(f"CSV saved to {dataset_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean, crop, and normalize raw images using MediaPipe.")
    parser.parse_args()
    build_dataset()
