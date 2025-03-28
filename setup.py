"""
Setup script for Alexandrea Library.
"""

from setuptools import find_packages, setup

setup(
    name="alexandrea_library",
    version="0.1.0",
    description="A modern library management system inspired by the ancient Library of Alexandria",
    author="J Christensen",
    author_email="jchristensen719@example.com",
    url="https://github.com/jchristensen719/Alexandrea-Library",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        # "dataclasses;python_version<'3.7'", # Removed: Unnecessary with python_requires >= 3.8
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=20.8b1",
            "pylint>=2.6.0",
            "isort>=5.6.4",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
