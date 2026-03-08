import cv2
import os
import argparse
from pathlib import Path


def extract_frames(video_path: str, output_dir: str, frame_rate: int = 1) -> None:
    """
    Extracts frames from a video file and saves them to a directory.

    Args:
        video_path (str): Path to the input video file or directory containing videos.
        output_dir (str): Directory where extracted frames will be saved.
        frame_rate (int): Extract 1 frame every `frame_rate` frames.
    """
    # Normalize and get absolute path
    abs_video_path = os.path.abspath(os.path.normpath(video_path))
    
    if not os.path.exists(abs_video_path):
        print(f"Error: Video file or directory not found at {abs_video_path}")
        return

    # If a directory is provided, look for common video files
    if os.path.isdir(abs_video_path):
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
        videos = [f for f in os.listdir(abs_video_path) if f.lower().endswith(video_extensions)]
        
        if not videos:
            print(f"Error: No video files found in directory {abs_video_path}")
            return
        
        print(f"Directory detected. Found {len(videos)} videos. Extracting from the first one: {videos[0]}")
        abs_video_path = os.path.join(abs_video_path, videos[0])

    os.makedirs(output_dir, exist_ok=True)
    video_name = Path(abs_video_path).stem

    cap = cv2.VideoCapture(abs_video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {abs_video_path}")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_rate == 0:
            frame_filename = os.path.join(
                output_dir, f"{video_name}_frame_{saved_count:04d}.jpg"
            )
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Extracted {saved_count} frames from {video_name} into {output_dir}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract frames from personal videos for the positive class."
    )
    parser.add_argument("video_path", type=str, help="Path to the source video file")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/raw/positive",
        help="Output directory for frames",
    )
    parser.add_argument(
        "--frame_rate", type=int, default=5, help="Extract 1 frame every N frames"
    )

    args = parser.parse_args()
    extract_frames(args.video_path, args.output_dir, args.frame_rate)
