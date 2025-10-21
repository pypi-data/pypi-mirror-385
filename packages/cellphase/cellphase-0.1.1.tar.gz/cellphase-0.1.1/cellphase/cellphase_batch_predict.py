# cellphase_batch_predict.py

import os
import cv2
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from cellpose import models

def run_cellphase_batch_predict(
    input_dir,
    diameter,
    flow_threshold,
    num_images=None,
    pretrained_model="cellpose_train_folder_qpi_live_0520",
    visualize=True
):
    valid_exts = ('.tif', '.tiff', '.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_exts)]
    if not files:
        raise FileNotFoundError("No valid image files found in input_dir.")

    if num_images is not None:
        files = files[:num_images]

    output_dir = "test_pred" #os.path.join(input_dir, "test_pred")
    os.makedirs(output_dir, exist_ok=True)

    model = models.CellposeModel(pretrained_model=pretrained_model, gpu=True)

    for fname in files:
        # === Load image ===
        img_path = os.path.join(input_dir, fname)
        if fname.lower().endswith(('.tif', '.tiff')):
            img = tifffile.imread(img_path)
        else:
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Warning: Could not read {fname}, skipping.")
            continue
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # === Normalize to uint8 ===
        img = img.astype(np.float32)
        img = img - img.min()
        img = img / (img.max() + 1e-8)
        img_uint8 = (img * 255).astype(np.uint8)

        # === Predict ===
        masks = model.eval(img_uint8, diameter=diameter, flow_threshold=flow_threshold, channels=[0, 0])[0]
        mask_name = os.path.splitext(fname)[0] + "_pred.png"
        mask_path = os.path.join(output_dir, mask_name)
        masks = masks/masks.max()
        masks = (masks*255)
        # === Save predicted mask ===
        cv2.imwrite(mask_path, masks.astype(np.uint8))

        # === Visualize if requested ===
        if visualize:
            plt.figure(figsize=(10, 5))
            plt.subplot(1, 2, 1)
            plt.imshow(img_uint8, cmap='gray')
            plt.title(f"Original: {fname}")
            plt.axis('off')

            plt.subplot(1, 2, 2)
            plt.imshow(masks, cmap='nipy_spectral')
            plt.title(f"Predicted Mask | Dia={diameter}, Flow={flow_threshold}")
            plt.axis('off')

            plt.tight_layout()
            plt.show()
