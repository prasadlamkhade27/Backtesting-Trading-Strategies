# HFT Configuration Presets

Pre-configured strategy settings for different trading scenarios.

## 📋 Available Presets

### Scalping Strategies (High Frequency)
- **CONSERVATIVE_SCALPING** (0.3% risk, high win rate)
- **MODERATE_SCALPING** (0.5% risk, recommended)
- **AGGRESSIVE_SCALPING** (1.0% risk, high returns)

### Market Making Strategies (Spread Capture)
- **CONSERVATIVE_MARKET_MAKING** (low risk)
- **MODERATE_MARKET_MAKING** (balanced)

### Trend Following Strategies (Momentum)
- **CONSERVATIVE_TREND_FOLLOWING** (steady trends)
- **MODERATE_TREND_FOLLOWING** (standard)
- **AGGRESSIVE_TREND_FOLLOWING** (larger moves)

### Specialized
- **NEWS_TRADER** (high volatility events)
- **DEMO_ACCOUNT** (testing preset)

## 🚀 Usage

```python
from hft.config.hft_config import get_preset, list_presets

# List all presets
print(list_presets())

# Get specific preset
config = get_preset('MODERATE_SCALPING')

# Access parameters
risk = config.get('risk_percent_per_trade')
ma_fast = config.get('ma_fast_period')
strategy_type = config.get('strategy_type')

# Export configuration
config_dict = config.to_dict()
```

## 📊 Preset Comparison

| Preset | Risk | Win Rate | Return | Drawdown |
|--------|------|----------|--------|----------|
| Conservative | 0.3% | 60-70% | 1-2% | 5% |
| Moderate | 0.5% | 55-65% | 3-5% | 10% |
| Aggressive | 1.0% | 50-60% | 5-10% | 15% |
| Market Making | 0.3% | 65-75% | 2-3% | 3-5% |
| Trend Following | 0.5% | 45-55% | 5-8% | 10-15% |

## 📝 Configuration Structure

Each preset includes:
- Strategy type
- Technical indicator parameters
- Risk management settings
- Position management rules
- Performance targets
- Best use cases

## 🔧 Parameters

Key parameters in each preset:
- `strategy_type`: 'scalping', 'market_making', 'trend_following'
- `risk_percent_per_trade`: 0.3-1.0
- `ma_fast_period`: Fast moving average
- `ma_slow_period`: Slow moving average
- `rsi_period`: RSI period
- `atr_sl_multiple`: Stop loss distance
- `atr_tp_multiple`: Take profit distance

See `hft_config.py` for full parameter list.

## 💡 Choosing a Preset

**For Beginners**: Start with MODERATE_SCALPING  
**For Risk-Averse**: Use CONSERVATIVE_SCALPING  
**For Spread Trading**: Use MARKET_MAKING  
**For Trending Markets**: Use TREND_FOLLOWING  

## 📖 Documentation

- Full guide: See `docs/SYSTEM_GUIDE.md`
- Integration: See `docs/INTEGRATION_GUIDE.md`
- Quick ref: See `docs/QUICK_REFERENCE.md`

---

**Version**: 1.5
