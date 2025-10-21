from setuptools import setup, find_packages

setup(
  name="zachvit",
    version="1.0.0",
    author="Athanasios Angelakis",
    author_email="angelakis.athanasios@gmail.com",
    description="Official implementation of ZACH-ViT: Zero-Token Adaptive Compact Hierarchical Vision Transformer with ShuffleStrides Data Augmentation (SSDA).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Bluesman79/ZACH-ViT",
    project_urls={
        "Paper": "https://arxiv.org/abs/2510.17650",
        "DOI": "https://doi.org/10.48550/arXiv.2510.17650",
    },
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "tensorflow==2.19.0",
        "keras==3.5.0",
        "numpy==1.26.4",
        "pandas==2.3.2",
        "matplotlib==3.10.5",
        "pydicom==3.0.1",
        "scikit-image==0.20.0",
        "Pillow==11.3.0",
        "scikit-learn==1.7.1",
        "IPython==8.20.0",
    ],
    entry_points={
        "console_scripts": [
            "zachvit-preprocess=scripts.preprocess_cli:main",
            "zachvit-train=scripts.train_zachvit_cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Intended Audience :: Science/Research",
    ],
    keywords=[
        "vision transformer",
        "medical imaging",
        "ultrasound",
        "explainable AI",
        "deep learning",
        "lung ultrasound",
        "computer vision",
    ],
)
