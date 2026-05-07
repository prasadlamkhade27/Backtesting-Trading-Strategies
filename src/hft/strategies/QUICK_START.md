# Pairs Trading - 5-Minute Quick Start

**Get up and running in 5 minutes**

---

## What Is Pairs Trading?

Trade the **relationship** between two correlated currency pairs, not the price direction.

```
EUR/USD goes up 50 pips
GBP/USD stays flat
→ Spread widened (EUR strong vs GBP)
→ SELL EUR, BUY GBP (bet on reversion)
→ Both come back together
→ Profit on BOTH legs
```

---

## Key Concept: Z-Score

```
Z = (Spread - Average) / Deviation

Z = 0   → Normal (no trade)
Z = ±2  → Extreme (ENTRY signal)
Z = 0   → Back to normal (EXIT, take profit)
Z = ±3  → DANGER (hard stop loss)
```

---

## Run the Example (2 minutes)

```bash
cd d:\str.  testing
python hft/examples/run_pairs_trading_complete.py
```

This will generate realistic data, analyze correlations, generate signals, and show results.

---

## Use It Yourself (3 minutes)

```python
from hft.strategies.pairs_trading_strategy import PairsTradingStrategy
import pandas as pd

# Load your data
df1 = pd.read_csv('eurusd.csv')  # Must have OHLC columns
df2 = pd.read_csv('gbpusd.csv')

# Create strategy
strategy = PairsTradingStrategy(
    pair1='EURUSD',
    pair2='GBPUSD',
)

# Get signals
signals = strategy.generate_signals(df1, df2)

# Signals now has:
#   signal_pair1: 1=BUY, -1=SELL, 0=HOLD
#   zscore: Current Z-score
#   spread: Current spread value
```

---

## Critical Rules

**MUST DO:**
1. ✓ Check correlation > 0.7 (verify relationship exists)
2. ✓ Set stop loss at Z > ±3.0 (hard stop)
3. ✓ Scale volumes by hedge ratio (maintain balance)
4. ✓ Execute both legs within 2 seconds (avoid imbalance)

**NEVER DO:**
1. ✗ use equal volumes (creates directional bias)
2. ✗ enter without pre-analysis (might not be correlated)
3. ✗ ignore stop losses (correlation can break suddenly)
4. ✗ hold when Z > ±3.0 (means correlation failed)

---

## Trade Example

```
EUR/USD: 1.1050
GBP/USD: 1.2700

Hedge Ratio (β): 0.85
Spread = 1.1050 - (0.85 × 1.2700) = 0.0255
Z-Score = +2.1 ← ENTRY SIGNAL

TRADE:
  Sell 1.0 lot EUR @ 1.1050
  Buy 0.85 lot GBP @ 1.2700

Market reverts:
  EUR: 1.1020 (↓30 pips from entry)
  GBP: 1.2720 (↑20 pips from entry)

EXIT:
  Close EUR @ 1.1020 = +30 pips profit
  Close GBP @ 1.2720 = +20 pips profit
  Total: +50 pips profit (both legs!)
```

---

## Files You Have

| File | Purpose |
|------|---------|
| `pairs_trading_strategy.py` | Main implementation |
| `pairs_backtest_engine.py` | Backtesting |
| `PAIRS_TRADING_README.md` | Complete reference (read this!) |
| `PAIRS_TRADING_GUIDE.py` | Deep theory |
| `pairs_trading_config.py` | Pre-built configurations |
| `run_pairs_trading_complete.py` | Working example |

---

## Next Steps

1. **Right now**: Run the example
2. **Today**: Read `PAIRS_TRADING_README.md`
3. **This week**: Backtest on your data
4. **Next week**: Paper trade
5. **When ready**: Live trade with small position size

---

## Common Questions

**Q: What if both pairs go down?**
A: That's OK! You're short EUR (+pips profit) and long GBP (-pips loss). Net could still be profit because of the spread relationship.

**Q: Can I trade with unequal volumes?**
A: NO. This creates directional bias and breaks the hedge. Always scale by hedge ratio.

**Q: How do I know which pairs to trade?**
A: Use the analyzer:
```python
from hft.strategies.pairs_trading_strategy import PairsTradingAnalyzer
analyzer = PairsTradingAnalyzer()
analysis = analyzer.analyze_pair_relationship(df1, df2)
print(f"Correlation: {analysis['correlation']}")  # Need > 0.7
print(f"Cointegrated: {analysis['is_cointegrated']}")  # Need True
```

**Q: What if I lose money on both legs?**
A: Stop loss triggered (Z > ±3.0), meaning correlation broke. This is expected occasionally. Proper stops prevent catastrophic losses.

---

## Pre-Trade Checklist

Before each trade:
- [ ] Correlation > 0.7?
- [ ] Cointegrated (statistically significant relationship)?
- [ ] Z-score > ±2.0?
- [ ] No major news event in next hour?
- [ ] Can I execute both legs within 2 seconds?

---

## Red Flags (Exit Immediately)

- [ ] Z-score > ±3.0 (correlation broken)
- [ ] Correlation dropped to < 0.5 (hedge failed)
- [ ] One leg profitable, other losing (execution problem)
- [ ] Spread keeps expanding (trending, not reverting)

---

## Resources

- **Theory**: `PAIRS_TRADING_GUIDE.py` (Parts 1-4)
- **How-to**: `PAIRS_TRADING_README.md` (Best practices)
- **Code**: `pairs_trading_strategy.py` (Implementation)
- **Example**: `run_pairs_trading_complete.py` (Working demo)
- **Config**: `pairs_trading_config.py` (Pre-built setups)

---

## One-Liner Commands

```bash
# Run the complete working example
python hft/examples/run_pairs_trading_complete.py

# Test with your data
python -c "
from hft.strategies.pairs_trading_strategy import PairsTradingStrategy
import pandas as pd
df1 = pd.read_csv('EURUSD.csv')
df2 = pd.read_csv('GBPUSD.csv')
s = PairsTradingStrategy('EURUSD','GBPUSD')
print(s.generate_signals(df1, df2))
"
```

---

## Remember

> **This is NOT direction prediction. This is NOT arbitrage. This is statistical arbitrage based on mean reversion.**

- High win rate (60-70%) ✓
- Small profit per trade (20-50 pips) ⚠
- Correlation can break (immediate loss risk) ✗
- Proper stops ESSENTIAL (no exceptions) ✓

---

## Ready?

1. Run: `python hft/examples/run_pairs_trading_complete.py`
2. Read: `PAIRS_TRADING_README.md`
3. Code: Load your data and generate signals
4. Test: Backtest different parameters
5. Trade: Start small and monitor carefully

**Good luck! Remember: correlation is king, hard stops are sacred.**

---

*For detailed theory, read PAIRS_TRADING_GUIDE.py*  
*For configuration templates, read pairs_trading_config.py*  
*For complete reference, read PAIRS_TRADING_README.md*
