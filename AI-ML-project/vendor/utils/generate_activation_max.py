import os
import cv2
import numpy as np
import tensorflow as tf

def generate_activation_image(model_path, output_dir, iterations=100, learning_rate=0.1):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    
    # Extract the expected image size from the model's input layer
    img_size = model.input_shape[1]
    
    # Initialize an image with random noise, centered around a neutral gray
    img = tf.random.normal((1, img_size, img_size, 3), mean=0.5, stddev=0.1)
    img = tf.Variable(img)

    print(f"Running gradient ascent for {iterations} iterations...")
    for i in range(iterations):
        with tf.GradientTape() as tape:
            tape.watch(img)
            # Pass the image through the model
            predictions = model(img)
            # The model outputs a single sigmoid probability for the 'Miro' class
            loss = predictions[0, 0] 

        # Calculate how each pixel affects the confidence score
        gradients = tape.gradient(loss, img)
        
        # Normalize the gradients for smooth updates
        gradients /= (tf.math.reduce_std(gradients) + 1e-8)
        
        # Add the gradients to the image to increase the confidence score
        img.assign_add(gradients * learning_rate)
        
        # Clip pixel values to ensure they remain in the valid [0, 1] range
        img.assign(tf.clip_by_value(img, 0.0, 1.0))

        if (i + 1) % 20 == 0:
            print(f"Iteration {i + 1}/{iterations}, Confidence: {loss.numpy():.4f}")

    os.makedirs(output_dir, exist_ok=True)
    
    # Convert the resulting tensor back into a standard image format
    final_img = img.numpy()[0]
    final_img = (final_img * 255).astype(np.uint8)
    
    # Convert from RGB to BGR for OpenCV to save correctly
    final_img_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
    
    output_path = os.path.join(output_dir, "miro_activation_maximization.png")
    cv2.imwrite(output_path, final_img_bgr)
    print(f"Image saved successfully to {output_path}")

if __name__ == "__main__":
    generate_activation_image("../../vendor/models/miro_detector.keras", "../../data/processed")