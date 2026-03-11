import os
import cv2
import numpy as np
import tensorflow as tf
import math
from tqdm import tqdm


@tf.function
def gradient_ascent_step(img, target_model, base_size, loss_mode, filter_idx, jitter=2):
    """
    Core gradient ascent step optimized with TensorFlow XLA.
    """
    # Spatial jitter to prevent noise patterns
    shift_x = tf.random.uniform(shape=[], minval=-jitter, maxval=jitter + 1, dtype=tf.int32)
    shift_y = tf.random.uniform(shape=[], minval=-jitter, maxval=jitter + 1, dtype=tf.int32)
    img_shifted = tf.roll(tf.roll(img, shift_x, axis=1), shift_y, axis=2)

    with tf.GradientTape() as tape:
        tape.watch(img_shifted)
        img_resized = tf.image.resize(img_shifted, (base_size, base_size))
        outputs = target_model(img_resized, training=False)

        if loss_mode == "output":
            loss = tf.reduce_mean(outputs)
        else:
            loss = tf.reduce_mean(outputs[0, :, :, filter_idx])

        # Total Variation penalty for clustered/smooth features
        loss -= 1e-3 * tf.reduce_sum(tf.image.total_variation(img_shifted))
        # Simple L2 decay
        loss -= 1e-4 * tf.reduce_sum(tf.square(img_shifted))

    gradients = tape.gradient(loss, img_shifted)
    # Normalize gradients
    gradients /= (tf.math.sqrt(tf.reduce_mean(tf.square(gradients))) + 1e-8)
    # Unshift gradients
    gradients = tf.roll(tf.roll(gradients, -shift_x, axis=1), -shift_y, axis=2)
    return gradients


def run_gradient_ascent(
    target_model, initial_img, base_size, iterations, learning_rate, octaves,
    octave_scale, loss_mode="output", filter_idx=None
):
    img = initial_img

    # Progress bar for Octaves
    octave_pbar = tqdm(range(octaves), desc="  Octaves", leave=False)
    for octave in octave_pbar:
        img = tf.Variable(img)

        # Progress bar for Iterations
        iter_pbar = tqdm(
            range(iterations), desc=f"    Scaling {img.shape[1]}x{img.shape[2]}", leave=False
        )
        for i in iter_pbar:
            gradients = gradient_ascent_step(img, target_model, base_size, loss_mode, filter_idx)
            img.assign_add(gradients * learning_rate)
            img.assign(tf.clip_by_value(img, 0.0, 1.0))

            # Periodic Gaussian blur to destroy persistent high-frequency static
            if i > 0 and i % 10 == 0:
                img_np = img.numpy()[0]
                img_blurred = cv2.GaussianBlur(img_np, (3, 3), 0.5)
                img.assign(tf.expand_dims(tf.convert_to_tensor(img_blurred, dtype=tf.float32), 0))

        if octave < octaves - 1:
            new_size = int(img.shape[1] * octave_scale)
            img = tf.image.resize(img.numpy(), (new_size, new_size))
            img = tf.Variable(img)

    return tf.image.resize(img, (base_size, base_size))


def get_inference_submodel(model, target="output"):
    """Bypasses augmentation layers and targets raw logits or conv filters."""
    # Find the index of the first Conv2D layer to skip RandomFlip/Rotation/Zoom
    first_conv_idx = next(
        i for i, l in enumerate(model.layers) if isinstance(l, tf.keras.layers.Conv2D)
    )
    input_layer = tf.keras.layers.Input(shape=model.input_shape[1:])

    x = input_layer
    for i in range(first_conv_idx, len(model.layers)):
        layer = model.layers[i]
        if i == len(model.layers) - 1 and target == "output":
            # Strip sigmoid to maximize raw logit values
            x = tf.keras.layers.Dense(layer.units, activation=None, name="logit_output")(x)
            new_model = tf.keras.Model(inputs=input_layer, outputs=x)
            new_model.layers[-1].set_weights(layer.get_weights())
            return new_model
        x = layer(x)
        if target == "conv" and isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_output = x

    return tf.keras.Model(inputs=input_layer, outputs=last_conv_output if target == "conv" else x)


def generate_output_maximization(model, output_dir, base_size, iterations, learning_rate):
    print("\n[1/2] Generating Class Maximization...")
    activation_model = get_inference_submodel(model, target="output")
    initial_img = tf.random.uniform(
        (1, int(base_size / 2), int(base_size / 2), 3), minval=0.48, maxval=0.52
    )
    img_final = run_gradient_ascent(
        activation_model, initial_img, base_size, iterations, learning_rate,
        octaves=3, octave_scale=1.4, loss_mode="output"
    )
    final_img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
    cv2.imwrite(
        os.path.join(output_dir, "target_activation_maximization.png"),
        cv2.cvtColor(final_img_np, cv2.COLOR_RGB2BGR)
    )


def generate_filter_grid(model, output_dir, base_size, iterations, learning_rate, filters_to_visualize=4):
    print(f"\n[2/2] Generating {filters_to_visualize} Conv Filters...")
    feature_extractor = get_inference_submodel(model, target="conv")
    total_filters = feature_extractor.output.shape[-1]
    filter_indices = np.linspace(0, total_filters - 1, filters_to_visualize, dtype=int)
    grid_images = []

    for idx, filter_idx in enumerate(filter_indices):
        print(f"  Visualizing Filter {filter_idx} ({idx+1}/{filters_to_visualize})")
        initial_img = tf.random.uniform(
            (1, int(base_size / 2), int(base_size / 2), 3), minval=0.4, maxval=0.6
        )
        img_final = run_gradient_ascent(
            feature_extractor, initial_img, base_size, iterations, learning_rate,
            octaves=3, octave_scale=1.4, loss_mode="filter", filter_idx=filter_idx
        )
        img_np = (img_final.numpy()[0] * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        cv2.putText(
            img_bgr, f"Filter {filter_idx}", (5, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
        )
        grid_images.append(img_bgr)

    grid_cols = math.ceil(math.sqrt(filters_to_visualize))
    grid_rows = math.ceil(filters_to_visualize / grid_cols)
    rows = [
        np.hstack(grid_images[r * grid_cols:(r + 1) * grid_cols])
        for r in range(grid_rows)
    ]
    cv2.imwrite(
        os.path.join(output_dir, "target_filter_grid.png"), np.vstack(rows)
    )


def generate_activation_image(model_path, output_dir, iterations=150, learning_rate=0.05):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
    model = tf.keras.models.load_model(model_path)
    base_size = model.input_shape[1]
    os.makedirs(output_dir, exist_ok=True)
    generate_output_maximization(model, output_dir, base_size, iterations, learning_rate)
    generate_filter_grid(model, output_dir, base_size, iterations, learning_rate)
