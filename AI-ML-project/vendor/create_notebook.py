import json
import os

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Miro Face Detector - CNN Model Training\n",
    "\n",
    "This notebook trains a Convolutional Neural Network (CNN) to classify images as either "
    "'Miro' (1) or 'Random' (0). The data should be preprocessed by `src/build_dataset.py` "
    "before running this notebook. It is designed to be executable in Google Colab as requested."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Configuration\n",
    "\n",
    "Ensure your `config.yaml` file is properly positioned before training. "
    "For example, if the drive mounted fine and the location of the dataset is at "
    "`/content/drive/MyDrive/processed`, place the config file there or at the project root.\n",
    "\n",
    "Example `config.yaml` content:\n",
    "```yaml\n",
    "model:\n",
    "  img_size: 128\n",
    "  output_path: /content/drive/MyDrive/processed/models/miro_detector.h5\n",
    "data:\n",
    "  dataset_csv: /content/drive/MyDrive/processed/dataset.csv\n",
    "```"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import cv2\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import tensorflow as tf\n",
    "from tensorflow.keras import layers, models\n",
    "import matplotlib.pyplot as plt\n",
    "yaml_path = '../config.yaml'\n",
    "if os.path.exists(yaml_path):\n",
    "    import yaml\n",
    "    with open(yaml_path, 'r') as f:\n",
    "        config = yaml.safe_load(f)\n",
    "    DATA_CSV = '../' + config['data']['dataset_csv']\n",
    "    IMG_SIZE = config['model']['img_size']\n",
    "    MODEL_OUTPUT = '../' + config['model']['output_path']\n",
    "    DATA_DIR = '../'\n",
    "else:\n",
    "    # Fallback for Colab execution where structure might differ\n",
    "    DATA_CSV = 'data/processed/dataset.csv'\n",
    "    IMG_SIZE = 128\n",
    "    MODEL_OUTPUT = 'models/miro_detector.h5'\n",
    "    DATA_DIR = '.'\n",
    "\n",
    "print(f\"TensorFlow Version: {tf.__version__}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Data Loading and Preparation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv(DATA_CSV)\n",
    "\n",
    "def load_images_from_df(dataframe):\n",
    "    images = []\n",
    "    labels = []\n",
    "    for idx, row in dataframe.iterrows():\n",
    "        img_path = os.path.join(DATA_DIR, row['filepath'])\n",
    "        img = cv2.imread(img_path)\n",
    "        if img is not None:\n",
    "            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)\n",
    "            images.append(img)\n",
    "            labels.append(row['label'])\n",
    "    return np.array(images) / 255.0, np.array(labels)\n",
    "\n",
    "train_df = df[df['split'] == 'train']\n",
    "test_df = df[df['split'] == 'test']\n",
    "\n",
    "print(\"Loading training data...\")\n",
    "X_train, y_train = load_images_from_df(train_df)\n",
    "print(\"Loading testing data...\")\n",
    "X_test, y_test = load_images_from_df(test_df)\n",
    "\n",
    "print(f\"Training Data Shape: {X_train.shape}\")\n",
    "print(f\"Testing Data Shape: {X_test.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Model Architecture\n",
    "\n",
    "Building a custom CNN following the assignment specification: "
    "Convolutional -> Max Pooling -> Flatten -> Dense."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "model = models.Sequential([\n",
    "    # Convolutional & Pooling Layer 1\n",
    "    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),\n",
    "    layers.MaxPooling2D((2, 2)),\n",
    "    \n",
    "    # Convolutional & Pooling Layer 2\n",
    "    layers.Conv2D(64, (3, 3), activation='relu'),\n",
    "    layers.MaxPooling2D((2, 2)),\n",
    "    \n",
    "    # Convolutional & Pooling Layer 3\n",
    "    layers.Conv2D(128, (3, 3), activation='relu'),\n",
    "    layers.MaxPooling2D((2, 2)),\n",
    "    \n",
    "    # Flatten 2D feature maps to 1D vector\n",
    "    layers.Flatten(),\n",
    "    \n",
    "    # Dense Fully Connected layers\n",
    "    layers.Dense(128, activation='relu'),\n",
    "    layers.Dropout(0.5),\n",
    "    layers.Dense(1, activation='sigmoid') # Binary classification\n",
    "])\n",
    "\n",
    "model.compile(optimizer='adam',\n",
    "              loss='binary_crossentropy',\n",
    "              metrics=['accuracy'])\n",
    "\n",
    "model.summary()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Training and Evaluation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "history = model.fit(\n",
    "    X_train, y_train,\n",
    "    epochs=10,\n",
    "    validation_data=(X_test, y_test),\n",
    "    batch_size=32\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.plot(history.history['accuracy'], label='accuracy')\n",
    "plt.plot(history.history['val_accuracy'], label = 'val_accuracy')\n",
    "plt.xlabel('Epoch')\n",
    "plt.ylabel('Accuracy')\n",
    "plt.ylim([0.5, 1])\n",
    "plt.legend(loc='lower right')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Exporting Model Weights"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)\n",
    "model.save(MODEL_OUTPUT)\n",
    "print(f\"Model saved to {MODEL_OUTPUT}\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

notebook_path = os.path.join("..", "notebooks", "model_training.ipynb")
os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
with open(notebook_path, "w") as f:
    json.dump(notebook, f, indent=1)
