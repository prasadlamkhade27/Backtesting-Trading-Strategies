"""
Pairs Trading - Backtest Example
════════════════════════════════════════════════════════════════════════════

Complete example showing how to backtest the pairs trading strategy
with realistic forex data.

Run this to see pairs trading performance on sample data.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hft.utils.pairs_backtest_integration import PairsBacktestIntegration


def create_correlated_forex_data(
    pair_name: str,
    bars: int = 500,
    start_price: float = None,
    base_drift: float = 0.0,
) -> pd.DataFrame:
    """
    Generate realistic forex OHLCV data
    
    Args:
        pair_name: Currency pair name
        bars: Number of bars (H1 candles)
        start_price: Starting price
        base_drift: Trend bias
        
    Returns:
        DataFrame with OHLC data
    """
    
    np.random.seed(hash(pair_name) % 2**32)
    
    if start_price is None:
        start_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.2700,
            'AUDUSD': 0.7500,
            'NZDUSD': 0.6200,
        }
        start_price = start_prices.get(pair_name, 1.0)
    
    # Generate price series
    returns = np.random.normal(base_drift * 0.0001, 0.008, bars)
    close_prices = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC
    opens = close_prices * (1 + np.random.uniform(-0.001, 0.001, bars))
    highs = np.maximum(close_prices, opens) + abs(np.random.normal(0, 0.002, bars))
    lows = np.minimum(close_prices, opens) - abs(np.random.normal(0, 0.002, bars))
    volumes = np.random.randint(10000, 100000, bars)
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'volume': volumes,
    })
    
    return df


def create_pair_with_correlation(
    pair1_name: str,
    pair2_name: str,
    bars: int = 500,
    target_correlation: float = 0.8,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create two price series with target correlation
    
    Args:
        pair1_name: First pair
        pair2_name: Second pair
        bars: Number of bars
        target_correlation: Target correlation between pairs
        
    Returns:
        (df1, df2) with correlated prices
    """
    
    # Create independent series
    df1 = create_correlated_forex_data(pair1_name, bars)
    df2 = create_correlated_forex_data(pair2_name, bars)
    
    # Blend to achieve correlation
    price1 = df1['close'].values
    price2 = df2['close'].values
    
    # Simple correlation blending
    price2_blended = (
        target_correlation * price1 / np.mean(price1) +
        (1 - target_correlation) * price2
    ) * np.mean(price2) / np.mean(price1)
    
    # Rebuild OHLC for pair2
    df2['close'] = price2_blended
    df2['high'] = price2_blended * (1 + abs(np.random.normal(0, 0.001, bars)))
    df2['low'] = price2_blended * (1 - abs(np.random.normal(0, 0.001, bars)))
    df2['open'] = (df2['high'] + df2['low']) / 2
    
    return df1, df2


def run_basic_pairs_backtest():
    """
    Run basic pairs trading backtest with default parameters
    """
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "PAIRS TRADING BACKTEST - BASIC EXAMPLE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Configuration
    pair1 = 'EURUSD'
    pair2 = 'GBPUSD'
    account_size = 10000
    risk_pct = 0.02
    bars = 500
    
    print(f"\n📋 Configuration:")
    print(f"  Pair 1: {pair1}")
    print(f"  Pair 2: {pair2}")
    print(f"  Account: ${account_size:,.2f}")
    print(f"  Risk per Trade: {risk_pct*100:.1f}%")
    print(f"  Bars: {bars} (H1 timeframe ≈ ~{bars//24} days)")
    
    # Generate data
    print(f"\n📊 Generating correlated pair data...")
    df1, df2 = create_pair_with_correlation(
        pair1, pair2,
        bars=bars,
        target_correlation=0.82
    )
    print(f"  ✓ {pair1}: {df1['close'].iloc[0]:.5f} → {df1['close'].iloc[-1]:.5f}")
    print(f"  ✓ {pair2}: {df2['close'].iloc[0]:.5f} → {df2['close'].iloc[-1]:.5f}")
    
    # Create backtest integration
    print(f"\n⚙️  Initializing pairs trading backtest...")
    integration = PairsBacktestIntegration(
        pair1=pair1,
        pair2=pair2,
        account_size=account_size,
        risk_pct=risk_pct,
        lookback=100,
        z_entry=2.0,
        z_exit=0.5,
        z_stop=3.0,
    )
    
    # Run backtest
    result = integration.run_full_backtest(
        df1, df2,
        sl_pips=30,
        tp_pips=50,
        verbose=True
    )
    
    # Export results
    print(f"\n💾 Exporting results...")
    integration.export_results_to_csv(result, "backtest_pairs_trading")
    
    return result


def run_parameter_optimization():
    """
    Run parameter optimization to find best settings
    """
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "PAIRS TRADING - PARAMETER OPTIMIZATION".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Generate test data
    print("\n📊 Generating test data...")
    df1, df2 = create_pair_with_correlation('EURUSD', 'GBPUSD', bars=500)
    
    # Create integration
    integration = PairsBacktestIntegration(
        pair1='EURUSD',
        pair2='GBPUSD',
        account_size=10000,
        risk_pct=0.02,
    )
    
    # Run optimization
    opt_results = integration.optimize_parameters(
        df1, df2,
        z_entry_range=(1.8, 2.4, 0.2),  # Shorter range for speed
        z_exit_range=(0.3, 0.7, 0.2),
        z_stop_range=(2.8, 3.2, 0.2),
    )
    
    return opt_results


def run_multiple_pairs_comparison():
    """
    Compare performance across different pair combinations
    """
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "COMPARING MULTIPLE PAIR COMBINATIONS".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Pair combinations to test
    combinations = [
        ('EURUSD', 'GBPUSD', 0.82),  # European
        ('EURUSD', 'AUDUSD', 0.72),  # Cross
        ('AUDUSD', 'NZDUSD', 0.78),  # Commodity
    ]
    
    results_summary = []
    
    for pair1, pair2, target_corr in combinations:
        print(f"\n{'─'*80}")
        print(f"Testing: {pair1} vs {pair2} (target corr: {target_corr})")
        print(f"{'─'*80}")
        
        # Generate data
        df1, df2 = create_pair_with_correlation(pair1, pair2, bars=500, target_correlation=target_corr)
        
        # Backtest
        integration = PairsBacktestIntegration(
            pair1=pair1,
            pair2=pair2,
            account_size=10000,
            risk_pct=0.02,
        )
        
        result = integration.run_full_backtest(df1, df2, verbose=False)
        
        # Summarize
        results_summary.append({
            'Pair Combo': f"{pair1}/{pair2}",
            'Trades': result.total_trades,
            'Win Rate': f"{result.win_rate:.1f}%",
            'Total P&L': f"${result.total_pnl:,.2f}",
            'Return': f"{result.return_pct:.2f}%",
            'Sharpe': f"{result.sharpe_ratio:.2f}",
            'Correlation': f"{result.pair_analysis['correlation']:.3f}",
        })
    
    # Display comparison
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    comparison_df = pd.DataFrame(results_summary)
    print("\n" + comparison_df.to_string(index=False))


def main():
    """Run all examples"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║                 PAIRS TRADING BACKTEST EXAMPLES                         ║
    ║                                                                          ║
    ║  This script demonstrates how to use the pairs trading strategy        ║
    ║  with the backtesting system.                                          ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Example 1: Basic Backtest
    print("\nExample 1: BASIC BACKTEST")
    print("─" * 80)
    result1 = run_basic_pairs_backtest()
    
    # Example 2: Parameter Optimization
    print("\n\nExample 2: PARAMETER OPTIMIZATION")
    print("─" * 80)
    opt_results = run_parameter_optimization()
    
    # Example 3: Multiple Pairs Comparison
    print("\n\nExample 3: MULTIPLE PAIRS COMPARISON")
    print("─" * 80)
    run_multiple_pairs_comparison()
    
    # Summary
    print("\n" + "="*80)
    print("BACKTEST SUMMARY")
    print("="*80)
    print(f"""
    ✓ Basic backtest completed
      - Total Trades: {result1.total_trades}
      - Win Rate: {result1.win_rate:.1f}%
      - Total P&L: ${result1.total_pnl:,.2f}
      - Return: {result1.return_pct:.2f}%
    
    ✓ Parameter optimization completed
      - Best configuration identified
    
    ✓ Multiple pairs comparison completed
      - Different combinations analyzed
    
    📁 Results exported:
      - backtest_pairs_trading_trades.csv
      - backtest_pairs_trading_equity.csv
    """)


if __name__ == '__main__':
    from typing import Tuple
    main()
