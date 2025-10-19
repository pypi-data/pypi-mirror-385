from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="dsites",
    version="1.1.0",
    author="Pankaj, Kanaka KK",
    author_email="ft.pank@gmail.com",
    description="D-Sites: Hybrid TFBS predictor (PWM + DNA shape + RF)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dsites",  # Replace with your repo URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "biopython>=1.79",
        "pandas>=1.3",
        "numpy>=1.21",
        "scikit-learn>=1.0",
        "matplotlib>=3.3",
        "tqdm>=4.62",
    ],
    entry_points={
        "console_scripts": [
            "dsites=dsites.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
    include_package_data=True,
    zip_safe=False,
)
