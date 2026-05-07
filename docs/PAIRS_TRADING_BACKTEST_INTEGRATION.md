# Pairs Trading Integration with Backtest System

**Using pairs trading strategy with your existing backtesting infrastructure**

---

## 🚀 Quick Start

### Option 1: Run the Complete Example (Easiest)

```bash
cd d:\str.  testing
python hft/examples/backtest_pairs_trading.py
```

This will:
- Run basic pairs trading backtest
- Optimize parameters
- Compare multiple pair combinations
- Export results to CSV

### Option 2: Integrate into Your Code

```python
from hft.utils.pairs_backtest_integration import PairsBacktestIntegration
import pandas as pd

# Load your OHLC data
df1 = pd.read_csv('eurusd_h1.csv')
df2 = pd.read_csv('gbpusd_h1.csv')

# Create backtest
backtest = PairsBacktestIntegration(
    pair1='EURUSD',
    pair2='GBPUSD',
    account_size=10000,
    risk_pct=0.02,
)

# Run backtest
result = backtest.run_full_backtest(df1, df2, verbose=True)

# Export results
backtest.export_results_to_csv(result, 'my_backtest')
```

---

## 📊 Understanding the Output

### Backtest Results Include:

```
Trade Statistics:
  ✓ Total Trades: Number of completed trades
  ✓ Win Rate: Percentage of profitable trades
  ✓ Avg Trade Duration: How many bars per trade

P&L Metrics:
  ✓ Total P&L: Dollar profit/loss
  ✓ Return %: Return on account
  ✓ Profit Factor: Wins/Losses ratio
  ✓ Avg Win/Loss: Average per winning/losing trade

Risk Metrics:
  ✓ Max Drawdown: Worst losing period
  ✓ Sharpe Ratio: Risk-adjusted returns

Pair Analysis:
  ✓ Correlation: How related the pairs are
  ✓ Hedge Ratio: Price scaling factor (β)
  ✓ Cointegrated: Long-term relationship valid?
```

---

## 🔧 Integration with Your System

### Using with `EnhancedBacktestRunner`

Your existing `EnhancedBacktestRunner` is for single-pair trading. The pairs integration works **alongside** it:

```python
# For single pairs (existing system):
backtest_single = EnhancedBacktestRunner(
    account_size=10000,
    risk_pct=0.01,
    pair='EURUSD'
)
results_single = backtest_single.run_backtest_with_lots(df, sl_pips=30, tp_pips=50)

# For pairs (new system):
backtest_pairs = PairsBacktestIntegration(
    pair1='EURUSD',
    pair2='GBPUSD',
    account_size=10000,
    risk_pct=0.02,
)
results_pairs = backtest_pairs.run_full_backtest(df1, df2)
```

---

## 📈 Common Backtesting Scenarios

### Scenario 1: Basic Backtest (Test if Strategy Works)

```python
from hft.utils.pairs_backtest_integration import PairsBacktestIntegration

integration = PairsBacktestIntegration(
    pair1='EURUSD',
    pair2='GBPUSD',
    account_size=10000,
)

result = integration.run_full_backtest(df1, df2, verbose=True)
```

**What you're checking:**
- Does it generate signals?
- Win rate > 50%?
- Correlation > 0.7?
- Cointegrated?

---

### Scenario 2: Parameter Optimization (Find Best Settings)

```python
opt_results = integration.optimize_parameters(
    df1, df2,
    z_entry_range=(1.5, 2.5, 0.1),   # Test 1.5 to 2.5 step 0.1
    z_exit_range=(0.3, 0.7, 0.1),    # Test 0.3 to 0.7 step 0.1
    z_stop_range=(2.8, 3.5, 0.1),    # Test 2.8 to 3.5 step 0.1
)

# Best parameters are in opt_results['best_params']
best = opt_results['best_params']
```

**What you're finding:**
- Z-entry threshold that works best
- Optimal exit level (take profit)
- Hard stop loss level

---

### Scenario 3: Compare Multiple Pairs

```python
pairs_to_test = [
    ('EURUSD', 'GBPUSD'),
    ('EURUSD', 'AUDUSD'),
    ('AUDUSD', 'NZDUSD'),
]

for pair1, pair2 in pairs_to_test:
    integration = PairsBacktestIntegration(pair1=pair1, pair2=pair2)
    result = integration.run_full_backtest(df1, df2, verbose=False)
    
    print(f"{pair1} vs {pair2}: Win Rate {result.win_rate:.1f}%")
```

**What you're finding:**
- Which pair combinations work best
- Which have highest correlation
- Which generate most trades

---

### Scenario 4: Sensitivity Analysis (How sensitive is strategy?)

```python
for lookback in [80, 100, 120, 150]:
    integration = PairsBacktestIntegration(
        pair1='EURUSD',
        pair2='GBPUSD',
        lookback=lookback,
    )
    result = integration.run_full_backtest(df1, df2, verbose=False)
    print(f"Lookback {lookback}: {result.win_rate:.1f}% win rate")
```

**What you're checking:**
- How sensitive to lookback period
- Which setting is most robust

---

## 📁 Output Files

### CSV Exports:

**`backtest_pairs_trading_trades.csv`**
```
Columns: direction, entry_zscore, exit_zscore, total_pnl, duration_bars, exit_reason
Each row: One completed trade
Use for: Analyzing individual trades
```

**`backtest_pairs_trading_equity.csv`**
```
Columns: bar, equity
Each row: Equity after each bar
Use for: Drawing equity curve, calculating drawdown
```

---

## 🎯 Key Metrics to Check

### Must-Have Metrics:

| Metric | Target | What It Means |
|--------|--------|---------------|
| **Correlation** | > 0.70 | Pairs should be related |
| **Cointegrated** | True (p < 0.05) | Should have long-term relationship |
| **Win Rate** | > 55% | More winners than losers |
| **Profit Factor** | > 1.2 | Wins exceed losses |
| **Max Drawdown** | < 15% | Acceptable downside |

### Nice-to-Have Metrics:

| Metric | Target | What It Means |
|--------|--------|---------------|
| Avg Trade Duration | < 50 bars | Trades close quickly (good) |
| Sharpe Ratio | > 1.0 | Good risk-adjusted returns |
| Avg Win/Loss Ratio | > 1.5 | Winners are bigger than losers |

---

## ⚠️ Common Issues & Solutions

### Issue: "Few or No Trades Generated"

**Causes:**
- Z-score never reaches entry threshold
- Correlation too low (pairs filtered out)
- Volatility too high (news filtering)

**Solutions:**
```python
# Adjust thresholds
integration = PairsBacktestIntegration(
    z_entry=1.8,  # Lower from 2.0
    z_exit=0.6,   # Adjust exit level
    min_correlation=0.65,  # Lower from 0.70
)
```

---

### Issue: "High Drawdown / Many Losses"

**Causes:**
- Pairs not actually correlated
- Using unbalanced volumes
- Z-stop too wide (not exiting on correlation break)

**Solutions:**
```python
# Verify pair relationship first
from hft.strategies.pairs_trading_strategy import PairsTradingAnalyzer
analyzer = PairsTradingAnalyzer()
info = analyzer.analyze_pair_relationship(df1, df2)

print(f"Correlation: {info['correlation']}")  # Must be > 0.7
print(f"Cointegrated: {info['is_cointegrated']}")  # Must be True

# Tighten hard stop
integration = PairsBacktestIntegration(
    z_stop=2.8,  # Tighter from 3.0
)
```

---

### Issue: "Backtest Results Don't Match Live Trading"

**Causes:**
- Slippage assumptions wrong
- Commission too low/high
- Data quality issues
- Order execution differences

**Solutions:**
```python
# Verify integration parameters
print(f"Account size: {integration.account_size}")
print(f"Risk % per trade: {integration.risk_pct}")
print(f"Slippage: {integration.backtest_engine.slippage_pips}")
print(f"Commission: {integration.backtest_engine.commission_pct}")

# Match your actual trading conditions
```

---

## 🔄 Full Workflow Example

```python
#!/usr/bin/env python3
"""
Complete pairs trading backtest workflow
"""

from hft.utils.pairs_backtest_integration import PairsBacktestIntegration
from hft.strategies.pairs_trading_strategy import PairsTradingAnalyzer
import pandas as pd

# 1. Load Data
print("Loading data...")
df1 = pd.read_csv('eurusd_h1.csv')
df2 = pd.read_csv('gbpusd_h1.csv')

# 2. Pre-flight Checks
print("\nPre-flight Analysis...")
analyzer = PairsTradingAnalyzer()
analysis = analyzer.analyze_pair_relationship(df1, df2)

if analysis['correlation'] < 0.7:
    print(f"WARNING: Low correlation {analysis['correlation']:.2f}")
if not analysis['is_cointegrated']:
    print(f"WARNING: Not cointegrated (p={analysis['cointegration_pvalue']:.4f})")

# 3. Run Basic Backtest
print("\nRunning basic backtest...")
integration = PairsBacktestIntegration(
    pair1='EURUSD',
    pair2='GBPUSD',
    account_size=10000,
    risk_pct=0.02,
)

result = integration.run_full_backtest(df1, df2, verbose=True)

# 4. Check Results
print("\nResults:")
print(f"Total Trades: {result.total_trades}")
print(f"Win Rate: {result.win_rate:.1f}%")
print(f"Total P&L: ${result.total_pnl:,.2f}")

# 5. Optimize if Needed
if result.win_rate < 55:
    print("\nOptimizing parameters...")
    opt_results = integration.optimize_parameters(
        df1, df2,
        z_entry_range=(1.8, 2.2, 0.1),
        z_exit_range=(0.4, 0.6, 0.1),
    )

# 6. Export Results
print("\nExporting results...")
integration.export_results_to_csv(result, 'final_backtest')

print("\n✓ Backtest complete!")
```

---

## 🚀 Next Steps

1. **Run the example:**
   ```bash
   python hft/examples/backtest_pairs_trading.py
   ```

2. **Load your own data:**
   ```python
   df1 = pd.read_csv('your_pair1.csv')
   df2 = pd.read_csv('your_pair2.csv')
   
   integration = PairsBacktestIntegration()
   result = integration.run_full_backtest(df1, df2)
   ```

3. **Optimize parameters:**
   ```python
   opt_results = integration.optimize_parameters(df1, df2)
   ```

4. **Compare different pairs:**
   - Test multiple pair combinations
   - Find best performers
   - Deploy top 2-3 combinations

5. **Paper trade:**
   - Use best parameters
   - Trade for 1-2 weeks on demo
   - Verify results match backtest

6. **Live trade:**
   - Start small (0.01 lots)
   - Monitor correlation continuously
   - Exit if correlation drops < 0.5

---

## 📞 Quick Reference

### Most Common Commands:

```python
# Basic backtest
result = integration.run_full_backtest(df1, df2)

# With custom parameters
integration = PairsBacktestIntegration(
    pair1='EURUSD',
    pair2='GBPUSD',
    account_size=10000,
    risk_pct=0.02,
    z_entry=2.0,
    z_exit=0.5,
    z_stop=3.0,
)

# Optimize
opt_results = integration.optimize_parameters(df1, df2)

# Export
integration.export_results_to_csv(result, 'my_results')

# Get pair analysis
analyzer = PairsTradingAnalyzer()
analysis = analyzer.analyze_pair_relationship(df1, df2)
```

---

## ✅ Checklist Before Live Trading

- [ ] Backtest completed (run `backtest_pairs_trading.py`)
- [ ] Win rate > 50% on backtest
- [ ] Correlation > 0.7
- [ ] Cointegrated (p < 0.05)
- [ ] Parameters optimized
- [ ] Results exported
- [ ] Paper traded for 1-2 weeks
- [ ] Metrics match backtest
- [ ] Ready for live trade

---

## 📝 Integration Summary

**Files Added:**
- `hft/utils/pairs_backtest_integration.py` - Main integration
- `hft/examples/backtest_pairs_trading.py` - Ready-to-run examples

**How to Use:**
1. Import `PairsBacktestIntegration`
2. Create instance with pair names
3. Call `run_full_backtest(df1, df2)`
4. Analyze results

**Output:**
- Trade statistics (win rate, P&L, etc.)
- Equity curve
- Individual trades
- Pair analysis

---

**Ready to backtest? → Run `python hft/examples/backtest_pairs_trading.py`**

