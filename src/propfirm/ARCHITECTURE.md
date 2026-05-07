"""
PROPFIRM 3-LAYER ARCHITECTURE GUIDE
═════════════════════════════════════════════════════════════════════════

SYSTEM OVERVIEW
───────────────────────────────────────────────────────────────────────

Your backtest system is now organized in 3 independent layers:

┌─────────────────────────────────────────────────────────────────────┐
│                        MARKET ENGINE                                 │
│                   (Trades & P&L Calculation)                         │
│                                                                       │
│  • Execute trades based on signals                                   │
│  • Calculate profit/loss                                             │
│  • Track open positions                                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      ACCOUNT ENGINE                                  │
│              (Balance, Drawdown, Phase Tracking)                     │
│                                                                       │
│  • Update real-time balance                                          │
│  • Track peak balance                                                │
│  • Calculate drawdown (fixed / trailing intraday / trailing EOD)     │
│  • Manage daily/weekly/monthly P&L                                   │
│  • Handle phase transitions (1-step or 2-step)                       │
│  • Enforce profit targets                                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLIANCE ENGINE                                 │
│              (Rule Validation & Breach Detection)                    │
│                                                                       │
│  ✅ Pre-entry validation:   Position size, RR ratio, news trading    │
│  ✅ Post-trade checks:      Daily loss, drawdown, consistency        │
│  ✅ Daily boundaries:       Overnight holding, trading days,         │
│                             minimum days requirements                 │
│  ✅ Account pass/fail determination                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    REPORTING ENGINE                                  │
│              (Analytics & Performance Metrics)                       │
│                                                                       │
│  • Performance metrics (win rate, profit factor, etc)                │
│  • Dashboard summaries                                               │
│  • Detailed trade logs                                               │
│  • Pass/fail determination                                           │
│  • Compliance reports                                                │
└─────────────────────────────────────────────────────────────────────┘


LAYER 1: ACCOUNT & FUNDING RULES (account_rules.py)
─────────────────────────────────────────────────────────────────────

Purpose: Define what each firm's challenge looks like

Key Data Models:
  • AccountConfig       Main account configuration container
  • PhaseRules          Rules for each evaluation phase (1 or 2)
  • EvaluationType      ONE_STEP vs TWO_STEP
  • DrawdownType        FIXED vs TRAILING
  • TrailMode           INTRADAY vs END_OF_DAY

Example Usage:
  account = create_lucid_preset(50000)
  # → Creates Lucid $50K config:
  #   - 1-step evaluation
  #   - $3K profit target (6%)
  #   - $2.5K max drawdown (5%)
  #   - End-of-day trailing (realistic)
  #   - 5 min trading days
  #   - 50% consistency rule (best day ≤ 50% profit)

Key Presets:
  ✅ Apex:    Intraday trailing, no min days, no consistency
  ✅ Lucid:   EOD trailing, 5 min days, 50% consistency
  ✅ Topstep: 2-step, EOD trailing, flexible rules


LAYER 2: TRADING RESTRICTIONS & RISK RULES
────────────────────────────────────────────────────────────────────

Purpose: Enforce trader behavior and risk limits

Modules:
  • trading_rules.py        Trading restrictions (hours, positions, etc)
  • payout_rules.py         Profit splits and earnings rules

Key Data Models:
  • TradingRules           Position limits, session restrictions, holidays
  • RiskManagementRules    Risk per trade, consecutive losses, RR ratios
  • ConsistencyRule        Best day ≤ X% of profit
  • ProfitSplitRules       Trader %, firm %, tiered splits
  • ScalingPlan            Account scaling after profit milestones
  • ResetRules             Account reset options

Example Usage - Lucid:
  trading = create_lucid_trading_rules()
  # → Creates:
  #   - Min 5 trading days
  #   - Max 4 contracts per trade
  #   - No overnight holds
  #   - No weekend trading
  #   - No trading during news (±2 min)
  #   - No daily loss limit

  payout = create_lucid_payout_rules()
  # → Creates:
  #   - 90% flat profit split
  #   - 50% consistency rule ENFORCED
  #   - Scaling available after $3K profit


LAYER 3: ACCOUNT LIFECYCLE ENGINES
────────────────────────────────────────────────────────────────────

Purpose: Simulate real account trading and compliance

Modules:
  • account_engine.py       Real-time balance and drawdown tracking
  • compliance_engine.py    Rule validation and breach detection
  • reporting_engine.py     Analytics and performance reporting
  • unified_backtest.py     Main execution engine (combines all 3)

Key Components:

  A) AccountEngine
     ├─ current_balance          Real-time account balance
     ├─ peak_balance             Highest balance ever
     ├─ trailing_peak_balance    Trailing DD calculation
     ├─ current_drawdown         Loss from peak
     ├─ current_phase            1 or 2
     ├─ phase_profit_target      Target for current phase
     ├─ daily_records            Per-day breakdown
     └─ Methods:
        • update_balance()       Update balance after trade
        • check_profit_target()  Did we hit target?
        • close_trading_day()    End-of-day processing
        • fail_account()         Mark failed

  B) ComplianceEngine
     ├─ Pre-entry validation:
     │  • Position size limits (total & per-symbol)
     │  • Risk/reward ratio
     │  • News trading blackout
     │  • After-hours trading
     │  • Overnight holds
     │
     ├─ Post-trade checks:
     │  • Daily loss limits
     │  • Drawdown breach
     │  • Consistency violation
     │  • Consecutive losses
     │
     └─ Daily boundaries:
        • Min trading days
        • Overnight position holding
        • Weekend restrictions

  C) ReportingEngine
     ├─ Performance metrics:
     │  • Win rate, win/loss counts
     │  • Profit factor, expectancy
     │  • Best/worst day
     │  • Max consecutive losses
     │
     ├─ Pass/fail determination:
     │  • Check critical breaches
     │  • Verify profit target
     │  • Check min trading days
     │  • Check consistency
     │
     └─ Reports:
        • Dashboard summary (quick view)
        • Detailed report (full analysis)
        • Trade logs
        • Compliance reports


LAYER 4: UNIFIED BACKTEST ENGINE (unified_backtest.py)
──────────────────────────────────────────────────────────────────

Purpose: Master orchestrator that brings all 3 layers together

Main Class: UnifiedPropFirmBacktest

Usage:
  backtest = UnifiedPropFirmBacktest(
      account_config=create_lucid_preset(50000),
      trading_rules=create_lucid_trading_rules(),
      risk_rules=create_risk_management_professional(),
      payout_rules=create_lucid_payout_rules(),
  )
  
  result = backtest.run(
      data=df_with_signals,
      symbol='ES',
      entry_col='BUY',
      exit_col='SELL',
      sl_pips=50,
      tp_pips=100,
  )

Execution Loop:
  FOR each candle in data:
      # 1. Check for entry signal
      IF signal appears:
          → ComplianceEngine.validate_trade_entry()  # Pre-entry check
          → If OK, execute trade
          → Add to trades_log
      
      # 2. Check for exit condition (SL/TP hit or signal)
      IF exit condition met:
          → Calculate P&L
          → ComplianceEngine.validate_trade_exit()   # Post-exit check
          → AccountEngine.update_balance()            # Update account
          → ComplianceEngine.check_post_trade_compliance()
          → If critical breach → Account fails

  AT day boundary:
      → AccountEngine.close_trading_day()
      → ComplianceEngine.check_daily_boundary()

  WHEN backtest ends:
      → ReportingEngine.determine_pass_fail()
      → Return comprehensive result


EDITING RULES FOR YOUR STRATEGIES
────────────────────────────────────────────────────────────────────

The entire rule system is EDITABLE. Here's how:

1) Create custom AccountConfig for unique profit/drawdown targets
   
   from propfirm.account_rules import AccountConfig, PhaseRules
   
   custom = AccountConfig(
       initial_balance=50000,
       phases=[PhaseRules(
           profit_target=4000,
           max_drawdown=2000,
           min_days=7,
           consistency_rule_pct=40,
       )]
   )

2) Create custom TradingRules for position limits
   
   trading = TradingRules(
       min_trading_days=3,
       max_contracts_total=5,
       max_daily_loss_amount=1000,
       allow_overnight=False,
   )

3) Create custom RiskManagementRules
   
   risk = RiskManagementRules(
       risk_per_trade_pct=1.0,
       min_rr_ratio=2.0,
       max_consecutive_losing_trades=5,
   )

4) Create custom PayoutRules
   
   payout = PayoutRules(
       consistency=ConsistencyRule(enabled=False),
       profit_split=ProfitSplitRules(flat_split_pct=85),
   )


KEY DIFFERENCES: APEX vs LUCID vs TOPSTEP
──────────────────────────────────────────────────────────────────

Feature                 Apex           Lucid          Topstep
───────────────────────────────────────────────────────────────────
Evaluation              1-step         1-step         2-step
Drawdown Type           INTRADAY       EOD            EOD
Max Drawdown            5%             5%             5%
Profit Target           6%             6%             Phase1: 6%, Phase2: 4%
Min Trading Days        0              5              5
Consistency Rule        ❌ No          ✅ Yes (50%)   ❌ No
Daily Loss Limit        ❌ No          ❌ No          ✅ Yes ($1K)
Profit Split            90% flat       90% flat       90% flat
Scaling Available       ✅ Yes         ✅ Yes         ❌ No (2-step instead)
News Trading Wait       ❌ No          ✅ 2 min bfr   ✅ 2 min bfr


WORKFLOW EXAMPLE: Running Backtests
────────────────────────────────────────────────────────────────────

Step 1: Load your strategy data
  df = pd.read_csv('es_5min_data.csv')
  df['BUY'] = your_buy_signal_logic(df)
  df['SELL'] = your_sell_signal_logic(df)

Step 2: Choose a firm preset
  account = create_lucid_preset(50000)
  trading = create_lucid_trading_rules()
  risk = create_risk_management_professional()
  payout = create_lucid_payout_rules()

Step 3: Create backtest engine
  backtest = UnifiedPropFirmBacktest(
      account_config=account,
      trading_rules=trading,
      risk_rules=risk,
      payout_rules=payout,
  )

Step 4: Run backtest
  result = backtest.run(df, symbol='ES', sl_pips=50, tp_pips=100)

Step 5: Analyze results
  if result['passed']:
      print("✅ PASSED!")
  else:
      print(f"❌ FAILED: {result['reason']}")
  
  dashboard = backtest.get_live_status()
  # or for detailed analysis:
  detailed = backtest.reporting_engine.get_detailed_report()


COMMON EDITS FOR YOUR RULES
────────────────────────────────────────────────────────────────────

Edit 1: Stricter consistency rule
  payout_rules.consistency.best_day_max_pct = 25  # Best day ≤ 25% of profit

Edit 2: Smaller daily loss limit
  trading_rules.max_daily_loss_amount = 500  # $500 max per day

Edit 3: Require more trading days
  account_config.phases[0].min_days = 10  # Min 10 trading days

Edit 4: Higher position limits
  trading_rules.max_contracts_total = 10
  trading_rules.max_contracts_per_symbol['ES'] = 8

Edit 5: Trailing instead of fixed drawdown
  phase_rules.drawdown_type = DrawdownType.TRAILING
  phase_rules.trail_mode = TrailMode.INTRADAY  # Real-time (Apex-style)


FILES INCLUDED IN THIS SYSTEM
──────────────────────────────────────────────────────────────────

Core Modules:
  ✅ propfirm/account_rules.py          Account & evaluation phases
  ✅ propfirm/trading_rules.py          Trading restrictions & risk
  ✅ propfirm/payout_rules.py           Earnings, consistency, payouts
  ✅ propfirm/account_engine.py         Real-time account tracking
  ✅ propfirm/compliance_engine.py      Rule validation & breaches
  ✅ propfirm/reporting_engine.py       Analytics & reports
  ✅ propfirm/unified_backtest.py       Master execution engine
  ✅ propfirm/examples.py               Example usage

Usage:
  from propfirm.account_rules import create_lucid_preset
  from propfirm.trading_rules import create_lucid_trading_rules
  from propfirm.payout_rules import create_lucid_payout_rules
  from propfirm.unified_backtest import UnifiedPropFirmBacktest


NEXT STEPS
──────────────────────────────────────────────────────────────────

1. Load your real OHLC data and generate entry signals
2. Choose preset or customize rules
3. Run backtest with UnifiedPropFirmBacktest
4. Analyze results and iterate
5. Fine-tune rules to match your strategy

This system is PRODUCTION-READY for analyzing prop firm trading challenges!
"""

# This file is just documentation - import from the modules above
pass
