from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="x-spaces-dl",
    version="1.0.8",
    description="A powerful command-line tool and Python library for downloading Twitter/X Spaces recordings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/w3Abhishek/x-spaces-dl",
    author="pyvrma",
    author_email="insightfulverma@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="twitter x spaces download audio recording cli",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
        python_requires=">=3.10",
    install_requires=[
        "click>=8.3.0",
        "mutagen>=1.47.0",
        "python-dateutil>=2.9.0.post0",
        "pyyaml>=6.0.3",
        "requests>=2.32.5",
        "rich>=14.2.0",
        "tqdm>=4.67.1",
    ],
    extras_require={
        "dev": [
            "black>=25.9.0",
            "flake8>=7.3.0",
            "isort>=7.0.0",
            "mypy>=1.18.2",
            "pytest>=8.4.2",
            "pytest-cov>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "x-spaces-dl=xspacesdl.cli:main",
            "xspacesdl=xspacesdl.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/w3Abhishek/x-spaces-dl/issues",
        "Source": "https://github.com/w3Abhishek/x-spaces-dl",
    },
)