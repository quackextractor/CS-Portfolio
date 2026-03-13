
### 6-Part Inference Pipeline Implementation Plan

**Phase 1: Define the Tiling Helper Function**
Create a standalone generator function outside of the `main()` function in `src/app.py`.

* **Calculate Dimensions:** Accept the `detection_frame` as an argument and extract its total width and height.
* **Yield 1 (Full Frame):** Yield the original, uncropped `detection_frame` with an `x_offset` of 0 and a `y_offset` of 0 to capture extreme close-ups.
* **Yield 2 to 5 (Quadrants):** Calculate the exact midpoint coordinates to split the frame into top-left, top-right, bottom-left, and bottom-right patches. Yield each tile with its respective `x` and `y` offsets.
* **Yield 6 (Center Crop):** Calculate a sixth patch centered precisely in the middle of the frame, ensuring its width and height overlap the inner boundaries of the four quadrants to catch faces split down the middle. Yield it with its respective offsets.

**Phase 2: Modify the Local Inference Loop**
Inside the `while True:` loop in `src/app.py`, locate the block where you finalize the `detection_frame`.

* **Initialize Storage:** Create empty lists named `all_boxes` and `all_scores` immediately before face detection begins.
* **Iterate Tiles:** Implement a `for` loop that iterates over the six distinct tiles yielded by your new helper function.
* 
**Format for MediaPipe:** Inside the loop, convert the current tile from BGR to RGB and wrap it in an `mp.Image` object using `mp.ImageFormat.SRGB`.


* 
**Run Inference:** Pass the formatted tile to `face_detector.detect(mp_image)`.



**Phase 3: Coordinate Transformation**
Immediately after receiving the detection results for a specific tile, you must map the local bounding boxes back to the global `detection_frame` space.

* 
**Extract Local Coordinates:** Iterate through the `detection_result.detections` list and extract `origin_x`, `origin_y`, `width`, and `height`.


* **Apply Offsets:** Add the current tile's `x_offset` to `origin_x` and the `y_offset` to `origin_y`.
* **Store Data:** Append the translated bounding box list `[new_x, new_y, width, height]` to `all_boxes`.
* **Store Scores:** Append the detection confidence score (extracted from the MediaPipe detection object) to `all_scores` for the upcoming Non-Maximum Suppression step.

**Phase 4: Bounding Box Fusion (NMS)**
Once the loop finishes processing all six tiles, consolidate the overlapping detections to prevent duplicate bounding boxes.

* **Check for Detections:** Verify that `all_boxes` is not empty before proceeding.
* **Format for OpenCV:** Convert `all_boxes` and `all_scores` into NumPy arrays.
* **Apply NMS:** Execute `cv2.dnn.NMSBoxes()`, providing your arrays alongside a confidence threshold of 0.5 and an NMS threshold of 0.4.
* **Filter Boxes:** Extract the final valid boxes by indexing `all_boxes` with the specific indices returned by the NMS function, saving them to a new list called `final_boxes`.

**Phase 5: Reconnect to the CNN Pipeline**
Plug your filtered global coordinates back into the existing scaling and cropping logic in `src/app.py`.

* 
**Replace the Loop:** Replace your current `for detection in detection_result.detections:` loop with a loop that iterates directly over `final_boxes`.


* **Scale Coordinates:** Extract `x`, `y`, `w`, and `h` from the current final box.
* 
**Map to Original Resolution:** Divide each coordinate by your existing `scale_factor` variable and cast them to integers to map them perfectly back to the unscaled original frame.


* **Proceed as Normal:** Maintain your exact existing logic below this point. The code will continue to calculate the 5 percent margin, crop the face, append it to `faces_batch`, run the Keras prediction, and generate the Grad-CAM overlays without requiring any further modifications.