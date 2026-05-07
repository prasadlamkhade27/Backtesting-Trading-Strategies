"""Pairs Trading Strategy - Mean Reversion"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add HFT module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hft.strategies.pairs_trading_strategy import PairsTradingStrategy, PairsTradingAnalyzer
from hft.utils.data_loader import DataLoader


def create_sample_data(pair: str, n_bars: int = 500, start_price: float = None) -> pd.DataFrame:
    """
    Create realistic sample OHLC data for testing
    Simulates correlated pairs with occasional divergences
    """
    np.random.seed(42)
    
    # Default starting prices for major pairs
    if start_price is None:
        start_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.2700,
            'AUDUSD': 0.7500,
            'NZDUSD': 0.6200,
        }
        start_price = start_prices.get(pair, 1.0)
    
    # Generate correlated random walk
    daily_return = np.random.normal(0.0001, 0.003, n_bars)
    close_prices = start_price * np.exp(np.cumsum(daily_return))
    
    # OHLC from close
    data = []
    for close in close_prices:
        # High is close + random
        high = close * (1 + abs(np.random.normal(0, 0.001)))
        # Low is close - random
        low = close * (1 - abs(np.random.normal(0, 0.001)))
        # Open is within range
        open_ = np.random.uniform(low, high)
        
        data.append({
            'open': open_,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.randint(1000, 100000),
        })
    
    df = pd.DataFrame(data)
    df['symbol'] = pair
    return df


def example_basic_pairs_trading():
    """
    Example 1: Basic pairs trading setup
    EUR/USD vs GBP/USD
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic Pairs Trading Setup")
    print("=" * 80)
    print("\nTrade Concept: EUR/USD vs GBP/USD")
    print("Why: Both respond to European economy, but can diverge")
    print("Strategy: Trade the spread, not the direction\n")
    
    # Create sample data
    df_eur = create_sample_data('EURUSD', n_bars=500)
    df_gbp = create_sample_data('GBPUSD', n_bars=500)
    
    # Correlate them (real pairs would be downloaded)
    df_gbp['close'] = df_gbp['close'] * 0.95 + df_eur['close'] * 0.05
    df_gbp['high'] = df_gbp['close'] * (1 + abs(np.random.normal(0, 0.001)))
    df_gbp['low'] = df_gbp['close'] * (1 - abs(np.random.normal(0, 0.001)))
    
    print("Step 1: Pre-Trade Analysis")
    print("-" * 80)
    
    # Analyze the pair relationship
    analyzer = PairsTradingAnalyzer()
    analysis = analyzer.analyze_pair_relationship(df_eur, df_gbp, lookback=100)
    
    print(f"Correlation (last 100 bars):  {analysis['correlation']:.4f}")
    print(f"  → {('✓ Good' if analysis['correlation'] > 0.5 else '✗ Weak')} for pairs trading")
    print(f"\nHedge Ratio (β):              {analysis['hedge_ratio']:.4f}")
    print(f"  → EUR moves {analysis['hedge_ratio']:.2f}x relative to GBP")
    print(f"\nCointegration Test:")
    print(f"  P-value:                   {analysis['cointegration_pvalue']:.4f}")
    print(f"  Status:                    {'✓ Cointegrated' if analysis['is_cointegrated'] else '✗ Not Cointegrated'}")
    print(f"  (p < 0.05 = true relationship exists)")
    print(f"\nSpread Statistics:")
    print(f"  Mean:                      {analysis['spread_mean']:.6f}")
    print(f"  Std Dev:                   {analysis['spread_std']:.6f}")
    print(f"  Current Z-Score:           {analysis['current_zscore']:.2f}")
    
    print("\n" + "=" * 80)
    print("Step 2: Generate Trading Signals")
    print("-" * 80)
    
    # Initialize strategy
    strategy = PairsTradingStrategy(
        pair1='EURUSD',
        pair2='GBPUSD',
        lookback=100,
        z_entry=2.0,      # Entry when spread is 2 std away from mean
        z_exit=0.5,       # Exit when spread returns to 0.5 std (profit taking)
        z_stop=3.0,       # Hard stop at extreme 3 std (regime change warning)
    )
    
    # Generate signals
    signals_df = strategy.generate_signals(df_eur, df_gbp)
    
    # Count signals
    entries = (signals_df['BUY'] == 1).sum()
    
    print(f"\nStrategy Parameters:")
    print(f"  Entry Z-Score:             ±{strategy.z_entry}")
    print(f"  Exit Z-Score:              ±{strategy.z_exit}")
    print(f"  Hard Stop Z-Score:         ±{strategy.z_stop}")
    print(f"  Lookback Window:           {strategy.lookback} bars")
    
    print(f"\nSignal Summary (last 50 bars):")
    recent_signals = signals_df.tail(50)
    active_trades = recent_signals['trade_active'].sum()
    print(f"  Total Signals Generated:   {entries}")
    print(f"  Active Trades (last 50):   {active_trades}")
    
    # Show signal distribution
    print(f"\nRecent Signal Breakdown (last 20 bars):")
    recent_20 = signals_df.tail(20)
    for idx, (_, row) in enumerate(recent_20.iterrows(), 1):
        sig = row['signal_pair1']
        zscore = row['zscore']
        signal_str = "BUY EUR/Sell GBP" if sig == 1 else "SELL EUR/Buy GBP" if sig == -1 else "CLOSE"
        
        if signal_str != "CLOSE":
            print(f"  Bar {idx}: {signal_str:20s} Z={zscore:6.2f}")
    
    print("\n" + "=" * 80)
    print("Step 3: Understanding The Logic")
    print("-" * 80)
    print("""
When Z-Score > +2 (Spread Too High):
  ➡️  EUR is overpriced relative to GBP
  ➡️  Action: SELL EUR/USD, BUY GBP/USD
  ➡️  Expectation: EUR ↓ and/or GBP ↑ → spread contracts → profit

When Z-Score < -2 (Spread Too Low):
  ➡️  EUR is underpriced relative to GBP
  ➡️  Action: BUY EUR/USD, SELL GBP/USD
  ➡️  Expectation: EUR ↑ and/or GBP ↓ → spread expands → profit

When Z-Score ≈ 0 (Back to Mean):
  ➡️  Spread normalized
  ➡️  Action: CLOSE POSITION
  ➡️  Profit realized (relative movement, not directional)

When |Z-Score| > 3 (Extreme):
  ➡️  Warning: Correlation may be breaking
  ➡️  Action: STOP LOSS (hedge failure, regime change)
    """)
    
    print("=" * 80)
    print("Step 4: Risk Management Considerations")
    print("-" * 80)
    print("""
✓ Position Sizing:
  - Risk only 1-2% of account per trade
  - Size pair1 and pair2 to be equal risk exposure
  
✓ Stop Loss:
  - Hard SL at Z > ±3.0 (extreme deviation)
  - If correlation breaks, hedge fails = loss on both sides
  
✓ Take Profit:
  - TP at Z ≈ 0.5 (spread normalized)
  - Exit on time if no progress (max hold time)
  
✓ Volatility Filter:
  - Skip entries during high-impact news
  - Strategies fail when correlation breaks (Brexit, rate changes)
  
✓ When It Fails:
  - Correlation breakdown (central bank divergence)
  - Trending regime (spread keeps expanding)
  - Currency block rotation (risk-on/risk-off)
    """)


def example_multiple_pairs():
    """
    Example 2: Comparing multiple pair combinations
    """
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Comparing Multiple Pair Combinations")
    print("=" * 80)
    
    pairs_combinations = [
        ('EURUSD', 'GBPUSD'),  # European block
        ('EURUSD', 'NZDUSD'),  # Cross-currency
        ('AUDUSD', 'NZDUSD'),  # Commodity pairs
    ]
    
    results = []
    
    for pair1, pair2 in pairs_combinations:
        # Create sample data
        df1 = create_sample_data(pair1, n_bars=500)
        df2 = create_sample_data(pair2, n_bars=500)
        
        # Correlate them
        df2['close'] = df2['close'] * 0.90 + df1['close'] * 0.10
        
        # Analyze
        analyzer = PairsTradingAnalyzer()
        analysis = analyzer.analyze_pair_relationship(df1, df2)
        
        results.append({
            'Pair Combination': f"{pair1} vs {pair2}",
            'Correlation': f"{analysis['correlation']:.3f}",
            'Cointegrated': '✓' if analysis['is_cointegrated'] else '✗',
            'Hedge Ratio': f"{analysis['hedge_ratio']:.3f}",
            'Setup Quality': 'Good' if analysis['correlation'] > 0.7 and analysis['is_cointegrated'] else 'Fair',
        })
    
    results_df = pd.DataFrame(results)
    print("\n" + results_df.to_string(index=False))
    print("\nViable Pairs Summary:")
    print("  - Correlation > 0.7: High quality setups")
    print("  - Cointegrated (p < 0.05): True relationship exists")
    print("  - Lower correlation: Less reliable, wider deviations")


def example_signal_workflow():
    """
    Example 3: Complete workflow from data to trading
    """
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Complete Pairs Trading Workflow")
    print("=" * 80)
    
    print("\nWorkflow Steps:")
    print("1. ✓ Load OHLC data for both pairs")
    print("2. ✓ Analyze relationship (correlation, cointegration)")
    print("3. ✓ Calculate hedge ratio")
    print("4. ✓ Compute spread and Z-scores")
    print("5. ✓ Generate entry signals")
    print("6. ✓ Manage positions with SL/TP")
    print("7. ✓ Track pair trades (both legs)")
    print("8. ✓ Evaluate performance (treat as spread, not pairs separately)")
    
    print("\nPython Code Example:")
    print("""
# Step 1: Load data
df1 = load_data('EURUSD', timeframe='H1')
df2 = load_data('GBPUSD', timeframe='H1')

# Step 2: Create strategy
strategy = PairsTradingStrategy(
    pair1='EURUSD',
    pair2='GBPUSD',
    lookback=100,
    z_entry=2.0,
)

# Step 3: Generate signals
signals_df = strategy.generate_signals(df1, df2)

# Step 4: Trade (1:1 matching on both legs)
for i in range(len(signals_df)):
    if signals_df['signal_pair1'].iloc[i] == 1:
        # Buy EUR, Sell GBP in equal notional value
        place_trade(pair1, 'BUY', volume=x)
        place_trade(pair2, 'SELL', volume=x)
    
    elif signals_df['signal_pair1'].iloc[i] == -1:
        # Sell EUR, Buy GBP
        place_trade(pair1, 'SELL', volume=x)
        place_trade(pair2, 'BUY', volume=x)
    """)


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "PAIRS TRADING STRATEGY - MEAN REVERSION EXAMPLES".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run examples
    example_basic_pairs_trading()
    example_multiple_pairs()
    example_signal_workflow()
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("""
1. Load your own OHLC data using DataLoader
2. Create strategy instance with your pairs
3. Analyze pre-trade (run analyzer.analyze_pair_relationship)
4. Generate signals and backtest
5. Monitor correlation and cointegration ongoing
6. Adjust parameters (z_entry, z_exit) based on backtest results

For live trading:
- Use MT5 integration from propfirm module
- Execute both legs as pair (simultaneous entry)
- Use SL at Z > 3.0 and TP at Z ≈ 0.5
- Monitor hedge ratio in case pair relationship changes
    """)
    print("=" * 80)
