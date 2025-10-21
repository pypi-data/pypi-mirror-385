from setuptools import setup, find_packages

setup(
    name="cellphase",
    version="0.1.1",
    description="CellPhase: QPI-focused cell segmentation utilities",
    author="Sourya Sengupta",
    python_requires=">=3.9",
    packages=find_packages(),  # <-- no 'where='
    include_package_data=True,
    install_requires=[
        "numpy<2",
        "scipy",
        "matplotlib",
        "tqdm",
        "scikit-image",
        "pillow",
        "cellpose==3.1.1",
        "opencv-python-headless==4.8.0.76",
        "tifffile",
        "roifile",
        "notebook",
        "ipykernel",
        "ipywidgets",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
