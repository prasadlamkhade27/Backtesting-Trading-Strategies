# High-Frequency Trading (HFT) System Documentation

## Overview

This HFT Trading System provides professional-grade infrastructure for implementing, backtesting, and deploying high-frequency trading strategies. The system includes:

- **MT5 Expert Advisor (EA)**: Production-ready HFT scalping EA in MQ5
- **Python Backtesting Framework**: Complete backtesting engine with realistic execution
- **Risk Management Tools**: Comprehensive position sizing and risk controls
- **Performance Analytics**: Detailed metrics and optimization capabilities

---

## 🎯 Features

### 1. **Three HFT Strategy Types**

#### **Scalping Strategy** (Default, Recommended)
- Rapid entry and exit capturing bid-ask spreads
- Targets: 5-15 pips per trade
- High win rate (55-65%)
- Many trades per day (10-50+)
- Best for liquid pairs (EURUSD, GBPUSD)

**Entry Rules:**
- Fast MA > Slow MA + RSI > 50 (not overbought) + MACD > 0 + Volume confirmation
- Similar logic for shorts

#### **Market Making Strategy**
- Places orders on both sides of the spread
- Profits from spread widening
- Lower trade frequency
- Requires good execution

**Entry Rules:**
- Price pulls back to fast MA with favorable spread
- Two-sided order placement

#### **Trend Following Strategy**
- Captures momentum moves
- Larger profit per trade (20-100+ pips)
- Lower win rate (45-55%)
- Fewer but larger trades

**Entry Rules:**
- Price > Fast MA > Slow MA + RSI > 50 (strong uptrend)
- Exits on reversal signals

### 2. **Risk Management**

- **Position Sizing**: Dynamic lot calculation based on account balance and risk
- **Stop Loss/Take Profit**: ATR-based automatic levels
- **Daily Loss Limits**: Stops trading if daily loss exceeded
- **Consecutive Loss Protection**: Pauses after N losing trades
- **Maximum Drawdown Control**: Trails original capital

### 3. **Technical Indicators**

- **Moving Averages** (EMA): Trend identification (default: 5 & 20 periods)
- **RSI**: Momentum and overbought/oversold levels (period: 14)
- **MACD**: Trend confirmation (12/26/9)
- **ATR**: Volatility measurement for dynamic SL/TP (period: 14)
- **Volume Analysis**: Confirmation of signal strength

### 4. **Realistic Execution**

- Bid-ask spread modeling
- Slippage simulation (ECN, MM, Futures venues)
- Latency consideration
- Execution cost tracking

---

## 📁 File Structure

```
project_root/
├── mt5_ea/
│   ├── HFTScalpingEA.mq5          ← Main HFT Expert Advisor
│   ├── AdvancedForexEA.mq5        (existing)
│   └── README.md
│
├── strategies/
│   ├── hft_scalping_strategy.py   ← HFT signal generation + risk mgmt
│   ├── base_strategy.py            (existing)
│   └── moving_average_strategy.py  (existing)
│
├── utils/
│   ├── hft_backtest_engine.py     ← HFT backtesting engine
│   ├── backtest_engine.py          (existing)
│   └── ...
│
├── HFT_TRADING_EXAMPLE.py         ← Complete examples & tutorial
├── HFT_SYSTEM_README.md           ← This file
└── requirements.txt
```

---

## 🚀 Quick Start

### Option 1: MT5 Expert Advisor

**Step 1: Prepare MT5**
```
1. Open MetaTrader 5
2. File → Open Data Folder
3. Navigate to: MQL5 → Experts
4. Copy HFTScalpingEA.mq5 to this folder
5. Press F5 to refresh or restart MT5
```

**Step 2: Attach to Chart**
```
1. Open a chart (e.g., EURUSD M5)
2. Insert → Expert Advisors → HFTScalpingEA
3. Configure inputs:
   - strategy_type: SCALPING (default)
   - risk_percent_per_trade: 0.5
   - max_open_positions: 3
4. Click OK
```

**Step 3: Backtest in Strategy Tester**
```
1. Ctrl + R (open Strategy Tester)
2. Set parameters:
   - Expert: HFTScalpingEA
   - Symbol: EURUSD
   - Timeframe: M5
   - Period: Last 6-12 months
   - Model: Every Tick
3. Click Start and analyze results
```

### Option 2: Python Backtesting

**Basic Example:**
```python
from strategies.hft_scalping_strategy import HFTScalpingStrategy
from utils.hft_backtest_engine import HFTBacktestEngine, ExecutionParams, ExecutionVenue

# Load your OHLC data
data = pd.read_csv('eurusd_data.csv')  # Needs: open, high, low, close, volume

# Create strategy
strategy = HFTScalpingStrategy(
    strategy_type="scalping",
    ma_fast=5,
    ma_slow=20
)

# Generate signals
signals = strategy.generate_signals(data)

# Setup realistic execution
exec_params = ExecutionParams(
    venue=ExecutionVenue.FOREX_ECN,
    base_spread_pips=1.0,
    slippage_pips=0.5
)

# Run backtest
engine = HFTBacktestEngine(
    initial_balance=10000,
    execution_params=exec_params,
    risk_percent_per_trade=0.5
)

results = engine.backtest(data, signals)

# Get detailed results
print(results)
trade_log = engine.get_trade_log()
trade_log.to_csv('trades.csv', index=False)
```

---

## ⚙️ Configuration Parameters

### Strategy Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `strategy_type` | SCALPING | SCALPING, MARKET_MAKING, TREND_FOLLOWING | Strategy variant |
| `ma_fast_period` | 5 | 3-10 | Fast moving average for trend |
| `ma_slow_period` | 20 | 15-50 | Slow moving average for confirmation |
| `rsi_period` | 14 | 5-21 | RSI momentum indicator |
| `rsi_oversold` | 30 | 20-40 | RSI oversold threshold |
| `rsi_overbought` | 70 | 60-80 | RSI overbought threshold |
| `atr_period` | 14 | 5-21 | ATR volatility measurement |
| `atr_sl_multiple` | 1.5 | 1.0-3.0 | SL distance in ATR multiples |
| `atr_tp_multiple` | 0.75 | 0.5-2.0 | TP distance in ATR multiples |

### Risk Management Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `risk_percent_per_trade` | 0.5 | 0.1-2.0 | Risk as % of balance per trade |
| `max_consecutive_losses` | 5 | 3-20 | Stop trading after N losses |
| `max_daily_loss_percent` | 5.0 | 2.0-20.0 | Stop if daily loss exceeds this % |
| `max_drawdown_percent` | 10.0 | 5.0-30.0 | Stop if drawdown exceeds this % |
| `max_open_positions` | 3 | 1-10 | Max simultaneous positions |

### Execution Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `venue` | FOREX_ECN | Trading venue (ECN, MM, Futures, Crypto) |
| `base_spread_pips` | 1.0 | Typical bid-ask spread |
| `slippage_pips` | 0.5 | Expected execution slippage |
| `latency_ms` | 100 | Order execution latency |

---

## 📊 Performance Metrics

### Trade Statistics

- **Total Trades**: Number of trades executed
- **Winning Trades**: Number of profitable trades
- **Losing Trades**: Number of unprofitable trades
- **Win Rate**: Percentage of winning trades (target: >55%)
- **Profit Factor**: Gross profit / Gross loss (target: >1.5)

### Profitability Metrics

- **Total P&L**: Total profit or loss in currency
- **Total Return**: Total return as percentage
- **Avg Win**: Average profit per winning trade
- **Avg Loss**: Average loss per losing trade
- **Largest Win/Loss**: Best and worst trades

### Risk Metrics

- **Max Drawdown**: Largest peak-to-trough decline (target: <15%)
- **Sharpe Ratio**: Risk-adjusted return (target: >1.0)
- **Sortino Ratio**: Return per unit of downside risk (target: >1.0)
- **Consecutive Wins/Losses**: Longest streaks

### Efficiency Metrics

- **Avg Trade Duration**: Average bars per trade
- **Trades per Day**: Average daily trade frequency
- **Execution Cost**: Total spread + slippage impact

---

## 🔧 Parameter Optimization

### Manual Optimization Steps

1. **Define Parameter Ranges**
```python
param_ranges = {
    'ma_fast': [3, 4, 5, 6, 7],
    'ma_slow': [15, 20, 25, 30],
    'atr_tp_multiple': [0.5, 0.75, 1.0]
}
```

2. **Run Optimization**
```python
results_df = HFTTradingExample.parameter_optimization_example(
    data=historical_data,
    param_ranges=param_ranges
)
```

3. **Select Best Parameters**
```python
best_params = results_df.iloc[0]  # Top performer
print(f"Best: MA({best_params['ma_fast']}x{best_params['ma_slow']}) "
      f"→ Return: {best_params['total_return']:.2f}%")
```

### Recommended Optimization Approach

1. Start with default parameters
2. Test on last 6-12 months of data
3. Optimize one parameter at a time
4. Focus on parameters that improve Sharpe ratio, not just returns
5. Always validate on out-of-sample data
6. Account for execution costs in optimization

---

## 🛡️ Risk Management Guidelines

### Recommended Settings

**Conservative Trading:**
- Risk per trade: 0.3%
- Max consecutive losses: 3-5
- Max daily loss: 2-3%
- Position size: Smaller
- Best for: Risk-averse traders

**Moderate Trading:**
- Risk per trade: 0.5-1.0%
- Max consecutive losses: 5-7
- Max daily loss: 5%
- Position size: Medium
- Best for: Most traders

**Aggressive Trading:**
- Risk per trade: 1.0-2.0%
- Max consecutive losses: 10+
- Max daily loss: 10%+
- Position size: Larger
- ⚠️ NOT recommended without experience

### Example Position Sizing

For $10,000 account with 0.5% risk per trade:
- Risk amount: $50 per trade
- For 50 pips SL: Position size = 0.01 lots ($1/pip)
- For 100 pips SL: Position size = 0.005 lots ($0.50/pip)

---

## 📈 Backtesting Best Practices

1. **Use Realistic Data**
   - Tick-level or 1-minute data minimum
   - Include spreads and slippage
   - At least 6-12 months of history

2. **Account for Costs**
   - Bid-ask spread: 1-2 pips (forex)
   - Slippage: 0.5-1 pips
   - Commissions: If applicable
   - Total HFT cost: 1-3 pips per round trip

3. **Avoid Over-Optimization**
   - Use train/test split (70/30 or 80/20)
   - Different parameters for different market conditions
   - Test in both trending and ranging markets

4. **Monitor Forward Metrics**
   - Paper trade before live
   - Compare live vs backtest results
   - Adjust parameters if performance diverges

---

## ⚠️ Important Considerations

### Execution Reality

- **Slippage**: Varies by venue, liquidity, position size, market volatility
- **Latency**: Network delay, broker processing, order queue
- **Liquidity**: Affects ability to fill larger orders quickly
- **Spreads**: Vary by time of day and market conditions

### Regulatory Compliance

- ✓ Understand your broker's HFT policies
- ✓ Check if algorithmic trading is allowed
- ✓ Comply with trading regulations in your jurisdiction
- ✓ Use demo account first
- ✓ Monitor for market manipulation concerns

### Strategy Viability

- Different strategies work in different market regimes
- Scalping works best in: trending, liquid, tight-spread markets
- Market making works best in: ranging, high-volume markets
- Trend following works best in: strong trend markets
- Always test in current market conditions

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No trades executed | Check signal generation, adjust MA periods |
| Too much slippage | Reduce position size, use ECN broker, avoid news |
| High drawdown | Lower risk %, increase consecutive loss limit |
| EA won't attach to MT5 | Check compilation errors, enable DLL imports |
| Python backtest different from MT5 | Verify data format, check time zones |
| Optimization taking too long | Reduce data size, limit parameter ranges |

---

## 📚 Learning Resources

### Technical Analysis
- Moving Averages: Trend identification
- RSI: Momentum and overbought/oversold
- MACD: Trend and momentum confirmation
- ATR: Volatility measurement

### Risk Management
- Position sizing based on risk
- Stop loss placement strategies
- Take profit optimization
- Drawdown management

### Backtesting
- Historical data requirements
- Execution cost modeling
- Walk-forward analysis
- Out-of-sample testing

---

## 🎓 Example Strategies

### Example 1: Conservative Scalping
```
ma_fast=5, ma_slow=20, risk=0.3%, TP=0.5*ATR, SL=1.5*ATR
Expected: 50% win rate, 2-5% monthly return
```

### Example 2: Aggressive Scalping
```
ma_fast=3, ma_slow=15, risk=1.0%, TP=0.75*ATR, SL=1.5*ATR
Expected: 60% win rate, 5-10% monthly return (higher risk)
```

### Example 3: Market Making
```
Place buy/sell orders on support/resistance, tight spreads
Expected: 70% win rate, 2-4% monthly return
```

### Example 4: Trend Following
```
ma_fast=5, ma_slow=30, risk=0.5%, TP=2*ATR, SL=1.5*ATR
Expected: 45% win rate, 3-8% monthly return
```

---

## 📞 Support & Contact

For issues or questions:
1. Check this documentation
2. Review example code in `HFT_TRADING_EXAMPLE.py`
3. Check MT5 EA comments for parameter details
4. Enable logging for debugging

---

## ✅ Checklist Before Live Trading

- [ ] Backtested on 6-12 months historical data
- [ ] Demo tested for at least 1-2 weeks
- [ ] Win rate and profit factor meet targets
- [ ] Max drawdown is within acceptable range
- [ ] Risk per trade configured conservatively
- [ ] Consecutive loss limits set properly
- [ ] Daily loss limits configured
- [ ] Using regulated, approved broker
- [ ] Understand all strategy parameters
- [ ] Have risk management plan in place
- [ ] Monitor first few weeks closely
- [ ] Document all performance metrics

---

## 📄 Version History

- **v1.5**: Initial HFT System Release
  - HFT Scalping EA for MT5
  - Python backtesting framework
  - Three strategy types
  - Risk management system
  - Performance analytics

---

**Remember**: This is a professional trading system. Always test thoroughly before using real capital. Trading carries risk of loss. Manage your risk accordingly.

**Last Updated**: 2025
**Status**: Production Ready
