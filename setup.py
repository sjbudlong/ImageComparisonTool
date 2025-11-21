"""
Setup script for Image Comparison Tool.
Allows installation as a package: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="image-comparison-system",
    version="1.0.0",
    author="Your Name",
    author_email="sjbudlong@gmail.com",
    description="Modular Python system for comparing images with advanced diff analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sjbudlong/image-comparison-system",
    project_urls={
        "Bug Tracker": "https://github.com/sjbudlong/ImageComparisonTool/issues",
        "Documentation": "https://github.com/sjbudlong/ImageComparisonTool#readme",
        "Source Code": "https://github.com/sjbudlong/ImageComparisonTool",
    },
    py_modules=[
        "main",
        "config",
        "ui",
        "analyzers",
        "processor",
        "comparator",
        "report_generator",
        "dependencies",
        "verify_installation",
        "check_system",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "scikit-image>=0.21.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "imgcompare=main:main",
            "imgcompare-check=check_system:main",
            "imgcompare-deps=dependencies:main",
            "imgcompare-verify=verify_installation:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: X11 Applications",
    ],
    keywords=[
        "image",
        "comparison",
        "diff",
        "visual-regression",
        "opencv",
        "computer-vision",
        "3d-rendering",
        "testing",
        "qa",
        "histogram",
        "ssim",
    ],
    include_package_data=True,
    zip_safe=False,
)
