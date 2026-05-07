# Pairs Trading Strategy - Complete Implementation Guide

**Trade the RELATIONSHIP between assets, not the price direction**

A comprehensive mean reversion pairs trading system for forex, using statistical arbitrage principles to identify and profit from temporary divergences between correlated currency pairs.

---

## 📚 Quick Links

- **Main Strategy**: [`hft/strategies/pairs_trading_strategy.py`](pairs_trading_strategy.py)
- **Backtest Engine**: [`hft/utils/pairs_backtest_engine.py`](../utils/pairs_backtest_engine.py)
- **Complete Guide**: [`PAIRS_TRADING_GUIDE.py`](PAIRS_TRADING_GUIDE.py)
- **Examples**: 
  - [`hft/examples/pairs_trading_example.py`](../examples/pairs_trading_example.py) - Basic concepts
  - [`hft/examples/run_pairs_trading_complete.py`](../examples/run_pairs_trading_complete.py) - Full working example

---

## 🧠 Core Concept

### The Market Maker's Mindset

Pairs trading is **NOT** about predicting direction. It's about believing:

> **Two related assets temporarily diverge, but eventually come back to equilibrium.**

#### Example:
```
EUR/USD → goes up 50 pips
GBP/USD → stays flat (or goes down)

Result: The spread between them expanded (EUR ↑, GBP →)
       This is an imbalance → creates trading opportunity

Trade: SELL EUR/USD, BUY GBP/USD
Belief: The spread will contract (EUR ↓ and/or GBP ↑)
Profit: Both legs normalize → position makes money on BOTH
```

---

## 🎯 What You're Actually Trading

### NOT the price of EUR/USD or GBP/USD

### YES the spread between them

```
Raw Spread (simple):
  Spread = EURUSD - GBPUSD

Normalized Spread (correct):
  Spread = EURUSD - (β × GBPUSD)
              ↑ hedge ratio balances the movements
```

**Why the hedge ratio (β)?**
- EUR might move 50 pips while GBP moves 80 pips
- Without normalization, equal volumes create directional bias
- β ensures movements are proportionally balanced

---

## 🔬 The Z-Score (Your Trading Engine)

```
Z = (Current_Spread - Mean_Spread) / StdDev_Spread
```

### Interpretation:
- **Z = 0**: Spread is normal (at equilibrium) → NO TRADE
- **Z = ±1**: Spread is 1 std dev away → monitoring
- **Z = ±2**: Spread is 2 std dev away → ENTRY SIGNAL (unusual, mean reversion expected)
- **Z = ±3**: Spread is 3 std dev away → HARD STOP (correlation breakdown warning)

### Trading Decisions:

| Condition | Action | Rationale |
|-----------|--------|-----------|
| **Z > +2.0** | **SELL** Pair1, **BUY** Pair2 | Pair1 overpriced, Pair2 underpriced |
| **Z < -2.0** | **BUY** Pair1, **SELL** Pair2 | Pair1 underpriced, Pair2 overpriced |
| **-0.5 < Z < +0.5** | **CLOSE** (profit taking) | Spread normalized, trade complete |
| **\|Z\| > 3.0** | **STOP LOSS** | Correlation breakdown, hedge failed |

---

## 🎲 Complete Trade Example

### Day 1: Setup
```
EUR/USD: 1.1000
GBP/USD: 1.2700
Spread = 1.1000 - (0.85 × 1.2700) = 0.0205
Z-Score = +0.5 (normal, no trade)
```

### Day 2: Signal Generated
```
EUR/USD: 1.1050 (↑50 pips)
GBP/USD: 1.2700 (flat)
Spread = 1.1050 - (0.85 × 1.2700) = 0.0255 (expanded!)
Z-Score = +2.1 ← ENTRY SIGNAL

Trade Initiated:
  SELL 1 lot EUR/USD @ 1.1050
  BUY 1 lot GBP/USD @ 1.2700
```

### Day 3: Mean Reversion
```
EUR/USD: 1.1020 (↓30 pips)
GBP/USD: 1.2720 (↑20 pips)
Spread = 1.1020 - (0.85 × 1.2720) = 0.0198 (contracted!)
Z-Score = 0.0 ← EXIT SIGNAL

Trade Closed:
  CLOSE EUR/USD @ 1.1020
  CLOSE GBP/USD @ 1.2720
  
Profit:
  EUR: Sold @ 1.1050, Close @ 1.1020 → +30 pips ✓
  GBP: Sent @ 1.2700, Close @ 1.2720 → +20 pips ✓
  
  Total: Both legs profitable because spread reverted!
```

---

## ⚙️ Implementation

### Python Usage

```python
from hft.strategies.pairs_trading_strategy import (
    PairsTradingStrategy,
    PairsTradingAnalyzer
)
from hft.utils.pairs_backtest_engine import PairsBacktestEngine

# Step 1: Create strategy
strategy = PairsTradingStrategy(
    pair1='EURUSD',
    pair2='GBPUSD',
    lookback=100,          # Use last 100 bars for calculations
    z_entry=2.0,           # Entry when Z > ±2.0
    z_exit=0.5,            # Exit when Z < ±0.5 (profit taking)
    z_stop=3.0,            # Hard stop at Z > ±3.0
)

# Step 2: Load OHLC data for both pairs (H1 timeframe)
df_eur = load_data('EURUSD', 'H1', bars=500)
df_gbp = load_data('GBPUSD', 'H1', bars=500)

# Step 3: PRE-TRADE ANALYSIS (MUST DO BEFORE TRADING)
analyzer = PairsTradingAnalyzer()
analysis = analyzer.analyze_pair_relationship(df_eur, df_gbp)

print(f"Correlation: {analysis['correlation']:.3f}")        # Should be > 0.7
print(f"Cointegrated: {analysis['is_cointegrated']}")        # Should be True (p < 0.05)
print(f"Hedge Ratio: {analysis['hedge_ratio']:.3f}")         # Use for position sizing

# Step 4: Generate signals
signals = strategy.generate_signals(df_eur, df_gbp)

# Step 5: Run backtest
backtest_engine = PairsBacktestEngine(
    account_size=10000,
    risk_pct_per_trade=0.02,  # Risk 2% per trade
    pair1_pip_size=0.0001,
    pair2_pip_size=0.0001,
)

results = backtest_engine.backtest(
    signals, df_gbp,
    z_exit_threshold=0.5,
    z_stop_threshold=3.0,
)

print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']}")
print(f"Total P&L: {results['total_pnl']}")
```

---

## 📊 Key Metrics & Interpretation

| Metric | Expected Range | What It Means |
|--------|----------------|---------------|
| **Win Rate** | 60-70% | High win rate (mean reversion) |
| **Avg Win vs Loss** | 1.5-2.0x | Modest profit per trade |
| **Profit Factor** | > 1.5 | Wins exceed losses |
| **Sharpe Ratio** | > 1.0 | Good risk-adjusted returns |
| **Max Drawdown** | < 15% | Manageable downside |
| **Avg Trade Duration** | 10-50 bars | Quick trades (mean reverts fast) |

---

## ⚠️ Critical Prerequisites

### Before Trading Any Pair Combination

1. **Correlation > 0.70**
   - Lower correlation = less reliable relationship
   - Test correlation over 100-bar lookback window

2. **Cointegration (p-value < 0.05)**
   - NOT just correlation, but true long-term relationship
   - Use Engle-Granger test
   - Ensures spread is stationary (mean-reverting)

3. **Volatile Not Explosive**
   - Current volatility < 0.2% (to avoid news impact)
   - Calculate rolling volatility over 20-bar window

4. **Hedge Ratio Stability**
   - β shouldn't change wildly between bars
   - Recalculate every bar (rolling window)
   - If changes > 20% over 10 bars → exit immediately

---

## 🚨 When It FAILS (And Why)

### ❌ Correlation Breakdown

```
Example: Brexit announcement

Before:
  EUR ↑ 100 pips
  GBP ↑ 80 pips
  Correlation: 0.82

After announcement:
  EUR ↑ 100 pips
  GBP ↓ 150 pips (unexpected divergence!)
  Correlation: -0.20

Result:
  Position: Short GBP (+150), Long EUR (+100)
  Expected profit: Yes (GBP stronger than expected)
  Actual: MASSIVE LOSS (both legs go wrong way!)
  
Solution: Hard stop at Z > ±3.0 exits position
```

### ❌ Trending Regime

```
Strong directional trend:
  Spread keeps expanding (doesn't revert)
  Z-score keeps increasing
  Trader keeps adding losing positions
  Account blows up

Check: If 5+ consecutive trades don't exit at Z < 0.5
       → Regime changed, close strategy
```

### ❌ Slippage on Entry

```
Wrong:
  Fill EUR/USD @ 1.1050 ✓
  Try to fill GBP/USD @ 1.2700 but market moved ✗
  Get filled @ 1.2705 (5 pips slippage)
  
Result: Imbalanced entry, directional bias → hedge fails

Solution: Use bracket orders, market orders on both legs SIM
          Or algorithmic execution (VWAP, TWAP)
```

---

## 🎯 Best Practices

### Position Sizing

```python
# Calculate for each trade:
risk_amount = account_balance × 0.02  # 2% risk rule
initial_sl = entry_price - (3.0 × std_dev)  # SL at Z=3
volume_pair1 = risk_amount / (entry_price × pip_size)

# For pair2, scale by hedge ratio:
beta = calculate_hedge_ratio(pair1_prices, pair2_prices)
volume_pair2 = (volume_pair1 × price1) / (price2 × beta)
```

### Entry Management

- ✓ Fill BOTH legs within 1-2 seconds
- ✓ Use same execution type (OCO, bracket, etc.)
- ✗ Never fill one leg alone (creates directional bias)
- ✗ Never chase fills if price moves away

### Exit Management

- **Profit Taking**: Z ≈ 0.5 (spread reverted ~50%)
- **Scaling**: Exit 50% at Z=0.5, 50% at Z=0.2 (more return)
- **Hard Stop**: Z > ±3.0 (correlation breakdown, must exit)
- **Time Stop**: 50 bars without progress (trend likely started)

### Monitoring

After each entry, continuously check:
1. **Correlation**: Should remain > 0.7
2. **Hedge Ratio**: Should remain stable (within 10% of entry)
3. **Spread Movement**: Should start reverting toward mean
4. **Volume**: Dry up when outcome obvious (positive sign)

---

## 📈 Strategy Performance Expectations

### Realistic Numbers

- **Win Rate**: 60-70% (mean reversion is natural)
- **Profit per Trade**: Small (20-50 pips spread compression)
- **Sharpe Ratio**: 1.0-2.0 (depends on pair correlation)
- **Annual Return**: 20-40% with proper sizing
- **Max Drawdown**: 10-15% (manageable with stops)

### Monthly Pattern

- Best months: Stable correlation environments
- Worst months: News-heavy (Fed, ECB announcements)
- Slower in Forex vacation periods (early Jan, Aug)

### Scale Optimization

- Works better with HIGH volume (compound gains)
- Need precise execution for tight spreads
- Algo/MT5 integration helps with consistency

---

## 🔧 Advanced Enhancements

### 1. Multi-Pair Framework

Trade best setup across multiple combinations:
```
Simultaneously analyze:
  EUR/USD vs GBP/USD
  EUR/USD vs AUD/USD
  GBP/USD vs NZD/USD
  
Choose: Highest Z-score + highest correlation combination
```

### 2. Dynamic Thresholds

Instead of fixed Z = ±2.0:
```
Use percentile-based thresholds:
  95th percentile of history Z → entry
  Adapts to changing volatility regime
```

### 3. Volatility-Based Sizing

```
high_vol_period = current_vol > average_vol
trade_size = base_size / vol_multiplier
```

### 4. Machine Learning Enhancement

```
Features: Recent Z-scores, correlation, volatility
Target: Will spread revert within N bars?
Model: Predict probability of success
Trade: Only enter high-probability setups (> 70%)
```

### 5. Correlation Change Detection

```
Alert if:
  Correlation drops > 20% in 10 bars
  Hedge ratio changes > 15% in 10 bars
  Spread std dev increases > 30%
  
Action: Exit immediately, re-analyze relationship
```

---

## 📁 Files & Structure

```
hft/
├── strategies/
│   ├── pairs_trading_strategy.py       ← Main strategy
│   ├── PAIRS_TRADING_GUIDE.py           ← Detailed theory
│   └── ...
├── utils/
│   ├── pairs_backtest_engine.py         ← Backtesting engine
│   └── ...
├── examples/
│   ├── pairs_trading_example.py         ← Basic examples
│   ├── run_pairs_trading_complete.py    ← Full working example
│   └── ...
└── README.md
```

---

## 🚀 Quick Start

### 1. Run the Complete Example

```bash
python hft/examples/run_pairs_trading_complete.py
```

This will:
- Generate realistic paired data
- Perform pre-trade analysis
- Generate signals
- Run full backtest
- Display results

### 2. Test Your Own Data

```python
from hft.strategies.pairs_trading_strategy import PairsTradingStrategy

# Your data
df1 = pd.read_csv('eurusd_h1.csv')
df2 = pd.read_csv('gbpusd_h1.csv')

# Create strategy
strat = PairsTradingStrategy('EURUSD', 'GBPUSD')

# Generate signals
signals = strat.generate_signals(df1, df2)

# Signals now has: signal_pair1, signal_pair2, zscore, spread, etc.
```

### 3. Trade Live (with caution!)

```python
# Step 1: Verify setup
analysis = analyzer.analyze_pair_relationship(df1, df2)
assert analysis['is_cointegrated']
assert analysis['correlation'] > 0.7

# Step 2: Generate signals
signals = strategy.generate_signals(df1, df2)

# Step 3: Execute (your MT5/API code)
if signals['signal_pair1'].iloc[-1] == 1:
    execute_long_pair1()
    execute_short_pair2()
```

---

## 📖 Reading Guide

**Start Here:**
1. Read the "Core Concept" section above
2. Study the "Complete Trade Example"
3. Run `run_pairs_trading_complete.py`

**Deepen Understanding:**
1. Read `PAIRS_TRADING_GUIDE.py` (comprehensive theory)
2. Review `pairs_trading_strategy.py` (code implementation)
3. Study `pairs_backtest_engine.py` (how P&L is calculated)

**Live Trading:**
1. Verify cointegration on your pair
2. Backtest with your risk parameters
3. Start small (0.01 lots)
4. Monitor correlation continuously
5. Exit if correlation drops < 0.5

---

## ❓ FAQ

### Q: Why would I trade this instead of just predicting direction?

**A:** Because mean reversion is reliable and directional prediction is hard.
- 60% win rate from mean reversion > 50% from direction guessing
- High volume of small wins compounds better than rare big wins
- Works in sideways markets (directional trading doesn't)

### Q: What if both pairs go down together?

**A:** That's OK! The hedge protects you:
```
EUR down 100 pips, you're SHORT EUR = +100 profit
GBP down 80 pips, you're LONG GBP = -80 loss
Net: +20 pips profit

The relationship (spread) mattered, not direction!
```

### Q: Can I trade with unequal volumes?

**A:** No. This is critical. Must scale by hedge ratio:
```
volume_pair2 = volume_pair1 × (price1/price2) × (1/beta)

Equal volumes = directional bias = hedge fails
```

### Q: How often do I recalculate the hedge ratio?

**A:** Every bar (rolling window).
```
for each bar:
    window = last 100 bars prices
    beta = calculate_hedge_ratio(pair1, pair2)
    spread = pair1 - (beta × pair2)
    zscore = calculate_zscore(spread)
```

### Q: What if correlation isn't stable?

**A:** Don't trade. Unstable correlation = unreliable hedge.
```python
if analysis['correlation'] < 0.7:
    print("Skip this pair")
    # Find different combination
```

---

## 🎓 Key Takeaways

✓ **Trade relationships, not prices**
- EUR/USD and GBP/USD diverge → profitable opportunity

✓ **Use Z-scores to quantify extremes**
- Z = ±2.0: Entry (unusual condition)
- Z ≈ 0: Exit (normalcy restored)

✓ **Hedging both legs reduces risk**
- Long one, short the other
- Profit from relative movement, not direction

✓ **Mean reversion is natural and reliable**
- Markets oscillate around equilibrium
- Create high-probability trades

✓ **Correlation breakdown is the primary risk**
- Hard stop at Z > ±3.0
- Monitor correlation continuously

✓ **Small wins compound into big returns**
- High win rate × high volume = consistent profit

---

## ⚡ Critical Rules

1. **ALWAYS check cointegration before trading** (p-value < 0.05)
2. **NEVER trade with unequal volumes** (must scale by β)
3. **ALWAYS exit at hard stops** (Z > ±3.0, no exceptions)
4. **ALWAYS execute both legs simultaneously** (avoid imbalance)
5. **ALWAYS monitor correlation ongoing** (exit if < 0.5)

---

## 📧 Support & Questions

For issues or questions:
1. Check `PAIRS_TRADING_GUIDE.py` (comprehensive reference)
2. Run `run_pairs_trading_complete.py` (practical example)
3. Review code comments in `pairs_trading_strategy.py`

---

**Remember: This is statistical arbitrage, not risk-free arbitrage. Correlations can break. Hedge can fail. Always use proper risk management.**

---

*Last Updated: 2025*
*Version: 1.0*
