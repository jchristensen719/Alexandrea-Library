# Module 1: Platform Setup

## Core Development Environment Setup

### VS Code Installation
1. **Download VS Code**:
   - Visit [Visual Studio Code website](https://code.visualstudio.com/)
   - Download the appropriate version for your operating system (Windows, macOS, or Linux)
   - Run the installer and follow the on-screen instructions

2. **Essential VS Code Extensions**:
   - Python (Microsoft)
   - Jupyter (Microsoft)
   - GitLens
   - Python Indent
   - Prettier - Code formatter

   To install extensions: Click the Extensions icon in the sidebar (or press Ctrl+Shift+X), search for each extension, and click "Install".

### Anaconda Installation
1. **Download Anaconda**:
   - Visit [Anaconda website](https://www.anaconda.com/products/individual)
   - Download the appropriate version for your operating system
   - Run the installer and follow the on-screen instructions
   - During installation, select "Add Anaconda to my PATH environment variable" (though it's not recommended by Anaconda, it makes things easier for beginners)

2. **Verify Installation**:
   - Open Command Prompt/Terminal
   - Type `conda --version` and press Enter
   - You should see the installed version number

### GitHub Setup
1. **Create GitHub Account**:
   - Visit [GitHub](https://github.com/)
   - Sign up for a free account

2. **Install Git**:
   - Visit [Git website](https://git-scm.com/downloads)
   - Download and install for your operating system

3. **Configure Git**:
   - Open Command Prompt/Terminal
   - Set your name: `git config --global user.name "Your Name"`
   - Set your email: `git config --global user.email "your.email@example.com"`

4. **Set Up GitHub Copilot** (optional paid service):
   - If you're a student, you may be eligible for a free GitHub Student Developer Pack
   - Otherwise, consider the free trial or alternatives like Tabnine

### Orange Data Miner Installation
1. **Download Orange**:
   - Visit [Orange Data Mining website](https://orangedatamining.com/download/)
   - Download the appropriate version for your operating system

2. **Installation**:
   - Run the installer and follow the on-screen instructions
   - After installation, open Orange to verify it works

## Project Structure Setup

### Create Your Project Structure
1. **Create a Main Project Directory**
```
```shell
mkdir "Alexandrea Library"
cd "Alexandrea Library"
```
 
   



2. **Set Up Virtual Environment**:
   ```shell
   conda create --name alexandrea python=3.10
   conda activate alexandrea
   ```

3. **Create Project Subdirectories**:
   For Unix-like systems (Linux/macOS):
   ```bash
   mkdir -p src/scrapers src/data_processing src/content_generation data/raw data/processed notebooks config logs
   ```
   For Windows   
   mkdir src\scrapers src\data_processing src\content_generation data\raw data\processed notebooks config logs
   ```

4. **Initialize Git Repository**:
   ```
   git init
   ```

5. **Create .gitignore File**:
   Create a file named `.gitignore` in your project root with the following content:
   ```
   files
   .env
   .env.*
   .env.development.local
   .env.test.local
   .env.production.local
   .env.local
   .idea/
   .DS_Store
   Thumbs.db
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   env/
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   *.egg-info/
   .installed.cfg
   *.egg

   # Jupyter Notebook
   .ipynb_checkpoints

   # Virtual Environment
   venv/
   ENV/

   # VS Code
   .vscode/*
   !.vscode/settings.json
   !.vscode/tasks.json
   !.vscode/launch.json
   !.vscode/extensions.json

   # Data
   data/raw/*
   data/processed/*
   !data/raw/.gitkeep
   !data/processed/.gitkeep

   # Logs
   logs/*
   !logs/.gitkeep
   ```

6. **Create Empty Placeholder Files**:
   ```
   For Unix-like systems (Linux/macOS):
   ```shell
   touch data/raw/.gitkeep data/processed/.gitkeep logs/.gitkeep
   ```
   For Windows:
   ```shell   New-Item -ItemType File -Path "data/raw/.gitkeep", "data/processed/.gitkeep", "logs/.gitkeep" -Force
   ```
   ```

7. **Set Up Requirements File**:
   Create a file named `requirements.txt` in your project root:
   ```
   beautifulsoup4
   requests
   selenium
   playwright
   pandas
   numpy
   scikit-learn
   nltk
   pymongo
   schedule
   python-dotenv
   fastapi
   uvicorn
   ```

8. **Install Required Packages**:
   ```
   pip install -r requirements.txt
   ```

## Additional Setup for Web Scraping

### Selenium Setup
1. **Install WebDriver**:
   - For Chrome: Download [ChromeDriver](https://sites.google.com/chromium.org/driver/)
   - For Firefox: Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
   - Place the executable in a directory in your PATH

### Playwright Setup
1. **Install Playwright**:
   ```
   pip install playwright
   playwright install
   ```

## API Keys Setup (Free Tiers)
1. **Create `.env` File**:
   Create a file named `.env` in your project root:
   ```
   # API Keys
   PERPLEXITY_API_KEY=YOUR_PERPLEXITY_API_KEY
   DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY
   # Optional: Database Configuration
   DB_PATH=./data/database.sqlite
   ```

2. **Register for Free API Keys**:
   - Perplexity: Visit [Perplexity API](https://www.perplexity.ai/api) for free tier access
   - DeepSeek: Register at [DeepSeek website](https://www.deepseek.com/)

## Final Check
Run this simple test script to verify your setup:

Create a file named `setup_test.py` in your project root:
```python
import sys
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Test environment
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Test package installation
packages = ["pandas", "numpy", "beautifulsoup4", "requests", "selenium", "scikit-learn", "nltk"]
for package in packages:
    try:
        __import__(package)
        print(f"{package}: Successfully imported")
    except ImportError:
        print(f"{package}: Import failed")
```

Run the test:
```
python setup_test.py
```

### Troubleshooting Common Issues

1. **Python not found**: Make sure Anaconda is added to PATH or use the full path to the Python executable
2. **Package installation failures**: Try installing problematic packages individually with `pip install package_name`
3. **WebDriver issues**: Make sure the WebDriver is compatible with your browser version
4. **Permission denied errors**: Use sudo (Linux/Mac) or run as administrator (Windows)

Congratulations! Your development environment is now set up and ready for building the Alexandrea Library system.
