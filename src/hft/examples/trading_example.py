"""HFT Trading System Examples

Demonstrates HFT Scalping strategy backtesting and performance analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import json
from datetime import datetime

from hft.strategies.hft_scalping_strategy import (
    HFTScalpingStrategy,
    HFTRiskManager,
    HFTPerformanceAnalyzer
)
from hft.utils.hft_backtest_engine import (
    HFTBacktestEngine,
    ExecutionParams,
    ExecutionVenue
)


class HFTTradingExample:
    """HFT trading system example"""
    
    @staticmethod
    def mt5_setup_guide() -> str:
        """MT5 HFT EA setup instructions"""
        guide = """
MT5 HFT EA SETUP

1. Install
   - Copy HFTScalpingEA.mq5 to MQL5/Experts folder
   - Restart MT5 or press F5

2. Compile
   - Open MetaEditor (Ctrl+Shift+E)
   - Open HFTScalpingEA.mq5
   - Compile (F5)

3. Configure
   - Set risk_percent_per_trade = 0.5
   - Set max_daily_loss_percent = 5.0
   - Adjust MA periods: fast=5, slow=20
   - RSI: period=14, oversold=30

4. Attach to Chart
   - Open chart for desired instrument
   - Drag EA to chart
   - Enable AutoTrading

5. Monitor
   - Watch Trade Log for entries/exits
   - Check daily balance updates
"""
  - rsi_overbought = 70

Stop Loss / Take Profit:
  - fixed_sl_pips = 0 (Use 0 for automatic ATR-based)
  - fixed_tp_pips = 0 (Use 0 for automatic ATR-based)
  - atr_period = 14
  - atr_sl_multiple = 1.5 (SL = Entry ± 1.5 × ATR)
  - atr_tp_multiple = 0.75 (TP = Entry ± 0.75 × ATR) - TIGHT for HFT

Position Management:
  - max_open_positions = 3 (Max simultaneous trades)
  - max_trades_per_hour = 20 (Rate limiting)
  - min_bars_between_trades = 2 (Prevents over-trading)

STEP 4: ATTACH TO CHART
────────────────────────
1. Open a chart for your target symbol (e.g., EURUSD)
2. Timeframe: M1, M5, or M15 (HFT timeframes)
3. Go to: Insert → Expert Advisors → HFTScalpingEA
4. Or drag the EA from Navigator onto the chart
5. In the properties dialog:
   - Go to "Inputs" tab
   - Configure parameters
   - Enable "Allow DLL imports" if needed
   - Click OK

STEP 5: BACKTEST IN STRATEGY TESTER
────────────────────────────────────
1. In MT5, go to: View → Strategy Tester (Ctrl+R)
2. Settings:
   - Expert Advisor: HFTScalpingEA
   - Symbol: EURUSD (or your symbol)
   - Timeframe: M5
   - Period: Last 6-12 months
   - Model: Every Tick (most realistic for HFT)
   - Optimization: Enable for parameter optimization
3. Click "Start" to begin testing
4. Review results:
   - Win Rate (target: >50%)
   - Profit Factor (target: >1.5)
   - Max Drawdown (target: <15%)
   - Sharpe Ratio (target: >1.0)

STEP 6: LIVE TRADING (DEMO FIRST!)
──────────────────────────────────
🚨 IMPORTANT: ALWAYS TEST ON DEMO ACCOUNT FIRST!

1. Start with demo account:
   - Low risk exposure
   - Real order execution
   - Test actual conditions
   
2. Monitor for at least 1-2 weeks
   
3. Check:
   - Actual slippage vs backtest
   - Execution speed
   - Win rate in live conditions
   - Drawdown management
   
4. Only move to live if satisfied with demo results

RECOMMENDED SYMBOLS FOR HFT
──────────────────────────
✓ EURUSD - Most liquid, tight spreads
✓ GBPUSD - Good liquidity
✓ USDJPY - Lower spread variance
✗ Exotic pairs - Wide spreads, not suitable for HFT

RECOMMENDED HOURS FOR HFT
────────────────────────
✓ European Session (8:00-12:00 UTC)
✓ US Session (13:00-17:00 UTC)
✓ Overlap (12:00-13:00 UTC)
✗ Asian Session (off-hours) - Lower liquidity

TROUBLESHOOTING
───────────────
Q: EA won't attach to chart?
A: Check compilation errors, enable algo trading in tools

Q: Getting too much slippage?
A: Reduce position size, change broker, avoid news times

Q: Drawdown too high?
A: Lower risk_percent_per_trade, increase max_consecutive_losses

Q: Not enough trades?
A: Check signal generation, adjust MA periods

Q: Execution too slow?
A: Use VPS, reduce position size, optimize code

PERFORMANCE BENCHMARKS
──────────────────────
Target Monthly Returns: 3-8% (HFT is risk-controlled)
Target Win Rate: 55-65%
Target Profit Factor: 1.5-2.0
Target Sharpe Ratio: 1.0-2.0
Target Max Drawdown: 5-15%

Remember: Consistency and risk management > Home run trades!
"""
        return guide
    
    @staticmethod
    def python_backtest_example(data: pd.DataFrame, strategy_type: str = "scalping") -> Dict:
        """Run HFT backtesting example."""
        
        print("\nHFT Python Backtesting")
        print("="*60)
        
        strategy = HFTScalpingStrategy(
            strategy_type=strategy_type,
            ma_fast=5,
            ma_slow=20,
            rsi_period=14,
            atr_period=14
        )
        print(f"Strategy: {strategy}")
        
        signals_df = strategy.generate_signals(data)
        print(f"Signals - Buy: {signals_df['BUY'].sum()}, Sell: {signals_df['SELL'].sum()}")
        
        exec_params = ExecutionParams(
            venue=ExecutionVenue.FOREX_ECN,
            base_spread_pips=1.0,
            slippage_pips=0.5,
            latency_ms=100
        )
        
        engine = HFTBacktestEngine(
            initial_balance=10000,
            execution_params=exec_params,
            risk_percent_per_trade=0.5,
            max_concurrent_positions=3,
            use_realistic_execution=True
        )
        
        results = engine.backtest(data, signals_df)
        
        print(f"\nResults:")
        print(f"  Total Trades: {results['total_trades']}")
        print(f"  Win Rate: {results['win_rate']:.2f}%")
        print(f"  Total P&L: ${results['total_pnl']:.2f}")
        print(f"  Return: {results['total_return_percent']:.2f}%")
        print(f"  Sharpe: {results['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {results['max_drawdown_percent']:.2f}%")
        
        return {
            'results': results,
            'trade_log': engine.get_trade_log(),
            'strategy': strategy,
            'engine': engine
        }
    
    @staticmethod
    def parameter_optimization_example(data: pd.DataFrame, param_ranges: Dict) -> pd.DataFrame:
        """Run HFT parameter optimization."""
        
        print("\nHFT Parameter Optimization")
        print("="*60)
        
        results = []
        total = 1
        for values in param_ranges.values():
            total *= len(values)
        
        print(f"Testing {total} parameter combinations...")
        
        combo = 0
        for ma_fast in param_ranges.get('ma_fast', [5]):
            for ma_slow in param_ranges.get('ma_slow', [20]):
                for atr_tp in param_ranges.get('atr_tp_multiple', [0.75]):
                    combo += 1
                    
                    # Create and test strategy
                    strategy = HFTScalpingStrategy(
                        ma_fast=ma_fast,
                        ma_slow=ma_slow,
                        atr_tp_multiple=atr_tp
                    )
                    
                    signals_df = strategy.generate_signals(data)
                    
                    # Run backtest
                    exec_params = ExecutionParams(
                        venue=ExecutionVenue.FOREX_ECN,
                        base_spread_pips=1.0,
                        slippage_pips=0.5
                    )
                    
                    engine = HFTBacktestEngine(
                        initial_balance=10000,
                        execution_params=exec_params
                    )
                    
                    backtest_results = engine.backtest(data, signals_df)
                    
                    # Store results
                    results.append({
                        'ma_fast': ma_fast,
                        'ma_slow': ma_slow,
                        'atr_tp_multiple': atr_tp,
                        'total_trades': backtest_results['total_trades'],
                        'win_rate': backtest_results['win_rate'],
                        'profit_factor': backtest_results['profit_factor'],
                        'total_return': backtest_results['total_return_percent'],
                        'max_drawdown': backtest_results['max_drawdown_percent'],
                        'sharpe_ratio': backtest_results['sharpe_ratio'],
                    })
                    
                    print(f"[{combo}/{total_combinations}] MA({ma_fast}x{ma_slow}) TP({atr_tp}) "
                          f"→ Return: {backtest_results['total_return_percent']:.2f}% "
                          f"| Win Rate: {backtest_results['win_rate']:.1f}%")
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Sort by total return (descending)
        results_df = results_df.sort_values('total_return', ascending=False)
        
        print("\n" + "-"*70)
        print("TOP 5 PARAMETER COMBINATIONS")
        print("-"*70)
        print(results_df.head(5).to_string(index=False))
        
        return results_df
    
    @staticmethod
    def risk_management_scenario_analysis() -> Dict:
        """
        Analyze different risk management scenarios
        """
        print("\n" + "="*70)
        print("RISK MANAGEMENT SCENARIO ANALYSIS")
        print("="*70)
        
        scenarios = {
            'Conservative': {
                'risk_percent': 0.3,
                'max_consecutive_losses': 5,
                'max_daily_loss': 3.0
            },
            'Moderate': {
                'risk_percent': 0.5,
                'max_consecutive_losses': 5,
                'max_daily_loss': 5.0
            },
            'Aggressive': {
                'risk_percent': 1.0,
                'max_consecutive_losses': 10,
                'max_daily_loss': 10.0
            }
        }
        
        print("\nScenario Comparison for $10,000 Account:\n")
        
        for name, params in scenarios.items():
            risk_mgr = HFTRiskManager(
                initial_balance=10000,
                risk_percent_per_trade=params['risk_percent'],
                max_consecutive_losses=params['max_consecutive_losses'],
                max_daily_loss_percent=params['max_daily_loss']
            )
            
            # Calculate metrics
            per_trade_risk = 10000 * (params['risk_percent'] / 100)
            max_position_size = per_trade_risk / 50  # Assuming 50 pips typical SL
            daily_loss_limit = 10000 * (params['max_daily_loss'] / 100)
            
            print(f"{name}:")
            print(f"  • Risk per Trade: ${per_trade_risk:.2f}")
            print(f"  • Max Position Size: {max_position_size:.2f} lots")
            print(f"  • Daily Loss Limit: ${daily_loss_limit:.2f}")
            print(f"  • Max Losses Before Pause: {params['max_consecutive_losses']}")
            print()
        
        return scenarios


def main():
    """Main example runner"""
    
    # Display MT5 setup guide
    example = HFTTradingExample()
    print(example.mt5_setup_guide())
    
    # Print Python backtesting overview
    print("\n\n" + "="*70)
    print("PYTHON BACKTESTING FRAMEWORK")
    print("="*70)
    
    print("""
The Python backtesting framework includes:

1. HFTScalpingStrategy
   - Implements 3 strategies: Scalping, Market Making, Trend Following
   - Generates trading signals from technical indicators
   - Configuration for parameters

2. HFTBacktestEngine
   - Tick-by-tick simulation
   - Realistic execution costs (spread + slippage)
   - Position management with SL/TP
   - Comprehensive performance metrics

3. HFTRiskManager
   - Position sizing based on risk
   - Stop loss/Take profit calculation
   - Daily loss tracking
   - Consecutive loss management

4. HFTPerformanceAnalyzer
   - Win rate and profit factor
   - Sharpe and Sortino ratios
   - Drawdown analysis
   - Trade statistics

USAGE EXAMPLE:
──────────────
    from strategies.hft_scalping_strategy import HFTScalpingStrategy
    from utils.hft_backtest_engine import HFTBacktestEngine, ExecutionParams
    
    # Create strategy
    strategy = HFTScalpingStrategy(strategy_type='scalping')
    signals = strategy.generate_signals(your_data)
    
    # Setup execution
    exec_params = ExecutionParams(base_spread_pips=1.0)
    
    # Run backtest
    engine = HFTBacktestEngine(initial_balance=10000, 
                               execution_params=exec_params)
    results = engine.backtest(your_data, signals)
    
    # Get trade log
    trades = engine.get_trade_log()
""")
    
    # Risk management scenarios
    example.risk_management_scenario_analysis()


if __name__ == "__main__":
    main()


# ====================== QUICK REFERENCE ======================
# 
# MT5 FILE LOCATION: mt5_ea/HFTScalpingEA.mq5
# 
# PYTHON FILES:
#   - strategies/hft_scalping_strategy.py (strategy + risk manager)
#   - utils/hft_backtest_engine.py (backtesting engine)
#
# KEY CLASSES:
#   - HFTScalpingStrategy: Signal generation
#   - HFTBacktestEngine: Backtest execution
#   - HFTRiskManager: Risk calculations
#   - HFTPerformanceAnalyzer: Metrics
#
# QUICK START:
#   1. Copy HFTScalpingEA.mq5 to MT5 Experts folder
#   2. Import Python modules in your backtest script
#   3. Follow examples above
#
# ================================================================
