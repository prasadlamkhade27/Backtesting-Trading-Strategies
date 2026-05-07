# 🚀 Getting Started Guide

Welcome to the Professional Algorithmic Trading System! This guide will get you up and running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip or conda package manager
- ~500MB disk space
- Basic Python knowledge

## Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
cd hft
python examples/verify_installation.py
```

You should see: ✅ Installation verified successfully!

---

## Quick Start Options

### Option 1: Web Dashboard (Easiest)

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**What you can do:**
- 📊 Build and test trading strategies
- 📈 Backtest across multiple forex pairs
- 💱 Execute live or simulated trades
- 🤖 Run algorithmic trading

### Option 2: MQL King 1 Strategy (5 Minutes)

```bash
python run_mql_king_1_backtest.py
```

This runs a complete backtest of the Smart Money Concepts strategy.

### Option 3: Python API (For Developers)

```python
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine
from hft.config.hft_config import get_preset

# Load a preset configuration
config = get_preset('CONSERVATIVE_SCALPING')

# Create strategy
strategy = HFTScalpingStrategy(**config.config)

# Run backtest
backtest = HFTBacktestEngine(strategy=strategy)
results = backtest.run()

# View results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
```

---

## Next Steps

### For Beginners
1. Run the web dashboard: `streamlit run app.py`
2. Explore the Strategy Builder page
3. Read [TRADING_GUIDE.md](TRADING_GUIDE.md)

### For Experienced Traders
1. Review [hft/docs/QUICK_REFERENCE.md](../hft/docs/QUICK_REFERENCE.md)
2. Explore the strategies in `hft/strategies/`
3. Run examples in `hft/examples/`

### For Developers
1. Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
2. Review the module documentation
3. Check out the code examples

---

## Troubleshooting

### Python Version Error
```bash
# Check your Python version
python --version

# You need 3.8 or higher
# If not, install from python.org or use pyenv/conda
```

### Import Errors
```bash
# Make sure you're in the virtual environment
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

### Streamlit Not Found
```bash
pip install streamlit
```

### Module Not Found
```bash
# Make sure you're in the project root
cd trading-system

# Reinstall in editable mode
pip install -e .
```

---

## Common Tasks

### Test a Strategy
1. Open dashboard: `streamlit run app.py`
2. Go to "Multi Pair Backtest" page
3. Select strategy and pairs
4. Click "Run Backtest"

### Create Custom Strategy
1. See [hft/examples/trading_example.py](../hft/examples/trading_example.py)
2. Or use Strategy Builder in dashboard

### Set Up Live Trading
1. Add API credentials in dashboard settings
2. Go to "Trading Hub" page
3. Configure risk parameters
4. Start trading

---

## Key Concepts

### Strategies
Pre-built or custom trading logic that generates buy/sell signals.

### Backtesting
Testing a strategy on historical data to see performance before risking real money.

### Risk Management
Rules to protect your account: position sizing, stop losses, daily limits, etc.

### Compliance
PropFirm rules that your strategy must follow (drawdown limits, consistency, etc.)

---

## Resources

- 📖 [Full Documentation](../README.md)
- 🎓 [HFT Quick Reference](../hft/docs/QUICK_REFERENCE.md)
- 💻 [Code Examples](../hft/examples/)
- ❓ [FAQ](FAQ.md)

---

## Get Help

1. **Check the docs** - Most questions are answered in documentation
2. **Run examples** - See `hft/examples/` for working code
3. **Search issues** - Check GitHub Issues for similar problems
4. **Ask in discussions** - Create a new discussion on GitHub

---

**You're all set!** 🎉

Start with one of the Quick Start options above, and you'll be trading in minutes.

