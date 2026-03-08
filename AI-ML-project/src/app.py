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
                    
                    # Depending on threshold, classify. Positive (1) is Miro.
                    if prediction >= 0.5:
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
