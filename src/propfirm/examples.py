"""
PropFirm Backtest System - Example Usage & Integration Guide
═════════════════════════════════════════════════════════════════════════

This module demonstrates:
1. How to use presets (Apex, Lucid, Topstep)
2. How to customize rules
3. How to run backtests with the 3-layer system
4. How to access reports and analytics
"""

import pandas as pd
from datetime import datetime, timedelta

from propfirm.account_rules import (
    create_apex_preset,
    create_lucid_preset,
    create_topstep_preset,
    AccountConfig,
)
from propfirm.trading_rules import (
    TradingRules,
    RiskManagementRules,
    create_apex_trading_rules,
    create_lucid_trading_rules,
    create_topstep_trading_rules,
    create_risk_management_professional,
)
from propfirm.payout_rules import (
    PayoutRules,
    create_apex_payout_rules,
    create_lucid_payout_rules,
    create_topstep_payout_rules,
)
from propfirm.unified_backtest import UnifiedPropFirmBacktest


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: Run Backtest with Lucid Preset
# ════════════════════════════════════════════════════════════════════════════

def example_lucid_backtest():
    """
    Run a backtest using Lucid's preset rules
    
    Lucid Rules:
    ✅ $50K account
    ✅ 1-step evaluation
    ✅ 6% profit target ($3000)
    ✅ 5% max drawdown ($2500)
    ✅ End-of-day trailing drawdown
    ✅ 5 minimum trading days
    ✅ 50% consistency rule (best day ≤ 50% profit)
    """
    
    # Load or generate sample data
    data = _generate_sample_data()
    
    # Create backtest with Lucid preset
    backtest = UnifiedPropFirmBacktest(
        account_config=create_lucid_preset(account_size=50000),
        trading_rules=create_lucid_trading_rules(),
        risk_rules=create_risk_management_professional(),
        payout_rules=create_lucid_payout_rules(),
    )
    
    # Run backtest
    result = backtest.run(
        data=data,
        symbol='ES',
        entry_col='BUY',
        exit_col='SELL',
        sl_pips=50,
        tp_pips=100,
    )
    
    # Get results
    print("\\n" + "="*80)
    print("LUCID BACKTEST RESULT")
    print("="*80)
    print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    print(f"Reason: {result['reason']}")
    
    if result['summary']:
        print(f"\\nBalance: ${result['summary']['balance']['current']:.2f}")
        print(f"P&L: ${result['summary']['balance']['cumulative_pnl']:.2f} ({result['summary']['balance']['cumulative_pnl_pct']})")
        print(f"Drawdown: {result['summary']['drawdown']['current']} (Max: {result['summary']['drawdown']['max']})")
        print(f"Trades: {result['summary']['trading']['total_trades']} (Win Rate: {result['summary']['trading']['win_rate']})")
    
    return result


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: Run Backtest with Apex Preset
# ════════════════════════════════════════════════════════════════════════════

def example_apex_backtest():
    """
    Run a backtest using Apex's strict rules
    
    Apex Rules:
    ✅ $50K account
    ✅ 1-step evaluation
    ✅ 6% profit target ($3000)
    ✅ 5% max drawdown ($2500)
    ✅ INTRADAY trailing drawdown (REAL-TIME, STRICT)
    ✅ 0 minimum trading days
    ❌ NO consistency rule
    """
    
    data = _generate_sample_data()
    
    backtest = UnifiedPropFirmBacktest(
        account_config=create_apex_preset(account_size=50000),
        trading_rules=create_apex_trading_rules(),
        risk_rules=create_risk_management_professional(),
        payout_rules=create_apex_payout_rules(),
    )
    
    result = backtest.run(
        data=data,
        symbol='ES',
        entry_col='BUY',
        exit_col='SELL',
        sl_pips=50,
        tp_pips=100,
    )
    
    print("\\n" + "="*80)
    print("APEX BACKTEST RESULT")
    print("="*80)
    print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    print(f"Reason: {result['reason']}")
    
    return result


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: Run Backtest with Custom Rules
# ════════════════════════════════════════════════════════════════════════════

def example_custom_backtest():
    """
    Create custom rules tailored to your strategy
    """
    
    from propfirm.account_rules import (
        AccountConfig, PhaseRules, EvaluationType, DrawdownType, TrailMode
    )
    
    # Create custom account config
    custom_account = AccountConfig(
        account_id="my_custom_account",
        firm_name="MyFirm",
        initial_balance=50000,
        evaluation_type=EvaluationType.ONE_STEP,
        phases=[
            PhaseRules(
                profit_target=2500,  # $2500 target
                drawdown_type=DrawdownType.TRAILING,
                max_drawdown=2000,  # $2000 max loss
                trail_mode=TrailMode.END_OF_DAY,
                min_days=3,
                max_days=60,
                consistency_rule_pct=40,  # Strict: best day ≤ 40%
            )
        ]
    )
    
    # Create custom trading rules
    custom_trading = TradingRules(
        min_trading_days=3,
        max_contracts_total=3,
        allow_overnight=False,
        enable_daily_loss_limit=True,
        max_daily_loss_amount=500,  # $500 per day
    )
    
    # Create custom risk rules
    custom_risk = RiskManagementRules(
        risk_per_trade_pct=0.5,  # 0.5% per trade
        min_rr_ratio=2.5,
        min_win_rate_pct=40,
    )
    
    # Create custom payout rules
    custom_payout = create_lucid_payout_rules()
    
    # Run backtest
    data = _generate_sample_data()
    
    backtest = UnifiedPropFirmBacktest(
        account_config=custom_account,
        trading_rules=custom_trading,
        risk_rules=custom_risk,
        payout_rules=custom_payout,
    )
    
    result = backtest.run(data=data, symbol='ES')
    
    print("\\n" + "="*80)
    print("CUSTOM BACKTEST RESULT")
    print("="*80)
    print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    print(f"Reason: {result['reason']}")
    
    return result


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Accessing Detailed Reports
# ════════════════════════════════════════════════════════════════════════════

def example_detailed_reporting():
    """Show how to access comprehensive reports"""
    
    data = _generate_sample_data()
    
    backtest = UnifiedPropFirmBacktest(
        account_config=create_lucid_preset(50000),
        trading_rules=create_lucid_trading_rules(),
        risk_rules=create_risk_management_professional(),
        payout_rules=create_lucid_payout_rules(),
    )
    
    result = backtest.run(data=data, symbol='ES')
    
    # Dashboard Summary (quick view)
    dashboard = backtest.get_live_status()
    print("\\n" + "="*80)
    print("DASHBOARD SUMMARY")
    print("="*80)
    print(f"Account: {dashboard['account_status']['account_id']}")
    print(f"Status: {dashboard['account_status']['status']}")
    print(f"Result: {'PASSED' if dashboard['account_status']['passed'] else 'FAILED'}")
    print(f"Current Balance: ${dashboard['balance']['current']:.2f}")
    print(f"P&L: ${dashboard['balance']['cumulative_pnl']:.2f} ({dashboard['balance']['cumulative_pnl_pct']})")
    print(f"Drawdown: {dashboard['drawdown']['current']} (Max: {dashboard['drawdown']['max']})")
    print(f"Profit Target: {dashboard['profit_target']['progress_pct']}")
    print(f"Compliance Score: {dashboard['compliance']['score']}")
    
    # Detailed Report (full analysis)
    detailed = backtest.reporting_engine.get_detailed_report()
    
    print("\\n" + "="*80)
    print("PERFORMANCE METRICS")
    print("="*80)
    metrics = detailed['performance_metrics']
    print(f"Total Trades: {dashboard['trading']['total_trades']}")
    print(f"Win Rate: {dashboard['trading']['win_rate']}")
    print(f"Profit Factor: {dashboard['trading']['profit_factor']}")
    print(f"Best Day: {metrics['best_day']}")
    print(f"Best Day % of Total: {metrics['best_day_pct_of_total']}")
    print(f"Max Consecutive Losses: {metrics['max_consecutive_losses']}")
    
    # Trade Log
    print("\\n" + "="*80)
    print("TRADE LOG")
    print("="*80)
    for trade in detailed['trade_log'][:5]:  # Show first 5 trades
        print(f"Trade {trade['trade_num']}: {trade['type']} {trade['symbol']} "
              f"@ {trade['entry_price']:.2f} → {trade['exit_price']:.2f} "
              f"| P&L: ${trade['pnl']:.2f}")
    
    return result


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: Comparing Firm Presets
# ════════════════════════════════════════════════════════════════════════════

def example_compare_presets():
    """
    Compare performance across different preset firms
    Useful for: determining which firm rules suit your strategy
    """
    
    data = _generate_sample_data()
    
    presets = [
        ("Apex", create_apex_preset, create_apex_trading_rules, create_apex_payout_rules),
        ("Lucid", create_lucid_preset, create_lucid_trading_rules, create_lucid_payout_rules),
        ("Topstep", create_topstep_preset, create_topstep_trading_rules, create_topstep_payout_rules),
    ]
    
    results = {}
    
    print("\\n" + "="*80)
    print("PRESET COMPARISON")
    print("="*80)
    
    for firm_name, account_fn, trading_fn, payout_fn in presets:
        backtest = UnifiedPropFirmBacktest(
            account_config=account_fn(50000),
            trading_rules=trading_fn(),
            risk_rules=create_risk_management_professional(),
            payout_rules=payout_fn(),
        )
        
        result = backtest.run(data=data.copy(), symbol='ES')
        results[firm_name] = result
        
        print(f"\\n{firm_name}:")
        print(f"  Result: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
        print(f"  Reason: {result['reason']}")
        if result['summary']:
            print(f"  P&L: ${result['summary']['balance']['cumulative_pnl']:.2f}")
            print(f"  Drawdown: {result['summary']['drawdown']['current']}")
    
    return results


# ════════════════════════════════════════════════════════════════════════════
# HELPER: Generate Sample Data
# ════════════════════════════════════════════════════════════════════════════

def _generate_sample_data(num_candles=1000):
    """
    Generate synthetic trading data with BUY/SELL signals
    
    For production: load real OHLC data and apply your strategy indicators
    """
    
    import numpy as np
    
    # Generate prices with random walk
    returns = np.random.normal(0.0001, 0.005, num_candles)
    prices = 5000 * np.exp(np.cumsum(returns))
    
    # Create OHLC
    data = pd.DataFrame({
        'timestamp': pd.date_range(start=datetime.now() - timedelta(days=5), periods=num_candles, freq='5T'),
        'open': prices + np.random.normal(0, 5, num_candles),
        'high': prices + abs(np.random.normal(10, 5, num_candles)),
        'low': prices - abs(np.random.normal(10, 5, num_candles)),
        'close': prices,
        'volume': np.random.randint(1000, 10000, num_candles),
    })
    
    # Add simple buy/sell signals (MA crossover simulation)
    data['SMA_10'] = data['close'].rolling(10).mean()
    data['SMA_20'] = data['close'].rolling(20).mean()
    data['BUY'] = (data['SMA_10'] > data['SMA_20']).astype(int)
    data['SELL'] = (data['SMA_10'] < data['SMA_20']).astype(int)
    
    # Clean NaN
    data = data.dropna()
    
    return data


# ════════════════════════════════════════════════════════════════════════════
# RUN EXAMPLES
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\\n🚀 PropFirm Backtest System - Examples\\n")
    
    # Run examples
    # example_lucid_backtest()
    # example_apex_backtest()
    # example_custom_backtest()
    # example_detailed_reporting()
    # example_compare_presets()
    
    print("\\n✅ Examples ready to run!")
    print("\\nUncomment the examples in __main__ to execute them")
