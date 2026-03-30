import os
import argparse
import sys
import importlib.util
import yaml
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Suppress TensorFlow informational logs and oneDNN warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


def setup_logging():
    """Sets up global logging with console and rotating file handlers."""
    log_dir = Path("out")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console Handler
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(c_handler)

    # File Handler (Rotating)
    f_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2)
    f_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(f_handler)


def generate_docs():
    scripts = [
        ("gen_docs", os.path.join("vendor", "utils", "LaTeX-gen", "gen-docs.py")),
        ("gen_manual", os.path.join("vendor", "utils", "LaTeX-gen", "gen-manual.py")),
    ]

    for module_name, script_path in scripts:
        if not os.path.exists(script_path):
            logging.warning(f"Script not found at {script_path}")
            continue

        logging.info(f"Executing {module_name}...")
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        if hasattr(module, "build_pdf"):
            module.build_pdf()


def main():
    setup_logging()
    config_path = Path("config.yaml")
    if not config_path.exists():
        logging.error(f"Config file not found at {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    validate_config(config)
    sanitize_paths(config)

    defaults = config.get("defaults", {})

    parser = argparse.ArgumentParser(
        description=(
            "Target Face Detector - Unified CLI Tool\n\n"
            "Deployment Commands:\n"
            "  python main.py serve             # start the inference server (home PC)\n"
            "  python main.py run --client      # launch lightweight webcam client (school PC)\n"
            "  python main.py run               # launch standard local inference"
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

    # Command: serve
    subparsers.add_parser(
        "serve",
        help="Start the Flask inference server to process images remotely",
    )

    # Command: run
    parser_run = subparsers.add_parser(
        "run",
        help="Launch the live webcam face detection application, run on a video, or screenshare",
    )
    parser_run.add_argument(
        "--client",
        action="store_true",
        help="Run in lightweight client mode (bypasses local TensorFlow requirements)",
    )
    parser_run.add_argument(
        "--video", type=str, default=None, help="Path to a video file for inference"
    )
    parser_run.add_argument(
        "--screen",
        action="store_true",
        help="Capture and run inference on your primary screen",
    )
    parser_run.add_argument(
        "--gradcam", action="store_true", help="Enable Grad-CAM heatmaps by default"
    )
    parser_run.add_argument(
        "--heatmap_sensitivity",
        type=float,
        default=defaults.get("run", {}).get("heatmap_sensitivity", 5.0),
        help="Initial sensitivity multiplier for Grad-CAM heatmap",
    )
    parser_run.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override the target face detection threshold from config.yaml",
    )
    parser_run.add_argument(
        "--mine", action="store_true", help="Enable live false positive mining."
    )
    parser_run.add_argument(
        "--minefr",
        type=int,
        default=None,
        help="Frame-rate (interval) for mining extractions.",
    )

    # Command: process
    parser_process = subparsers.add_parser(
        "process",
        help="Clean, crop, and normalize raw images from raw/ folders to processed/ folders",
    )
    parser_process.add_argument(
        "--class_target",
        type=str,
        choices=["positive", "negative", "both"],
        default="both",
        help="Restrict processing to a specific class",
    )
    parser_process.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Process only a specific subfolder within the target class directory",
    )
    parser_process.add_argument(
        "--build",
        action="store_true",
        help="Trigger dataset CSV generation after processing finishes",
    )
    parser_process.add_argument(
        "--no_skip_blurry",
        action="store_false",
        dest="skip_blurry",
        help="Do not skip blurry faces",
    )
    parser_process.add_argument(
        "--blur_threshold",
        type=float,
        default=defaults.get("build", {}).get("blur_threshold", 10.0),
        help="Variance of Laplacian threshold for blur detection",
    )

    # Command: build
    parser_build = subparsers.add_parser(
        "build",
        help="Generate the dataset CSV from processed images",
    )
    parser_build.add_argument(
        "--output_csv",
        type=str,
        default=config.get("data", {}).get("dataset_csv", "data/processed/dataset.csv"),
        help="Override standard dataset CSV output path",
    )
    parser_build.add_argument(
        "--no_balance",
        action="store_false",
        dest="balance_dataset",
        help="Disable automatic proportional dataset balancing",
    )
    parser_build.set_defaults(
        balance_dataset=defaults.get("build", {}).get("balance_dataset", True)
    )

    # Command: scrape
    parser_scrape = subparsers.add_parser(
        "scrape",
        help="Download portrait images from Pexels for the negative class",
    )
    parser_scrape.add_argument(
        "--query",
        type=str,
        default=defaults.get("scrape", {}).get("query", "portrait face"),
        help="Search query for Pexels",
    )
    parser_scrape.add_argument(
        "--total",
        type=int,
        default=defaults.get("scrape", {}).get("total", 1200),
        help="Total number of images to download",
    )
    parser_scrape.add_argument(
        "--output_dir",
        type=str,
        default=defaults.get("scrape", {}).get("output_dir", "data/raw/negative/scraped"),
        help="Output directory",
    )

    parser_extract = subparsers.add_parser(
        "extract",
        help="Extract frames from personal videos for the positive or negative class",
    )
    parser_extract.add_argument(
        "--negative",
        action="store_true",
        help="Route extracted frames to the negative class directory",
    )
    parser_extract.add_argument(
        "video_path",
        type=str,
        nargs="?",
        help="Path to the source video file (optional if --config is used)"
    )
    parser_extract.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a JSON batch extraction configuration file"
    )
    parser_extract.add_argument(
        "--output_dir",
        type=str,
        default=defaults.get("extract", {}).get("output_dir", "data/raw/positive"),
        help="Output directory",
    )
    parser_extract.add_argument(
        "--frame_rate",
        type=str,
        default=str(defaults.get("extract", {}).get("frame_rate", "auto")),
        help="Extract 1 frame every N frames, or 'auto'",
    )
    parser_extract.add_argument(
        "--batch", action="store_true", help="Process all videos in a given directory"
    )

    # Command: docs
    subparsers.add_parser(
        "docs",
        help="Generate the LaTeX project documentation PDF",
    )

    # Command: visualize
    parser_visualize = subparsers.add_parser(
        "visualize",
        help="Generate activation maximization and filter grid images",
    )
    parser_visualize.add_argument(
        "--model",
        type=str,
        default=config.get("model", {}).get(
            "output_path", "vendor/models/target_detector.keras"
        ),
        help="Path to the trained model file",
    )
    parser_visualize.add_argument(
        "--output_dir",
        type=str,
        default=defaults.get("visualize", {}).get("output_dir", "data/processed"),
        help="Directory to save the generated images",
    )
    parser_visualize.add_argument(
        "--iterations",
        type=int,
        default=defaults.get("visualize", {}).get("iterations", 150),
        help="Number of gradient ascent iterations per octave",
    )
    parser_visualize.add_argument(
        "--lr",
        type=float,
        default=defaults.get("visualize", {}).get("lr", 1.0),
        help="Learning rate for gradient ascent",
    )

    # Command: status
    subparsers.add_parser(
        "status",
        help="Show dataset statistics (counts and sizes)",
    )

    # Command: pack
    parser_pack = subparsers.add_parser(
        "pack",
        help="Copy dataset frames to a temp folder, zip them into an archive, and clean up",
    )
    parser_pack.add_argument(
        "--csv",
        type=str,
        default=config.get("data", {}).get("dataset_csv", "data/processed/dataset.csv"),
        help="Path to the dataset.csv file",
    )
    parser_pack.add_argument(
        "--output",
        type=str,
        default="data/processed.zip",
        help="Path and name for the output zip file",
    )

    # Check if no arguments were passed, print help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Use resolve() for directories if they exist
    if hasattr(args, "output_dir") and args.output_dir:
        args.output_dir = str(Path(args.output_dir).resolve())

    if args.command == "setup":
        from vendor.setup_models import download_models
        download_models()
    elif args.command == "serve":
        from src.server import run_server
        run_server()
    elif args.command == "run":
        if getattr(args, "client", False):
            from src.client import main as run_inference
            logging.info("Running in lightweight client mode (Remote Inference)")
        else:
            from src.app import main as run_inference
            logging.info("Running in standard mode (Local Inference)")

        screen_mode = getattr(args, "screen", False)
        gradcam_mode = getattr(args, "gradcam", False)
        heatmap_sensitivity = getattr(args, "heatmap_sensitivity", 5.0)
        threshold_val = getattr(args, "threshold", None)
        run_inference(
            video_path=args.video,
            screen=screen_mode,
            use_gradcam=gradcam_mode,
            heatmap_sensitivity=heatmap_sensitivity,
            threshold_override=threshold_val,
            mine_enabled=args.mine,
            mine_frame_rate=args.minefr,
        )
    elif args.command == "process":
        from src.build_dataset import run_processing
        skip_blurry = getattr(args, "skip_blurry", True)
        blur_threshold = getattr(args, "blur_threshold", 10.0)
        run_processing(
            class_target=args.class_target,
            folder=args.folder,
            trigger_build=args.build,
            skip_blurry=skip_blurry,
            blur_threshold=blur_threshold,
        )
    elif args.command == "build":
        from src.build_dataset import run_building
        run_building(
            output_csv=args.output_csv,
            balance_dataset=args.balance_dataset
        )
    elif args.command == "scrape":
        from src.pexels_scraper import download_pexels_images
        download_pexels_images(args.query, args.total, args.output_dir)
    elif args.command == "extract":
        from vendor.utils.video_extractor import extract_frames
        batch_mode = getattr(args, "batch", False)
        
        # Load the auto target interval from config
        auto_target_list = defaults.get("extract", {}).get("auto_frame_target", [200, 300])
        auto_target = tuple(auto_target_list)

        if args.config:
            extract_frames(
                config_path=args.config,
                output_dir=args.output_dir,
                frame_rate=args.frame_rate,
                batch=batch_mode,
                negative=args.negative,
                auto_target=auto_target
            )
        elif args.video_path:
            extract_frames(
                video_path=args.video_path,
                output_dir=args.output_dir,
                frame_rate=args.frame_rate,
                batch=batch_mode,
                negative=args.negative,
                auto_target=auto_target
            )
        else:
            print("Error: Either video_path or --config must be provided.")
            sys.exit(1)
    elif args.command == "docs":
        generate_docs()
    elif args.command == "visualize":
        from vendor.utils.generate_activation_max import generate_activation_image
        generate_activation_image(args.model, args.output_dir, args.iterations, args.lr)
    elif args.command == "status":
        from src.dataset_status import print_status
        print_status(config)
    elif args.command == "pack":
        from vendor.utils.pack_dataset import pack_dataset
        pack_dataset(args.csv, args.output)


def validate_config(config):
    """Basic validation for critical configuration keys."""
    required_keys = [
        ("model.output_path", str),
        ("model.img_size", int),
        ("data.dataset_csv", str)
    ]

    for key_path, expected_type in required_keys:
        keys = key_path.split('.')
        val = config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                logging.error(f"Missing critical config key: {key_path}")
                sys.exit(1)

        if not isinstance(val, expected_type):
            logging.error(f"Config key {key_path} must be of type {expected_type.__name__}")
            sys.exit(1)


def sanitize_paths(config):
    """Recursively wraps string paths in Path objects where appropriate."""
    path_keys = ["output_path", "dataset_csv", "output_dir", "video_path"]

    def _walk(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k in path_keys and isinstance(v, str):
                    d[k] = Path(v)
                else:
                    _walk(v)
        elif isinstance(d, list):
            for i in range(len(d)):
                _walk(d[i])

    _walk(config)


if __name__ == "__main__":
    main()