import os
import cv2
import numpy as np
import tensorflow as tf

def generate_activation_image(model_path, output_dir, iterations_per_octave=150, learning_rate=1.0, octaves=3, octave_scale=1.4):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    
    base_size = model.input_shape[1]
    
    # Start with a smaller resolution image
    current_size = int(base_size / (octave_scale ** (octaves - 1)))
    
    img = tf.random.uniform((1, current_size, current_size, 3), minval=0.45, maxval=0.55)
    
    print(f"Running gradient ascent with {octaves} octaves...")
    for octave in range(octaves):
        print(f"Processing Octave {octave + 1}/{octaves} (Size: {current_size}x{current_size})...")
        
        img = tf.Variable(img)
        
        for i in range(iterations_per_octave):
            shift_x = tf.random.uniform(shape=[], minval=-4, maxval=5, dtype=tf.int32)
            shift_y = tf.random.uniform(shape=[], minval=-4, maxval=5, dtype=tf.int32)
            img_shifted = tf.roll(tf.roll(img, shift_x, axis=1), shift_y, axis=2)

            with tf.GradientTape() as tape:
                tape.watch(img_shifted)
                
                # Resize temporarily to the model's expected input size for the prediction
                img_resized = tf.image.resize(img_shifted, (base_size, base_size))
                
                predictions = model(img_resized)
                confidence = predictions[0, 0] 

                tv_loss = tf.image.total_variation(img_shifted)
                loss = confidence - (0.008 * tv_loss[0])

            gradients = tape.gradient(loss, img_shifted)
            gradients = tf.roll(tf.roll(gradients, -shift_x, axis=1), -shift_y, axis=2)
            gradients /= (tf.math.reduce_std(gradients) + 1e-8)
            
            img.assign_add(gradients * learning_rate)
            img.assign(tf.clip_by_value(img, 0.0, 1.0))

            if (i + 1) % 50 == 0:
                numpy_img = img.numpy()[0]
                blurred_img = cv2.GaussianBlur(numpy_img, (3, 3), 0.5)
                blurred_img = blurred_img.astype(np.float32)
                img.assign(tf.expand_dims(blurred_img, axis=0))

        # If not the last octave, scale the image up for the next pass
        if octave < octaves - 1:
            current_size = int(current_size * octave_scale)
            img_numpy = img.numpy()
            img = tf.image.resize(img_numpy, (current_size, current_size))

    # Final resize to ensure it perfectly matches the model output expectations
    img = tf.image.resize(img, (base_size, base_size))

    os.makedirs(output_dir, exist_ok=True)
    
    final_img = img.numpy()[0]
    final_img = (final_img * 255).astype(np.uint8)
    final_img_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
    
    output_path = os.path.join(output_dir, "miro_activation_maximization.png")
    cv2.imwrite(output_path, final_img_bgr)
    print(f"Image saved successfully to {output_path}")

if __name__ == "__main__":
    generate_activation_image("../../vendor/models/miro_detector.keras", "../../data/processed")