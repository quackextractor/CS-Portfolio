Here is the step-by-step implementation plan to apply the data leakage fix, improve data augmentation, and tighten the crop margins.

### 1. File: `build_dataset.py`

You need to make two distinct changes in this file to address the crop margins and the dataset splitting logic.

**A. Tighten the Crop Margin (Point 4)**
Locate the `process_images` function. Find the lines calculating the bounding box margins and reduce the multiplier from `0.1` to `0.05`.

* **Change:**
```python
margin_x = int(w * 0.1)
margin_y = int(h * 0.1)

```


* **To:**
```python
margin_x = int(w * 0.05)
margin_y = int(h * 0.05)

```



**B. Fix Data Leakage with Video-Level Splits (Point 1)**
Locate the `build_dataset` function. Delete the current frame-level split logic that relies on `.iloc[:train_end]`. Replace it with logic that groups frames by their source video name before distributing them to the train, validation, and test sets.

* **Remove:**
```python
df = df.sort_values("filepath").reset_index(drop=True)
# ... all the way down to ...
test_subset['split'] = 'test'
test_dfs.append(test_subset)

```


* **Implement:**
Create a new column that extracts the base video name from the `filepath`. Get a list of unique video names for both the positive and negative classes. Shuffle these lists and slice them by your 70/15/15 ratio. Finally, map those assignments back to the main dataframe so every frame from a specific video gets the same split label.

### 2. File: `app.py`

You must mirror the crop margin adjustment here so your real-time inference sees the exact same framing as your training data.

**A. Tighten the Crop Margin (Point 4)**
Locate the `main` function. Inside the detection loop, find the bounding box margin calculations and reduce them to `0.05`.

* **Change:**
```python
margin_x, margin_y = int(w * 0.1), int(h * 0.1)

```


* **To:**
```python
margin_x, margin_y = int(w * 0.05), int(h * 0.05)

```



### 3. File: `model_training.ipynb`

You need to add the new color and contrast jittering layers to your Convolutional Neural Network architecture.

**A. Improve Data Augmentation (Point 3)**
Locate Cell 4, where the `model = models.Sequential([...])` is defined. Add the two new preprocessing layers directly after the geometric augmentations.

* **Change:**
```python
layers.RandomFlip("horizontal"),
layers.RandomRotation(0.1),
layers.RandomZoom(0.1),

layers.Conv2D(32, (3, 3), activation='relu', padding='same', kernel_regularizer=tf.keras.regularizers.l2(0.001)),

```


* **To:**
```python
layers.RandomFlip("horizontal"),
layers.RandomRotation(0.1),
layers.RandomZoom(0.1),
layers.RandomBrightness(factor=0.2),
layers.RandomContrast(factor=0.2),

layers.Conv2D(32, (3, 3), activation='relu', padding='same', kernel_regularizer=tf.keras.regularizers.l2(0.001)),
