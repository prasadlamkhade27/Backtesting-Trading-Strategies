# MetaTrader 5 Expert Advisors

This folder contains professional-grade Expert Advisors (EAs) for MetaTrader 5, including high-frequency trading scalping strategies.

## 📁 Files

### **HFTScalpingEA.mq5** ⭐ NEW
**High-Frequency Trading Scalping Expert Advisor**
- **Type**: Scalping, Market Making, Trend Following
- **Timeframes**: M1, M5, M15 (Best on M5)
- **Symbols**: EURUSD, GBPUSD, USDJPY, etc.
- **Features**:
  - Three trading strategy variants
  - Advanced risk management
  - Realistic execution costs
  - Performance logging
  - Dynamic position sizing

**Quick Start**:
1. Copy to `MQL5/Experts` folder
2. Compile in MetaEditor
3. Attach to M5 chart
4. Configure parameters
5. Backtest in Strategy Tester

**Key Parameters**:
```
strategy_type         : SCALPING (1), MARKET_MAKING (2), TREND_FOLLOWING (3)
risk_percent_per_trade: 0.5% (recommended)
ma_fast_period        : 5
ma_slow_period        : 20
max_open_positions    : 3
atr_sl_multiple       : 1.5
atr_tp_multiple       : 0.75
```

**Performance Targets**:
- Win Rate: 55-65%
- Profit Factor: 1.5-2.5
- Monthly Return: 3-5%
- Max Drawdown: 5-15%

### **AdvancedForexEA.mq5**
Advanced Forex trading EA using RSI + Stochastic strategies for higher timeframes (1H, 4H, 1D).

### **MAForexEA.mq5**
Simple moving average crossover strategy for swing trading on forex pairs.

---

## 🚀 Quick Start Guide

### Installation

1. **Open MetaTrader 5**
2. **Navigate to**: File → Open Data Folder
3. **Go to**: MQL5 → Experts
4. **Copy** the `.mq5` file to this folder
5. **Restart MT5** or press F5 to refresh
6. **Open MetaEditor** (Ctrl+Shift+E) and compile

### Attach to Chart

1. **Open a chart** (EURUSD M5 recommended)
2. **Drag EA** from Navigator onto chart, OR
3. **Insert** → **Expert Advisors** → Select EA
4. **Double-click** to open properties
5. **Inputs** tab: Configure parameters
6. **Click OK** to attach

### Backtest

1. **Open Strategy Tester**: Ctrl+R
2. **Select**:
   - Expert: HFTScalpingEA (or your EA)
   - Symbol: EURUSD
   - Timeframe: M5
   - Period: Last 6-12 months
   - Model: "Every Tick" (most realistic)
3. **Click Start** to begin
4. **Review Results** tab for statistics

---

## 📊 Strategy Details

### Scalping Strategy (Default)

**Entry Rules**:
- **BUY**: 
  - Fast MA > Slow MA
  - RSI > 50 and < 70 (not overbought)
  - MACD > 0 (positive momentum)
  - Volume > average
  
- **SELL**:
  - Fast MA < Slow MA
  - RSI < 50 and > 30 (not oversold)
  - MACD < 0 (negative momentum)
  - Volume > average

**Exit Rules**:
- **Take Profit**: Price reaches ATR-based target (0.75×ATR)
- **Stop Loss**: Price hits ATR-based level (1.5×ATR)
- **Trailing**: Moves SL to breakeven after 10 pips profit
- **Time**: Closes at day end if enabled

**Best For**: 
- Liquid pairs (EURUSD, GBPUSD, USDJPY)
- M5 timeframe
- European/US trading sessions
- Tight spreads (<1.5 pips)

### Market Making Strategy

**Entry Rules**:
- Places buy orders at support levels (fast MA -offset)
- Places sell orders at resistance levels (fast MA +offset)
- Only when spread is favorable (<2×ATR)

**Best For**:
- Ranging markets
- Capturing bid-ask spreads
- Two-sided order placement

### Trend Following Strategy

**Entry Rules**:
- **BUY**: Price > Fast MA > Slow MA + RSI > 50 (strong uptrend)
- **SELL**: Price < Fast MA < Slow MA + RSI < 50 (strong downtrend)

**Best For**:
- Trending markets
- Larger profit targets
- Lower trade frequency

---

## ⚙️ Configuration Guide

### Risk Management

```mql5
input double risk_percent_per_trade = 0.5;    // Risk as % (0.3-1.0 recommended)
input int max_consecutive_losses = 5;          // Stop after N losses
input double max_daily_loss_percent = 5.0;     // Close all if loss >5%
input double max_drawdown_percent = 10.0;      // Stop if drawdown >10%
input int max_open_positions = 3;              // Max simultaneous trades
```

### Technical Indicators

```mql5
input int ma_fast_period = 5;                  // Fast MA (3-10 recommended)
input int ma_slow_period = 20;                 // Slow MA (15-30 recommended)
input int rsi_period = 14;                     // RSI momentum indicator
input int rsi_oversold = 30;                   // RSI lower threshold
input int rsi_overbought = 70;                 // RSI upper threshold
```

### Stop Loss & Take Profit

```mql5
input int fixed_sl_pips = 0;                   // 0 = auto ATR-based
input int fixed_tp_pips = 0;                   // 0 = auto ATR-based
input double atr_sl_multiple = 1.5;            // SL = Entry ± 1.5×ATR
input double atr_tp_multiple = 0.75;           // TP = Entry ± 0.75×ATR
```

---

## 📈 Performance Expectations

### Scalping Strategy

| Metric | Conservative | Moderate | Aggressive |
|--------|--------------|----------|-----------|
| Risk % | 0.3% | 0.5% | 1.0% |
| Win Rate | 60-70% | 55-65% | 50-60% |
| Profit Factor | 1.5-2.0 | 1.5-2.5 | 1.3-2.0 |
| Monthly Return | 1-2% | 3-5% | 5-10% |
| Max Drawdown | 5% | 10% | 15% |

### Market Making Strategy

- Win Rate: 65-75% (high probability, small spreads)
- Monthly Return: 2-3% (consistent but smaller)
- Max Drawdown: 3-5% (lower risk)

### Trend Following Strategy

- Win Rate: 45-55% (fewer trades, larger wins)
- Monthly Return: 5-8% (larger per-trade profits)
- Max Drawdown: 10-15% (needs wider stops)

---

## 🛡️ Safety Features

### Built-in Risk Controls

✓ **Position Sizing**: Risk-based lot calculation  
✓ **Stop Loss Protection**: Automatic SL/TP calculation  
✓ **Daily Loss Limit**: Stops trading if daily loss exceeded  
✓ **Drawdown Management**: Tracks and limits account drawdown  
✓ **Consecutive Loss Protection**: Pauses after N losing trades  
✓ **Time Filter**: Can restrict trading hours  
✓ **News Filter**: Can avoid news event times  
✓ **Slippage Control**: Maximum allowed slippage setting  

### Good Trading Practices

1. **Start with small risk** (0.3-0.5%)
2. **Always use stop loss** (never manage manually)
3. **Never override risk limits** (trust the engine)
4. **Monitor first week** (compare to backtest)
5. **Keep records** (track performance daily)
6. **Never use margin** (only what you can afford)
7. **Avoid news events** (high volatility, slippage)
8. **Use demo first** (test before real money)

---

## 📊 Recommended Settings

### For EUR/USD (Most Liquid)

**Conservative**:
```
strategy_type         = SCALPING (1)
risk_percent_per_trade = 0.3
ma_fast_period        = 5
ma_slow_period        = 20
max_open_positions    = 2
atr_sl_multiple       = 1.5
atr_tp_multiple       = 0.5
```

**Moderate** (Recommended):
```
strategy_type         = SCALPING (1)
risk_percent_per_trade = 0.5
ma_fast_period        = 5
ma_slow_period        = 20
max_open_positions    = 3
atr_sl_multiple       = 1.5
atr_tp_multiple       = 0.75
```

**Aggressive**:
```
strategy_type         = SCALPING (1)
risk_percent_per_trade = 1.0
ma_fast_period        = 4
ma_slow_period        = 15
max_open_positions    = 5
atr_sl_multiple       = 1.2
atr_tp_multiple       = 1.0
```

### Best Trading Hours

- **London Session**: 08:00-12:00 UTC (tight spreads, high liquidity)
- **US Session**: 13:00-17:00 UTC (consistent volatility)
- **Overlap**: 12:00-13:00 UTC (most active)
- **Asian Session**: Lower liquidity, wider spreads, avoid for HFT

---

## 🔄 Workflow

### 1. Backtest
```
Backtest on 6-12 months of historical data
Check: Win rate >50%, Profit Factor >1.5, Drawdown <15%
If OK → proceed, If NOT → adjust parameters
```

### 2. Demo Trade
```
Trade on demo for 1-2 weeks
Monitor win rate, average trade size, slippage
Compare to backtest results
If similar → ready for live, If different → investigate
```

### 3. Live Trade
```
Start with small account/risk
Monitor daily and weekly metrics
Compare live vs backtest performance
Document all PnL
After 1 month of consistent profits → increase size gradually
```

---

## 🐛 Troubleshooting

### EA won't compile
- Check MQL5 syntax
- Verify all includes present
- Use MetaEditor compile (F5)

### No trades are executing
- Check signal generation (add Print statements)
- Verify MA values are calculating
- Check RSI/MACD indicators
- Ensure spread is not too wide

### Too much slippage
- Reduce position size
- Change broker (try ECN)
- Trade during peak hours
- Avoid major news events

### Losing trades
- Backtest on latest data
- Adjust parameters
- Check market regime (ranging vs trending)
- Lower risk % temporarily

### EA keeps restarting
- Check for compilation errors
- Verify indicator handles created
- Check OnInit() return value

---

## 📚 Learning Resources

### Technical Indicators
- **MA Crossover**: Trend identification
- **RSI**: Momentum, overbought/oversold
- **MACD**: Trend confirmation
- **ATR**: Dynamic position sizing

### Risk Management
- Position sizing formulas
- Stop loss placement
- Take profit optimization
- Account risk limits

### Backtesting
- Strategy Tester overview
- Optimization basics
- Result interpretation
- Forward testing

---

## ⚠️ Important Disclaimers

- **Past performance** does not guarantee future results
- **Always test thoroughly** before live trading
- **Trading carries risk** of total loss
- **Use demo accounts** first
- **Start with small capital** you can afford to lose
- **Monitor manually** especially during first week
- **Never override** risk management limits
- **Keep stop losses** always active

---

## 📋 Backtest Checklist

Before deploying any EA to live trading:

- [ ] Backtested ≥6 months historical data
- [ ] Win rate ≥50%
- [ ] Profit factor ≥1.5
- [ ] Max drawdown ≤15%
- [ ] Sharpe ratio ≥1.0
- [ ] Demo tested 1-2 weeks
- [ ] Live results match backtest
- [ ] Risk management activated
- [ ] All parameters documented
- [ ] Emergency contact plan ready

---

## 🔗 Related Files

- **Strategy Code**: `/strategies/hft_scalping_strategy.py` (Python version)
- **Backtesting**: `/utils/hft_backtest_engine.py` (Python backtest)
- **Examples**: `/HFT_TRADING_EXAMPLE.py` (Code examples)
- **Documentation**: `/HFT_SYSTEM_README.md` (Complete guide)
- **Config Presets**: `/hft_config.py` (Ready-made configurations)

---

## 📞 Support

For issues or questions:
1. Review parameter descriptions in EA code comments
2. Check MT5 logs for errors
3. Backtest with simple parameters first
4. Gradually add complexity
5. Monitor trade execution manually

---

**Version**: 1.5 (HFT Compatible)  
**Last Updated**: 2025  
**Status**: Production Ready  
**Best Timeframe**: M5  
**Best Symbol**: EURUSD
