# setup.py
from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").exists() else ""

setup(
    name="Cb_FloodDy",
    version="0.1.4",
    description="A cluster-based temporal attention approach for predicting cyclone-induced compound flood dynamics",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Samuel Daramola",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
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
    project_urls={
        "Homepage": "https://pypi.org/project/Cb-FloodDy/",
        "Repository": "https://github.com/SamuelDara/Cb_FloodDy.git",
    },
)
