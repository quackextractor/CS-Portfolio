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
            # Stochastic jitter to improve pattern robustness
            shift_x = tf.random.uniform(shape=[], minval=-8, maxval=9, dtype=tf.int32)
            shift_y = tf.random.uniform(shape=[], minval=-8, maxval=9, dtype=tf.int32)
            img_shifted = tf.roll(tf.roll(img, shift_x, axis=1), shift_y, axis=2)

            with tf.GradientTape() as tape:
                tape.watch(img_shifted)
                img_resized = tf.image.resize(img_shifted, (base_size, base_size))
                
                # Use training=False to ensure BatchNormalization uses learned stats
                outputs = target_model(img_resized, training=False)
                
                if loss_mode == "output":
                    # Maximize the raw logit score (pre-sigmoid) to avoid vanishing gradients
                    loss = tf.reduce_mean(outputs)
                else:
                    # Filter visualization: Maximize specific filter activation
                    loss = tf.reduce_mean(outputs[0, :, :, filter_idx])
                
                # L2 decay to keep the image from getting "blown out"
                loss -= 1e-3 * tf.reduce_sum(tf.square(img_shifted))

            gradients = tape.gradient(loss, img_shifted)
            
            # Gradient Blurring: Smooths out high-frequency "goop"
            gradients_np = gradients.numpy()[0]
            sigma = max(0.5, 1.5 * (1 - i / iterations))
            gradients_blurred = cv2.GaussianBlur(gradients_np, (0, 0), sigma)
            gradients = tf.expand_dims(tf.convert_to_tensor(gradients_blurred, dtype=tf.float32), 0)

            # Normalize gradients using L2 norm for stability in deep VGG blocks
            grad_norm = tf.math.sqrt(tf.reduce_mean(tf.square(gradients))) + 1e-8
            gradients /= grad_norm
            
            # Undo jitter and update image
            gradients = tf.roll(tf.roll(gradients, -shift_x, axis=1), -shift_y, axis=2)
            img.assign_add(gradients * learning_rate)
            img.assign(tf.clip_by_value(img, 0.0, 1.0))

        if octave < octaves - 1:
            # Upscale for multi-scale feature synthesis
            new_size = int(img.shape[1] * octave_scale)
            img = tf.image.resize(img.numpy(), (new_size, new_size))
            img = tf.Variable(img)
            
    return tf.image.resize(img, (base_size, base_size))

def get_inference_submodel(model, target="output"):
    """
    Strips augmentation layers and returns a submodel targeting 
    either the last conv layer or the final logit.
    """
    # 1. Identify the first 'real' processing layer (Conv2D) to skip Augmentation
    first_conv_idx = next(i for i, l in enumerate(model.layers) if isinstance(l, tf.keras.layers.Conv2D))
    input_layer = tf.keras.layers.Input(shape=model.input_shape[1:])
    
    # 2. Build a new graph bypassing augmentation
    x = input_layer
    for i in range(first_conv_idx, len(model.layers)):
        layer = model.layers[i]
        # For the final output, we strip the 'sigmoid' to get raw logits
        if i == len(model.layers) - 1 and target == "output":
            # Rebuild last dense layer without activation
            x = tf.keras.layers.Dense(layer.units, activation=None, name="logit_output")(x)
            # Transfer weights
            x_model = tf.keras.Model(inputs=input_layer, outputs=x)
            x_model.layers[-1].set_weights(layer.get_weights())
            return x_model
        x = layer(x)
        if target == "conv" and isinstance(layer, tf.keras.layers.Conv2D):
            # We want the very last conv layer
            last_conv_output = x
            
    if target == "conv":
        return tf.keras.Model(inputs=input_layer, outputs=last_conv_output)
    return tf.keras.Model(inputs=input_layer, outputs=x)

def generate_output_maximization(model, output_dir, base_size, iterations, learning_rate):
    print("Generating class maximization (Logit-based)...")
    activation_model = get_inference_submodel(model, target="output")
    
    # Start with neutral gray noise
    initial_img = tf.random.uniform((1, int(base_size / 2), int(base_size / 2), 3), minval=0.48, maxval=0.52)
    
    img_final = run_gradient_ascent(activation_model, initial_img, base_size, iterations, learning_rate, octaves=3, octave_scale=1.4, loss_mode="output")
    
    final_img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "miro_activation_maximization.png"), cv2.cvtColor(final_img_np, cv2.COLOR_RGB2BGR))

def generate_filter_grid(model, output_dir, base_size, iterations, learning_rate, filters_to_visualize=4):
    print("Generating filter grid (Augmentation-stripped)...")
    feature_extractor = get_inference_submodel(model, target="conv")
    
    total_filters = feature_extractor.output.shape[-1]
    filter_indices = np.linspace(0, total_filters - 1, filters_to_visualize, dtype=int)
    grid_images = []
    
    for filter_idx in filter_indices:
        initial_img = tf.random.uniform((1, int(base_size / 2), int(base_size / 2), 3), minval=0.4, maxval=0.6)
        img_final = run_gradient_ascent(feature_extractor, initial_img, base_size, iterations, learning_rate, octaves=3, octave_scale=1.4, loss_mode="filter", filter_idx=filter_idx)
        
        img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        cv2.putText(img_bgr, f"Filter {filter_idx}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        grid_images.append(img_bgr)

    grid_cols = math.ceil(math.sqrt(filters_to_visualize))
    grid_rows = math.ceil(filters_to_visualize / grid_cols)
    rows = [np.hstack(grid_images[r*grid_cols : (r+1)*grid_cols]) for r in range(grid_rows)]
    cv2.imwrite(os.path.join(output_dir, "miro_filter_grid.png"), np.vstack(rows))

def generate_activation_image(model_path, output_dir, iterations=150, learning_rate=0.05):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
    
    # Load model and strip activation/augmentation for visualization
    model = tf.keras.models.load_model(model_path)
    base_size = model.input_shape[1]
    os.makedirs(output_dir, exist_ok=True)
    
    generate_output_maximization(model, output_dir, base_size, iterations, learning_rate)
    generate_filter_grid(model, output_dir, base_size, iterations, learning_rate)