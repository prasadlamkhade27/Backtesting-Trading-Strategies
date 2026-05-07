"""
Pairs Trading - Configuration Templates
════════════════════════════════════════════════════════════════════════════

Pre-configured setups for different pair combinations and market conditions.
Copy and modify these for your specific needs.
"""


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: PAIR PRESETS
# ════════════════════════════════════════════════════════════════════════════

PAIR_PRESETS = {
    # European Block (Highest correlation, best for pairs trading)
    'EUR_GBP': {
        'pair1': 'EURUSD',
        'pair2': 'GBPUSD',
        'typical_correlation': 0.82,
        'rationale': 'Both respond to EU/UK economy, high correlation stable',
        'best_timeframe': 'H1',
        'expected_win_rate': 0.65,
    },
    
    # Cross-Currency (Medium correlation, good hedge)
    'EUR_AUD': {
        'pair1': 'EURUSD',
        'pair2': 'AUDUSD',
        'typical_correlation': 0.72,
        'rationale': 'Different regions, but both influenced by global risk appetite',
        'best_timeframe': 'H1-H4',
        'expected_win_rate': 0.60,
    },
    
    # Commodity Currency Pair (Stable correlation)
    'AUD_NZD': {
        'pair1': 'AUDUSD',
        'pair2': 'NZDUSD',
        'typical_correlation': 0.78,
        'rationale': 'Same region, commodity-driven, highly correlated',
        'best_timeframe': 'H1',
        'expected_win_rate': 0.62,
    },
    
    # North American Block (Decent correlation)
    'USD_CAD_vs_USD_MXN': {
        'pair1': 'USDCAD',
        'pair2': 'USDMXN',
        'typical_correlation': 0.68,
        'rationale': 'North American pairs, oil-influenced',
        'best_timeframe': 'H4',
        'expected_win_rate': 0.58,
    },
    
    # Safe Haven Trades (Low correlation, use as hedge)
    'EUR_CHF': {
        'pair1': 'EURUSD',
        'pair2': 'USDCHF',  # Note: Inverted CHF
        'typical_correlation': 0.55,
        'rationale': 'Lower correlation, good for diversification',
        'best_timeframe': 'H4-D1',
        'expected_win_rate': 0.52,
    },
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: STRATEGY PRESETS (By Trading Style)
# ════════════════════════════════════════════════════════════════════════════

STRATEGY_PRESETS = {
    # CONSERVATIVE: Lower risk, smaller profits per trade
    'CONSERVATIVE': {
        'lookback': 150,           # Longer history for stability
        'z_entry': 2.5,            # Enter only at extreme deviation
        'z_exit': 0.3,             # Tight exits (safe but fewer points)
        'z_stop': 3.5,             # Wide stop (rare to hit)
        'min_correlation': 0.75,   # Strict correlation filter
        'volatility_threshold': 0.0015,  # Tight volatility filter
        'risk_per_trade': 0.01,    # 1% risk (very conservative)
        'description': 'Low risk, high precision entries, small frequent wins',
    },
    
    # BALANCED: Moderate risk/reward (Recommended for beginners)
    'BALANCED': {
        'lookback': 100,           # Standard window
        'z_entry': 2.0,            # Enter at standard deviation
        'z_exit': 0.5,             # Normal exit (capture most reversion)
        'z_stop': 3.0,             # Standard hard stop
        'min_correlation': 0.70,   # Reasonable filter
        'volatility_threshold': 0.002,   # Normal filter
        'risk_per_trade': 0.02,    # 2% risk (standard)
        'description': 'Balanced approach, good for learning',
    },
    
    # AGGRESSIVE: Higher risk, larger profits per trade
    'AGGRESSIVE': {
        'lookback': 80,            # Shorter history for sensitivity
        'z_entry': 1.8,            # Enter earlier (sooner to mean)
        'z_exit': 0.7,             # Looser exits (capture full reversion)
        'z_stop': 2.8,             # Tight hard stop (early exit on reversal)
        'min_correlation': 0.65,   # Loose correlation filter
        'volatility_threshold': 0.003,   # Loose volatility filter
        'risk_per_trade': 0.03,    # 3% risk per trade
        'description': 'Higher stakes, larger moves, more frequent trades',
    },
    
    # SCALPING: Many small trades, very tight entries/exits
    'SCALPING': {
        'lookback': 50,            # Short-term focus (M15 candles)
        'z_entry': 1.5,            # Very early entries
        'z_exit': 0.2,             # Exit immediately on reversion
        'z_stop': 2.5,             # Quick stops
        'min_correlation': 0.60,   # Loose filter (more setups)
        'volatility_threshold': 0.005,   # Very loose
        'risk_per_trade': 0.02,    # 2% per trade (many trades)
        'description': 'High frequency, small pip profits, needs execution speed',
        'best_for': 'M15/M30 timeframes with good platform',
    },
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: TIMEFRAME OPTIMIZED PRESETS
# ════════════════════════════════════════════════════════════════════════════

TIMEFRAME_PRESETS = {
    'M15': {
        'lookback': 60,
        'z_entry': 1.9,
        'z_exit': 0.4,
        'z_stop': 2.8,
        'expected_duration_bars': 5,      # trades close quickly
        'best_pairs': ['EUR_GBP', 'AUD_NZD'],
        'note': 'Requires fast execution, frequent trades',
    },
    
    'M30': {
        'lookback': 80,
        'z_entry': 2.0,
        'z_exit': 0.5,
        'z_stop': 3.0,
        'expected_duration_bars': 10,
        'best_pairs': ['EUR_GBP', 'EUR_AUD'],
        'note': 'Good balance, moderate execution speed needed',
    },
    
    'H1': {  # Default / Most popular
        'lookback': 100,
        'z_entry': 2.0,
        'z_exit': 0.5,
        'z_stop': 3.0,
        'expected_duration_bars': 20,
        'best_pairs': ['EUR_GBP', 'AUD_NZD', 'EUR_AUD'],
        'note': 'Standard choice, good for learning',
    },
    
    'H4': {
        'lookback': 150,
        'z_entry': 2.1,
        'z_exit': 0.6,
        'z_stop': 3.2,
        'expected_duration_bars': 50,
        'best_pairs': ['EUR_GBP', 'EUR_AUD', 'AUD_NZD'],
        'note': 'Swing trading, fewer but larger moves',
    },
    
    'D1': {
        'lookback': 200,
        'z_entry': 2.2,
        'z_exit': 0.7,
        'z_stop': 3.3,
        'expected_duration_bars': 100,
        'best_pairs': ['EUR_GBP'],
        'note': 'Long-term positions, often takes many days',
    },
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4: MARKET CONDITION PRESETS
# ════════════════════════════════════════════════════════════════════════════

CONDITION_PRESETS = {
    # During high volatility / uncertainty
    'HIGH_VOLATILITY': {
        'z_entry': 2.5,              # Extreme entries only
        'z_exit': 0.2,               # Exit quickly (don't let it swing back)
        'z_stop': 2.7,               # Super tight stop (early exit)
        'min_correlation': 0.80,     # Only best pairs
        'volatility_threshold': 0.001,  # Skip if too volatile
        'note': 'News events, economic crisis, bank interventions',
    },
    
    # During normal / stable conditions
    'NORMAL': {
        'z_entry': 2.0,
        'z_exit': 0.5,
        'z_stop': 3.0,
        'min_correlation': 0.70,
        'volatility_threshold': 0.002,
        'note': 'Regular trading, most days fall into this',
    },
    
    # During low volatility / sleepy market
    'LOW_VOLATILITY': {
        'z_entry': 1.8,              # Enter on smaller deviation
        'z_exit': 0.6,               # Let it revertt fully
        'z_stop': 3.2,               # Wider stop
        'min_correlation': 0.65,     # Looser filter
        'volatility_threshold': 0.003,   # Allow more
        'note': 'Holidays, weekends, no data',
    },
    
    # After correlation breakdown event
    'POST_BREAKDOWN': {
        'action': 'PAUSE_TRADING',
        'reason': 'Correlation has broken, strategy unreliable',
        'recovery_plan': 'Wait 50 bars, re-analyze, verify cointegration restored',
        'note': 'After Brexit-type events, rate cut surprises, etc.',
    },
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5: POSITION SIZING TEMPLATES
# ════════════════════════════════════════════════════════════════════════════

POSITION_SIZING = {
    'ULTRA_CONSERVATIVE': {
        'account_size': 10000,
        'risk_per_trade_pct': 0.01,   # 1% risk
        'max_positions': 1,            # One at a time
        'scale_out_at': [0.5],         # Exit 100% at once
        'description': 'Suitable for accounts < $5k or high risk aversion',
    },
    
    'CONSERVATIVE': {
        'account_size': 10000,
        'risk_per_trade_pct': 0.02,   # 2% risk
        'max_positions': 1,
        'scale_out_at': [0.5],         # Exit all at target
        'description': 'Recommended for most traders',
    },
    
    'BALANCED': {
        'account_size': 25000,
        'risk_per_trade_pct': 0.02,   # 2% risk per trade
        'max_positions': 2,            # Can have 2 pair trades simultaneously
        'scale_out_at': [0.3, 0.7],    # Exit 50% early, 50% at target
        'description': 'Multiple pair setups, scale in/out',
    },
    
    'AGGRESSIVE': {
        'account_size': 50000,
        'risk_per_trade_pct': 0.03,   # 3% risk per trade
        'max_positions': 3,
        'scale_out_at': [0.3, 0.6, 0.9],  # Pyramid exits
        'description': 'High volume, multiple pairs traded simultaneously',
    },
}


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6: QUICK CONFIG BUILDER
# ════════════════════════════════════════════════════════════════════════════

def build_config(
    pair_preset='EUR_GBP',
    strategy_preset='BALANCED',
    timeframe='H1',
    account_size=10000,
    risk_pct=0.02,
):
    """
    Build complete configuration from presets
    
    Usage:
        config = build_config(
            pair_preset='EUR_GBP',
            strategy_preset='BALANCED',
            timeframe='H1',
            account_size=10000,
        )
        strategy = PairsTradingStrategy(**config)
    """
    
    # Get presets
    pair_info = PAIR_PRESETS.get(pair_preset, {})
    strategy_info = STRATEGY_PRESETS.get(strategy_preset, {})
    timeframe_info = TIMEFRAME_PRESETS.get(timeframe, {})
    
    # Merge with timeframe overrides
    config = {
        # Pair info
        'pair1': pair_info.get('pair1', 'EURUSD'),
        'pair2': pair_info.get('pair2', 'GBPUSD'),
        
        # Strategy params (timeframe overrides strategy preset)
        'lookback': timeframe_info.get('lookback', strategy_info.get('lookback', 100)),
        'z_entry': timeframe_info.get('z_entry', strategy_info.get('z_entry', 2.0)),
        'z_exit': timeframe_info.get('z_exit', strategy_info.get('z_exit', 0.5)),
        'z_stop': timeframe_info.get('z_stop', strategy_info.get('z_stop', 3.0)),
        'min_correlation': strategy_info.get('min_correlation', 0.70),
        'volatility_threshold': strategy_info.get('volatility_threshold', 0.002),
    }
    
    # Backtest config
    backtest_config = {
        'account_size': account_size,
        'risk_pct_per_trade': risk_pct,
        'pair1_name': config['pair1'],
        'pair2_name': config['pair2'],
    }
    
    return config, backtest_config


# ════════════════════════════════════════════════════════════════════════════
# SECTION 7: EXAMPLE CONFIGURATIONS
# ════════════════════════════════════════════════════════════════════════════

# Example 1: Conservative day trader
EXAMPLE_CONFIG_1 = build_config(
    pair_preset='EUR_GBP',
    strategy_preset='CONSERVATIVE',
    timeframe='H1',
    account_size=20000,
    risk_pct=0.01,
)

# Example 2: Balanced trader (recommended for learning)
EXAMPLE_CONFIG_2 = build_config(
    pair_preset='EUR_GBP',
    strategy_preset='BALANCED',
    timeframe='H1',
    account_size=10000,
    risk_pct=0.02,
)

# Example 3: Aggressive scalper
EXAMPLE_CONFIG_3 = build_config(
    pair_preset='AUD_NZD',
    strategy_preset='AGGRESSIVE',
    timeframe='M15',
    account_size=50000,
    risk_pct=0.03,
)

# Example 4: Swing trader (H4)
EXAMPLE_CONFIG_4 = build_config(
    pair_preset='EUR_GBP',
    strategy_preset='BALANCED',
    timeframe='H4',
    account_size=25000,
    risk_pct=0.02,
)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 8: USAGE EXAMPLES
# ════════════════════════════════════════════════════════════════════════════

"""
HOW TO USE THESE TEMPLATES:

1. Simple Usage:
   
   from hft.strategies.pairs_trading_strategy import PairsTradingStrategy
   from pairs_trading_config import EXAMPLE_CONFIG_2  # Balanced example
   
   strategy_config, backtest_config = EXAMPLE_CONFIG_2
   strategy = PairsTradingStrategy(**strategy_config)
   
   # Use strategy...


2. Custom Configuration:
   
   from pairs_trading_config import build_config
   
   config, backtest_config = build_config(
       pair_preset='EUR_GBP',
       strategy_preset='BALANCED',
       timeframe='H1',
       account_size=15000,
   )
   
   strategy = PairsTradingStrategy(**config)


3. Using Presets Directly:
   
   from pairs_trading_config import STRATEGY_PRESETS
   
   conservative_params = STRATEGY_PRESETS['CONSERVATIVE']
   strategy = PairsTradingStrategy(
       pair1='EURUSD',
       pair2='GBPUSD',
       **conservative_params  # Unpack all params
   )


4. Building Your Own:
   
   MY_CONFIG = {
       'pair1': 'EURUSD',
       'pair2': 'GBPUSD',
       'lookback': 100,
       'z_entry': 2.0,
       'z_exit': 0.5,
       'z_stop': 3.0,
   }
   
   strategy = PairsTradingStrategy(**MY_CONFIG)
"""


# ════════════════════════════════════════════════════════════════════════════
# SECTION 9: DEBUGGING CHECKLIST
# ════════════════════════════════════════════════════════════════════════════

DEBUG_CHECKLIST = {
    'correlation_low': {
        'symptom': 'Few signals generated',
        'possible_causes': [
            'Correlation below min_correlation threshold',
            'Pairs not actually correlated (bad setup)',
        ],
        'solutions': [
            'Lower min_correlation threshold',
            'Choose different pair combination',
            'Check with analyzer.analyze_pair_relationship()',
        ],
    },
    
    'no_signals': {
        'symptom': 'Zero trades in backtest',
        'possible_causes': [
            'Z-score never reaches entry threshold',
            'Volatility filter blocking all entries',
            'Correlation fails filter',
        ],
        'solutions': [
            'Lower z_entry threshold',
            'Raise volatility_threshold',
            'Lower min_correlation',
            'Check if pairs actually diverge',
        ],
    },
    
    'high_drawdown': {
        'symptom': 'Too many losing trades, large losses',
        'possible_causes': [
            'z_stop too wide (holding through correlation breaks)',
            'Position size too large',
            'Bad pair combination',
        ],
        'solutions': [
            'Tighten z_stop to 2.8-2.9',
            'Lower risk_per_trade',
            'Verify cointegration with analyzer',
            'Use CONSERVATIVE preset',
        ],
    },
    
    'small_profits': {
        'symptom': 'Few pips profit per trade',
        'possible_causes': [
            'z_exit too tight (exiting too early)',
            'Pairs not volatile enough',
            'Slippage/commission eating profits',
        ],
        'solutions': [
            'Raise z_exit threshold (0.7-1.0)',
            'Choose more volatile pairs',
            'Scale in/out (exit 50% early, 50% at target)',
        ],
    },
}


if __name__ == '__main__':
    print("Pairs Trading Configuration Templates\n")
    print("=" * 80)
    print("\nPredefined Pairs:")
    for name in PAIR_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nStrategy Presets:")
    for name in STRATEGY_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nTimeframe Presets:")
    for name in TIMEFRAME_PRESETS.keys():
        print(f"  - {name}")
    
    print("\nTo Use:")
    print("""
    from pairs_trading_config import build_config
    config, backtest_config = build_config(
        pair_preset='EUR_GBP',
        strategy_preset='BALANCED',
        timeframe='H1',
    )
    """)
