import setuptools
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r") as f:
    # Filter out comments and empty lines
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setuptools.setup(
    name="threat-scanner",
    version="0.1.3",
    author="Ogo-Oluwasubomi Popoola",
    author_email="52616005+popoolasubomi@users.noreply.github.com",
    description="Detect threats in videos using MovieNet locally or via Vertex AI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/threatscan-ai/threatscan",
    license="MIT",
    packages=setuptools.find_packages(exclude=["tests*", "docs*"]), 
    include_package_data=True,
    package_data={
        'threat_scanner': ['kinetics_600_labels.json'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    project_urls={ 
        "Bug Tracker": "https://github.com/threatscan-ai/threatscan/issues",
        "Source Code": "https://github.com/threatscan-ai/threatscan",
        "Documentation": "https://github.com/threatscan-ai/threatscan/blob/main/README.md",
    },
    keywords="vertex ai, video analysis, threat detection, action recognition, movienet, google cloud",
)
