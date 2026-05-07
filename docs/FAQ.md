# FAQ - Frequently Asked Questions

## General Questions

### What is this system?

This is a professional-grade algorithmic trading system that combines:
- **HFT Strategies** - 10+ high-frequency trading strategies
- **Backtesting Engine** - Test strategies on historical data
- **Live Trading** - Execute real or simulated trades
- **Prop Firm Simulator** - Validate against trading challenge rules
- **ML Analysis** - Deep insights from backtest results
- **Smart Money Concepts** - MQL King 1 XAUUSD EA

### Do I need coding experience?

No! You can:
- Use the web dashboard (no coding)
- Use pre-built strategies and presets
- Use simple configuration files

Advanced users can write custom strategies in Python.

### Is this for beginners or professionals?

Both! The system has:
- **Easy Path** - Use web dashboard with presets
- **Advanced Path** - Write custom strategies in Python
- **Professional Path** - Full API access and customization

### Is live trading safe?

The system includes:
- **Simulated Mode** - Paper trading (recommended first)
- **Risk Management** - Position sizing, stop losses, daily limits
- **Account Protection** - Maximum drawdown limits
- **Credentials Manager** - Secure API key storage

Always test thoroughly in simulated mode first.

---

## Installation & Setup

### I'm getting "Python not found"

**Solution:**
```bash
# Check if Python is installed
python --version

# If not, install from python.org
# Then add Python to PATH and restart terminal
```

### I'm getting import errors

**Solution:**
```bash
# Activate virtual environment
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### Installation is very slow

**Solution:**
```bash
# Use faster resolver
pip install -r requirements.txt --use-deprecated=legacy-resolver

# Or install packages individually
pip install streamlit pandas numpy scikit-learn
```

### I have multiple Python versions

**Solution:**
```bash
# Use specific version
python3.10 -m venv venv

# Or
py -3.10 -m venv venv
```

---

## Usage Questions

### How do I start?

1. **Install**: `pip install -r requirements.txt`
2. **Run**: `streamlit run app.py`
3. **Test**: Go to "Multi Pair Backtest" page
4. **Read**: [GETTING_STARTED.md](docs/GETTING_STARTED.md)

### What's the quickest way to backtest?

```bash
python run_mql_king_1_backtest.py
```

This runs a complete backtest in ~5 minutes.

### How do I create a custom strategy?

Option 1: Use web dashboard Strategy Builder  
Option 2: Extend `BaseStrategy` (see [TRADING_GUIDE.md](docs/TRADING_GUIDE.md))  
Option 3: Use existing strategies as templates

### Can I trade multiple pairs?

Yes! Use Multi-Pair Backtesting:
```python
pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
backtest = EnhancedBacktestEngine(strategy=your_strategy, pairs=pairs)
results = backtest.run()
```

### How do I test for prop firm challenge?

```python
from propfirm.unified_backtest import UnifiedBacktest
from propfirm.account_rules import get_preset

account_config = get_preset('APEX')
backtest = UnifiedBacktest(strategy=your_strategy, account_config=account_config)
results = backtest.run()
```

---

## Strategy Questions

### What's MQL King 1?

Smart Money Concepts strategy for XAUUSD M1:
- Market structure detection
- Order block identification
- Fair value gap detection
- Professional entry/exit logic

Ready to deploy on MetaTrader 5.

### How do I deploy the EA to MetaTrader?

1. Get the EA: `hft/ea/MQL_King_1.mq5`
2. Open MetaTrader 5
3. File → Open Data Folder
4. Go to MQL5/Experts
5. Copy the `.mq5` file
6. Compile and deploy

### Can I modify the strategies?

Yes! You can:
- Create new strategies extending `BaseStrategy`
- Modify existing strategies
- Use configuration presets
- Create custom parameters

### What's the difference between strategies?

Each strategy has different entry/exit logic:
- **Scalping** - Fast, many small trades
- **Momentum** - Trend following
- **Mean Reversion** - Reverting to average
- **Grid Trading** - Defined price levels
- See [hft/strategies/](hft/strategies/) for all

---

## Backtesting Questions

### Why are my backtest results unrealistic?

Common reasons:
1. **Slippage** - Not accounted for
2. **Spreads** - Check your data
3. **Commission** - Might not be included
4. **Data Quality** - Use reliable data sources

### How long should backtest period be?

- **Minimum**: 6-12 months
- **Recommended**: 2-3 years
- **Ideal**: 5+ years for robust strategy

### What metrics should I focus on?

1. **Win Rate** - Should be >50%
2. **Profit Factor** - Should be >1.5
3. **Sharpe Ratio** - Should be >1.0
4. **Max Drawdown** - Should be <20%
5. **Recovery Factor** - Should be >3.0

### My strategy has high win rate but loses money

Your strategy might have:
1. **Small wins, big losses** - Check risk/reward ratio
2. **Drawdown issues** - Reduce position size
3. **Slippage problems** - Account for spreads

Try optimizing parameters using StrategyOptimizer.

---

## Live Trading Questions

### What broker does this support?

Currently supports:
- **MetaTrader 5** (MT5)
- **OANDA**

Can be extended to other brokers.

### How do I add broker credentials?

```python
from propfirm.credentials_manager import CredentialsManager

creds = CredentialsManager()
creds.set_api_key('MT5', 'your_id')
creds.set_api_secret('MT5', 'your_password')
```

### Should I use live or simulated mode?

**Always start with simulated mode:**
1. Test your setup
2. Validate strategy performance
3. Ensure risk management works
4. Only then go live with small capital

### How much should I risk per trade?

**Recommended**: 1-2% of account per trade

```python
# Calculate position size
account_size = 10000
risk_pct = 0.02  # 2%
risk_amount = account_size * risk_pct  # $200

# Adjust position size based on this
```

### Can I trade 24/7?

Yes, but consider:
- **Different sessions** have different liquidity
- **Spreads vary** by session
- **Slippage** differs by time
- **Recommended**: Focus on major sessions (London, NY)

---

## Performance Questions

### My backtest shows 100% return, is that real?

Probably not. Check:
- **Overfitting** - Strategy too specific to historical data
- **Survivorship bias** - Cherry-picked data
- **Look-ahead bias** - Using future information
- **Unrealistic parameters** - Too good to be true

Always optimize and validate on unseen data.

### How do I avoid overfitting?

1. **Use more data** - Test on 5+ years
2. **Out-of-sample testing** - Validate on new data
3. **Walk-forward analysis** - Rolling window backtests
4. **Simple parameters** - Fewer parameters = less overfitting

### What's a realistic return?

**Backtesting:**
- Conservative: 10-20% annual
- Moderate: 20-50% annual
- Aggressive: 50%+ annual

**Live trading** typically produces 30-50% lower returns than backtest.

---

## Prop Firm Questions

### What's the prop firm challenge?

Simulate trading challenge with rules like:
- Profit target (e.g., $1,000)
- Maximum drawdown (e.g., 10%)
- Daily loss limit (e.g., 5%)
- Trading days required (e.g., 5 days)

### Which presets are available?

- **Apex** - Popular challenge
- **Lucid** - Alternative rules
- **Topstep** - Different parameters

### How do I know if I passed?

```python
if results['passed']:
    print("✅ PASSED!")
else:
    print(f"❌ FAILED: {results['failure_reason']}")
```

### Can I create custom rules?

Yes! Edit `propfirm/account_rules.py` or create new preset.

---

## Technical Questions

### What Python version do I need?

- **Minimum**: Python 3.8
- **Recommended**: Python 3.10+

### What are the system requirements?

- **RAM**: 2GB minimum, 8GB recommended
- **Disk**: 500MB+ for data and cache
- **OS**: Windows, Mac, or Linux

### Can I use this in production?

Yes, but:
- Test thoroughly first
- Use simulated mode initially
- Start with small amounts
- Monitor constantly
- Have risk management safeguards

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guide.

---

## Troubleshooting

### Dashboard won't start

```bash
# Kill existing process
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows

# Then restart
streamlit run app.py
```

### Data loading is slow

```python
# Use sample data first for testing
data = load_sample_data()  # Faster

# Or load specific period
data = load_data(symbol='EURUSD', start='2023-01-01', end='2024-01-01')
```

### Memory errors during backtest

```python
# Reduce data size
backtest = HFTBacktestEngine(
    strategy=strategy,
    max_bars=10000  # Limit data
)
```

### API connection fails

```python
# Test connection
from propfirm.live_trader import LiveTrader
trader = LiveTrader(broker='MT5')
if trader.test_connection():
    print("✅ Connected")
else:
    print("❌ Failed")
```

---

## Still Have Questions?

1. **Check Documentation**: [README.md](README.md)
2. **Read Guides**: [docs/](docs/)
3. **See Examples**: [hft/examples/](hft/examples/)
4. **Open Issue**: GitHub Issues
5. **Check Discussions**: GitHub Discussions

---

**Last Updated**: April 2026  
**Version**: 2.0
