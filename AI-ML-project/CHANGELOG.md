# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.19.0] - 2026-03-11
### Added
- Pre-built multi-output gradient model in `src/app.py` for faster Grad-CAM inference.
- Total Variation (TV) penalty and spatial jitter to activation maximization in `vendor/utils/generate_activation_max.py`.
- Dataset caching and mixed precision support in `notebooks/model_training.ipynb` for accelerated training.

### Changed
- Migrated to `blaze_face_full_range.task` for improved face detection on high-resolution screens.
- Implemented dynamic frame downscaling and coordinate re-mapping in the inference loop to handle 4K/high-res inputs efficiently.
- Optimized Grad-CAM calculation with `@tf.function` and implemented 1:5 frame skipping/caching mechanism for higher FPS.
- Enhanced Grad-CAM visibility with peak min-max normalization and non-linear power transformation (gamma 0.6).
- Refactored activation maximization gradient ascent into specialized `@tf.function` steps for XLA-ready execution.
- Periodic Gaussian blurring added to visualization cycles in `generate_activation_max.py` to destroy persistent high-frequency static.

### Fixed
- Resolved "The layer sequential has never been called" error in `src/app.py` by ensuring the model is built before creating the Grad-CAM sub-model.

## [1.18.0] - 2026-03-11
### Changed
- Renamed project focus from "Miro" to "Target" across configuration, source code, notebooks, and documentation.
- Renamed model files: `miro_detector.keras` -> `target_detector.keras`, `miro_detector-old.keras` -> `target_detector-old.keras`.
- Renamed visualization assets: `miro_activation_maximization.png` -> `target_activation_maximization.png`, `miro_filter_grid.png` -> `target_filter_grid.png`.

## [1.17.0] - 2026-03-10
### Added
- New `status` command to display dataset statistics, including frame counts, storage size in MB, and percentage differences between raw and processed data.
- Automated grouping of positive frames by their video source video with individual subtotals.
- Unit tests for the status calculation logic and filename parsing.

## [1.16.0] - 2026-03-10
### Added
- Integrated `tqdm` progress bars into `build`, `extract`, and `scrape` commands for real-time processing feedback.
- Aligned CLI aesthetic with existing `visualize` command.

## [1.15.2] - 2026-03-10
### Changed
- Updated `gen-docs.py` to use existing professional Activation Maximization and Filter Grid visualizations instead of generating placeholders.
- Updated the LaTeX documentation template with correct relative path references to the provided assets.

## [1.15.1] - 2026-03-10
### Fixed
- Fixed `python main.py docs` crashing with `'RandomFlip' object has no attribute 'output_shape'`.
  `visualkeras` cannot introspect layers of a Keras model loaded from disk because `output_shape`
  is not populated until the model is called. The doc generator now uses `tf.keras.utils.plot_model`
  directly, which works reliably for all model types. Removed the dead `visualkeras` path and
  `_build_visualkeras_compatible_model` helper, and cleaned up an unused `pathlib.Path` import.

## [1.15.0] - 2026-03-10
### Changed
- Removed the external Graphviz binary dependency for automated model architecture diagrams.
- Replaced `tf.keras.utils.plot_model` with `visualkeras` for generating hierarchical, layered visualizations of the model architecture.
- Updated `requirements.txt` to include `visualkeras` and `Pillow`.
- Updated `README.md` to remove manual Graphviz installation instructions.

## [1.14.2] - 2026-03-10
### Fixed
- Fixed corrupted UTF-8 characters in the `gen-docs.py` LaTeX template causing compilation failures.
- Improved error handling in the documentation pipeline to report detailed LaTeX log errors and handle `PermissionError` (when PDF is open).

### Changed
- Updated `README.md` with explicit `winget` installation instructions for Graphviz on Windows.

## [1.14.1] - 2026-03-10
### Added
- Added `pydot` and `graphviz` to `requirements.txt` to support automated model architecture diagrams.

### Changed
- Added `-interaction=nonstopmode` to `pdflatex` commands in `gen-docs.py` and `gen-manual.py` for more robust PDF generation.
- Updated `README.md` to clarify the system-level Graphviz requirement.

### Fixed
- Fixed an issue where `pdflatex` compilation would wait for interactive input if packages were missing.

## [1.14.0] - 2026-03-10
### Added
- Implemented Advanced Batch Extraction System (JSON-driven) in `vendor/utils/video_extractor.py`.
- Added support for segment-based seeking (`HH:MM:SS` or seconds) and dynamic frame skipping.
- Integrated automated CNN architecture diagrams into the documentation pipeline (`gen-docs.py`).
- Added CLI integration tests in `tests/test_main.py` covering all major commands.
- Implemented configuration schema validation in `main.py` for critical keys.

### Changed
- Transitioned MediaPipe FaceDetector to `VIDEO` and `LIVE_STREAM` modes in `src/app.py` for improved stability and performance.
- Implemented global logging with console and rotating file handlers (`out/app.log`).
- Refactored all path handling to use `pathlib` for robust cross-platform sanitization.
- Enhanced `src/pexels_scraper.py` to support multiple search queries and distribute download targets for hard negative mining.
- Updated `config.yaml` to support a list of search queries.

### Fixed
- Fixed `UnboundLocalError` in `main.py` related to early path resolution.
- Resolved a critical runtime crash caused by Byte Order Mark (BOM) encoding in `config.yaml`.
- Resolved various linting issues across the codebase to adhere to PEP 8 standards.

## [1.13.0] - 2026-03-10
### Added
- Refactored `vendor/utils/generate_activation_max.py` into a suite of reusable functions: `run_gradient_ascent`, `generate_output_maximization`, and `generate_filter_grid`.
- Added a `--filter <int>` CLI option to the `visualize` command to maximize a specific convolutional filter instead of the class output.
- Implemented automatic output directory creation for activation maximization results.
- Added a `hasattr` guard for dynamic documentation module loading to ensure stability if `pdflatex` is missing.

### Changed
- Improved gradient normalization and octave-based scaling in the activation maximization pipeline for crisper feature visualization.
- Updated default iterations to 150 and learning rate to 1.0 for the `visualize` command.

## [1.12.0] - 2026-03-09
### Added
- New `visualize` command that performs activation maximization to generate an image representing what features the model is looking for in a face (e.g., the 'Target' class).
- Integrated `vendor/utils/generate_activation_max.py` to handle gradient ascent on random noise images to maximize model activation.

## [1.11.3] - 2026-03-09
### Fixed
- Fixed `main.py` loading time by utilizing lazy imports, significantly improving startup time for simple commands like `main.py --help`.

## [1.11.2] - 2026-03-09
### Fixed
- Fixed a bug where the Grad-CAM heatmap would appear "totally dark" or cold. This was caused by hardcoding the target convolutional layer to `"conv2d_5"`, which would fail silently on models with a different structure. `src/app.py` now dynamically detects the last `Conv2D` layer.

## [1.11.1] - 2026-03-09
### Changed
- Modified the `[` and `]` keyboard shortcuts to control the heatmap's underlying pixel intensity (sensitivity multiplier) rather than its visual transparency (alpha).
- Renamed the `--heatmap_alpha` CLI parameter and config key to `--heatmap_sensitivity`, defaulting to `5.0`.

## [1.11.0] - 2026-03-09
### Added
- Implemented Grad-CAM heatmap sensitivity (alpha) adjustment using `[` and `]` keyboard shortcuts.
- Centralized all CLI argument defaults in `config.yaml` under the `defaults` section for easy user customization.
- Added a `--heatmap_alpha` parameter to the `run` command.

### Changed
- Increased the initial default heatmap alpha from `0.4` to `0.6` for better visibility.

## [1.10.0] - 2026-03-09
### Added
- Implemented horizontal camera/stream mirroring with the 'm' keyboard shortcut.
- Mirroring affects both the live display and the model inference, providing a consistent "selfie" view.

## [1.9.1] - 2026-03-09
### Fixed
- Added explicit activation instructions for Git Bash on Windows to `README.md` and `setup.bat`.
- Clarified that Git Bash requires the `source` command and forward slashes for virtual environment activation.

## [1.9.0] - 2026-03-08
### Added
- Integrated Grad-CAM (Gradient-weighted Class Activation Mapping) for model interpretability, allowing users to visualize which facial features influence the model's decision.
- Added a toggle for Grad-CAM heatmaps with the 'g' key in the inference application (`src/app.py`).
- Added a `--gradcam` CLI flag to `python main.py run` to enable heatmaps by default.
- Enhanced the project documentation (`gen-docs.py` and `gen-manual.py`) with a new section and sample images explaining Grad-CAM.
- Added new unit tests for Grad-CAM helper functions in `tests/test_app.py`.

## [1.8.0] - 2026-03-08
### Added
- Added blur detection functionality to the data pipeline (`src/build_dataset.py`) to automatically skip blurry faces during processing.
- Integrated variance of Laplacian method to evaluate face sharpness before saving the cropped images.
- Added `--blur_threshold` and `--no_skip_blurry` CLI arguments to `python main.py build`.

## [1.7.0] - 2026-03-08
### Added
- Added a `--screen` parameter to `python main.py run` to allow capturing the primary screen and running model inference on it.
- Integrated `mss` dependency to support rapid cross-platform screenshare captures.
- Added corresponding documentation updates in the README for the screenshare functionality.

## [1.6.6] - 2026-03-08
### Changed
- The `src/pexels_scraper.py` script now features persistent scraping functionality. It counts previously downloaded images inside the target directory and skips re-downloading them, only requesting new images until the global `--total` objective is reached without over-writing existing progress.

## [1.6.5] - 2026-03-08
### Added
- Added a `--batch` parameter to `python main.py extract` to allow batch processing of all video files present within a specified input directory.
- Updated `vendor/utils/video_extractor.py` to seamlessly handle multiple video inputs simultaneously.

## [1.6.4] - 2026-03-08
### Added
- Added a `--video` parameter to `python main.py run` to allow passing a local video file (`.mp4`) for model inference instead of using the live webcam stream.
- Added playback controls (Spacebar for pause/resume, 'a' and 'd' for skipping backward and forward 30 frames) to the video interface in `src/app.py`.
- Added a dynamic interactive progress trackbar for video playback and seeking.

## [1.6.3] - 2026-03-08
### Changed
- Updated `config.yaml`, `src/app.py`, and tests to enforce and use `.keras` model format instead of `.h5`.
- Added explicit file extension checking for `.keras` in the main application inference engine.

## [1.6.2] - 2026-03-08
### Added
- Added instructions on `config.yaml` positioning and content to the `create_notebook.py` generation output.
- Included `config.yaml` requirements in the generated `docs/user_manual.pdf` via `gen-manual.py`.

### Fixed
- Fixed Python 3.12+ compatibility in unit tests by migrating from the deprecated `imp` module to `importlib`.
- Fixed `ValueError: Invalid input shape` in generated `model_training.ipynb` by forcing explicit image resizing in `load_images_from_df` within `create_notebook.py`.
- Corrected relative path generation in `create_notebook.py` to use `__file__` to ensure notebooks are placed in `notebooks/` regardless of invocation context.
- Fixed a bug where Windows backslashes in dataset paths resulted in Colab failing to load any images (causing empty dataset `(0,)` shape). `create_notebook.py` now explicitly outputs a replace operation.

## [1.6.1] - 2026-03-08
### Fixed
- Resolved `TypeError` in `vendor/create_notebook.py` by fixing the `open()` call and adding the missing `os` import.
- Added `os.makedirs` check in `vendor/create_notebook.py` to ensure the `notebooks/` directory exists before writing.

## [1.6.0] - 2026-03-08
### Added
- New unit tests for the video extraction module in `tests/test_video_extractor.py`.
- Support for directory inputs in the `extract` command (automatically detects video files within a directory).

### Changed
- Improved error messaging in `extract_frames` to show absolute paths for easier debugging.
- Enhanced path normalization to better handle Windows-style backslashes and relative paths.
- Modified `vendor/utils/video_extractor.py` to be more robust against shell-specific path issues.

## [1.5.3] - 2026-03-08
### Fixed
- Fixed LaTeX rendering issue in `gen-manual.py` where double dashes (`--`) were incorrectly displayed as a single dash in the generated PDF.

## [1.5.2] - 2026-03-08
### Changed
- Moved `video_extractor.py` from `src/` to `vendor/utils/` to better organize utility scripts.
- Updated `main.py` and `docs/documentation.md` to reflect the new location.

## [1.5.1] - 2026-03-08
### Changed
- Moved `setup_models.py` and `create_notebook.py` from the project root to the `vendor/` directory to maintain a cleaner root structure.
- Updated `main.py` and `src/build_dataset.py` to reference the new location of `setup_models.py`.
- Updated `README.md` project structure and setup instructions.

## [1.5.0] - 2026-03-08
### Added
- `setup` subcommand in `main.py` (`python main.py setup`) that calls
  `setup_models.download_models()` to download required MediaPipe model files.
- `setup.bat`: Windows batch script that creates a virtual environment,
  installs `requirements.txt`, and runs `python main.py setup` in one step.
- First-time setup instructions added to the `argparse` description shown
  by `python main.py --help`.

### Changed
- Updated `README.md` to reference `python main.py setup` instead of the
  standalone `python setup_models.py` command.

## [1.4.0] - 2026-03-08

### Changed
- Migrated face detection in `src/build_dataset.py` and `src/app.py` from the
  removed `mediapipe.solutions` API to the current `mediapipe.tasks.vision.FaceDetector`
  Tasks API (required by mediapipe >= 0.10.x).
- `process_images` now accepts a `model_path` parameter; `build_dataset` reads
  the path from `config.yaml` (`model.face_detector_model_path`).
- Bounding box coordinates are now read as absolute pixels
  (`origin_x`, `origin_y`, `width`, `height`) instead of relative floats.

### Added
- `setup_models.py`: one-time helper script to download the required
  BlazeFace short-range `.task` model file into `models/`.
- `model.face_detector_model_path` key added to `config.yaml`.
- `test_build_face_detector_missing_model_raises` unit test covering the new
  `FileNotFoundError` code path.

### Fixed
- `app.py` now calls `face_detector.close()` on all exit paths (camera error,
  normal quit) to avoid resource leaks.

## [1.3.0] - 2026-03-08

### Fixed
- Replaced `import mediapipe as mp` / `mp.solutions.face_detection` with a lazy import
  in `src/build_dataset.py` and `src/app.py`. `mediapipe >= 0.10.x` removed `solutions`
  from the top-level module; the new `_get_mp_face_detection()` helper resolves the
  module on first use, raising a clear `ImportError` if mediapipe is missing and a
  descriptive `RuntimeError` if `FaceDetection` fails to initialise.

### Added
- Two new unit tests: `test_process_images_multiple_faces_discarded` and
  `test_face_detection_init_failure_raises_runtime_error`.

### Changed
- All test mocks updated to target `src.build_dataset._get_mp_face_detection` so
  the test suite runs without mediapipe installed.

## [1.2.0] - 2026-03-08
### Added
- Implemented a unified Command Line Interface (CLI) in `main.py` using `argparse` to centralize execution of all project phases (scrape, extract, build, run, docs).

### Changed
- Updated `README.md` deployment and execution instructions to use the new `main.py` entry point instead of running individual scripts.

## [1.1.0] - 2026-03-08
### Added
- Added rigorous test coverage for `app.py` and improved `build_dataset.py` mock tests.
- Centralized new configuration parameters in `config.yaml` (`test_split_size`, `random_seed`, and `threshold`).
- Added a `.flake8` configuration file and resolved linter warnings across authored scripts.

### Changed
- Refactored `src/build_dataset.py` and `src/app.py` to use dynamic parameters sourced from `config.yaml` instead of hardcoded values.
- Unified README installation steps to correctly point to `requirements.txt`.
- Enhanced Google Colab notebook (`model_training.ipynb`) compatibility by implementing dynamic OS path resolution and fallback paths.

### Fixed
- Fixed critical missing dependencies (`scikit-learn`, `matplotlib`) in `requirements.txt` to enable out-of-the-box build reproducibility.

## [1.0.0] - 2026-03-08
### Added
- Created data collection scripts: `src/video_extractor.py` and `src/pexels_scraper.py`.
- Implemented MediaPipe-based face extraction and preprocessing in `src/build_dataset.py`.
- Developed CNN model training pipeline in `notebooks/model_training.ipynb`.
- Created real-time webcam inference application in `src/app.py`.
- Added unit tests for data pipeline in `tests/test_data_pipeline.py`.
- Configured GitHub Actions CI pipeline for automated testing and linting.
- Established rigorous code separation between `src/` (authored) and `vendor/` (foreign).
