from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hepatitis-c-predictor",
    version="0.1.0",
    author="Ninjalice",
    author_email="ninjalice@users.noreply.github.com",
    description="Interactive ML application for Hepatitis C classification using PyTorch with Streamlit interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ninjalice/HEPATITIS_C_MODEL",
    project_urls={
        "Documentation": "https://ninjalice.github.io/HEPATITIS_C_MODEL/src.html",
        "Repository": "https://github.com/Ninjalice/HEPATITIS_C_MODEL",
        "Issues": "https://github.com/Ninjalice/HEPATITIS_C_MODEL/issues",
    },
    packages=find_packages(where="."),
    package_dir={"": "."},
    py_modules=["app"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "streamlit>=1.50.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.13.0",
        "plotly>=5.14.0",
        "torch>=2.0.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "ipykernel>=6.22.0",
            "ipython>=8.0.0",
        ],
        "docs": [
            "pdoc>=14.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hepatitis-c-demo=app:cli_main",
        ],
    },
    license="MIT",
    keywords=[
        "machine-learning",
        "pytorch",
        "hepatitis-c",
        "classification",
        "streamlit",
        "medical-ai",
        "deep-learning",
        "neural-network",
    ],
)
