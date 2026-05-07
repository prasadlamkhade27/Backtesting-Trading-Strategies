"""Pairs Trading Backtest Examples"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hft.utils.pairs_backtest_integration import PairsBacktestIntegration


def create_correlated_forex_data(
    pair_name: str,
    bars: int = 500,
    start_price: float = None,
    base_drift: float = 0.0,
) -> pd.DataFrame:
    """Generate realistic forex OHLCV data."""
    
    np.random.seed(hash(pair_name) % 2**32)
    
    if start_price is None:
        start_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.2700,
            'AUDUSD': 0.7500,
            'NZDUSD': 0.6200,
        }
        start_price = start_prices.get(pair_name, 1.0)
    
    returns = np.random.normal(base_drift * 0.0001, 0.008, bars)
    close_prices = start_price * np.exp(np.cumsum(returns))
    
    opens = close_prices * (1 + np.random.uniform(-0.001, 0.001, bars))
    highs = np.maximum(close_prices, opens) + abs(np.random.normal(0, 0.002, bars))
    lows = np.minimum(close_prices, opens) - abs(np.random.normal(0, 0.002, bars))
    volumes = np.random.randint(10000, 100000, bars)
    
    return pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': close_prices,
        'volume': volumes,
    })


def create_pair_with_correlation(
    pair1_name: str,
    pair2_name: str,
    bars: int = 500,
    target_correlation: float = 0.8,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create two price series with target correlation."""
    
    df1 = create_correlated_forex_data(pair1_name, bars)
    df2 = create_correlated_forex_data(pair2_name, bars)
    
    price1 = df1['close'].values
    price2 = df2['close'].values
    
    price2_blended = (
        target_correlation * price1 / np.mean(price1) +
        (1 - target_correlation) * price2
    ) * np.mean(price2) / np.mean(price1)
    
    df2['close'] = price2_blended
    df2['high'] = price2_blended * (1 + abs(np.random.normal(0, 0.001, bars)))
    df2['low'] = price2_blended * (1 - abs(np.random.normal(0, 0.001, bars)))
    df2['open'] = (df2['high'] + df2['low']) / 2
    
    return df1, df2


def run_basic_backtest():
    """Run basic pairs trading backtest."""
    
    print("\nBasic Pairs Trading Backtest")
    print("="*60)
    
    pair1, pair2 = 'EURUSD', 'GBPUSD'
    df1, df2 = create_pair_with_correlation(pair1, pair2, bars=500, target_correlation=0.82)
    
    integration = PairsBacktestIntegration(
        pair1=pair1,
        pair2=pair2,
        account_size=10000,
        risk_pct=0.02,
        lookback=100,
        z_entry=2.0,
        z_exit=0.5,
        z_stop=3.0,
    )
    
    result = integration.run_full_backtest(df1, df2, sl_pips=30, tp_pips=50, verbose=True)
    integration.export_results_to_csv(result, "backtest_pairs_trading")
    
    return result


def run_optimization():
    """Run parameter optimization."""
    
    print("\nParameter Optimization")
    print("="*60)
    
    df1, df2 = create_pair_with_correlation('EURUSD', 'GBPUSD', bars=500)
    
    integration = PairsBacktestIntegration(
        pair1='EURUSD',
        pair2='GBPUSD',
        account_size=10000,
        risk_pct=0.02,
    )
    
    opt_results = integration.optimize_parameters(
        df1, df2,
        z_entry_range=(1.8, 2.4, 0.2),
        z_exit_range=(0.3, 0.7, 0.2),
        z_stop_range=(2.8, 3.2, 0.2),
    )
    
    return opt_results


def run_multiple_pairs():
    """Compare multiple pair combinations."""
    
    print("\nMultiple Pairs Comparison")
    print("="*60)
    
    combinations = [
        ('EURUSD', 'GBPUSD', 0.82),
        ('EURUSD', 'AUDUSD', 0.72),
        ('AUDUSD', 'NZDUSD', 0.78),
    ]
    
    results_summary = []
    
    for pair1, pair2, target_corr in combinations:
        print(f"\nTesting: {pair1} vs {pair2}")
        
        df1, df2 = create_pair_with_correlation(pair1, pair2, bars=500, target_correlation=target_corr)
        
        integration = PairsBacktestIntegration(
            pair1=pair1,
            pair2=pair2,
            account_size=10000,
            risk_pct=0.02,
        )
        
        result = integration.run_full_backtest(df1, df2, verbose=False)
        
        results_summary.append({
            'Pair': f"{pair1}/{pair2}",
            'Trades': result.total_trades,
            'Win Rate': f"{result.win_rate:.1f}%",
            'P&L': f"${result.total_pnl:,.2f}",
            'Return': f"{result.return_pct:.2f}%",
        })
    
    comparison_df = pd.DataFrame(results_summary)
    print("\n" + comparison_df.to_string(index=False))


if __name__ == "__main__":
    print("\nPairs Trading Backtest Examples")
    print("="*60)
    
    print("\n1. Basic Backtest")
    print("-"*60)
    result1 = run_basic_backtest()
    
    print("\n2. Parameter Optimization")
    print("-"*60)
    opt_results = run_optimization()
    
    print("\n3. Multiple Pairs Comparison")
    print("-"*60)
    run_multiple_pairs()
    
    📁 Results exported:
      - backtest_pairs_trading_trades.csv
      - backtest_pairs_trading_equity.csv
    """)


if __name__ == '__main__':
    from typing import Tuple
    main()
