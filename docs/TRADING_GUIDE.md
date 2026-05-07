# 📚 Trading Guide

Complete guide to using the trading system for backtesting, strategy development, and live trading.

## Table of Contents

1. [Backtesting Strategies](#backtesting-strategies)
2. [Creating Custom Strategies](#creating-custom-strategies)
3. [Live Trading Setup](#live-trading-setup)
4. [Algorithmic Trading](#algorithmic-trading)
5. [Risk Management](#risk-management)
6. [Prop Firm Challenge](#prop-firm-challenge)

---

## Backtesting Strategies

### Using the Web Dashboard

**Easiest method - no coding required**

```bash
streamlit run app.py
```

1. Go to **"Multi Pair Backtest"** page
2. Select strategy type
3. Choose forex pairs to test
4. Set time period
5. Configure parameters
6. Click **"Run Backtest"**
7. View results and equity curve

### Using Python API

```python
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine
from hft.config.hft_config import get_preset
import pandas as pd

# 1. Get a preset configuration
config = get_preset('CONSERVATIVE_SCALPING')

# 2. Create strategy instance
strategy = HFTScalpingStrategy(**config.config)

# 3. Create backtest engine
backtest = HFTBacktestEngine(
    strategy=strategy,
    initial_capital=10000,
    risk_per_trade=0.02
)

# 4. Load data
data = pd.read_csv('eurusd_data.csv')

# 5. Run backtest
results = backtest.run(data)

# 6. View results
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
```

### Multi-Pair Backtesting

```python
from utils.enhanced_backtest import EnhancedBacktestEngine

# Test across multiple pairs
pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']

backtest = EnhancedBacktestEngine(
    strategy=your_strategy,
    pairs=pairs,
    start_date='2023-01-01',
    end_date='2024-01-01'
)

results = backtest.run()

# View performance per pair
for pair, metrics in results.items():
    print(f"\n{pair}:")
    print(f"  Return: {metrics['return']:.2f}%")
    print(f"  Win Rate: {metrics['win_rate']:.2f}%")
```

---

## Creating Custom Strategies

### Method 1: Using Strategy Builder (GUI)

1. Open dashboard: `streamlit run app.py`
2. Go to **"Strategy Builder"** page
3. Configure:
   - Entry conditions
   - Exit conditions
   - Risk parameters
4. Test on historical data
5. Save configuration

### Method 2: Extend Base Strategy (Code)

```python
from hft.strategies.base_strategy import BaseStrategy
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    """Custom trading strategy"""
    
    def __init__(self, fast_ma=10, slow_ma=30, **kwargs):
        super().__init__(**kwargs)
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals"""
        
        # Calculate moving averages
        data['fast_ma'] = data['close'].rolling(self.fast_ma).mean()
        data['slow_ma'] = data['close'].rolling(self.slow_ma).mean()
        
        # Generate signals
        data['signal'] = 0
        data.loc[data['fast_ma'] > data['slow_ma'], 'signal'] = 1  # Buy
        data.loc[data['fast_ma'] < data['slow_ma'], 'signal'] = -1  # Sell
        
        return data
    
    def calculate_entry_price(self, row):
        """Calculate entry price"""
        return row['close']
    
    def calculate_stop_loss(self, entry_price, direction):
        """Calculate stop loss"""
        atr = 0.02  # Example ATR
        if direction == 1:
            return entry_price * (1 - atr)
        else:
            return entry_price * (1 + atr)
    
    def calculate_take_profit(self, entry_price, direction):
        """Calculate take profit"""
        risk_reward = 2.0
        sl_distance = abs(entry_price - self.calculate_stop_loss(entry_price, direction))
        if direction == 1:
            return entry_price + (sl_distance * risk_reward)
        else:
            return entry_price - (sl_distance * risk_reward)

# Use your strategy
strategy = MyCustomStrategy(fast_ma=10, slow_ma=30)
backtest = HFTBacktestEngine(strategy=strategy)
results = backtest.run()
```

### Method 3: Smart Money Concepts (MQL King 1)

For ready-made advanced strategy:

```bash
python run_mql_king_1_backtest.py
```

This uses the Smart Money Concepts strategy tuned for XAUUSD M1.

---

## Live Trading Setup

### Step 1: Configure Broker Connection

```python
from propfirm.credentials_manager import CredentialsManager

# Initialize credentials manager
creds = CredentialsManager()

# Add your broker credentials
creds.set_api_key('MT5', 'your_login_id')
creds.set_api_secret('MT5', 'your_password')
creds.set_account('MT5', 'your_account_number')

# Retrieve credentials
api_key = creds.get_api_key('MT5')
```

### Step 2: Configure Risk Parameters

```python
from propfirm.config import RiskConfig

risk = RiskConfig(
    account_size=10000,           # Initial account balance
    risk_per_trade=0.02,          # 2% per trade
    max_daily_loss=0.05,          # Stop trading after 5% loss
    max_weekly_loss=0.10,         # Stop trading after 10% loss
    position_size_method='fixed'  # Or 'kelly', 'optimal'
)
```

### Step 3: Initialize Live Trader

```python
from propfirm.live_trader import LiveTrader

# Create trader instance
trader = LiveTrader(
    broker='MT5',
    strategy=your_strategy,
    risk_config=risk,
    mode='simulated'  # 'simulated' or 'live'
)

# Start trading
trader.start()

# Monitor positions
while True:
    positions = trader.get_positions()
    print(f"Open positions: {len(positions)}")
    print(f"Account balance: {trader.get_balance()}")
    
    time.sleep(60)  # Check every minute
```

### Step 4: Monitor Trades

```python
# Get open positions
positions = trader.get_positions()
for pos in positions:
    print(f"Symbol: {pos['symbol']}")
    print(f"Size: {pos['size']}")
    print(f"Entry: {pos['entry_price']}")
    print(f"Current P&L: {pos['pnl']}")

# Get trade history
history = trader.get_trade_history()
for trade in history[-10:]:  # Last 10 trades
    print(f"{trade['entry_time']}: {trade['symbol']} {trade['profit']:.2f}")
```

---

## Algorithmic Trading

### Run Multi-Pair Algorithm

```python
from propfirm.algo_trader import AlgoTrader

# Create algo trader
algo = AlgoTrader(
    broker='MT5',
    strategy=your_strategy,
    pairs=['EURUSD', 'GBPUSD', 'USDJPY'],
    risk_per_trade=0.02,
    mode='simulated'
)

# Start algorithm
algo.start()

# Monitor
while True:
    stats = algo.get_stats()
    print(f"Total P&L: {stats['total_pnl']:.2f}")
    print(f"Trades today: {stats['trades_today']}")
    print(f"Win rate: {stats['win_rate']:.2f}%")
    
    time.sleep(300)  # Check every 5 minutes

# Stop gracefully
algo.stop()
```

### Configure Multiple Strategies

```python
from propfirm.algo_trader import AlgoTrader

# Create algo trader with different strategies per pair
algo = AlgoTrader(
    broker='MT5',
    strategies={
        'EURUSD': strategy_1,
        'GBPUSD': strategy_2,
        'XAUUSD': strategy_3
    },
    mode='simulated'
)

algo.start()
```

---

## Risk Management

### Position Sizing

```python
from propfirm.lot_size_calculator import LotSizeCalculator

calculator = LotSizeCalculator(
    account_size=10000,
    risk_per_trade=0.02,
    account_currency='USD'
)

# Calculate lot size
lot_size = calculator.calculate(
    symbol='EURUSD',
    entry_price=1.0850,
    stop_loss=1.0800
)

print(f"Lot size: {lot_size}")
```

### Risk Per Trade

```python
risk_amount = account_size * risk_percentage
lot_size = risk_amount / (entry_price - stop_loss) / contract_size

# Example
account = 10000
risk_pct = 0.02  # 2%
entry = 1.0850
stop = 1.0800
contract_size = 100000

risk_amount = 10000 * 0.02  # $200
pip_distance = (1.0850 - 1.0800) * 10000  # 50 pips
lot_size = 200 / 50 / 100  # 0.04 lots
```

### Daily Loss Limit

```python
from propfirm.risk_manager import RiskManager

risk_mgr = RiskManager(
    max_daily_loss=0.05,  # 5%
    max_position_size=0.1,  # 10% of account
    max_correlation=0.7
)

# Check if can trade
if risk_mgr.can_trade():
    # Execute trade
    trader.open_trade()
else:
    print("Daily loss limit reached")
```

---

## Prop Firm Challenge

### Setup Challenge

```python
from propfirm.unified_backtest import UnifiedBacktest
from propfirm.account_rules import get_preset

# Load Apex challenge rules
account_config = get_preset('APEX')

# Create backtest with challenge rules
backtest = UnifiedBacktest(
    strategy=your_strategy,
    account_config=account_config,
    initial_capital=100000
)

# Run challenge
results = backtest.run()
```

### Validate Challenge Result

```python
if results['passed']:
    print("✅ PASSED the challenge!")
    print(f"  Max drawdown: {results['max_drawdown']:.2f}%")
    print(f"  Win rate: {results['win_rate']:.2f}%")
    print(f"  Consistency: {results['consistency']:.2f}%")
else:
    print("❌ FAILED the challenge")
    print(f"  Reason: {results['failure_reason']}")
    print(f"  Failed on: {results['failed_on']}")
```

### Check Specific Rules

```python
# Get detailed compliance report
compliance = backtest.get_compliance_report()

for rule in compliance['rules']:
    status = "✅" if rule['passed'] else "❌"
    print(f"{status} {rule['name']}: {rule['message']}")
```

---

## Performance Metrics

### Key Metrics Explained

| Metric | Formula | Good Value | Description |
|--------|---------|------------|-------------|
| **Return** | (Final Balance - Initial) / Initial | >50% | Total profit |
| **Win Rate** | Wins / Total Trades | >50% | % profitable trades |
| **Profit Factor** | Gross Profit / Gross Loss | >1.5 | Profitability ratio |
| **Sharpe Ratio** | (Return - Risk Free) / Std Dev | >1.0 | Risk-adjusted return |
| **Max Drawdown** | Peak-to-Trough / Peak | <20% | Worst peak-to-trough decline |
| **Recovery Factor** | Total Profit / Max Drawdown | >3.0 | Ability to recover |

### Analyzing Results

```python
results = backtest.run()

# Print summary
print("=" * 50)
print("BACKTEST RESULTS")
print("=" * 50)
print(f"Period: {results['start_date']} to {results['end_date']}")
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
print(f"Recovery Factor: {results['recovery_factor']:.2f}")
print("=" * 50)
```

---

## Advanced Features

### Strategy Optimization

```python
from hft.utils.strategy_optimizer import StrategyOptimizer

optimizer = StrategyOptimizer(strategy=MyCustomStrategy)

# Test different parameters
best_params = optimizer.optimize(
    param_ranges={
        'fast_ma': range(5, 20),
        'slow_ma': range(20, 50)
    },
    test_data=data
)

print(f"Best parameters: {best_params}")
```

### Machine Learning Analysis

```python
from utils.ml_analyzer import MLAnalyzer

analyzer = MLAnalyzer(backtest_results)

# Get insights
insights = analyzer.analyze()
print(insights)  # Recommendations for improvement
```

---

## Troubleshooting

### No Signals Generated

```python
# Check data
print(data.head())

# Verify strategy logic
signals = strategy.generate_signals(data)
print(signals[signals['signal'] != 0])

# Check parameters
print(f"Strategy params: {strategy.__dict__}")
```

### Poor Performance

1. Check your risk parameters
2. Optimize parameters using `StrategyOptimizer`
3. Test across different time periods
4. Validate strategy logic manually

### Live Trading Issues

1. Verify broker connection: `trader.test_connection()`
2. Check credentials: `creds.verify()`
3. Monitor logs: `trader.get_logs()`

---

## Resources

- [HFT Quick Reference](../hft/docs/QUICK_REFERENCE.md)
- [Strategy Examples](../hft/examples/)
- [Prop Firm Guide](../propfirm/README.md)

