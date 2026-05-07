# 📦 Installation Guide

Detailed installation instructions for different environments and use cases.

## System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 2GB | 8GB+ |
| Disk Space | 500MB | 2GB |
| OS | Windows/Mac/Linux | Windows/Mac/Linux |

---

## Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Verify Installation

```bash
python -c "import hft; print('✅ Installation successful')"
```

---

### Method 2: Conda Installation

```bash
# Create conda environment
conda create -n trading python=3.10

# Activate environment
conda activate trading

# Install dependencies
conda install -c conda-forge -r requirements.txt
```

---

### Method 3: Docker Installation

```bash
# Build Docker image
docker build -t trading-system .

# Run Docker container
docker run -p 8501:8501 trading-system
```

---

## Platform-Specific Setup

### Windows Setup

```bash
# 1. Install Python from python.org
# 2. Verify installation
python --version

# 3. Create virtual environment
python -m venv venv

# 4. Activate
venv\Scripts\activate

# 5. Install packages
pip install -r requirements.txt
```

### Mac Setup

```bash
# 1. Install Python (using Homebrew recommended)
brew install python@3.10

# 2. Verify
python3 --version

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate
source venv/bin/activate

# 5. Install packages
pip install -r requirements.txt
```

### Linux Setup

```bash
# 1. Install Python (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.10 python3-pip python3-venv

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate
source venv/bin/activate

# 4. Install packages
pip install -r requirements.txt
```

---

## Troubleshooting Installation

### Issue: Python Not Found

**Solution:**
```bash
# Check Python version
python --version

# If not found, install from python.org
# Or use package manager:
# Windows: chocolatey install python
# Mac: brew install python@3.10
# Linux: sudo apt-get install python3
```

### Issue: pip Not Found

**Solution:**
```bash
# Use python -m pip instead
python -m pip --version
python -m pip install -r requirements.txt
```

### Issue: Permission Denied

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Issue: Module Import Errors

**Solution:**
```bash
# Make sure virtual environment is active
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

### Issue: Long Installation Time

**Solution:**
```bash
# Use faster pip resolver
pip install -r requirements.txt --use-deprecated=legacy-resolver

# Or install specific packages
pip install streamlit pandas numpy scikit-learn
```

---

## Verifying Installation

### Quick Verification

```bash
python -c "import hft; print('✅ HFT module found')"
```

### Full Verification Script

```bash
cd hft
python examples/verify_installation.py
```

### Check Installed Packages

```bash
pip list
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Credentials
BROKER_API_KEY=your_api_key
BROKER_API_SECRET=your_api_secret

# Settings
RISK_PER_TRADE=0.02
ACCOUNT_SIZE=10000

# Data
DATA_PATH=./data
```

Load in your Python code:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('BROKER_API_KEY')
```

### Config File

Edit `propfirm/config.py` for permanent settings:

```python
# Example configuration
BROKER_CONFIG = {
    'name': 'MT5',
    'symbol': 'EURUSD',
    'timeframe': '1H'
}

RISK_CONFIG = {
    'account_size': 10000,
    'risk_per_trade': 0.02,
    'max_daily_loss': 0.05
}
```

---

## Development Installation

For development and contributions:

```bash
# Clone repository
git clone https://github.com/yourusername/trading-system.git
cd trading-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

---

## Docker Installation

### Build Docker Image

```bash
docker build -t trading-system:latest .
```

### Run Docker Container

```bash
# Run Streamlit app
docker run -p 8501:8501 trading-system:latest

# Run with volume mount
docker run -v $(pwd):/app -p 8501:8501 trading-system:latest
```

---

## Updating Installation

### Update All Packages

```bash
pip install --upgrade -r requirements.txt
```

### Update Specific Package

```bash
pip install --upgrade streamlit
```

### Check Outdated Packages

```bash
pip list --outdated
```

---

## Uninstallation

### Remove Virtual Environment

**Windows:**
```bash
venv\Scripts\deactivate
rmdir /s venv
```

**Mac/Linux:**
```bash
deactivate
rm -rf venv
```

### Remove Project Files

```bash
# Simply delete the project folder
rm -rf trading-system
```

---

## Support

- **Installation Issues**: Check [FAQ.md](FAQ.md)
- **Platform-Specific Help**: See relevant section above
- **Still Stuck**: Create an issue on GitHub

---

**Next Step**: Once installed, run [GETTING_STARTED.md](GETTING_STARTED.md)

