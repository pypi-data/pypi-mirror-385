from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the contents of requirements.txt
with open(os.path.join(this_directory, "requirements.txt"), "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="xkfuzzy",
    version="1.0.0",
    author="xkfuzzy",
    author_email="xkfuzzy@example.com",
    description="A Python library for fuzzy membership calculations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xkfuzzy/xkfuzzy",
    project_urls={
        "Bug Reports": "https://github.com/xkfuzzy/xkfuzzy/issues",
        "Source": "https://github.com/xkfuzzy/xkfuzzy",
        "Documentation": "https://github.com/xkfuzzy/xkfuzzy#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="fuzzy membership logic mathematics ai artificial intelligence",
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
