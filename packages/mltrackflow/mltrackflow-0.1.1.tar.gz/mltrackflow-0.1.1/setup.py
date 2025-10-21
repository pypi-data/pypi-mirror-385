"""
mltrackflow - Makine Öğrenimi Eğitim Sürecini Şeffaf ve İzlenebilir Kılan Kütüphane
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mltrackflow",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Makine öğrenimi eğitim süreçlerini şeffaf ve izlenebilir hale getiren kullanıcı dostu Python kütüphanesi. Otomatik metrik takibi, pipeline yönetimi, model karşılaştırma ve HTML raporlama özellikleri ile ML projelerinizi organize edin.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mltrackflow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "joblib>=1.0.0",
        "pyyaml>=5.4.0",
        "tqdm>=4.60.0",
        "tabulate>=0.8.9",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "sphinx>=4.0.0",
        ],
        "advanced": [
            "mlflow>=2.0.0",
            "optuna>=3.0.0",
            "shap>=0.41.0",
            "yellowbrick>=1.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "mltrackflow=mltrackflow.cli:main",
        ],
    },
)


