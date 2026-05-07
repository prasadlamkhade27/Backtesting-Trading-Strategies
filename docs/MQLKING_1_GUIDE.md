# 🧭 MQL KING 1 - Professional SMC HFT System

## Overview

**MQL King 1** is a high-frequency trading strategy for XAUUSD M1 timeframe built on **Smart Money Concepts (SMC)** and advanced price action analysis.

### Files Created:
1. **MQL_King_1.mq5** - MetaTrader 5 Expert Advisor
2. **mql_king_1_backtester.py** - Python backtesting framework

---

## 🎯 Strategy Summary

### Core Logic (8-Step Process)

```
INPUT: OHLC Price Data (M1)
  ↓
[1] DETECT MARKET STRUCTURE (HH/HL/LH/LL)
  ↓
[2] DETECT BREAK OF STRUCTURE (BOS)
  ↓
[3] MAP LIQUIDITY ZONES (Equal highs/lows)
  ↓
[4] IDENTIFY ORDER BLOCKS (High-quality entry zones)
  ↓
[5] DETECT FAIR VALUE GAPS (Imbalances to fill)
  ↓
[6] CONFIRM DISPLACEMENT (Strong impulse candles)
  ↓
[7] FIND ENTRY POINT (OB retest / FVG fill / Liquidity sweep)
  ↓
[8] EXECUTE TRADE
  ↓
OUTPUT: Trade with SL/TP levels
```

### Entry Signals (3 Options)

1. **Order Block Retest**
   - Price returns to test order block after displacement
   - Best for scalping with tight stops

2. **FVG Fill**
   - Price fills fair value gap (imbalance)
   - Strong trend continuation

3. **Liquidity Sweep + Reversal**
   - Equal highs/lows taken + reversal
   - Mean reversion opportunity

### Risk Management

- **Risk Per Trade:** 0.5% - 1%
- **Risk/Reward Ratio:** Minimum 1:2, Maximum 1:3
- **Max Trades/Day:** 5
- **Stop Loss:** Below/above liquidity level (ATR-adjusted)
- **Take Profit:** Next liquidity zone (ATR multiple)
- **Daily Loss Limit:** 3%

---

## 📊 MQL5 EA Setup

### Installation

1. **Copy file to MetaTrader folder:**
   ```
   C:\Users\[YourUsername]\AppData\Roaming\MetaQuotes\Terminal\[TerminalID]\MQL5\Experts\
   ```

2. **Open MetaEditor** (in MetaTrader 5)
   - File → Open → MQL_King_1.mq5
   - Compile (F7)

3. **Attach to Chart**
   - Open XAUUSD chart (M1 timeframe)
   - Drag MQL_King_1 EA onto chart
   - Review input parameters
   - Click OK to start

### Key Input Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **StructureLookback** | 10 | Bars for HH/HL/LH/LL detection |
| **OrderBlockLookback** | 5 | Bars for OB detection |
| **FVGMinGapPercent** | 0.01 | Minimum FVG size (%) |
| **DisplacementThreshold** | 2.0 | Min impulse (ATR multiplier) |
| **RiskPercent** | 0.5 | Risk per trade (%) |
| **MinRiskRewardRatio** | 1.5 | Minimum 1:1.5 RR |
| **MaxRiskRewardRatio** | 3.0 | Maximum 1:3 RR |
| **MaxTradesPerDay** | 5 | Daily trade limit |
| **LondonOpenHour** | 8 | London Open (GMT) |
| **NYOpenHour** | 13 | NY Open (GMT) |
| **UseSessionFilter** | true | Trade only London/NY sessions |

### Recommended Settings

**Conservative (High Winrate):**
```
StructureLookback: 15
DisplacementThreshold: 2.5
MinRiskRewardRatio: 2.0
MaxTradesPerDay: 3
RiskPercent: 0.3%
```

**Aggressive (More Trades):**
```
StructureLookback: 8
DisplacementThreshold: 1.5
MinRiskRewardRatio: 1.3
MaxTradesPerDay: 10
RiskPercent: 1.0%
```

---

## 🐍 Python Backtester Usage

### Installation

```bash
pip install pandas numpy matplotlib
```

### Basic Usage

```python
from hft.utils.mql_king_1_backtester import MQLKing1Backtester
import pandas as pd

# 1. Load XAUUSD M1 data (example: from CSV)
ohlc_data = pd.read_csv('xauusd_m1.csv')

# Required columns: time, open, high, low, close, volume

# 2. Initialize backtester with parameters
backtester = MQLKing1Backtester(
    ohlc_data,
    structure_lookback=10,
    min_structure_ratio=1.2,
    risk_percent=0.5,
    min_rr_ratio=1.5,
    max_rr_ratio=3.0,
    initial_balance=10000
)

# 3. Run backtest
results = backtester.backtest()

# 4. Export results
backtester.export_trades('trades.csv')
backtester.plot_equity('equity_curve.png')

# 5. Access results
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Net Profit: ${results['net_profit']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

### Understanding Results

```
BACKTEST RESULTS
───────────────────────────────────────
Total Trades:         45
Closed Trades:        44
Winning Trades:       28 (63.64%)
Losing Trades:        16
────────────────────────────────────────
Gross Profit:         $2,450.50
Gross Loss:          -$980.25
Net Profit:           $1,470.25
────────────────────────────────────────
Initial Balance:      $10,000.00
Final Equity:         $11,470.25
ROI:                  14.70%
Max Drawdown:         8.53%
════════════════════════════════════════
```

**Key Metrics to Monitor:**
- **Win Rate > 55%:** Profitable strategy
- **ROI > 2% per day:** Sustainable return
- **Max Drawdown < 15%:** Acceptable risk
- **Profit Factor > 2.0:** Good edge

### Loading Real Data

```python
# Option 1: From MetaTrader Export (CSV)
df = pd.read_csv('exported_data.csv')

# Option 2: Via MetaAPI (real-time data)
import requests

def get_m1_data(pair='XAUUSD', days=7):
    # Connect to your data provider
    # Return DataFrame with columns: time, open, high, low, close, volume
    pass

# Option 3: From your broker's API
from your_broker_api import get_quotes
df = get_quotes('XAUUSD', '2024-01-01', '2024-01-31', timeframe='M1')
```

---

## 🔧 Optimization Guide

### Test These Parameters

```python
# Test different structure lookback periods
for lookback in [5, 10, 15, 20]:
    backtester = MQLKing1Backtester(
        data,
        structure_lookback=lookback
    )
    results = backtester.backtest()
    print(f"Lookback {lookback}: {results['win_rate']:.2f}%")

# Test different RR ratios
for min_rr in [1.3, 1.5, 2.0, 2.5]:
    backtester = MQLKing1Backtester(
        data,
        min_rr_ratio=min_rr
    )
    results = backtester.backtest()
    print(f"Min RR {min_rr}: {results['net_profit']:.2f}")

# Test session filters
for use_session in [True, False]:
    backtester = MQLKing1Backtester(
        data,
        use_session_filter=use_session
    )
    results = backtester.backtest()
    print(f"Session Filter {use_session}: {results['final_equity']:.2f}")
```

---

## ⚠️ Important Warnings

### Before Live Trading

1. **Backtest on 3+ months of data** - Use at least 100+ trades
2. **Forward test** - Run on fresh data not used in optimization
3. **Drawdown planning** - Expect 20-30% drawdown in real trading
4. **News filter** - Add calendar event filter for major economic news
5. **Spread consideration** - Account for broker spreads in backtest
6. **Slippage** - Add 1-2 pips slippage to entry/exit

### Common Pitfalls

❌ **Don't:**
- Trade before London/NY opens (low liquidity)
- Ignore max drawdown limits
- Over-optimize on limited data
- Skip news events
- Trade during Asian hours (choppy)

✅ **Do:**
- Trade within sessions (best execution)
- Use position sizing correctly
- Monitor account drawdown daily
- Keep logs of all trades
- Update parameters monthly

---

## 📈 Expected Performance

Based on professional SMC traders:

| Metric | Realistic | Optimistic |
|--------|-----------|-----------|
| Win Rate | 55-65% | 60-70% |
| Monthly ROI | 2-5% | 5-10% |
| Profit Factor | 1.8-2.5 | 2.5-4.0 |
| Max Drawdown | 10-20% | 5-15% |
| Trades/Month | 20-40 | 40-80 |

---

## 🆘 Troubleshooting

### No trades generated?
- ✓ Check data quality (no gaps)
- ✓ Increase LiquidityMemory parameter
- ✓ Lower DisplacementThreshold
- ✓ Reduce MinRiskRewardRatio

### Too many false signals?
- ✓ Increase StructureLookback
- ✓ Require stronger displacement
- ✓ Add confirmation indicators
- ✓ Enable session filter

### High drawdown?
- ✓ Reduce RiskPercent (0.3-0.5%)
- ✓ Increase StopLoss buffer
- ✓ Strict session filter only
- ✓ Reduce MaxOpenTrades to 1

---

## 📚 Reference: SMC Concepts

### Market Structure
- **HH (Higher High):** New high above previous high
- **HL (Higher Low):** New low above previous low
- **LH (Lower High):** New high below previous high
- **LL (Lower Low):** New low below previous low

### Liquidity
- **Equal Highs:** Multiple touches of same level (resistance)
- **Equal Lows:** Multiple touches of same level (support)
- **Imbalance:** Rapid movement leaves price gaps

### Order Blocks
- **Bullish OB:** Strong bearish candle before bullish move
- **Bearish OB:** Strong bullish candle before bearish move
- **Uses:** Smart money enters/exits at OBs

### Fair Value Gaps (FVG)
- **Bullish FVG:** Gap up (price skips range)
- **Bearish FVG:** Gap down
- **Trading:** Price usually fills gaps

---

## 🎓 Next Steps

1. **Paper trade** for 1-2 weeks
2. **Backtest on 3 markets** (XAUUSD, EURUSD, GBPUSD)
3. **Add alerts** (Discord/Telegram)
4. **Create dashboard** (equity tracking)
5. **Optimize for your broker** (spreads, commission)

---

## 📞 Support

For issues:
1. Check console for error messages
2. Verify data format (OHLCV)
3. Review input parameters
4. Test with sample data first
5. Check terminal logs (MQL5)

---

**Last Updated:** April 2024  
**Version:** 1.0  
**Status:** ✅ Ready for Testing

Good luck! 🚀
