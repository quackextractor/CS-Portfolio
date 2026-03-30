import os
import cv2
import yaml
import logging
import base64
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify

def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_grad_model(model, last_conv_layer_name=None):
    if len(model.layers) >= 2 and isinstance(model.layers[6], tf.keras.Model):
        model = model.layers[6] 

    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if "Conv2D" in layer.__class__.__name__:
                last_conv_layer_name = layer.name
                break

    if last_conv_layer_name is None:
        return None, None

    try:
        input_shape = model.input_shape[1:]
    except AttributeError:
        input_shape = (128, 128, 3)

    feature_input = tf.keras.Input(shape=input_shape)
    x = feature_input
    
    last_conv_layer = None
    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.InputLayer):
            continue
        x = layer(x)
        if layer.name == last_conv_layer_name:
            last_conv_layer = layer
            break

    if last_conv_layer is None:
        return None, None
        
    feature_extractor = tf.keras.Model(inputs=feature_input, outputs=x)

    classifier_input = tf.keras.Input(shape=x.shape[1:])
    y = classifier_input
    
    layer_idx = model.layers.index(last_conv_layer)
    for layer in model.layers[layer_idx + 1:]:
        y = layer(y)
        
    classifier = tf.keras.Model(inputs=classifier_input, outputs=y)
    return feature_extractor, classifier

@tf.function(reduce_retracing=True)
def _compute_heatmap_graph(img_tensor, feature_extractor, classifier):
    with tf.GradientTape() as tape:
        last_conv_layer_output = feature_extractor(img_tensor, training=False)
        tape.watch(last_conv_layer_output)
        preds = classifier(last_conv_layer_output, training=False)
        class_channel = preds[:, 0] 

    grads = tape.gradient(class_channel, last_conv_layer_output)
    if grads is None:
        return tf.zeros(last_conv_layer_output.shape[1:3])
        
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0.0)

    heatmap_max = tf.reduce_max(heatmap)
    if heatmap_max > 0:
        heatmap = heatmap / heatmap_max
    return heatmap

def make_gradcam_heatmap(img_tensor, grad_model):
    if grad_model[0] is None:
        return np.zeros((img_tensor.shape[1], img_tensor.shape[2]))
    heatmap = _compute_heatmap_graph(img_tensor, grad_model[0], grad_model[1])
    return heatmap.numpy()

def run_server():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app = Flask(__name__)
    config = load_config()
    model_path = config["model"]["output_path"]
    img_size = config["model"]["img_size"]

    if not os.path.exists(model_path):
        logging.error(f"Error: Model file not found at {model_path}.")
        return

    logging.info(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
    grad_model = get_grad_model(model)

    @app.route("/predict", methods=["POST"])
    def predict():
        data = request.json
        if not data or "faces" not in data:
            return jsonify({"error": "No faces provided"}), 400
        
        needs_gradcam = data.get("gradcam", False)
        batch_faces = []
        
        for b64_face in data["faces"]:
            img_bytes = base64.b64decode(b64_face)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            resized_face = cv2.resize(img, (img_size, img_size))
            rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
            normalized_face = rgb_face / 255.0
            batch_faces.append(normalized_face)

        batch_tensor = np.array(batch_faces, dtype=np.float32)
        predictions = model(batch_tensor, training=False)
        
        results = []
        for idx, pred_tensor in enumerate(predictions):
            pred_val = float(pred_tensor[0].numpy())
            result = {"prediction": pred_val}

            if needs_gradcam:
                input_face = np.expand_dims(batch_faces[idx], axis=0)
                input_tensor = tf.convert_to_tensor(input_face, dtype=tf.float32)
                heatmap_np = make_gradcam_heatmap(input_tensor, grad_model)
                
                heatmap_uint8 = (heatmap_np * 255).astype(np.uint8)
                _, buffer = cv2.imencode('.png', heatmap_uint8)
                encoded_heatmap = base64.b64encode(buffer).decode('utf-8')
                result["heatmap"] = encoded_heatmap
                
            results.append(result)

        return jsonify({"results": results})

    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 5000)
    logging.info(f"Starting inference server on {host}:{port}")
    app.run(host=host, port=port, threaded=False)