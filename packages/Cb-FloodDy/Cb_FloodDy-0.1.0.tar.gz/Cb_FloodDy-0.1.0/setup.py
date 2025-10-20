# setup.py
from pathlib import Path
from setuptools import setup, find_packages

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="Cb_FloodDy",
    version="0.1.0",
    description="Cluster-based Flood Dynamics: Voronoi clustering + attention-based flood depth modeling",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Samuel Daramola",
    license="MIT",
    packages=find_packages(include=["Cb_FloodDy", "Cb_FloodDy.*"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "geopandas",
        "shapely",
        "pyproj",
        "rasterio",
        "scikit-learn",
        "tensorflow>=2.9",
        "optuna>=3.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "cbf-train=Cb_FloodDy.cli:train",
            "cbf-predict=Cb_FloodDy.cli:predict",
            "cbf-tune=Cb_FloodDy.cli:tune",
        ]
    },
    project_urls={
        "Homepage": "https://example.com/Cb_FloodDy",
        "Repository": "https://example.com/Cb_FloodDy.git",
    },
)
