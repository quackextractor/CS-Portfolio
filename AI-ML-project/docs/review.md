# Miro Face Detector - Comprehensive Code Review and Assessment

## Executive Summary

**Project Overview:** The project is a custom machine learning computer vision application designed to detect a specific person in a live camera feed and distinguish them from others. It involves creating a proprietary dataset from scratch to train a binary classification Convolutional Neural Network (CNN).

**Key Achievement:** The project demonstrates a strong, automated data collection and preprocessing pipeline using the Pexels API and MediaPipe. The automated generation of LaTeX documentation using a Python script is also highly commendable and ensures documentation stays synchronized with the project.

**Overall Impression:** The codebase is well-structured, modular, and adheres to many standard software engineering practices, including CI/CD workflows and linting. However, there are critical dependency issues and hardcoded values that prevent the project from being fully reproducible without manual debugging.

---

## 1. Architectural & Design Review

### Strengths

* 
**Pipeline Modularity:** The architecture correctly divides the system into distinct phases: data collection, preprocessing, model training, and real-time inference. This separation of concerns allows for easier debugging and independent scaling.


* 
**Code Authorship Separation:** The strict division between the `src/` directory for authored code and the `vendor/` directory for foreign code explicitly satisfies the strict assignment criteria.


* 
**Quality Assurance:** The inclusion of GitHub Actions for automated testing with `pytest` and linting with `flake8` and `black` ensures continuous code quality and prevents regressions.



### Areas for Improvement

* 
**Dependency Management:** The project utilizes `scikit-learn` in the dataset building script and `matplotlib` for documentation generation , but these are entirely missing from the `requirements.txt` file.


* **Recommendation:** Update the `requirements.txt` file to include all missing packages to ensure the project can be built and executed on a fresh machine.

---

## 2. Compliance Checklist

| Requirement | Status | Implementation Details |
| --- | --- | --- |
| **Real Data Only** | Pass | The project uses a custom script to extract frames from personal videos and queries the Pexels API for real portrait photos.

 |
| **Minimum 1500 Records** | Pass | The dataset generation scripts collect 800 positive images and 1200 negative images, totaling 2000 records.

 |
| **Minimum 5 Attributes** | Pass | The project uses 128x128x3 RGB images, resulting in 49,152 distinct pixel attributes per record.

 |
| **No IDE Requirement** | Pass | The documentation explicitly provides command-line instructions for deployment and execution without an IDE.

 |
| **Code Separation** | Pass | Authored code is placed in `src/` while foreign code and external snippets are isolated in `vendor/`.

 |

---

## 3. Deep Code Review

### Data Pipeline & Preprocessing (`src/build_dataset.py`)

The data pipeline successfully implements MediaPipe for strict face extraction. The logic automatically discards images with zero or multiple faces, which is excellent for maintaining dataset purity.

* 
**Fix/Optimization:** The dataset splitting relies on `scikit-learn`, which must be added to the project dependencies. Additionally, the `random_state=42` and `test_size=0.2` parameters are hardcoded. Moving these to `config.yaml` would improve modularity.



### Live Application (`src/app.py`)

The live application effectively loads the trained `.h5` model and processes the webcam feed in real-time. Error handling is present for camera availability and model loading.

* 
**Fix/Optimization:** The classification threshold is hardcoded to `0.5`. Moving this threshold to the configuration file allows users to fine-tune the strictness of the facial recognition without modifying the source code.



### Model Training (`notebooks/model_training.ipynb`)

The CNN implementation uses a standard Convolutional and Max Pooling architecture followed by Dense layers. The inclusion of Dropout helps prevent overfitting.

* 
**Fix/Optimization:** The fallback configuration paths in the Colab notebook assume the repository structure remains perfectly static. Using dynamic path resolution relative to the notebook's execution directory would increase robustness.



---

## 4. Documentation & UX Quality

* 
**README/Docs:** The `README.md` provides clear steps for environment setup and installation. However, it instructs the user to install `matplotlib` and `pandas` via command line , while the deployment instructions at the end of the documentation advise using `requirements.txt`. These instructions should be unified.


* 
**Visuals:** The automated LaTeX generation script creates high-quality PDF documentation complete with training history graphs and dataset distribution charts.


* 
**Developer Experience:** The project utilizes a `config.yaml` file for centralizing paths and variables, which significantly improves the developer experience. The use of `.env` for the Pexels API key follows security best practices.



---

## 5. Critical Issues and Actionable Fixes

### Issue 1: Missing Critical Dependencies

**Location:** `requirements.txt` - Entire file


**Problem:** The `src/build_dataset.py` file imports `sklearn.model_selection` , and `utils/LaTeX-gen/gen-docs.py` imports `matplotlib`. Neither of these packages are defined in `requirements.txt`. Running `pip install -r requirements.txt` on a fresh machine will result in `ModuleNotFoundError` exceptions during dataset compilation and documentation generation.
**Fix:**

```text
opencv-python>=4.8.0
mediapipe>=0.10.9
numpy>=1.26.0
pandas>=2.1.0
requests>=2.31.0
tqdm>=4.66.0
pyyaml>=6.0.1
python-dotenv>=1.0.0
pytest>=7.4.0
flake8>=6.1.0
black>=23.9.1
tensorflow>=2.14.0
scikit-learn>=1.3.0
matplotlib>=3.7.0

```

### Issue 2: Hardcoded Prediction Threshold

**Location:** `src/app.py`


**Problem:** The prediction logic strictly checks `if prediction >= 0.5:`. If the model is slightly underconfident or overconfident in real-world lighting, the user cannot calibrate the sensitivity without altering the source code.
**Fix:**

```python
import os
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]
    camera_index = config["camera"]["index"]
    threshold = config["model"].get("threshold", 0.5)

    print(f"Loading model from {model_path}...")
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}. Please train the model first.")
        # If the model doesn't exist, we can't run inference.
        # But for development/testing UI, we could mock the model.
        # However, the user is required to have the trained model for final deployment.
        return
        
    try:
        model = tf.keras.models.load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

    print(f"Opening camera {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera opened successfully. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and find faces
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x = int(bboxC.xmin * iw)
                y = int(bboxC.ymin * ih)
                w = int(bboxC.width * iw)
                h = int(bboxC.height * ih)

                # Margin for cropping
                margin_x = int(w * 0.1)
                margin_y = int(h * 0.1)
                
                x_min = max(0, x - margin_x)
                y_min = max(0, y - margin_y)
                x_max = min(iw, x + w + margin_x)
                y_max = min(ih, y + h + margin_y)

                cropped_face = frame[y_min:y_max, x_min:x_max]

                if cropped_face.size > 0:
                    # Preprocess for model
                    resized_face = cv2.resize(cropped_face, (img_size, img_size))
                    rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
                    normalized_face = rgb_face / 255.0
                    input_face = np.expand_dims(normalized_face, axis=0)

                    # Predict
                    prediction = model.predict(input_face, verbose=0)[0][0]
                    
                    # Depending on configurable threshold, classify. Positive (1) is Miro.
                    if prediction >= threshold:
                        label = f"Miro ({prediction:.2f})"
                        color = (0, 255, 0) # Green
                    else:
                        label = f"Unknown ({prediction:.2f})"
                        color = (0, 0, 255) # Red
                        
                    # Draw bounding box
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
                    cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Display the resulting frame
        cv2.imshow('Miro Face Detector', frame)

        # Exit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

```

---

## 6. Recommended Quality of Life (QoL) Features

### Feature 1: Expanded Configuration Management

**Benefit:** Centralizing the dataset test split size, random seed, and inference classification threshold into the `config.yaml` file removes hardcoded values from scripts and makes the pipeline highly adaptable.

**Draft Implementation:**

```yaml
data:
  raw_positive_dir: "data/raw/positive"
  raw_negative_dir: "data/raw/negative"
  processed_dir: "data/processed"
  dataset_csv: "data/processed/dataset.csv"
  test_split_size: 0.2
  random_seed: 42
model:
  output_path: "models/miro_detector.h5"
  img_size: 128
  threshold: 0.65
camera:
  index: 0

```

---

## 7. Conclusion

**Overall Score: 85/100**

**Top Strengths:**

1. Exceptional automation via custom scripts for both data gathering and documentation generation.
2. Perfect compliance with the assignment constraints regarding dataset size, attributes, and foreign code separation.

**Top Priorities for Improvement:**

1. Immediate resolution of the missing `scikit-learn` and `matplotlib` packages in the `requirements.txt` file.
2. Removal of hardcoded variables to fully utilize the configuration file.

**Final Verdict:** The project represents an impressive, end-to-end machine learning solution. Once the dependency lists are synchronized, the software will be fully robust, reproducible, and ready for deployment on the target hardware.

Would you like me to update the `README.md` file to reflect these dependency corrections as well?