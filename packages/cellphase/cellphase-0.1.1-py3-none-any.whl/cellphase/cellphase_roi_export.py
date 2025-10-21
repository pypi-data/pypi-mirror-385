# cellphase_roi_export.py (saving individual .roi files per object)

import os
import cv2
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from cellpose import models
import roifile


def run_cellphase_batch_predict_with_rois(
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

    roi_root = "test_roi"
    os.makedirs(roi_root, exist_ok=True)

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
        masks = model.eval(
            img_uint8, diameter=diameter, flow_threshold=flow_threshold, channels=[0, 0]
        )[0]

        # === Convert masks to individual .roi files and save ===
        labeled_mask = label(masks)
        image_base = os.path.splitext(fname)[0]
        roi_folder = os.path.join(roi_root, image_base)
        os.makedirs(roi_folder, exist_ok=True)

        for i, region in enumerate(regionprops(labeled_mask)):
            coords = region.coords
            points = np.array([[c[1], c[0]] for c in coords], dtype=np.int16)
            roi = roifile.ImagejRoi.frompoints(points)
            roi_path = os.path.join(roi_folder, f"roi_{i+1}.roi")
            roi.tofile(roi_path)
