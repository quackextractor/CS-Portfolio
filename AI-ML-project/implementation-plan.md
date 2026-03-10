### Phase 1: Advanced Batch Extraction System (JSON-Driven)

This phase addresses your specific idea to give users granular control over data extraction from large video files.

*
**Target Files:** `main.py` , `vendor/utils/video_extractor.py`.


* **Implementation Steps:**
1. **Define the JSON Schema:** Create a standardized format for the configuration file. It must support a list of video objects, where each object contains a file path, a base frame rate, and an array of segments defined by start and end timestamps (e.g., in seconds or `HH:MM:SS`).
2.
**Update CLI Arguments:** Modify the `extract` subparser in `main.py` to accept a `--config` argument. This will bypass the standard `video_path` positional argument if provided.


3.
**Refactor Video Extractor Logic:** Update the `extract_frames` function in `vendor/utils/video_extractor.py`  to parse the JSON file.


4.
**Implement Segment Seeking:** Utilize `cv2.CAP_PROP_POS_MSEC` or `cv2.CAP_PROP_POS_FRAMES`  to skip directly to the start of each defined segment, rather than reading and discarding every frame from the beginning of the file.


5.
**Dynamic Frame Skipping:** Implement a modulo counter against the defined `frame_rate` parameter to save only the nth frame within the active segment.





### Phase 2: Architectural and Performance Optimizations

This phase transitions the prototype from a functional script to a stable, performant application.

*
**Target Files:** `src/app.py` , `src/build_dataset.py`.


* **Implementation Steps:**
1.
**MediaPipe Mode Transition:** In `src/app.py`, change the `FaceDetectorOptions` from `VisionRunningMode.IMAGE` to `VisionRunningMode.VIDEO` for pre-recorded files, or `VisionRunningMode.LIVE_STREAM` for webcam feeds.


2. **Timestamp Integration:** For `VIDEO` mode, modify the detection loop to pass the current frame timestamp to the `face_detector.detect_for_video()` method. For `LIVE_STREAM`, implement the required asynchronous result listener callback.
3. **Global Logging Implementation:** Import the built-in `logging` module. Replace all `print()` calls in the application (e.g., "Opening camera..." ) with `logging.info()`, `logging.warning()`, or `logging.error()`.


4.
**Log File Handler:** Configure the logger in `main.py` to output to the console and simultaneously write to a rotating log file stored in the `out/` directory.


5. **Path Sanitization:** Import `pathlib`. Wrap all string-based file paths loaded from `config.yaml`  in `Path` objects. Use `Path.resolve()` to ensure absolute paths and `Path.exists()` before attempting to open files with OpenCV or TensorFlow.





### Phase 3: Model Robustness and Data Quality

This phase focuses on improving the CNN's discriminatory power and preventing configuration errors.

*
**Target Files:** `src/pexels_scraper.py` , `config.yaml` , `src/app.py`.


* **Implementation Steps:**
1.
**Hard Negative Mining Strategy:** Modify `config.yaml` to support a list of queries under the `scrape` defaults rather than a single string. Include highly specific queries that match the positive subject's general demographic (e.g., specific hair color, facial hair, accessories).


2.
**Update Scraper Logic:** Adjust `download_pexels_images` in `src/pexels_scraper.py` to iterate through the list of queries, evenly distributing the `total_images` target across all queries.


3.
**Configuration Schema Validation:** Create a validation function immediately after `yaml.safe_load(f)` in `main.py`. This function must assert that critical keys (`model.output_path`, `model.img_size`, `data.dataset_csv`) exist and match expected data types before proceeding.





### Phase 4: Documentation and Testing Evolution

This phase ensures the software remains maintainable and verifiable.

*
**Target Files:** `tests/test_main.py` (New), `vendor/utils/LaTeX-gen/gen-docs.py`.


* **Implementation Steps:**
1. **Automated Architecture Diagrams:** Integrate a library like `graphviz` into the documentation generator scripts. Programmatically read the `.keras` model layers  and generate a block diagram image representing the Convolutional and Dense layers. Insert this dynamically into the LaTeX stream






.
2.  **CLI Integration Testing:** Create `tests/test_main.py`. Use the `unittest.mock.patch` decorator to mock `sys.argv` with various command combinations (e.g., `["main.py", "build", "--no_skip_blurry"]`).
3.  **Assertion Logic:** Assert that the argparse logic correctly parses the mocked arguments and calls the underlying functions (like `build_dataset`) with the exact expected boolean or float values.
