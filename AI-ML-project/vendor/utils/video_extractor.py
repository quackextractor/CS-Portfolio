import cv2
import os
import argparse
import json
from tqdm import tqdm
from pathlib import Path
from typing import Optional, List, Dict, Union


def timestamp_to_seconds(timestamp: Union[str, int, float]) -> float:
    """Converts HH:MM:SS or seconds to float seconds."""
    if isinstance(timestamp, (int, float)):
        return float(timestamp)

    parts = timestamp.split(':')
    if len(parts) == 3:
        h, m, s = map(float, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = map(float, parts)
        return m * 60 + s
    return float(timestamp)


def extract_frames(
    video_path: Optional[str] = None,
    output_dir: str = "data/raw/positive",
    frame_rate: int = 1,
    batch: bool = False,
    config_path: Optional[str] = None,
    negative: bool = False
) -> None:
    """
    Extracts frames from video files based on CLI path or a JSON configuration.
    """
    jobs = []

    if config_path:
        config_path = os.path.abspath(config_path)
        if not os.path.exists(config_path):
            print(f"Error: Config file not found at {config_path}")
            return

        with open(config_path, 'r') as f:
            config_data = json.load(f)

        for entry in config_data:
            # Respect "is_positive" if present, otherwise use "negative"
            is_positive = entry.get("is_positive")
            if is_positive is not None:
                entry_negative = not is_positive
            else:
                entry_negative = entry.get("negative", negative)

            jobs.append({
                "video_path": entry.get("video_path"),
                "frame_rate": entry.get("frame_rate", frame_rate),
                "segments": entry.get("segments", []),
                "negative": entry_negative
            })
    elif video_path:
        abs_video_path = os.path.abspath(os.path.normpath(video_path))
        if not os.path.exists(abs_video_path):
            print(f"Error: Video file or directory not found at {abs_video_path}")
            return

        if os.path.isdir(abs_video_path):
            video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
            videos = [f for f in os.listdir(abs_video_path) if f.lower().endswith(video_extensions)]
            if not videos:
                print(f"Error: No video files found in directory {abs_video_path}")
                return

            paths = [os.path.join(abs_video_path, v) for v in videos]
            if not batch:
                patterns = [paths[0]]
            else:
                patterns = paths

            for p in patterns:
                jobs.append({"video_path": p, "frame_rate": frame_rate, "segments": [], "negative": negative})
        else:
            jobs.append({"video_path": abs_video_path, "frame_rate": frame_rate, "segments": [], "negative": negative})
    else:
        print("Error: Either video_path or config_path must be provided.")
        return

    for job in jobs:
        v_path = job["video_path"]
        v_rate = job["frame_rate"]
        segments = job["segments"]
        is_neg = job["negative"]
        video_name = Path(v_path).stem

        # Dynamic output directory within the specified output_dir
        # If the user explicitly passed output_dir, we respect it.
        # However, the requirement says frames should be in output_dir/video_name/
        current_output_dir = os.path.join(output_dir, video_name)
        
        # If we are using the 'main.py' defaults, output_dir will be 'data/raw/positive' or 'data/raw/negative'
        # But if the 'negative' flag is set, we want to ensure it goes to the negative dir.
        if is_neg and "positive" in output_dir:
            # Heuristic: if output_dir looks like positive but we want negative, swap it.
            # This is to handle the CLI --output_dir interacting with --negative.
            output_dir = output_dir.replace("positive", "negative")
            current_output_dir = os.path.join(output_dir, video_name)

        os.makedirs(current_output_dir, exist_ok=True)

        cap = cv2.VideoCapture(v_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {v_path}")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if not segments:
            # Traditional extraction: whole video
            segments = [{"start": 0, "end": total_frames / fps}]

        saved_count = 0
        for seg in segments:
            start_sec = timestamp_to_seconds(seg["start"])
            end_sec = timestamp_to_seconds(seg["end"])

            # Seek to start
            cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)

            # Estimate steps for the segment
            duration = end_sec - start_sec
            seg_frames_estimate = int(duration * fps)
            pbar = tqdm(total=seg_frames_estimate, desc=f"  Extracting {video_name}", leave=False)

            current_frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                if pos_msec > end_sec * 1000:
                    break

                if current_frame_idx % v_rate == 0:
                    frame_filename = os.path.join(
                        current_output_dir, f"{video_name}_frame_{saved_count:04d}.jpg"
                    )
                    cv2.imwrite(frame_filename, frame)
                    saved_count += 1

                current_frame_idx += 1
                pbar.update(1)
            pbar.close()

        cap.release()
        print(f"Extracted {saved_count} frames from {video_name} into {current_output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract frames from personal videos for the positive class."
    )
    parser.add_argument("video_path", type=str, nargs="?", help="Path to the source video file")
    parser.add_argument(
        "--config", type=str, help="Path to JSON batch config"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/raw/positive",
        help="Output directory for frames",
    )
    parser.add_argument(
        "--frame_rate", type=int, default=5, help="Extract 1 frame every N frames"
    )
    parser.add_argument(
        "--batch", action="store_true", help="Process all videos in a given directory"
    )
    parser.add_argument(
        "--negative", action="store_true", help="Route extracted frames to negative class"
    )

    args = parser.parse_args()
    extract_frames(
        video_path=args.video_path,
        output_dir=args.output_dir,
        frame_rate=args.frame_rate,
        batch=args.batch,
        config_path=args.config,
        negative=args.negative
    )
