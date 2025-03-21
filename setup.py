from setuptools import find_packages, setup

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="alexandrea_library",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    author="J Christensen",
    author_email="jchristensen719@github.com",
    description="Alexandrea Library project - A modern library management system",
    keywords="library, books, alexandria",
    url="https://github.com/jchristensen719/Alexandrea-Library",
)
