import os
import cv2
import numpy as np
import tensorflow as tf
import math

def run_gradient_ascent(target_model, initial_img, base_size, iterations, learning_rate, octaves, octave_scale, loss_mode="output", filter_idx=None):
    img = initial_img
    
    for octave in range(octaves):
        img = tf.Variable(img)
        for i in range(iterations):
            # Stochastic jitter to prevent the model from focusing on specific pixel locations
            shift_x = tf.random.uniform(shape=[], minval=-8, maxval=9, dtype=tf.int32)
            shift_y = tf.random.uniform(shape=[], minval=-8, maxval=9, dtype=tf.int32)
            img_shifted = tf.roll(tf.roll(img, shift_x, axis=1), shift_y, axis=2)

            with tf.GradientTape() as tape:
                tape.watch(img_shifted)
                img_resized = tf.image.resize(img_shifted, (base_size, base_size))
                outputs = target_model(img_resized, training=False)
                
                if loss_mode == "output":
                    p = tf.clip_by_value(outputs[0, 0], 1e-7, 1.0 - 1e-7)
                    logit_confidence = tf.math.log(p / (1.0 - p))
                    tv_loss = tf.image.total_variation(img_shifted)
                    loss = logit_confidence - (0.01 * tv_loss[0]) # Adjusted weight
                else:
                    # Filter visualization: Maximize mean activation + penalize noise
                    filter_activation = tf.reduce_mean(outputs[0, :, :, filter_idx])
                    tv_loss = tf.image.total_variation(img_shifted)
                    loss = filter_activation - (0.005 * tv_loss[0])

            gradients = tape.gradient(loss, img_shifted)
            # Normalize gradients
            gradients /= (tf.math.reduce_std(gradients) + 1e-8)
            
            # Undo jitter
            gradients = tf.roll(tf.roll(gradients, -shift_x, axis=1), -shift_y, axis=2)
            
            img.assign_add(gradients * learning_rate)
            img.assign(tf.clip_by_value(img, 0.0, 1.0))

            # Apply gentle smoothing more frequently to suppress high-frequency noise
            if (i + 1) % 5 == 0:
                numpy_img = img.numpy()[0]
                # Very light blur
                blurred_img = cv2.GaussianBlur(numpy_img, (0, 0), 0.3).astype(np.float32)
                img.assign(tf.expand_dims(blurred_img, axis=0))

        if octave < octaves - 1:
            # Upscale for the next octave
            new_size = int(img.shape[1] * octave_scale)
            img = tf.image.resize(img.numpy(), (new_size, new_size))
            img = tf.Variable(img)
            
    return tf.image.resize(img, (base_size, base_size))

def generate_output_maximization(model, output_dir, base_size, iterations, learning_rate):
    print("Generating output activation maximization...")
    initial_img = tf.random.uniform((1, int(base_size / (1.4 ** 2)), int(base_size / (1.4 ** 2)), 3), minval=0.45, maxval=0.55)
    img_final = run_gradient_ascent(model, initial_img, base_size, iterations, learning_rate, octaves=3, octave_scale=1.4, loss_mode="output")
    final_img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "miro_activation_maximization.png"), cv2.cvtColor(final_img_np, cv2.COLOR_RGB2BGR))

def generate_filter_grid(model, output_dir, base_size, iterations, learning_rate, filters_to_visualize=4):
    print("Generating filter visualization grid...")
    conv_layers = [layer for layer in model.layers if isinstance(layer, tf.keras.layers.Conv2D)]
    target_layer = conv_layers[-1]
    feature_extractor = tf.keras.Model(inputs=model.inputs, outputs=target_layer.output)
    
    total_filters = target_layer.output.shape[-1]
    filter_indices = np.linspace(0, total_filters - 1, filters_to_visualize, dtype=int)
    grid_images = []
    
    for filter_idx in filter_indices:
        initial_img = tf.random.uniform((1, int(base_size / (1.4 ** 2)), int(base_size / (1.4 ** 2)), 3), minval=0.0, maxval=1.0)
        img_final = run_gradient_ascent(feature_extractor, initial_img, base_size, iterations, learning_rate, octaves=3, octave_scale=1.4, loss_mode="filter", filter_idx=filter_idx)
        img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        cv2.putText(img_bgr, f"Filter {filter_idx}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        grid_images.append(img_bgr)

    grid_cols = math.ceil(math.sqrt(filters_to_visualize))
    grid_rows = math.ceil(filters_to_visualize / grid_cols)
    while len(grid_images) < grid_cols * grid_rows:
        grid_images.append(np.zeros((base_size, base_size, 3), dtype=np.uint8))
    
    rows = [np.hstack(grid_images[r*grid_cols : (r+1)*grid_cols]) for r in range(grid_rows)]
    cv2.imwrite(os.path.join(output_dir, "miro_filter_grid.png"), np.vstack(rows))

def generate_activation_image(model_path, output_dir, iterations=150, learning_rate=1.0):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
    model = tf.keras.models.load_model(model_path)
    base_size = model.input_shape[1]
    os.makedirs(output_dir, exist_ok=True)
    generate_output_maximization(model, output_dir, base_size, iterations, learning_rate)
    generate_filter_grid(model, output_dir, base_size, iterations, learning_rate)
    print(f"Visualization results saved to {output_dir}")