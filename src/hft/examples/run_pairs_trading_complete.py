"""
Pairs Trading - Complete Working Example
═══════════════════════════════════════════════════════════════════════════════

This example demonstrates:
1. Loading/creating OHLC data for two pairs
2. Pre-trade analysis (correlation, cointegration)
3. Strategy signal generation
4. Full backtest with proper P&L calculation
5. Results visualization
"""

import sys
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hft.strategies.pairs_trading_strategy import PairsTradingStrategy, PairsTradingAnalyzer
from hft.utils.pairs_backtest_engine import PairsBacktestEngine


def create_realistic_pair_data(
    pair_name: str,
    bars: int = 500,
    start_price: float = None,
    drift: float = 0.0001,
    volatility: float = 0.008,
) -> pd.DataFrame:
    """
    Create realistic OHLC data with desired drift and volatility
    
    Args:
        pair_name: Name of the pair
        bars: Number of bars to generate
        start_price: Starting price (auto-selected if None)
        drift: Mean daily return
        volatility: Daily volatility (std dev)
    
    Returns:
        DataFrame with OHLC data
    """
    
    if start_price is None:
        start_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.2700,
            'AUDUSD': 0.7500,
            'NZDUSD': 0.6200,
            'USDCAD': 1.3500,
            'USDCHF': 0.9200,
        }
        start_price = start_prices.get(pair_name, 1.0)
    
    np.random.seed(hash(pair_name) % 2**32)
    
    # Generate returns with drift and volatility
    returns = np.random.normal(drift, volatility, bars)
    prices = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC from prices
    data = {
        'open': [],
        'high': [],
        'low': [],
        'close': prices,
        'volume': np.random.randint(50000, 500000, bars),
    }
    
    for close in prices:
        # High-low range
        daily_range = close * volatility
        high = close + abs(np.random.normal(0, daily_range))
        low = close - abs(np.random.normal(0, daily_range))
        
        # Open within range
        open_ = np.random.uniform(low, high)
        
        data['open'].append(open_)
        data['high'].append(high)
        data['low'].append(low)
    
    df = pd.DataFrame(data)
    df['symbol'] = pair_name
    df.index = pd.date_range(start=datetime.now() - timedelta(hours=bars), periods=bars, freq='H')
    
    return df


def create_correlated_pairs(
    pair1_name: str,
    pair2_name: str,
    bars: int = 500,
    correlation_target: float = 0.8,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create two price series with desired correlation
    
    Args:
        pair1_name: First pair name
        pair2_name: Second pair name  
        bars: Number of bars
        correlation_target: Target correlation (0-1)
    
    Returns:
        (df1, df2) with correlated prices
    """
    
    # Create pair1
    df1 = create_realistic_pair_data(pair1_name, bars=bars)
    price1 = df1['close'].values
    
    # Create independent pair2
    df2 = create_realistic_pair_data(pair2_name, bars=bars)
    price2 = df2['close'].values
    
    # Blend to achieve target correlation
    # New price2 = correlation_target * price1 + (1 - correlation_target) * independent_price2
    price2_blended = (correlation_target * price1 / np.mean(price1)) * np.mean(price2) + \
                     (1 - correlation_target) * price2
    
    # Add some noise
    price2_blended = price2_blended * (1 + np.random.normal(0, 0.001, bars))
    
    # Rebuild OHLC for pair2 with blended price
    df2['close'] = price2_blended
    df2['high'] = price2_blended * (1 + abs(np.random.normal(0, 0.001, bars)))
    df2['low'] = price2_blended * (1 - abs(np.random.normal(0, 0.001, bars)))
    df2['open'] = (df2['high'] + df2['low']) / 2
    
    return df1, df2


def run_full_example():
    """Run complete pairs trading example with visualization"""
    
    print("\n" + "=" * 100)
    print("PAIRS TRADING - COMPLETE WORKING EXAMPLE".center(100))
    print("=" * 100 + "\n")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 1: Create Data
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("STEP 1: Creating Correlated Pair Data")
    print("-" * 100)
    
    pair1_name = 'EURUSD'
    pair2_name = 'GBPUSD'
    bars = 500
    correlation_target = 0.82
    
    print(f"\nGenerating {bars} hours of {pair1_name} vs {pair2_name} data")
    print(f"Target correlation: {correlation_target:.2f}")
    
    df1, df2 = create_correlated_pairs(
        pair1_name, pair2_name,
        bars=bars,
        correlation_target=correlation_target
    )
    
    print(f"✓ {pair1_name}: {df1['close'].iloc[0]:.5f} → {df1['close'].iloc[-1]:.5f}")
    print(f"✓ {pair2_name}: {df2['close'].iloc[0]:.5f} → {df2['close'].iloc[-1]:.5f}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 2: Pre-Trade Analysis
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 100)
    print("STEP 2: Pre-Trade Relationship Analysis")
    print("-" * 100)
    
    analyzer = PairsTradingAnalyzer()
    analysis = analyzer.analyze_pair_relationship(df1, df2, lookback=100)
    
    print(f"\nCorrelation Analysis:")
    print(f"  Overall Correlation (100 bars): {analysis['correlation']:.4f}")
    print(f"  Quality: {'✓ EXCELLENT' if analysis['correlation'] > 0.8 else '✓ GOOD' if analysis['correlation'] > 0.7 else '✗ POOR'}")
    
    print(f"\nHedge Ratio (β):")
    print(f"  β = {analysis['hedge_ratio']:.4f}")
    print(f"  Interpretation: {pair1_name} moves {analysis['hedge_ratio']:.2f}x relative to {pair2_name}")
    print(f"  Usage: Spread = {pair1_name} - ({analysis['hedge_ratio']:.3f} × {pair2_name})")
    
    print(f"\nCointegration Test (Engle-Granger):")
    print(f"  Test Statistic: {analysis['cointegration_pvalue']:.4f} (p-value)")
    status = "✓ COINTEGRATED" if analysis['is_cointegrated'] else "✗ NOT COINTEGRATED"
    print(f"  Status: {status}")
    print(f"  Meaning: Spread is {'stationary' if analysis['is_cointegrated'] else 'non-stationary'}")
    
    print(f"\nSpread Statistics:")
    print(f"  Mean: {analysis['spread_mean']:.6f}")
    print(f"  Std Dev: {analysis['spread_std']:.6f}")
    print(f"  Current Z-Score: {analysis['current_zscore']:+.2f}")
    
    # Quality check
    if analysis['correlation'] < 0.7:
        print("\n⚠️  WARNING: Correlation < 0.7, consider different pair combination")
    if not analysis['is_cointegrated']:
        print("\n⚠️  WARNING: Not cointegrated, relationship may not hold")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3: Generate Trading Signals
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 100)
    print("STEP 3: Generating Trading Signals")
    print("-" * 100)
    
    strategy = PairsTradingStrategy(
        pair1=pair1_name,
        pair2=pair2_name,
        lookback=100,
        z_entry=2.0,      # Enter when spread deviates 2 std devs
        z_exit=0.5,       # Exit when spread reverts to 0.5 std
        z_stop=3.0,       # Hard stop at 3 std (regime change)
        min_correlation=0.7,
        volatility_threshold=0.003,
    )
    
    print(f"\nStrategy Parameters:")
    print(f"  Entry Z-Score (absolute): ±{strategy.z_entry}")
    print(f"  Exit Z-Score (absolute): ±{strategy.z_exit}")
    print(f"  Stop Loss Z-Score (absolute): ±{strategy.z_stop}")
    print(f"  Lookback Window: {strategy.lookback} bars")
    print(f"  Min Correlation: {strategy.min_correlation}")
    
    # Generate signals
    signals_df = strategy.generate_signals(df1, df2)
    
    # Statistics
    total_signals = (signals_df['signal_pair1'] != 0).sum()
    entries = (signals_df['BUY'] == 1).sum()
    
    print(f"\nSignal Generation Results:")
    print(f"  Total Signals Generated: {entries}")
    
    # Show recent signals
    print(f"\nRecent Signals (last 30 bars):")
    print("  ┌─ Bar | Z-Score | Signal                                   ┐")
    
    recent = signals_df.tail(30)
    for idx, (bar_idx, row) in enumerate(recent.iterrows(), 1):
        zscore = row['zscore']
        signal = row['signal_pair1']
        corr = row['correlation']
        
        if signal == 1:
            signal_str = f"LONG SPREAD (Sell {pair1_name}, Buy {pair2_name})"
        elif signal == -1:
            signal_str = f"SHORT SPREAD (Buy {pair1_name}, Sell {pair2_name})"
        else:
            signal_str = "HOLD"
        
        # Only print non-trivial bars
        if signal != 0 or abs(zscore) > 1.5:
            print(f"  │ {idx:3d} │ {zscore:+7.2f} │ {signal_str:40s} │")
    
    print("  └─────┴─────────┴────────────────────────────────────────┘")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 4: Run Backtest
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 100)
    print("STEP 4: Running Full Backtest")
    print("-" * 100)
    
    engine = PairsBacktestEngine(
        account_size=10000,
        risk_pct_per_trade=0.02,
        pair1_pip_size=0.0001,
        pair2_pip_size=0.0001,
        pair1_name=pair1_name,
        pair2_name=pair2_name,
        slippage_pips=1.0,
        commission_pct=0.0002,
    )
    
    print(f"\nBacktest Settings:")
    print(f"  Account Size: ${engine.account_size:,.2f}")
    print(f"  Risk per Trade: {engine.risk_pct*100:.1f}%")
    print(f"  Slippage: {engine.slippage_pips:.1f} pips")
    print(f"  Commission: {engine.commission_pct*100:.2f}%")
    
    # Run backtest
    results = engine.backtest(
        signals_df, df2,
        z_exit_threshold=0.5,
        z_stop_threshold=3.0,
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 5: Display Results
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 100)
    print("STEP 5: Backtest Results")
    print("-" * 100)
    
    print(f"\nOverall Performance:")
    print(f"  Strategy: {strategy.name}")
    print(f"  Period: {bars} hours (H1)")
    
    if results['total_trades'] > 0:
        print(f"\nTrade Statistics:")
        print(f"  Total Trades: {results['total_trades']}")
        print(f"  Profitable: {results['profitable_trades']}")
        print(f"  Losing: {results['losing_trades']}")
        print(f"  Win Rate: {results['win_rate']}")
        
        print(f"\nProfit & Loss:")
        print(f"  Total P&L: {results['total_pnl']}")
        print(f"  Return: {results['return_pct']}")
        print(f"  Avg Win: {results['avg_win']}")
        print(f"  Avg Loss: -{results['avg_loss']}")
        
        if results['profitfactor'] != 'N/A':
            print(f"  Profit Factor: {results['profitfactor']}:1")
        
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown: {results['max_drawdown']}")
        print(f"  Sharpe Ratio: {results['sharpe_ratio']}")
        print(f"  Avg Trade Duration: {results['avg_bars_per_trade']} bars")
        
        # Top trades
        if results['trades']:
            print(f"\nTop 5 Trades:")
            print("  ┌─ # │ Entry Z  │ Exit Z   │ Direction      │ P&L      │ Duration ┐")
            
            sorted_trades = sorted(results['trades'], key=lambda t: float(t['total_pnl']), reverse=True)
            
            for idx, trade in enumerate(sorted_trades[:5], 1):
                print(f"  │ {idx} │ {trade['entry_zscore']:>7s} │ {trade['exit_zscore']:>7s} │ {trade['direction'][:14]:14s} │ {trade['total_pnl']:>7s} │ {trade['duration_bars']:>8s} │")
            
            print("  └───┴──────────┴──────────┴────────────────┴──────────┴──────────┘")
        
        # Interpretation
        print(f"\n\nAmplification Analysis:")
        print(f"  {'✓' if float(results['return_pct'].rstrip('%')) > 0 else '✗'} Return: {results['return_pct']} (goal: > 0%)")
        print(f"  {'✓' if float(results['win_rate'].rstrip('%')) > 55 else '⚠' if float(results['win_rate'].rstrip('%')) > 40 else '✗'} Win Rate: {results['win_rate']} (goal: > 55%)")
        
        if results['profitfactor'] != 'N/A':
            pf = float(results['profitfactor'].rstrip(':1'))
            print(f"  {'✓' if pf > 1.5 else '⚠' if pf > 1.0 else '✗'} Profit Factor: {results['profitfactor']} (goal: > 1.5)")
    else:
        print(f"\n⚠️  No trades generated in backtest period")
        print(f"  Possible reasons:")
        print(f"  - Correlation too low")
        print(f"  - Volatility filtering excluded all signals")
        print(f"  - Z-score never reached entry threshold")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 6: Key Takeaways
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 100)
    print("STEP 6: Key Takeaways")
    print("-" * 100)
    
    print(f"""
✓ What We Learned:

1. Pairs trading is about RELATIONSHIPS, not individual prices
   - We're shortselling the overpriced pair
   - We're longing the underpriced pair
   - Profit when they revert back to normal relationship

2. Mean reversion is a natural market property
   - Markets oscillate around equilibrium
   - Extreme deviations attract correction
   - Creates predictable profit opportunity

3. Critical factors for success:
   - Strong correlation (> 0.7)
   - True cointegration (p-value < 0.05)
   - Proper hedge ratio (β) calculation
   - Entries at statistical extremes (Z > ±2)
   - Exits on mean reversion (Z ≈ 0)

4. Risk management is ESSENTIAL:
   - Hard stop at Z > ±3.0 (correlation breakdown)
   - Position sizing tied to account risk (1-2% per trade)
   - Volatility filters to avoid regime changes
   - Correlation monitoring ongoing

5. Performance expectations:
   - High win rate (60-70%) but small profit per trade
   - Requires discipline and consistent execution
   - Benefits from scale (high volume trading)
   - Sensitive to correlation stability

Ready to trade? Remember:
  → Always verify cointegration before trading
  → Execute BOTH legs simultaneously (no slippage imbalance)
  → Monitor correlation ongoing (exit if < 0.5)
  → Follow hard stops rigorously
  → Track hedge ratio changes (may need recalculation)
    """)
    
    print("=" * 100 + "\n")


if __name__ == '__main__':
    run_full_example()
    
    print("""
═══════════════════════════════════════════════════════════════════════════════
NEXT STEPS:

1. Code Review:
   - Read pairs_trading_strategy.py (strategy logic)
   - Read pairs_backtest_engine.py (backtesting)
   - Study PAIRS_TRADING_GUIDE.py (theory & best practices)

2. Live Implementation:
   - Use MT5/API integration from propfirm module
   - Start with small position sizes (0.01 lots)
   - Trade during high-liquidity hours
   - Monitor correlation before each trade

3. Advanced Topics:
   - Multi-pair framework (trade best setup across combinations)
   - Machine learning (predict reversion probability)
   - Calendar filters (avoid news events)
   - Volatility-based position sizing

4. Common Questions:
   Q: Why both go down if hedge fails?
   A: They're correlated. If correlation breaks, both react same way.
   
   Q: Can I trade with unequal volumes?
   A: No. Must scale by hedge ratio to maintain balance.
   
   Q: What if correlation changes?
   A: Recalculate β every bar (rolling window). Exit if drops < 0.5.
   
   Q: Is this arbitrage (risk-free)?
   A: No. It's statistical arbitrage with execution risk.
      Correlation can break = both sides lose.

═══════════════════════════════════════════════════════════════════════════════
""")
