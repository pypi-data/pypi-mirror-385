from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="maraco-api",
    version="0.1.0",
    author="MarACO Team",
    author_email="contact@maraco.ai",
    description="Marine Acoustic Classification API - CPU-optimized marine sound classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maraco/maraco-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: English",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "maraco": [
            "models/pretrained/*.pkl",
            "models/pretrained/*.joblib",
            "config/*.json",
        ],
    },
    entry_points={
        "console_scripts": [
            "maraco-train=maraco.training.train_model:main",
            "maraco-validate=maraco.training.validate_model:main",
        ],
    },
    keywords=[
        "marine", "acoustic", "classification", "machine learning", "audio", 
        "whale", "sonar", "ocean", "bioacoustics", "marine biology",
        "sound detection", "audio analysis", "marine monitoring"
    ],
    project_urls={
        "Bug Reports": "https://github.com/maraco/maraco-api/issues",
        "Source": "https://github.com/maraco/maraco-api",
        "Documentation": "https://maraco-api.readthedocs.io/",
    },
)
