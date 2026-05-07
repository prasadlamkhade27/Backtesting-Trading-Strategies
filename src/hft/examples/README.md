# HFT Examples & Tests

Complete working examples for the HFT Trading System.

## 📚 Examples

### `trading_example.py`
Complete backtesting example with:
- Strategy creation
- Signal generation
- Backtest execution
- Results analysis
- Parameter optimization

**Run**:
```bash
python trading_example.py
```

### `verify_installation.py`
System verification that checks:
- File structure
- Python imports
- Module loading
- Configuration presets
- File contents

**Run**:
```bash
python verify_installation.py
```

## 🚀 Quick Start

### Example 1: Simple Backtest
```python
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine, ExecutionParams
import pandas as pd

# Load data
data = pd.read_csv('eurusd_m5.csv')

# Create strategy
strategy = HFTScalpingStrategy(strategy_type='scalping')
signals = strategy.generate_signals(data)

# Run backtest
engine = HFTBacktestEngine(10000, ExecutionParams())
results = engine.backtest(data, signals)

# Results
print(f"Win Rate: {results['win_rate']:.1f}%")
print(f"Return: {results['total_return_percent']:.2f}%")
print(f"Sharpe: {results['sharpe_ratio']:.2f}")
```

### Example 2: Use Presets
```python
from hft.config.hft_config import get_preset, list_presets

# List all presets
print(list_presets())

# Use preset
config = get_preset('MODERATE_SCALPING')
print(f"Risk: {config.get('risk_percent_per_trade')}%")
```

### Example 3: Parameter Optimization
```python
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine

# Test different parameters
for ma_fast in [3, 5, 7]:
    for ma_slow in [15, 20, 25]:
        strategy = HFTScalpingStrategy(ma_fast=ma_fast, ma_slow=ma_slow)
        signals = strategy.generate_signals(data)
        
        engine = HFTBacktestEngine(10000, ExecutionParams())
        results = engine.backtest(data, signals)
        
        print(f"MA({ma_fast}x{ma_slow}): {results['total_return_percent']:.2f}%")
```

## 📖 Documentation

- See `docs/README_START_HERE.md` for full getting started
- See `docs/SYSTEM_GUIDE.md` for comprehensive guide
- See `docs/QUICK_REFERENCE.md` for quick commands

---

**Version**: 1.5
