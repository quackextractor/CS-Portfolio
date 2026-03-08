# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
