"""PropFirm System Demo

Complete system demonstration with sample data.
Shows how the 3-layer prop firm system works end-to-end.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from propfirm.unified_backtest import UnifiedPropFirmBacktest
from propfirm.account_rules import (
    create_apex_preset,
    create_lucid_preset,
    create_topstep_preset,
)
from propfirm.trading_rules import (
    create_apex_trading_rules,
    create_lucid_trading_rules,
    create_topstep_trading_rules,
    create_risk_management_professional,
)
from propfirm.payout_rules import (
    create_apex_payout_rules,
    create_lucid_payout_rules,
    create_topstep_payout_rules,
)


def generate_sample_data(num_candles=500, symbol='ES'):
    """Generate synthetic trading data with entry/exit signals."""
    
    print(f"Generating {num_candles} candles for {symbol}...")
    
    # Generate realistic price movement
    np.random.seed(42)
    returns = np.random.normal(0.0002, 0.008, num_candles)
    
    if symbol == 'ES':
        start_price = 5000
    elif symbol == 'NQ':
        start_price = 18000
    elif symbol == 'GC':
        start_price = 2000
    else:
        start_price = 100
    
    prices = start_price * np.exp(np.cumsum(returns))
    
    # Create OHLC
    data = pd.DataFrame({
        'timestamp': pd.date_range(
            start=datetime.now() - timedelta(days=10),
            periods=num_candles,
            freq='5T'
        ),
        'open': prices + np.random.normal(0, 2, num_candles),
        'high': prices + abs(np.random.normal(5, 2, num_candles)),
        'low': prices - abs(np.random.normal(5, 2, num_candles)),
        'close': prices,
        'volume': np.random.randint(1000, 5000, num_candles),
    })
    
    # Add simple moving average signals
    data['SMA_10'] = data['close'].rolling(10).mean()
    data['SMA_20'] = data['close'].rolling(20).mean()
    
    # Generate entry/exit signals
    data['BUY'] = ((data['SMA_10'] > data['SMA_20']) & 
                   (data['SMA_10'].shift(1) <= data['SMA_20'].shift(1))).astype(int)
    data['SELL'] = ((data['SMA_10'] < data['SMA_20']) & 
                    (data['SMA_10'].shift(1) >= data['SMA_20'].shift(1))).astype(int)
    
    # Remove NaN
    data = data.dropna().reset_index(drop=True)
    
    print(f"✅ Generated {len(data)} valid candles")
    print(f"   Price range: {data['close'].min():.2f} - {data['close'].max():.2f}")
    print(f"   Signals: {data['BUY'].sum()} buy, {data['SELL'].sum()} sell\\n")
    
    return data


def run_single_backtest(preset_name, account_fn, trading_fn, payout_fn, data, symbol):
    """Run backtest with a single preset"""
    
    print(f"\\n{'='*70}")
    print(f"🎯 TESTING: {preset_name}")
    print(f"{'='*70}")
    
    try:
        # Create backtest engine
        backtest = UnifiedPropFirmBacktest(
            account_config=account_fn(50000),
            trading_rules=trading_fn(),
            risk_rules=create_risk_management_professional(),
            payout_rules=payout_fn(),
        )
        
        # Run backtest
        result = backtest.run(
            data=data.copy(),
            symbol=symbol,
            entry_col='BUY',
            exit_col='SELL',
            sl_pips=30,
            tp_pips=60,
        )
        
        # Display results
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"Result: {status}")
        print(f"Reason: {result['reason']}")
        print()
        
        if result['summary']:
            summary = result['summary']
            
            print("📊 ACCOUNT STATUS")
            print(f"  Initial Balance:    ${summary['balance']['initial']:,.2f}")
            print(f"  Current Balance:    ${summary['balance']['current']:,.2f}")
            print(f"  Peak Balance:       ${summary['balance']['peak']:,.2f}")
            print(f"  P&L:                ${summary['balance']['cumulative_pnl']:,.2f} ({summary['balance']['cumulative_pnl_pct']})")
            print()
            
            print("📉 DRAWDOWN METRICS")
            print(f"  Current Drawdown:   {summary['drawdown']['current']}")
            print(f"  Max Drawdown:       {summary['drawdown']['max']}")
            print(f"  Max Allowed:        {summary['drawdown']['threshold']}")
            print()
            
            print("🎯 PROFIT TARGET")
            print(f"  Target:             {summary['profit_target']['target']}")
            print(f"  Progress:           {summary['profit_target']['current_progress']}")
            print(f"  Achievement:        {summary['profit_target']['progress_pct']}")
            print()
            
            print("📈 TRADING METRICS")
            print(f"  Total Trades:       {summary['trading']['total_trades']}")
            print(f"  Winning Trades:     {summary['trading']['winning_trades']}")
            print(f"  Losing Trades:      {summary['trading']['losing_trades']}")
            print(f"  Win Rate:           {summary['trading']['win_rate']}")
            print(f"  Profit Factor:      {summary['trading']['profit_factor']}")
            print(f"  Best Day:           {summary['trading']['best_day']}")
            print(f"  Worst Day:          {summary['trading']['worst_day']}")
            print()
            
            print("📅 TRADING DAYS")
            print(f"  Days Traded:        {summary['days']['trading_days']}")
            print(f"  Days Required:      {summary['days']['min_required']}")
            print()
            
            print("✔️  COMPLIANCE")
            print(f"  Compliance Score:   {summary['compliance']['score']}")
            print(f"  Breaches:           {summary['compliance']['breaches']}")
            print(f"  Critical Breaches:  {summary['compliance']['critical_breaches']}")
        
        return result
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None


def compare_all_presets(data, symbol='ES'):
    """Compare performance across all preset firms"""
    
    print("\\n" + "="*70)
    print("🔄 COMPARING ALL PRESET FIRMS")
    print("="*70)
    
    presets = [
        ("APEX", create_apex_preset, create_apex_trading_rules, create_apex_payout_rules),
        ("LUCID", create_lucid_preset, create_lucid_trading_rules, create_lucid_payout_rules),
        ("TOPSTEP", create_topstep_preset, create_topstep_trading_rules, create_topstep_payout_rules),
    ]
    
    results = {}
    
    for preset_name, account_fn, trading_fn, payout_fn in presets:
        result = run_single_backtest(
            preset_name,
            account_fn,
            trading_fn,
            payout_fn,
            data,
            symbol
        )
        results[preset_name] = result
    
    # Summary comparison
    print("\\n" + "="*70)
    print("📊 COMPARISON SUMMARY")
    print("="*70)
    print(f"{'Firm':<12} {'Result':<15} {'P&L':<15} {'Drawdown':<12} {'Trades':<10}")
    print("-"*70)
    
    for preset_name, result in results.items():
        if result and result['summary']:
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            pnl = result['summary']['balance']['cumulative_pnl']
            dd = result['summary']['drawdown']['current']
            trades = result['summary']['trading']['total_trades']
            print(f"{preset_name:<12} {status:<15} ${pnl:>12,.2f} {dd:>12} {trades:>10}")
    
    return results


def test_custom_rules(data, symbol='ES'):
    """Example of creating custom rules"""
    
    from propfirm.account_rules import AccountConfig, PhaseRules, DrawdownType, TrailMode
    from propfirm.trading_rules import TradingRules, RiskManagementRules
    from propfirm.payout_rules import PayoutRules, ConsistencyRule
    
    print("\\n" + "="*70)
    print("⚙️  TESTING CUSTOM RULES")
    print("="*70)
    
    # Create custom configuration
    custom_account = AccountConfig(
        account_id="custom_experiment",
        firm_name="MyCustomFirm",
        initial_balance=50000,
        phases=[
            PhaseRules(
                profit_target=2500,         # $2.5K target
                profit_target_pct=5,        # 5% of account
                drawdown_type=DrawdownType.TRAILING,
                max_drawdown=1500,          # $1.5K max loss
                max_drawdown_pct=3,         # 3% of account
                trail_mode=TrailMode.INTRADAY,  # Real-time (strict)
                min_days=3,
                max_days=30,
            )
        ]
    )
    
    custom_trading = TradingRules(
        min_trading_days=3,
        max_contracts_total=3,
        allow_overnight=False,
        enable_daily_loss_limit=True,
        max_daily_loss_amount=400,  # $400 max per day
    )
    
    custom_risk = RiskManagementRules(
        risk_per_trade_pct=0.5,  # 0.5% per trade
        min_rr_ratio=3.0,        # Higher RR requirement
    )
    
    custom_payout = PayoutRules(
        consistency=ConsistencyRule(
            enabled=True,
            best_day_max_pct=30,  # Strict: best day ≤ 30%
        )
    )
    
    backtest = UnifiedPropFirmBacktest(
        account_config=custom_account,
        trading_rules=custom_trading,
        risk_rules=custom_risk,
        payout_rules=custom_payout,
    )
    
    result = backtest.run(
        data=data.copy(),
        symbol=symbol,
        entry_col='BUY',
        exit_col='SELL',
        sl_pips=30,
        tp_pips=60,
    )
    
    if result:
        print(f"Custom Rules Result: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
        print(f"Reason: {result['reason']}")
        
        if result.get('summary'):
            summary = result['summary']
            pnl = summary.get('balance', {}).get('cumulative_pnl')
            dd = summary.get('drawdown', {}).get('current')
            if pnl is not None:
                print(f"P&L: ${pnl:.2f}")
            if dd is not None:
                print(f"Drawdown: {dd}")
    else:
        print("❌ ERROR: Backtest failed to run")
    
    return result


def main():
    """Main execution"""
    
    print("\\n" + "="*70)
    print("🚀 PROPFIRM BACKTEST SYSTEM - COMPLETE DEMO")
    print("="*70)
    print()
    
    # Generate sample data
    data = generate_sample_data(num_candles=500, symbol='ES')
    
    # Test 1: Run all presets
    preset_results = compare_all_presets(data, symbol='ES')
    
    # Test 2: Run custom rules
    custom_result = test_custom_rules(data, symbol='ES')
    
    # Final summary
    print("\\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    print(f"\\nPresets tested: {len(preset_results)}")
    print(f"Custom configs tested: 1")
    print(f"\\nYour backtest system is ready!")
    print("📢 Next step: Load your real data and strategy")


if __name__ == "__main__":
    main()
