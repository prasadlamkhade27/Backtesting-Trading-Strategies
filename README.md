# Professional Algorithmic Trading System

A production-ready trading framework combining HFT strategies, prop firm challenge simulators, and multi-pair backtesting with comprehensive risk management.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

## Key Features

- **Multi-Pair Backtesting**: Test across major forex pairs
- **HFT Strategies**: 10+ high-frequency trading strategies
- **Prop Firm Simulator**: Account lifecycle and challenge validation
- **Live Trading**: Real-time execution with advanced risk management
- **Streamlit Dashboard**: Interactive UI for strategy development
- **Risk Management**: Per-trade and account-level position sizing

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for directory details.

- **Source Code**: [`src/`](src/)
- **Examples**: [`examples/`](examples/)
- **Tests**: [`tests/`](tests/)
- **Documentation**: [`docs/`](docs/)

## Installation

```bash
pip install -r requirements.txt
```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed setup.

## Usage

```bash
# Run dashboard
python app.py

# Run examples
python examples/run_demo.py

# Run tests
python tests/test_strategies.py
```

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Trading Guide](docs/TRADING_GUIDE.md)
- [System Overview](docs/SYSTEM_OVERVIEW.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License
- **Pre-configured Presets**: Apex, Lucid, Topstep

#### Forex Trading System
- **Strategy Builder**: Create custom trading strategies
- **Multi-Pair Backtesting**: Intelligent lot sizing per pair
- **Live Trading Hub**: Unified interface for live & algo trading
- **Risk Management**: Advanced position sizing & account protection

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trading-system.git
cd trading-system

# Install dependencies
pip install -r requirements.txt

# Verify installation
cd hft
python examples/verify_installation.py
```

### Run the System

**Option 1: Streamlit Web App**
```bash
streamlit run app.py
```
This launches the interactive trading dashboard with Strategy Builder, Backtesting, and Live Trading.

**Option 2: MQL King 1 Backtest**
```bash
python run_mql_king_1_backtest.py
```
Quick 5-minute backtest of the Smart Money Concepts strategy.

**Option 3: Direct Python**
```python
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine
from hft.config.hft_config import get_preset

# Get preset and backtest
config = get_preset('CONSERVATIVE_SCALPING')
strategy = HFTScalpingStrategy(**config.config)
backtest = HFTBacktestEngine(strategy=strategy)
results = backtest.run()
```

---

## 📁 Project Structure

```
trading-system/
│
├── 📄 app.py                           # Main Streamlit application
├── 📄 requirements.txt                 # Python dependencies
│
├── 📁 pages/                           # Streamlit pages
│   ├── 01_Strategy_Builder.py         # Create custom strategies
│   ├── 02_Multi_Pair_Backtest.py      # Multi-pair backtesting
│   ├── 03_Trading_Hub.py              # Live & algo trading
│   └── 04_Futures_Backtest.py         # Futures contract testing
│
├── 📁 hft/                            # HFT Trading System (Package)
│   ├── config/                        # Configuration presets
│   ├── strategies/                    # 10+ Trading Strategies
│   ├── utils/                         # Utilities & Engines
│   ├── ea/                            # MetaTrader 5 Expert Advisors
│   ├── examples/                      # Code Examples
│   ├── docs/                          # Comprehensive Documentation
│   └── README.md                      # HFT package overview
│
├── 📁 propfirm/                       # Prop Firm Challenge System
│   ├── account_engine.py              # Account lifecycle management
│   ├── account_rules.py               # Account configuration & rules
│   ├── compliance_engine.py           # Rule validation & breaches
│   ├── risk_manager.py                # Risk management
│   ├── live_trader.py                 # Trade execution
│   ├── algo_trader.py                 # Algorithmic trading
│   ├── reporting_engine.py            # Performance metrics
│   ├── credentials_manager.py         # API credential management
│   └── README.md                      # Prop firm guide
│
├── 📁 utils/                          # Core Utilities
│   └── ...
│
├── 📁 strategies/                     # Trading Strategies
│   └── ...
│
├── 📁 docs/                           # Root Documentation
│   ├── GETTING_STARTED.md
│   ├── INSTALLATION.md
│   ├── TRADING_GUIDE.md
│   └── ...
│
└── 📁 config/                         # Global Configuration
    └── settings.json
```

---

## 🎯 Modules Overview

### 1. HFT Trading System (`hft/`)

Professional high-frequency trading system with 10+ strategies.

**Key Components:**
- Strategies: Scalping, momentum, mean reversion, grid trading
- Backtesting: 2 engines for speed & analysis
- Expert Advisors: MT5 ready-to-deploy EAs
- Configuration: 10 presets for different trading styles

**Quick Start:**
```bash
cd hft
python examples/verify_installation.py
```

---

### 2. MQL King 1 - Smart Money Concepts

Professional XAUUSD M1 strategy based on Smart Money Concepts.

**Strategy Logic (8 Steps):**
1. Detect Market Structure - Identify trends
2. Break of Structure - Confirm trend changes
3. Map Liquidity - Find price targets
4. Order Blocks - Identify entry zones
5. Fair Value Gaps - Spot imbalances
6. Displacement - Confirm with impulse candle
7. Entry Points - Retest, gap fill, or sweep
8. Execute Trade - Risk/reward validated trade

**Components:**
- **MT5 EA**: `hft/ea/MQL_King_1.mq5`
- **Python Backtester**: `hft/utils/mql_king_1_backtester.py`
- **Quick Test**: `run_mql_king_1_backtest.py`

---

### 3. Prop Firm Challenge System (`propfirm/`)

Complete simulator for prop firm trading challenges.

**Features:**
- Account Engine: Real-time lifecycle management
- Compliance: Full rule validation & breach detection
- Risk Management: Position sizing & drawdown tracking
- Analytics: Complete performance metrics
- Presets: Apex, Lucid, Topstep configurations

---

### 4. Streamlit Trading Dashboard

Interactive web interface for trading operations.

**Pages:**
- Strategy Builder: Create custom trading strategies
- Multi-Pair Backtest: Test across multiple pairs with ML insights
- Trading Hub: Unified live & algo trading interface
- Futures Backtest: Test futures contracts (ES, NQ, etc.)

**Run:**
```bash
streamlit run app.py
```

---

## 📖 Documentation

### Getting Started

- [Quick Start](docs/GETTING_STARTED.md) - 5 minute setup
- [Installation Guide](docs/INSTALLATION.md) - Detailed setup
- [Trading Guide](docs/TRADING_GUIDE.md) - How to use

### HFT System Docs

- [HFT Quick Start](hft/docs/README_START_HERE.md)
- [Full HFT Guide](hft/docs/SYSTEM_GUIDE.md)
- [Quick Reference](hft/docs/QUICK_REFERENCE.md)

### Prop Firm Docs

- [Prop Firm Guide](propfirm/README.md)

---

## 💡 Examples

### Example 1: HFT Backtest

```python
from hft.strategies.hft_scalping_strategy import HFTScalpingStrategy
from hft.utils.hft_backtest_engine import HFTBacktestEngine
from hft.config.hft_config import get_preset

config = get_preset('CONSERVATIVE_SCALPING')
strategy = HFTScalpingStrategy(**config.config)
backtest = HFTBacktestEngine(strategy=strategy)
results = backtest.run()
```

### Example 2: Prop Firm Challenge

```python
from propfirm.unified_backtest import UnifiedBacktest
from propfirm.account_rules import get_preset

account_config = get_preset('APEX')
backtest = UnifiedBacktest(strategy=your_strategy, account_config=account_config)
results = backtest.run()
```

### Example 3: Multi-Pair Backtesting

```python
from utils.enhanced_backtest import EnhancedBacktestEngine

pairs = ['EURUSD', 'GBPUSD', 'XAUUSD']
backtest = EnhancedBacktestEngine(strategy=your_strategy, pairs=pairs)
results = backtest.run()
```

---

## 🔐 Security

### API Keys & Credentials

```python
from propfirm.credentials_manager import CredentialsManager

creds = CredentialsManager()
creds.set_api_key('broker_name', 'your_api_key')
```

**Security Tips:**
- Never hardcode credentials
- Use environment variables
- Store credentials in `.env` file (add to `.gitignore`)

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

Licensed under the MIT License - see LICENSE file for details.

---

## 🆘 Support

1. **Check Documentation** - Start with [GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. **Read Examples** - See `hft/examples/` for code samples
3. **Check Issues** - Browse existing issues on GitHub
4. **Create Issue** - Describe your problem with details

---

## 📈 Roadmap

- [ ] ML strategy optimization
- [ ] Real-time market data integration
- [ ] Advanced risk analytics dashboard
- [ ] Strategy performance comparison tool
- [ ] Community strategy sharing

---

**Last Updated**: April 2026  
**Version**: 2.0  
**Status**: ✅ Production Ready
=======
# Backtesting-Trading-Strategies
A complete trading ecosystem that combines strategy development, backtesting, live trading, and prop firm challenge simulation in one integrated platform.
>>>>>>> 5ea313ca96958705250bf4ce27c5fa6f9fd22f6c
