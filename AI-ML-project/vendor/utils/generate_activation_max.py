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
            # Random jitter to improve feature localization
            shift_x = tf.random.uniform(shape=[], minval=-8, maxval=9, dtype=tf.int32)
            shift_y = tf.random.uniform(shape=[], minval=-8, maxval=9, dtype=tf.int32)
            img_shifted = tf.roll(tf.roll(img, shift_x, axis=1), shift_y, axis=2)

            with tf.GradientTape() as tape:
                tape.watch(img_shifted)
                img_resized = tf.image.resize(img_shifted, (base_size, base_size))
                # training=False is critical for models with BatchNormalization
                outputs = target_model(img_resized, training=False)
                
                if loss_mode == "output":
                    # Target the last available neuron (works for binary or multi-class)
                    score = tf.reduce_mean(outputs)
                    # Total Variation regularization to reduce high-frequency noise
                    tv_loss = tf.reduce_sum(tf.image.total_variation(img_shifted))
                    loss = score - (0.01 * tv_loss)
                else:
                    # Filter visualization: Maximize mean activation of the specific filter
                    filter_activation = tf.reduce_mean(outputs[0, :, :, filter_idx])
                    tv_loss = tf.reduce_sum(tf.image.total_variation(img_shifted))
                    loss = filter_activation - (0.005 * tv_loss)

            gradients = tape.gradient(loss, img_shifted)
            
            # Improved Gradient Normalization: L2 norm prevents "exploding" or "vanishing" steps
            grad_norm = tf.math.sqrt(tf.reduce_mean(tf.square(gradients))) + 1e-8
            gradients /= grad_norm
            
            # Undo jitter
            gradients = tf.roll(tf.roll(gradients, -shift_x, axis=1), -shift_y, axis=2)
            
            img.assign_add(gradients * learning_rate)
            img.assign(tf.clip_by_value(img, 0.0, 1.0))

            # Adaptive smoothing: frequent light blurs prevent the "noisy grain" look
            if (i + 1) % 4 == 0:
                numpy_img = img.numpy()[0]
                blurred_img = cv2.GaussianBlur(numpy_img, (0, 0), 0.25).astype(np.float32)
                img.assign(tf.expand_dims(blurred_img, axis=0))

        if octave < octaves - 1:
            # Upscale for the next octave to build complex patterns from simple ones
            new_size = int(img.shape[1] * octave_scale)
            img = tf.image.resize(img.numpy(), (new_size, new_size))
            img = tf.Variable(img)
            
    return tf.image.resize(img, (base_size, base_size))

def find_target_layers(model):
    """Dynamically finds the last conv layer and the final output layer."""
    conv_layers = [l for l in model.layers if isinstance(l, tf.keras.layers.Conv2D)]
    if not conv_layers:
        raise ValueError("No Conv2D layers found in the model.")
    
    # We use the very last layer for class maximization and last conv for filters
    return conv_layers[-1], model.layers[-1]

def generate_output_maximization(model, output_dir, base_size, iterations, learning_rate):
    print("Generating output activation maximization...")
    _, last_layer = find_target_layers(model)
    # We build a sub-model that outputs the final prediction
    activation_model = tf.keras.Model(inputs=model.inputs, outputs=last_layer.output)
    
    # Start with a slightly "warmer" noise to give the optimizer a better starting point
    initial_img = tf.random.uniform((1, int(base_size / (1.4**2)), int(base_size / (1.4**2)), 3), minval=0.4, maxval=0.6)
    
    img_final = run_gradient_ascent(activation_model, initial_img, base_size, iterations, learning_rate, octaves=3, octave_scale=1.4, loss_mode="output")
    
    final_img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "miro_activation_maximization.png"), cv2.cvtColor(final_img_np, cv2.COLOR_RGB2BGR))

def generate_filter_grid(model, output_dir, base_size, iterations, learning_rate, filters_to_visualize=4):
    print("Generating filter visualization grid...")
    last_conv_layer, _ = find_target_layers(model)
    feature_extractor = tf.keras.Model(inputs=model.inputs, outputs=last_conv_layer.output)
    
    total_filters = last_conv_layer.output.shape[-1]
    filter_indices = np.linspace(0, total_filters - 1, filters_to_visualize, dtype=int)
    grid_images = []
    
    for filter_idx in filter_indices:
        initial_img = tf.random.uniform((1, int(base_size / (1.4**2)), int(base_size / (1.4**2)), 3), minval=0.1, maxval=0.9)
        img_final = run_gradient_ascent(feature_extractor, initial_img, base_size, iterations, learning_rate, octaves=3, octave_scale=1.4, loss_mode="filter", filter_idx=filter_idx)
        
        img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        cv2.putText(img_bgr, f"Filter {filter_idx}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        grid_images.append(img_bgr)

    # Calculate grid layout
    grid_cols = math.ceil(math.sqrt(filters_to_visualize))
    grid_rows = math.ceil(filters_to_visualize / grid_cols)
    
    while len(grid_images) < grid_cols * grid_rows:
        grid_images.append(np.zeros((base_size, base_size, 3), dtype=np.uint8))
    
    rows = [np.hstack(grid_images[r*grid_cols : (r+1)*grid_cols]) for r in range(grid_rows)]
    cv2.imwrite(os.path.join(output_dir, "miro_filter_grid.png"), np.vstack(rows))

def generate_activation_image(model_path, output_dir, iterations=150, learning_rate=0.05):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
    
    model = tf.keras.models.load_model(model_path)
    base_size = model.input_shape[1]
    os.makedirs(output_dir, exist_ok=True)
    
    # Note: Lower learning rate usually yields much clearer "deep" features
    generate_output_maximization(model, output_dir, base_size, iterations, learning_rate)
    generate_filter_grid(model, output_dir, base_size, iterations, learning_rate)
    print(f"Visualization results saved to {output_dir}")