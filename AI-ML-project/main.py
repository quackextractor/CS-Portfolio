import os
import argparse
import sys
import importlib.util

# Suppress TensorFlow informational logs and oneDNN warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Import the core functions from your existing modules
from src.app import main as run_inference  # noqa: E402
from src.build_dataset import build_dataset  # noqa: E402
from src.pexels_scraper import download_pexels_images  # noqa: E402
from vendor.utils.video_extractor import extract_frames  # noqa: E402
from vendor.setup_models import download_models  # noqa: E402


def generate_docs():
    scripts = [
        ("gen_docs", os.path.join("vendor", "utils", "LaTeX-gen", "gen-docs.py")),
        ("gen_manual", os.path.join("vendor", "utils", "LaTeX-gen", "gen-manual.py")),
    ]

    for module_name, script_path in scripts:
        if not os.path.exists(script_path):
            print(f"Warning: Script not found at {script_path}")
            continue

        print(f"Executing {module_name}...")
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        module.build_pdf()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Miro Face Detector - Unified CLI Tool\n\n"
            "Typical first-time setup:\n"
            "  python main.py setup   # download required model files\n"
            "  python main.py build   # process raw images into dataset CSV\n"
            "  python main.py run     # launch live webcam inference"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # Command: setup
    subparsers.add_parser(
        "setup",
        help="Download required MediaPipe model files (run once after pip install)",
    )

    # Command: run
    parser_run = subparsers.add_parser(
        "run",
        help="Launch the live webcam face detection application, run on a video, or screenshare",
    )
    parser_run.add_argument(
        "--video", type=str, default=None, help="Path to a video file for inference"
    )
    parser_run.add_argument(
        "--screen", action="store_true", help="Capture and run inference on your primary screen"
    )

    # Command: build
    parser_build = subparsers.add_parser(
        "build",
        help="Clean, crop, and normalize raw images to build the dataset CSV",
    )
    parser_build.add_argument(
        "--no_skip_blurry",
        action="store_false",
        dest="skip_blurry",
        help="Do not skip blurry faces",
    )
    parser_build.add_argument(
        "--blur_threshold",
        type=float,
        default=10.0,
        help="Variance of Laplacian threshold for blur detection",
    )

    # Command: scrape
    parser_scrape = subparsers.add_parser(
        "scrape",
        help="Download portrait images from Pexels for the negative class",
    )
    parser_scrape.add_argument(
        "--query", type=str, default="portrait face", help="Search query for Pexels"
    )
    parser_scrape.add_argument(
        "--total", type=int, default=1200, help="Total number of images to download"
    )
    parser_scrape.add_argument(
        "--output_dir", type=str, default="data/raw/negative", help="Output directory"
    )

    # Command: extract
    parser_extract = subparsers.add_parser(
        "extract",
        help="Extract frames from personal videos for the positive class",
    )
    parser_extract.add_argument(
        "video_path", type=str, help="Path to the source video file"
    )
    parser_extract.add_argument(
        "--output_dir", type=str, default="data/raw/positive", help="Output directory"
    )
    parser_extract.add_argument(
        "--frame_rate", type=int, default=5, help="Extract 1 frame every N frames"
    )
    parser_extract.add_argument(
        "--batch", action="store_true", help="Process all videos in a given directory"
    )

    # Command: docs
    subparsers.add_parser(
        "docs",
        help="Generate the LaTeX project documentation PDF",
    )

    # Check if no arguments were passed, print help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.command == "setup":
        download_models()
    elif args.command == "run":
        screen_mode = getattr(args, "screen", False)
        run_inference(video_path=args.video, screen=screen_mode)
    elif args.command == "build":
        skip_blurry = getattr(args, "skip_blurry", True)
        blur_threshold = getattr(args, "blur_threshold", 10.0)
        build_dataset(skip_blurry, blur_threshold)
    elif args.command == "scrape":
        download_pexels_images(args.query, args.total, args.output_dir)
    elif args.command == "extract":
        batch_mode = getattr(args, "batch", False)
        extract_frames(args.video_path, args.output_dir, args.frame_rate, batch_mode)
    elif args.command == "docs":
        generate_docs()


if __name__ == "__main__":
    main()
