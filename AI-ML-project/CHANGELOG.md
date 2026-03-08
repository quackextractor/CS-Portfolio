# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
