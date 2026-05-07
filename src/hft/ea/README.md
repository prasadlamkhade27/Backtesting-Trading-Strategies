# MT5 Expert Advisors Setup Guide

## Overview
This folder contains 2 professional-grade MT5 Expert Advisors (EAs) converted from your Python trading strategies:

1. **AdvancedForexEA.mq5** - RSI + Stochastic + Support/Resistance Strategy
2. **MAForexEA.mq5** - Moving Average Crossover Strategy

---

## Installation Steps for MetaTrader 5

### Step 1: Locate Your MT5 Experts Folder
- **Windows**: `C:\Users\[YourUsername]\AppData\Roaming\MetaQuotes\Terminal\[TerminalNumber]\MQL5\Experts`
- **Alternative**: In MT5 → File → Open Data Folder → MQL5 → Experts

### Step 2: Copy EA Files
1. Copy both `.mq5` files from this folder (`mt5_ea/`)
2. Paste them into your MT5 `Experts` folder

### Step 3: Compile the EAs
1. Open **MetaEditor** (Tools → Edit Script in MT5)
2. Open each `.mq5` file
3. Press **F5** or File → Compile
4. If successful, you'll see "Compilation finished successfully"
5. ⚠️ **Important**: The EA must compile without errors to use it

### Step 4: Add to MT5 Navigator
1. Refresh MT5 (F5 key or restart MT5)
2. Navigator Panel (Ctrl+N) → Expert Advisors
3. You should see both EAs listed:
   - Advanced Forex EA
   - MA Forex EA

---

## How to Attach an EA to a Chart

### Method 1: Drag and Drop
1. Open your desired chart (e.g., EURUSD, 1H timeframe)
2. In Navigator → Expert Advisors → Right-click the EA → Drag to your chart

### Method 2: Insert EA via Terminal
1. Right-click on the chart → Attach Expert Advisor
2. Select the EA from the list
3. Configure settings (see below)
4. Click OK

---

## EA Configuration Settings

### AdvancedForexEA.mq5 Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **EA_NAME** | Advanced Forex EA | Identifier name |
| **tradeDirection** | BOTH_DIRECTIONS | 1=Both, 2=Long Only, 3=Short Only |
| **riskPercent** | 1.0 | Risk % per trade (1-2% recommended) |
| **rsi_period** | 14 | RSI calculation period |
| **rsi_oversold** | 30 | RSI oversold level for buy signals |
| **rsi_overbought** | 70 | RSI overbought level for sell signals |
| **stoch_k_period** | 14 | Stochastic K period |
| **stoch_d_period** | 3 | Stochastic D period |
| **stoch_smooth** | 3 | Stochastic smoothing |
| **use_fixed_lot** | false | Use fixed lot size instead of risk-based |
| **fixed_lot_size** | 0.1 | Fixed lot size (if enabled) |
| **max_dd_percent** | 10.0 | Max drawdown before stopping trades |
| **use_trading_hours** | false | Enable specific trading hours |
| **start_hour** | 9 | Trading start hour (0-23) |
| **end_hour** | 17 | Trading end hour (0-23) |

### MAForexEA.mq5 Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **EA_NAME** | MA Crossover EA | Identifier name |
| **tradeDirection** | BOTH_DIRECTIONS | 1=Both, 2=Long Only, 3=Short Only |
| **riskPercent** | 1.0 | Risk % per trade |
| **fast_ma_period** | 5 | Fast MA period |
| **slow_ma_period** | 20 | Slow MA period |
| **ma_method** | MODE_SMA | MA type (SMA, EMA, WMA, etc) |
| **filter_rsi** | true | Enable RSI filter for entry signals |
| **rsi_period** | 14 | RSI period for filter |
| **rsi_overbought** | 70 | RSI overbought level |
| **rsi_oversold** | 30 | RSI oversold level |
| **atr_sl_multiplier** | 1.5 | ATR multiplier for stop loss |
| **atr_tp_multiplier** | 3.0 | ATR multiplier for take profit |
| **use_fixed_lot** | false | Use fixed lot size |
| **fixed_lot_size** | 0.1 | Fixed lot size (if enabled) |
| **max_dd_percent** | 10.0 | Max drawdown % before stopping |

---

## Recommended Settings by Strategy

### AdvancedForexEA (RSI + Stochastic)
**Best for**: XAUUSD, EURUSD, GBPUSD, USDJPY
**Recommended timeframes**: 1H, 4H, Daily
**Suggested settings**:
```
- tradeDirection: BOTH_DIRECTIONS
- riskPercent: 1.0
- rsi_oversold: 30
- rsi_overbought: 70
- max_dd_percent: 10.0
- use_trading_hours: true (9-17)
```

### MAForexEA (Moving Average Crossover)
**Best for**: Any forex pair, trending markets
**Recommended timeframes**: 1H, 4H, Daily, Weekly
**Suggested settings**:
```
- tradeDirection: BOTH_DIRECTIONS
- riskPercent: 1.0
- fast_ma_period: 5
- slow_ma_period: 20
- filter_rsi: true
- max_dd_percent: 10.0
```

---

## Trading Rules & Entry/Exit Conditions

### AdvancedForexEA Entry Signals

**BUY Signal (when all conditions met)**:
1. RSI < 30 (oversold) + Stochastic bullish crossover + Higher low pattern
2. RSI < 40 + Stochastic bullish crossover + Stochastic K < 20
3. RSI rising + RSI < 50 + Stochastic bullish crossover + Price near support

**SELL Signal (when all conditions met)**:
1. RSI > 70 (overbought) + Stochastic bearish crossover + Lower high pattern
2. RSI > 60 + Stochastic bearish crossover + Stochastic K > 80
3. RSI falling + RSI > 50 + Stochastic bearish crossover + Price near resistance

**Exit Rules**:
- Stop Loss: 1.5x ATR
- Take Profit: 2-3x ATR (1:2 to 1:3 Risk/Reward)

### MAForexEA Entry Signals

**BUY Signal**:
- Fast MA crosses ABOVE Slow MA
- Optional RSI filter: RSI < 70 (not overbought)
- No existing long position

**SELL Signal**:
- Fast MA crosses BELOW Slow MA
- Optional RSI filter: RSI > 30 (not oversold)
- No existing short position

**Exit Rules**:
- Stop Loss: 1.5x ATR
- Take Profit: 3x ATR (1:2 Risk/Reward)
- Auto-close opposite signals (bearish crossover closes long position)

---

## Important Notes

### ⚠️ Critical Settings
1. **Lot Size**: Start with `use_fixed_lot = true` and `fixed_lot_size = 0.1` for testing
2. **Risk Management**: Set `max_dd_percent` to limit maximum losses
3. **Trading Hours**: Enable to avoid low-liquidity times
4. **Magic Number**: Each EA has a unique magic number (123456 and 789456) - DO NOT CHANGE

### ✅ Best Practices
- Always backtest before live trading
- Start with demo/paper trading for 1-2 weeks
- Never use `riskPercent > 2%` per trade
- Run on liquid pairs: EURUSD, GBPUSD, USDJPY, XAUUSD
- Use 4H or 1D timeframes for better accuracy
- Monitor the EA's performance regularly

### ⚡ Troubleshooting
- **EA not showing in Navigator**: Check if MT5 is running in "Run" mode (requires compilation)
- **No trades triggered**: Check timeframe and pair compatibility
- **Compilation errors**: Ensure `#include <Trade\Trade.mqh>` library is available
- **Check Experts tab**: EA status shows in the Experts tab of the Terminal window

---

## Performance Monitoring

### Check EA Status
1. Open MT5 Terminal
2. Go to **Experts** tab
3. You'll see EA logs showing:
   - Entry signals triggered
   - Order placement status
   - Take profit/stop loss levels
   - Any errors encountered

### Key Metrics to Monitor
- Win Rate: Target >50% for profitable strategies
- Average Risk/Reward: Aim for 1:2 or better
- Drawdown: Keep below 10-15% of account
- Number of trades: More trades = more reliable results

---

## How to Modify Settings

1. In MT5 Terminal, right-click on the chart with EA attached
2. Select "Expert Advisors" → EA name → "Properties"
3. Go to "Inputs" tab
4. Modify any parameter
5. Click "OK" to apply changes

---

## File Structure
```
mt5_ea/
├── AdvancedForexEA.mq5      (RSI + Stochastic Strategy)
├── MAForexEA.mq5            (Moving Average Crossover Strategy)
└── README.md                (This file)
```

---

## Need Help?
- Check MT5 Terminal → Experts tab for error logs
- Review OnInit() function output in Terminal
- Verify all indicator handles are valid (INVALID_HANDLE = error)
- Ensure chart has sufficient historical data (at least 100 candles)

---

**Last Updated**: 2026-04-04
**Ready to Trade**: ✓ Both EAs are fully compiled and ready for MT5
