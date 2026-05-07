"""
PROPFIRM SYSTEM - QUICK REFERENCE GUIDE
═════════════════════════════════════════════════════════════════════════

IMPORT EVERYTHING YOU NEED
───────────────────────────────────────────────────────────────────────

# Account Configuration & Presets
from propfirm.account_rules import (
    create_apex_preset,
    create_lucid_preset,
    create_topstep_preset,
    AccountConfig,
    PhaseRules,
)

# Trading Rules & Restrictions
from propfirm.trading_rules import (
    create_apex_trading_rules,
    create_lucid_trading_rules,
    create_topstep_trading_rules,
    create_risk_management_professional,
    TradingRules,
    RiskManagementRules,
)

# Payout & Earnings Rules
from propfirm.payout_rules import (
    create_apex_payout_rules,
    create_lucid_payout_rules,
    create_topstep_payout_rules,
    PayoutRules,
    ConsistencyRule,
    ProfitSplitRules,
)

# Main Backtest Engine
from propfirm.unified_backtest import UnifiedPropFirmBacktest


QUICK API REFERENCE
───────────────────────────────────────────────────────────────────────

1. CREATE A BACKTEST (3 ways)

   # Way 1: Use preset directly
   backtest = UnifiedPropFirmBacktest(
       account_config=create_lucid_preset(50000),
       trading_rules=create_lucid_trading_rules(),
       risk_rules=create_risk_management_professional(),
       payout_rules=create_lucid_payout_rules(),
   )

   # Way 2: Mix and match rules from different presets
   backtest = UnifiedPropFirmBacktest(
       account_config=create_lucid_preset(100000),  # Lucid account
       trading_rules=create_apex_trading_rules(),    # But Apex restrictions
       risk_rules=create_risk_management_professional(),
       payout_rules=create_topstep_payout_rules(),  # And Topstep payouts
   )

   # Way 3: Fully custom rules
   custom_account = AccountConfig(
       initial_balance=50000,
       phases=[PhaseRules(profit_target=3000, max_drawdown=2500)],
   )
   backtest = UnifiedPropFirmBacktest(
       account_config=custom_account,
       trading_rules=TradingRules(min_trading_days=5, ...),
       risk_rules=RiskManagementRules(risk_per_trade_pct=1.0, ...),
       payout_rules=PayoutRules(...),
   )


2. RUN A BACKTEST

   result = backtest.run(
       data=your_dataframe,           # DataFrame with OHLC + signals
       symbol='ES',                   # Trading symbol
       entry_col='BUY',               # Column for entry signals
       exit_col='SELL',               # Column for exit signals
       sl_pips=50,                    # Stop loss distance
       tp_pips=100,                   # Take profit distance
       init_time=datetime.now(),      # Optional: start time
   )


3. CHECK RESULT

   # Simple check
   if result['passed']:
       print("✅ PASSED!")
   else:
       print(f"❌ FAILED: {result['reason']}")
   
   # Full info
   summary = result['summary']
   print(f"Balance: ${summary['balance']['current']:.2f}")
   print(f"P&L: {summary['balance']['cumulative_pnl_pct']}")
   print(f"Drawdown: {summary['drawdown']['current']}")
   print(f"Trades: {summary['trading']['total_trades']}")
   print(f"Compliance: {summary['compliance']['score']}")


4. GET DETAILED ANALYTICS

   # Live dashboard
   dashboard = backtest.get_live_status()
   
   # Detailed report
   detailed = backtest.reporting_engine.get_detailed_report()
   
   # Export
   csv = backtest.reporting_engine.export_csv_summary()


COMMON USAGE PATTERNS
───────────────────────────────────────────────────────────────────────

Pattern 1: Compare across all presets
  ───────────────────────────────────
  
  results = {}
  for preset_name, account_fn, trading_fn, payout_fn in [
      ('Apex', create_apex_preset, create_apex_trading_rules, create_apex_payout_rules),
      ('Lucid', create_lucid_preset, create_lucid_trading_rules, create_lucid_payout_rules),
      ('Topstep', create_topstep_preset, create_topstep_trading_rules, create_topstep_payout_rules),
  ]:
      backtest = UnifiedPropFirmBacktest(
          account_config=account_fn(50000),
          trading_rules=trading_fn(),
          risk_rules=create_risk_management_professional(),
          payout_rules=payout_fn(),
      )
      results[preset_name] = backtest.run(df)
  
  for name, result in results.items():
      print(f"{name}: {'✅' if result['passed'] else '❌'} {result['reason']}")


Pattern 2: Test across multiple account sizes
  ───────────────────────────────────────────
  
  for account_size in [25000, 50000, 100000]:
      backtest = UnifiedPropFirmBacktest(
          account_config=create_lucid_preset(account_size),
          ...
      )
      result = backtest.run(df)
      print(f"${account_size}: {'✅' if result['passed'] else '❌'}")


Pattern 3: Find which rules work for your strategy
  ────────────────────────────────────────────────
  
  # Test different consistency thresholds
  for consistency_threshold in [25, 35, 50, 75]:
      payout = create_lucid_payout_rules()
      payout.consistency.best_day_max_pct = consistency_threshold
      
      backtest = UnifiedPropFirmBacktest(
          account_config=create_lucid_preset(50000),
          trading_rules=create_lucid_trading_rules(),
          risk_rules=create_risk_management_professional(),
          payout_rules=payout,
      )
      result = backtest.run(df)
      print(f"Best day ≤ {consistency_threshold}%: {'✅' if result['passed'] else '❌'}")


Pattern 4: Test with different symbols
  ─────────────────────────────────────
  
  for symbol in ['ES', 'NQ', 'YM', 'CL', 'GC']:
      df = load_data(symbol)
      df['BUY'], df['SELL'] = generate_signals(df)
      
      backtest = UnifiedPropFirmBacktest(...)
      result = backtest.run(df, symbol=symbol)
      
      print(f"{symbol}: {'✅' if result['passed'] else '❌'}")


MODIFYING RULES ON THE FLY
───────────────────────────────────────────────────────────────────────

# Modify account rules
account = create_lucid_preset(50000)
account.phases[0].profit_target = 5000  # Change target to $5K
account.phases[0].min_days = 10         # Change min days to 10

# Modify trading rules
trading = create_lucid_trading_rules()
trading.max_contracts_total = 10        # Increase position limit
trading.enable_daily_loss_limit = True  # Add daily loss limit
trading.max_daily_loss_amount = 500     # $500 max per day

# Modify risk rules
risk = create_risk_management_professional()
risk.risk_per_trade_pct = 0.5           # 0.5% per trade instead of 1%
risk.max_consecutive_losing_trades = 3  # Stricter

# Modify payout rules
payout = create_lucid_payout_rules()
payout.consistency.best_day_max_pct = 30  # Stricter consistency (30% instead of 50%)
payout.consistency.violation_is_fatal = True  # Fail account if violated


SPECIFIC IMPORT EXAMPLES
───────────────────────────────────────────────────────────────────────

# If you only need account rules:
from propfirm.account_rules import AccountConfig, create_lucid_preset

# If you only need trading rules:
from propfirm.trading_rules import TradingRules, create_lucid_trading_rules

# If you only need payout rules:
from propfirm.payout_rules import PayoutRules, create_lucid_payout_rules

# If you only need to run backtests:
from propfirm.unified_backtest import UnifiedPropFirmBacktest
from propfirm.account_rules import *
from propfirm.trading_rules import *
from propfirm.payout_rules import *

# If you only need analytics:
from propfirm.reporting_engine import ReportingEngine


DATA REQUIREMENTS
───────────────────────────────────────────────────────────────────────

Your DataFrame must have:
  ✅ 'open', 'high', 'low', 'close' columns
  ✅ Column for entry signals (default: 'BUY')
  ✅ Column for exit signals (default: 'SELL')
  ✅ Optional: 'volume' column
  ✅ Optional: 'timestamp' column (or use index)

Example DataFrame structure:
  
  timestamp            open    high    low     close   volume  BUY  SELL
  2024-01-01 09:30    5000    5010    4990    5005    10000    0     0
  2024-01-01 09:35    5005    5015    5000    5010    12000    1     0
  2024-01-01 09:40    5010    5020    5005    5008    11000    0     0
  2024-01-01 09:45    5008    5010    4995    5000    9000     0     1


RESULT STRUCTURE
───────────────────────────────────────────────────────────────────────

result = {
    'passed': True/False,           # Overall pass/fail
    'reason': 'PASSED_ONE_STEP'     # Why passed or failed
    'summary': {                    # Dashboard summary
        'account_status': {...},
        'balance': {...},
        'drawdown': {...},
        'profit_target': {...},
        'trading': {...},
        'days': {...},
        'compliance': {...},
    },
    'detailed_report': {            # Full analysis
        'summary': {...},
        'performance_metrics': {...},
        'daily_records': [...],
        'trade_log': [...],
        'compliance': {...},
    },
    'trades': 42,                   # Number of trades
    'daily_records': 10,            # Number of trading days
    'compliance_score': 92.5,       # 0-100 compliance rating
}


COMMON EDITS CHEAT SHEET
───────────────────────────────────────────────────────────────────────

# Allow overnight holding
trading_rules.allow_overnight = True

# Allow weekend trading
trading_rules.allow_weekend = True

# Disable news trading restriction
trading_rules.news_restriction.enabled = False

# Reduce position limit
trading_rules.max_contracts_total = 3

# Increase profit target
account_config.phases[0].profit_target = 5000

# Change drawdown type
from propfirm.account_rules import DrawdownType
account_config.phases[0].drawdown_type = DrawdownType.FIXED

# Add daily loss limit
trading_rules.enable_daily_loss_limit = True
trading_rules.max_daily_loss_amount = 500

# Enforce consistency rule
payout_rules.consistency.enabled = True
payout_rules.consistency.best_day_max_pct = 40

# Enable 2-step evaluation
from propfirm.account_rules import EvaluationType
account_config.evaluation_type = EvaluationType.TWO_STEP


DEBUGGING
───────────────────────────────────────────────────────────────────────

If account fails, check:
  1. Drawdown: backtest.account_engine.max_drawdown_hit_pct
  2. Profit: backtest.account_engine.cumulative_pnl
  3. Days: backtest.account_engine.trading_days_count
  4. Breaches: backtest.compliance_engine.critical_breaches
  5. Status: backtest.account_engine.status.value
  6. Failure: backtest.account_engine.failure_reason

Example debugging:
  
  if not result['passed']:
      engine = backtest.account_engine
      print(f"Final balance: ${engine.current_balance:.2f}")
      print(f"P&L: ${engine.cumulative_pnl:.2f}")
      print(f"Max DD: {engine.max_drawdown_hit_pct:.2f}%")
      print(f"Trading days: {engine.trading_days_count}")
      print(f"Reason: {engine.failure_reason}")


WHERE TO FIND THINGS
───────────────────────────────────────────────────────────────────────

Account config?              → propfirm/account_rules.py
Trading restrictions?        → propfirm/trading_rules.py
Payout rules?                → propfirm/payout_rules.py
Balance tracking?            → propfirm/account_engine.py
Rule validation?             → propfirm/compliance_engine.py
Analytics?                   → propfirm/reporting_engine.py
Main backtest?               → propfirm/unified_backtest.py
Usage examples?              → propfirm/examples.py
Full docs?                   → propfirm/ARCHITECTURE.md


THIS REFERENCE GUIDE IS COMPLETE!
You're ready to build production prop firm backtests.
"""

# This is documentation
pass
