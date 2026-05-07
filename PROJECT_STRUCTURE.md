# Project Structure

```
BackTesting-Python/
│
├── README.md                          # Main project documentation
├── CHANGELOG.md                       # Version history
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # License file
├── requirements.txt                   # Python dependencies
│
├── src/                               # Source code modules
│   ├── hft/                           # High-Frequency Trading module
│   │   ├── config/                    # Configuration files
│   │   ├── docs/                      # HFT documentation
│   │   ├── ea/                        # Expert Advisors (.mq5 files)
│   │   ├── examples/                  # HFT examples
│   │   ├── strategies/                # Trading strategies
│   │   ├── utils/                     # Utility functions
│   │   └── README.md
│   │
│   ├── propfirm/                      # Prop Firm module
│   │   ├── account_engine.py
│   │   ├── account_rules.py
│   │   ├── algo_trader.py
│   │   ├── compliance_engine.py
│   │   ├── config.py
│   │   ├── credentials_manager.py
│   │   ├── live_trader.py
│   │   ├── lot_size_calculator.py
│   │   ├── payout_rules.py
│   │   ├── reporting_engine.py
│   │   ├── risk_manager.py
│   │   ├── telegram_notifier.py
│   │   ├── trading_rules.py
│   │   ├── unified_backtest.py
│   │   └── ARCHITECTURE.md
│   │
│   └── pages/                         # Streamlit application pages
│       ├── 01_Strategy_Builder.py
│       ├── 02_Multi_Pair_Backtest.py
│       ├── 03_Trading_Hub.py
│       └── 04_Futures_Backtest.py
│
├── examples/                          # Example scripts and demonstrations
│   ├── run_demo.py
│   └── run_mql_king_1_backtest.py
│
├── tests/                             # Test files
│   ├── test_strategies.py
│   ├── test_futures.py
│   └── debug_custom.py
│
├── scripts/                           # Utility scripts
│   ├── create_backtest_engine.ps1
│   └── create_futures_files.ps1
│
├── docs/                              # Comprehensive documentation
│   ├── GETTING_STARTED.md
│   ├── INSTALLATION.md
│   ├── TRADING_GUIDE.md
│   ├── SYSTEM_OVERVIEW.md
│   ├── API_REFERENCE.md
│   ├── FAQ.md
│   ├── BUILD_COMPLETE.md
│   ├── DELIVERY_SUMMARY.md
│   ├── DOCUMENTATION_INDEX.md
│   ├── FIXES_APPLIED.md
│   ├── FUTURES_IMPLEMENTATION_COMPLETE.md
│   ├── HFT_START_HERE.md
│   ├── INDEX.md
│   ├── MQLKING_1_GUIDE.md
│   ├── PAIRS_TRADING_BACKTEST_INTEGRATION.md
│   ├── PAIRS_TRADING_BACKTEST_SETUP.md
│   ├── PROPFIRM_BUILD_SUMMARY.md
│   ├── README_START_HERE.md
│   ├── REPOSITORY_ORGANIZATION.md
│   └── SYSTEM_README.md
│
├── app.py                             # Main Streamlit application entry point
│
├── .github/                           # GitHub configuration
│   └── workflows/                     # CI/CD workflows
│
├── .git/                              # Git repository
└── .gitignore                         # Git ignore rules

```

## Directory Descriptions

### `src/` - Source Code
The main source code directory containing all modules:
- **hft/**: High-frequency trading strategies and configuration
- **propfirm/**: Prop firm trading rules, account management, and live trading
- **pages/**: Streamlit dashboard pages (called by app.py)

### `examples/` - Examples
Demonstration scripts showing how to use the framework:
- Example backtests
- Strategy demonstrations
- Integration examples

### `tests/` - Tests
Test files for verifying functionality:
- Unit tests
- Integration tests
- Debug utilities

### `scripts/` - Utility Scripts
PowerShell and bash scripts for automation:
- Setup scripts
- Configuration generators
- Maintenance utilities

### `docs/` - Documentation
Comprehensive documentation covering:
- Getting started guides
- Installation instructions
- API reference
- System architecture
- Trading guides
- Development notes

## Quick Navigation

- **To get started**: See `docs/GETTING_STARTED.md` or `docs/README_START_HERE.md`
- **For HFT strategies**: See `src/hft/README.md`
- **For prop firm features**: See `src/propfirm/ARCHITECTURE.md`
- **To run the app**: Execute `python app.py`
- **To run examples**: Check `examples/` folder
- **To run tests**: Execute test files in `tests/` folder

## Key Features

✓ Modular architecture
✓ Clean separation of concerns
✓ Comprehensive documentation
✓ Example-driven development
✓ Test coverage
✓ Streamlit dashboard
✓ Multiple trading strategies (HFT, Pairs Trading, Futures, etc.)
✓ Prop firm compliance and risk management
✓ Live and backtesting capabilities
