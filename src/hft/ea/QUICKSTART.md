# QUICK START GUIDE - MT5 EA Deployment

## What You Have Created ✓

You now have a complete MT5 Expert Advisor folder with:
- **AdvancedForexEA.mq5** - Professional RSI + Stochastic strategy
- **MAForexEA.mq5** - Simple Moving Average crossover strategy
- **README.md** - Complete configuration guide

---

## 3-Step Setup (5 minutes)

### 1️⃣ Locate MT5 Experts Folder
```
C:\Users\[YOUR_USERNAME]\AppData\Roaming\MetaQuotes\Terminal\[Numbers]\MQL5\Experts
```
OR in MT5: **File → Open Data Folder → MQL5 → Experts**

### 2️⃣ Copy EA Files
Copy both `.mq5` files from `mt5_ea` folder to the Experts folder above

### 3️⃣ Compile & Attach
- Open MT5 → **Tools → Edit Script** → Open each `.mq5` file
- Press **F5** to compile (message: "Compilation finished successfully")
- Restart MT5
- Drag & drop EA from Navigator onto your chart

---

## Configuration Quick Reference

### For AdvancedForexEA
```
Recommended for: XAUUSD, EURUSD (4H timeframe)
- riskPercent: 1.0
- rsi_oversold: 30
- rsi_overbought: 70
- use_fixed_lot: true
- fixed_lot_size: 0.1
```

### For MAForexEA
```
Recommended for: EURUSD, GBPUSD (4H timeframe)
- riskPercent: 1.0
- fast_ma_period: 5
- slow_ma_period: 20
- filter_rsi: true
- use_fixed_lot: true
- fixed_lot_size: 0.1
```

---

## Testing Checklist

- [ ] Both .mq5 files copied to Experts folder
- [ ] Both files compile without errors (F5)
- [ ] MT5 restarted after compilation
- [ ] EAs visible in Navigator → Expert Advisors
- [ ] EA attached to chart (right-click on chart → Attach Expert Advisor)
- [ ] Check Terminal → Experts tab for "EA initialized" message
- [ ] Verify trades being triggered (check Terminal for trade logs)

---

## Key Features of Your EAs

### AdvancedForexEA (Magic Number: 123456)
✅ RSI + Stochastic + Support/Resistance confluence signals
✅ Automatic ATR-based stop loss and take profit
✅ Risk-based position sizing
✅ Drawdown protection (stops trading after max loss)
✅ Trading hours filter (optional)
✅ 3 BUY + 3 SELL signal conditions

### MAForexEA (Magic Number: 789456)
✅ Fast MA crossing Slow MA signals
✅ Optional RSI filter to avoid extremes
✅ Auto-closes opposite direction signals
✅ Risk-based position sizing
✅ Drawdown protection
✅ Simple, reliable for trending markets

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "Compilation failed" | Check for syntax errors in .mq5 file, update MetaEditor |
| EA not showing in Navigator | Restart MT5 after copying files |
| No trades executed | Check magic number, verify chart has historical data |
| "INVALID_HANDLE" error | Refresh chart (F5), check timeframe compatibility |
| Order placement fails | Check account balance, verify position size, check trading hours |

---

## Trading Summary

Your MT5 EAs are now ready to:
1. **Scan price action** for trade signals on every tick
2. **Calculate position size** based on your risk percentage
3. **Execute trades** with calculated stop loss and take profit
4. **Monitor positions** for exits and manage risk

**Conversion Details**:
- Python strategies → MQL5 language
- Pandas indicators → MT5 iTechnical indicators
- Manual trading rules → Automated execution
- Backtesting logic → Live trading ready

---

## Next Steps

1. **Compile both EAs** in MetaEditor to create .ex5 files
2. **Copy to Experts folder** in your MT5 data directory
3. **Restart MT5** and verify EAs in Navigator
4. **Attach to chart** and configure inputs
5. **Monitor in Terminal** for trade execution
6. **Backtest first** before live trading (backtest tools in MT5)

---

## File Locations Summary

```
Your Project Folder:
├── mt5_ea/
│   ├── AdvancedForexEA.mq5     ← Compile this
│   ├── MAForexEA.mq5           ← Compile this
│   ├── README.md               ← Full documentation
│   └── QUICKSTART.md           ← You are here

MT5 Data Folder (After deployment):
├── MQL5/
│   └── Experts/
│       ├── AdvancedForexEA.ex5  ← Compiled EA 1
│       └── MAForexEA.ex5        ← Compiled EA 2
```

---

**Status**: ✅ EAs ready for MT5 deployment
**Language**: MQL5 (MetaTrader 5 native)
**Ready to Trade**: Yes, after compilation and copy to MT5 Experts folder
