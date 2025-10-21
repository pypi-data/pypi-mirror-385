# cellphase_grid_module.py

import os
import cv2
import random
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from cellpose import models

def run_cellphase_grid_search(
    input_dir,
    crop_size=None,
    diameters=[20, 40, 60, 80,100, 120],
    flow_thresholds=[0.4, 0.6, 0.8, 1.0],
    pretrained_model="cellpose_train_folder_qpi_live_0520"
):
    # === Load random image ===
    valid_exts = ('.tif', '.tiff', '.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_exts)]
    if not files:
        raise FileNotFoundError("No valid image files found in input_dir.")

    random_file = random.choice(files)
    img_path = os.path.join(input_dir, random_file)

    if random_file.lower().endswith(('.tif', '.tiff')):
        img = tifffile.imread(img_path)
    else:
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Failed to load image: {img_path}")
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if crop_size and img.shape[0] >= crop_size and img.shape[1] >= crop_size:
        x = random.randint(0, img.shape[1] - crop_size)
        y = random.randint(0, img.shape[0] - crop_size)
        img = img[y:y + crop_size, x:x + crop_size]
    img = img - img.min()
    img = img/img.max()
    img = (img*255).astype('uint8')
    print(f"Selected: {random_file}, shape: {img.shape}")

    # === Show original image ===
    plt.figure(figsize=(6, 6))
    plt.imshow(img, cmap='gray')
    plt.title(f"Original Image: {random_file}")
    plt.axis('off')
    plt.show()
    
    # === Load model ===
    model = models.CellposeModel(pretrained_model=pretrained_model, gpu=True)

    # === Run grid search ===
    results = []
    for diameter in diameters:
        for flow_thresh in flow_thresholds:
            masks = model.eval(
                img, diameter=diameter, flow_threshold=flow_thresh, channels=[0, 0]
            )[0]
            results.append({
                'diameter': diameter,
                'flow_thresh': flow_thresh,
                'masks': masks
            })

    # === Prepare figure ===
    n = len(results)
    
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows))
    axes = axes.flatten()

    for i, result in enumerate(results):
        ax = axes[i]
        #ax.imshow(img, cmap='gray')
        ax.imshow(result['masks'], cmap='nipy_spectral')
        ax.set_title(f"Dia={result['diameter']} | Flow={result['flow_thresh']}")
        ax.axis('off')

    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    fig.tight_layout()
    return fig  # ← Return the figure for inline display in Jupyter
