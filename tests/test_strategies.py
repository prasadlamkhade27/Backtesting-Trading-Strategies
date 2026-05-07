"""
Test script to verify all strategies are registered and discoverable
Shows how to use MQL King 1 strategy for backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import the strategy utilities
from hft.strategies import get_available_strategies, get_strategy, AVAILABLE_STRATEGIES


def print_available_strategies():
    """Print all available strategies"""
    print("\n" + "="*70)
    print("📊 AVAILABLE STRATEGIES")
    print("="*70)
    
    strategies = get_available_strategies()
    for i, name in enumerate(strategies, 1):
        print(f"{i}. {name}")
    
    print(f"\nTotal strategies: {len(strategies)}")
    print("="*70 + "\n")


def generate_sample_data(days=7, symbol='XAUUSD'):
    """Generate sample OHLCV data for testing"""
    
    dates = pd.date_range(start='2024-01-01', periods=days*1440, freq='1min')
    
    np.random.seed(42)
    
    # Generate realistic price movement
    if symbol == 'XAUUSD':
        start_price = 2000
        drift = 0.0001
        volatility = 0.002
    else:
        start_price = 1.0
        drift = 0.00001
        volatility = 0.0005
    
    returns = np.random.normal(drift, volatility, len(dates))
    close = start_price * (1 + returns).cumprod()
    
    # Generate OHLC
    open_prices = close + np.random.uniform(-volatility*100, volatility*100, len(dates))
    high_prices = np.maximum(close, open_prices) + np.abs(np.random.uniform(0, volatility*50, len(dates)))
    low_prices = np.minimum(close, open_prices) - np.abs(np.random.uniform(0, volatility*50, len(dates)))
    volume = np.random.uniform(100, 1000, len(dates))
    
    df = pd.DataFrame({
        'time': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close,
        'volume': volume,
    })
    
    return df


def test_strategy(strategy_name, data):
    """Test a strategy on sample data"""
    
    print(f"\n{'─'*70}")
    print(f"Testing: {strategy_name}")
    print(f"{'─'*70}")
    
    try:
        # Get strategy instance
        strategy = get_strategy(strategy_name)
        
        print(f"✅ Strategy loaded: {strategy.name}")
        print(f"   Description: {strategy.description}")
        
        # Generate signals
        print(f"🔄 Generating signals...")
        result_df = strategy.generate_signals(data)
        
        # Count signals
        buy_signals = result_df['BUY'].sum()
        sell_signals = result_df['SELL'].sum()
        
        print(f"✅ Signals generated!")
        print(f"   Buy signals:  {buy_signals}")
        print(f"   Sell signals: {sell_signals}")
        print(f"   Total signals: {buy_signals + sell_signals}")
        
        # Show parameters
        params = strategy.get_parameters()
        print(f"\n📋 Strategy Parameters:")
        for key, value in params.items():
            if key != 'strategy':
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing strategy: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test execution"""
    
    print("\n" + "="*70)
    print("🧭 STRATEGY DISCOVERY & TESTING")
    print("="*70)
    
    # 1. Show all available strategies
    print_available_strategies()
    
    # 2. Generate sample data
    print("📊 Generating sample data...")
    data = generate_sample_data(days=7, symbol='XAUUSD')
    print(f"✅ Generated {len(data)} candles ({data.iloc[0]['time']} to {data.iloc[-1]['time']})")
    
    # 3. Test each strategy
    print("\n" + "="*70)
    print("🧪 TESTING STRATEGIES")
    print("="*70)
    
    strategies = get_available_strategies()
    passed = 0
    failed = 0
    
    for strategy_name in strategies:
        if test_strategy(strategy_name, data):
            passed += 1
        else:
            failed += 1
    
    # 4. Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total strategies:   {len(strategies)}")
    print(f"Passed:            {passed} ✅")
    print(f"Failed:            {failed} ❌")
    print("="*70 + "\n")
    
    # 5. Show MQL King 1 specific example
    print("="*70)
    print("🎯 MQL KING 1 STRATEGY EXAMPLE")
    print("="*70)
    
    try:
        # Create MQL King 1 strategy with custom parameters
        mql_king = get_strategy('MQL King 1 - SMC HFT', 
                                structure_lookback=10,
                                displacement_threshold=2.0,
                                min_rr_ratio=1.5)
        
        print(f"✅ MQL King 1 created with custom parameters")
        print(f"   Strategy: {mql_king.name}")
        print(f"   Description: {mql_king.description}")
        
        # Generate signals
        print(f"\n🔄 Backtesting on sample data...")
        signals_df = mql_king.generate_signals(data)
        
        buy_count = signals_df['BUY'].sum()
        sell_count = signals_df['SELL'].sum()
        
        print(f"✅ Backtest complete!")
        print(f"   Buy signals:  {buy_count}")
        print(f"   Sell signals: {sell_count}")
        
        # Show signal details
        if buy_count > 0:
            print(f"\n📊 Sample BUY signals:")
            buy_idx = signals_df[signals_df['BUY']].head(3).index
            for idx in buy_idx:
                row = signals_df.loc[idx]
                print(f"   Time: {row['time']} | Entry: {row['close']:.2f}")
        
        if sell_count > 0:
            print(f"\n📊 Sample SELL signals:")
            sell_idx = signals_df[signals_df['SELL']].head(3).index
            for idx in sell_idx:
                row = signals_df.loc[idx]
                print(f"   Time: {row['time']} | Entry: {row['close']:.2f}")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error testing MQL King 1: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
