"""
PAIRS TRADING COMPLETE GUIDE
═══════════════════════════════════════════════════════════════════════════════

Master the Strategy That Trades RELATIONSHIPS, Not Prices

A comprehensive guide to understanding and implementing mean reversion pairs 
trading in forex based on statistical arbitrage principles.

═══════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: FOUNDATIONAL CONCEPTS
# ═══════════════════════════════════════════════════════════════════════════════

"""
🧠 THE FUNDAMENTAL SHIFT IN THINKING

Regular Trading:
  ❌ I think EUR will go up → buy EUR/USD
  ❌ Risk: If EUR stays flat or goes down, I lose
  ❌ Need: Correct directional prediction

Pairs Trading:
  ✓ EUR and GBP usually move together (common fundamentals)
  ✓ When they diverge → relationship breaks → correction coming
  ✓ Risk: Even if both go up, I can still profit if GBP goes up MORE
  ✓ Need: Correct relative prediction (not absolute direction)

KEY INSIGHT:
  You are NOT trading the price of EUR/USD
  You are trading the SPREAD between EUR/USD and GBP/USD
  
  Think of it like this:
    - If someone says "EURUSD is too high compared to GBPUSD"
    - You sell the relationship (sell EUR, buy GBP)
    - Market corrects the imbalance
    - You profit on both being right about the relationship
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: MATHEMATICAL FOUNDATION
# ═══════════════════════════════════════════════════════════════════════════════

"""
📊 THE SPREAD (Heart of the Strategy)

Simple spread:
  Spread = EURUSD - GBPUSD
  Problem: EUR and GBP have different volatilities
  Example: If EUR moves 50 pips and GBP moves 80 pips
           Raw spread might go sideways even if opportunity exists

Solution: Use hedge ratio (β)
  Spread = EURUSD - (β × GBPUSD)
  
  β is calculated by linear regression:
    - Fits best line between the two pairs
    - Normalizes their movements so they're comparable
    - Ensures both legs have equal "influence" on the spread

Example calculation:
  EUR closes at 1.1000
  GBP closes at 1.2700
  
  Linear regression finds β = 0.85
  
  Spread = 1.1000 - (0.85 × 1.2700)
  Spread = 1.1000 - 1.0795
  Spread = 0.0205

🎯 Z-SCORE: The Signal Generator

  Z = (Current_Spread - Mean_Spread) / StdDev_Spread
  
  |Z| = 0 → Spread at normal level (equilibrium)
  |Z| = 1 → Spread is 1 standard deviation away
  |Z| = 2 → Spread is 2 standard deviations away (unusual)
  |Z| = 3 → Spread is 3 standard deviations away (extreme)
  
  Intuition:
    - Market is in equilibrium most of the time
    - Deviations happen (supply/demand imbalances)
    - Extreme deviations attract arbitrage (market makers correct it)
    - This correction generates profit

📈 MEAN REVERSION (The Money Maker)

  "The bigger the deviation, the stronger the reversion to mean"
  
  Process:
    1. Spread expands → Z increases (tension building)
    2. Traders notice imbalance → start trading against it
    3. Spread contracts → Z approaches 0 (tension released)
    4. Position closes → profit collected
  
  High probability: 
    - Market corrections are consistent and reliable
    - Mean reversion trades > 50% win rate
    - Losses are small (stopped out early)
    - Wins are consistent (spread naturally reverts)
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: STRATEGY MECHANICS
# ═══════════════════════════════════════════════════════════════════════════════

"""
🎯 TRADING RULES (Step by Step)

CONTINUOUS PROCESS:

1. Calculate Spread (every bar)
   spread = EURUSD - (β × GBPUSD)
   
2. Calculate Z-Score (every bar)
   Use last 100 bars to calculate mean and std
   Z = (spread - mean) / std
   
3. Entry Decision (when Z crosses thresholds)
   
   If Z > +2.0:
     ➡️ Spread is UNUSUALLY HIGH
     ➡️ EUR is OVERPRICED relative to GBP
     ➡️ Action: SELL EUR/USD, BUY GBP/USD
     ➡️ Why: Both will likely revert (EUR down, GBP up, or both)
     ➡️ Exit: When Z returns to +0.5 (profit) or > +3.0 (stop loss)
   
   If Z < -2.0:
     ➡️ Spread is UNUSUALLY LOW
     ➡️ EUR is UNDERPRICED relative to GBP
     ➡️ Action: BUY EUR/USD, SELL GBP/USD
     ➡️ Why: Both will likely revert (EUR up, GBP down, or both)
     ➡️ Exit: When Z returns to -0.5 (profit) or < -3.0 (stop loss)
   
   If -0.5 < Z < +0.5:
     ➡️ Spread is NORMAL
     ➡️ No trade (market in equilibrium)
     ➡️ Close any open position (profit taking)

4. Position Management
   - Entry: When Z crosses ±2.0 threshold
   - Profit Taking: When Z approaches 0 (mean reversion completed)
   - Stop Loss: When Z exceeds ±3.0 (correlation breakdown warning)
   - Time SL: Hold max 20-50 bars without progress

🎲 EXAMPLE TRADE SEQUENCE:

Day 1:
  EUR: 1.1000
  GBP: 1.2700
  Spread = 1.1000 - (0.85 × 1.2700) = 0.0205
  Z = +1.5 (normal, wait)

Day 2:
  EUR: 1.1050 (↑50 pips)
  GBP: 1.2700 (flat)
  Spread = 1.1050 - (0.85 × 1.2700) = 0.0255
  Z = +2.1 (SIGNAL: EUR too strong relative to GBP)
  → SELL EUR (it's overpriced)
  → BUY GBP (it's underpriced)

Day 3:
  EUR: 1.1020 (↓30 pips)
  GBP: 1.2720 (↑20 pips)
  Spread = 1.1020 - (0.85 × 1.2720) = 0.0198
  Z = 0.0 (back to mean)
  → CLOSE POSITION
  → PROFIT from both spreads normalizing

Profit breakdown:
  EUR: Sold @ 1.1050, Close @ 1.1020 → +30 pips = ✓ Profit
  GBP: Sent @ 1.2700, Close @ 1.2720 → +20 pips = ✓ Profit
  
  Both legs profitable because spread reverted!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: WHY THIS WORKS (Market Structure)
# ═══════════════════════════════════════════════════════════════════════════════

"""
✓ REASONS FOR SUCCESS:

1. Fundamental Linkage
   EUR and GBP both tied to European economy
   → Share common drivers
   → Correlation is high and stable
   → Divergence is temporary

2. Institutional Aversion to Arbitrage
   Big players (algo traders, prop firms, banks):
   → Actively hunt for mispricings
   → Correct imbalances automatically
   → Create profit opportunity for us

3. Liquidity Flow Patterns
   When EUR rallies strongly:
   → European assets outflow
   → GBP often follows (funding currency effects)
   → Spread normalized quickly

4. Mean Reversion as Market Property
   Markets are not truly random:
   → Overextensions attract counter-traders
   → Supply/demand naturally reverts
   → Volatility clusters then settles

🚨 WHEN IT FAILS (Critical Understanding):

❌ Correlation Breakdown
   Examples:
   - Brexit announcement (GBP diverges from EUR)
   - ECB vs BoE policy divergence
   - Economic data surprises one country
   
   Result:
   - Pairs stop moving together
   - Hedge fails (both go down)
   - Large loss on both legs

❌ Trending Regime
   Market enters strong directional trend:
   - Spread keeps expanding (not reverting)
   - Z-score keeps increasing (doesn't return to mean)
   - Trader keeps adding losing position
   
   Result:
   - Series of losses
   - Account drawdown
   - Strategy break

❌ Extreme Volatility Events
   During news (NFP, ECB decision, etc.):
   - Correlations become unreliable
   - Slippage increases dramatically
   - Hedge may not work instantly
   
   Solution:
   - Filter out high volatility periods
   - Skip trades near major data releases
   - Reduce size during uncertain times

⚖️ Risk/Reward Profile:

Advantages:
  ✓ High win rate (60-70% when working)
  ✓ Low correlation risk (hedge both directions)
  ✓ Mean reversion is natural market property
  ✓ Can trade in sideways market (doesn't need trend)

Trade-offs:
  ⚠ Profit per trade is small (spread compression)
  ⚠ Requires discipline (high volume to compound)
  ⚠ Sensitive to regime changes
  ⚠ Needs precise execution (both legs filled correctly)
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: IMPLEMENTATION BEST PRACTICES
# ═══════════════════════════════════════════════════════════════════════════════

"""
✅ PROFESSIONAL SETUP CHECKLIST:

1. Cointegration Test (MUST DO)
   Before trading pairs:
   - Run Engle-Granger teste
   - Verify p-value < 0.05
   - Confirms true long-term relationship
   - Not just correlation, but genuine cointegration

2. Rolling Windows (Critical)
   - Don't use static parameters
   - Recalculate β, mean, std every bar
   - Use last 100-200 bars (1-2 H1 candles)
   - Adapt to market regime changes

3. Volatility Filter (Avoid Blown Stops)
   Skip entries when:
   - Recent volatility > 0.2% (threshold)
   - News calendar shows major events
   - VIX equivalent > 20
   - Recent price movement > 3 ATR

4. Entry Management
   When Z > +2.0 (or < -2.0):
   - Must fill BOTH legs simultaneously
   - Or within 1-2 seconds (maintain balance)
   - If one leg fills but not other:
     → Directional bias enters
     → Hedge fails
     → Potential catastrophic loss

5. Position Sizing
   For each trade:
   - Risk max 1-2% account per pair trade
   - Size pair1: Based on standard SL calculation
   - Size pair2: Scale by hedge ratio to equalize notional
   
   Formula:
     risk_amount = account * 0.02  (2% risk)
     volume_pair1 = risk_amount / (price * pip_size)
     volume_pair2 = (volume_pair1 × price1) / (price2 × beta)

6. Stop Loss Placement
   Hard Stop: Z > ±3.0
   - If Z reaches 3σ from mean, regime likely changed
   - Correlation breakdown warning
   - Take loss and wait for reestablishment
   
   Time Stop: No progress for 50 bars
   - If spread doesn't move toward mean
   - Exit and look for next setup
   - Don't hope for reversion (might be trending)

7. Profit Taking
   Primary TP: Z approaches 0.5
   - Spread reverted ~50%
   - Collect profit and move on
   
   Scaling: Exit half at Z=0.5, half at Z=0.2
   - Lock in profits early
   - Let winners run

8. Continuous Monitoring
   After entry:
   - Monitor correlation (should stay > 0.7)
   - Watch hedge ratio (should stay stable)
   - Check mean reversion progress
   - If correlation drops quickly → stop out
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: PYTHON IMPLEMENTATION GUIDE
# ═══════════════════════════════════════════════════════════════════════════════

"""
QUICK START CODE:

from hft.strategies.pairs_trading_strategy import PairsTradingStrategy
from hft.utils.pairs_backtest_engine import PairsBacktestEngine

# 1. Create strategy
strategy = PairsTradingStrategy(
    pair1='EURUSD',
    pair2='GBPUSD',
    lookback=100,
    z_entry=2.0,       # Entry threshold
    z_exit=0.5,        # Profit taking threshold
    z_stop=3.0,        # Hard stop loss
)

# 2. Load data (example with 500 bars of H1)
df1 = load_data('EURUSD', 'H1', bars=500)
df2 = load_data('GBPUSD', 'H1', bars=500)

# 3. Generate signals
signals = strategy.generate_signals(df1, df2)

# 4. Pre-trade analysis (MUST DO)
from hft.strategies.pairs_trading_strategy import PairsTradingAnalyzer
analyzer = PairsTradingAnalyzer()
analysis = analyzer.analyze_pair_relationship(df1, df2)

print(f"Correlation: {analysis['correlation']:.3f}")  # Should be > 0.7
print(f"Cointegrated: {analysis['is_cointegrated']}")  # Should be True
print(f"Hedge Ratio: {analysis['hedge_ratio']:.3f}")   # Factor for balance

# 5. Run backtest
engine = PairsBacktestEngine(
    account_size=10000,
    risk_pct_per_trade=0.02,
    pair1_name='EURUSD',
    pair2_name='GBPUSD',
)

results = engine.backtest(
    df1, df2,
    z_exit_threshold=0.5,
    z_stop_threshold=3.0,
)

print(results)  # Statistics and trade list

# 6. Live trading (both pairs simultaneously)
for i in range(len(signals)):
    signal = signals['signal_pair1'].iloc[i]
    
    if signal == 1:  # Long spread
        buy_eurusd(volume=1.0)    # Buy pair1
        sell_gbpusd(volume=0.95)  # Sell pair2 (scaled by beta)
    
    elif signal == -1:  # Short spread
        sell_eurusd(volume=1.0)   # Sell pair1
        buy_gbpusd(volume=0.95)   # Buy pair2 (scaled by beta)
    
    elif needs_exit:
        close_eurusd()
        close_gbpusd()
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 7: COMMON PITFALLS & SOLUTIONS
# ═══════════════════════════════════════════════════════════════════════════════

"""
❌ PITFALL 1: Using Correlation ≠ Cointegration

❌ Wrong:
  if correlation > 0.8:
      trade_pairs()

✓ Correct:
  # Check cointegration first
  t_stat, p_value = strategy.cointegration_test(spread)
  if p_value < 0.05:  # Cointegrated
      trade_pairs()

Why:
  - Correlation can be high but temporary (spurious)
  - Cointegration = true long-term relationship
  - Difference matters when regime changes

---

❌ PITFALL 2: Trading Without Hedge Ratio

❌ Wrong:
  eurusd_volume = 1.0
  gbpusd_volume = 1.0  # Equal, but wrong!

✓ Correct:
  beta = calculate_hedge_ratio(eurusd, gbpusd)
  eurusd_volume = 1.0
  gbpusd_volume = eurusd_volume * eurusd_price / (gbpusd_price * beta)

Why:
  - Equal volumes creates directional bias
  - Hedge fails if movements unequal
  - Beta ensures true offsetting

---

❌ PITFALL 3: Holding Through Correlation Breakdown

❌ Wrong:
  if abs(zscore) < 3.0:
      stay_in_trade()  # Even if correlation breaks

✓ Correct:
  correlation = calculate_correlation(pair1, pair2, window=20)
  if correlation < 0.5 or abs(zscore) > 3.0:
      exit_immediately()  # Regime change warning

Why:
  - Correlation breakdown = hedge fails
  - Both pairs go same direction = double loss
  - Must exit before real damage

---

❌ PITFALL 4: Overlapping Trades

❌ Wrong:
  if is_signal_generated():
      enter_trade()  # Don't care if already in trade

✓ Correct:
  if is_signal_generated() and position is None:
      enter_trade()  # Only one trade at a time
  elif is_exit_signal():
      close_trade()

Why:
  - Each pair trade is complete strategy
  - Stacking trades in same pairs = dangerous risk
  - Close fully before next entry

---

❌ PITFALL 5: Ignoring Z-Score Hard Stop

❌ Wrong:
  if abs(zscore) < 5.0:
      stay_in_trade()  # Hoping for revert

✓ Correct:
  if abs(zscore) > 3.0:
      stop_loss_immediate()  # Correlation likely broken

Why:
  - Z > 3σ is mathematically extreme (99.7% confidence)
  - Means correlation structure breakdown
  - Waiting costs MORE than exiting and re-entering later
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 8: ADVANCED IDEAS
# ═══════════════════════════════════════════════════════════════════════════════

"""
🔬 ADVANCED ENHANCEMENTS:

1. Multi-Pair Framework
   Don't trade just one pair combination
   - EUR/USD vs GBP/USD
   - EUR/USD vs AUD/USD  
   - GBP/USD vs NZD/USD
   
   Algorithm:
   - Calculate Z-score for all combinations
   - Pick best setup (highest z-score + highest correlation)
   - Trade the strongest setup
   - Improves win rate and reduce correlation overlap

2. Dynamic Z-Score Thresholds
   Instead of fixed Z = ±2.0:
   - Track historical z-score distribution
   - Use percentile-based thresholds
   - 95th percentile (Z ≈ 1.96) as entry
   - Adapts to changing volatility regime

3. Volatility-Based Position Sizing
   Adjust trade size with volatility:
   - High volatility → smaller size
   - Low volatility → larger size
   - Kelly Criterion: f* = (2p - 1) / b
   - Maximizes long-term growth while managing risk

4. Machine Learning Enhancement
   Predict which pairs will revert:
   - Input: Recent Z-scores, correlation, volatility
   - Output: Probability of reversion within N bars
   - Filter trades: Only trade high probability setups
   - Can increase win rate from 60% to 75%+

5. Calendar-Based Filters
   Avoid trading around:
   - Economic data (NFP, ECB decision)
   - Start of week (risk-on/off flows)
   - End of month (fund rebalancing)
   
   Benefits:
   - Reduced slippage
   - More stable correlations
   - Higher win rate

6. Fractional Position Management
   Instead of binary (in/out):
   - Add at Z > 2.5 (size 0.5x)
   - Add at Z > 3.0 (size 0.5x) - but check correlation!
   - Exit half at Z = 0.5
   - Exit half at Z = 0.0
   - Captures more of moves while managing risk

7. Ensemble Strategy
   Combine multiple timeframes:
   - H1: Generate signals
   - M15: Confirm entries (reduce false signals)
   - D1: Filter (avoid low-correlation periods)
   
   Logic:
   AND (H1 signal) AND (M15 confirmation) AND (D1 filter) → Entry
   Dramatically increases edge
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 9: MONITORING & METRICS
# ═══════════════════════════════════════════════════════════════════════════════

"""
📊 KEY METRICS TO TRACK:

Real-Time Monitoring:
  - Current Z-score: Where are we in the cycle?
  - Correlation (20-bar rolling): Is relationship stable?
  - Hedge ratio: Has it changed significantly?
  - Spread mean/std: Are thresholds still valid?

Trade Tracking:
  - Win rate: Should be 60%+ (mean reversion bias)
  - Avg win vs avg loss: Ratio > 1.5 (profitable)
  - Max trade duration: Usually < 50 bars
  - Max drawdown: Usually < 15% if sizing correct

Portfolio Level:
  - Sharpe ratio: Risk-adjusted return (goal > 1.0)
  - Profit factor: Total wins / Total losses (goal > 1.5)
  - Recovery factor: Total profit / Max drawdown (goal > 2.0)
  - Monthly return consistency: Should be relatively smooth

🚨 RED FLAGS TO EXIT STRATEGY:

  ❌ Win rate drops below 50%
  ❌ Average loss larger than average win
  ❌ Correlation drops below 0.5 for extended period
  ❌ Multiple trades hit hard stop (Z > 3.0)
  ❌ Drawdown exceeds planned threshold
  ❌ Spread never reverts (trends instead)

Action: Pause strategy and re-analyze pair relationship
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART 10: QUICK REFERENCE CARD
# ═══════════════════════════════════════════════════════════════════════════════

"""
╔════════════════════════════════════════════════════════════════════════════╗
║                        PAIRS TRADING CHEAT SHEET                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║ CORE FORMULA:                                                              ║
║   Spread = Pair1 - (β × Pair2)                                            ║
║   Z-Score = (Spread - Mean) / StdDev                                      ║
║                                                                            ║
║ ENTRY SIGNALS:                                                             ║
║   Z > +2.0  →  SELL Pair1, BUY Pair2  (Close spread/revert)              ║
║   Z < -2.0  →  BUY Pair1, SELL Pair2  (Open spread/revert)               ║
║                                                                            ║
║ EXIT SIGNALS:                                                              ║
║   |Z| < 0.5  →  CLOSE (Profit taking, spread reverted)                   ║
║   |Z| > 3.0  →  STOP LOSS (Correlation breakdown)                        ║
║   No progress 50 bars  →  EXIT (Time stop)                               ║
║                                                                            ║
║ PREREQUISITES:                                                             ║
║   ✓ Correlation > 0.7                                                     ║
║   ✓ Cointegration p-value < 0.05                                         ║
║   ✓ Volatility < 0.2%                                                     ║
║                                                                            ║
║ POSITION SIZING:                                                           ║
║   Risk = Account × 2% per trade                                          ║
║   Volume Pair1 = Risk / (Price × Pip Size)                               ║
║   Volume Pair2 = Volume1 × Price1 / (Price2 × β)                        ║
║                                                                            ║
║ PROFIT PROFILE:                                                            ║
║   Win Rate: 60-70%                                                        ║
║   Avg Win: Small (20-50 pips spread compression)                         ║
║   Avg Loss: Small (stopped at Z > 3.0)                                   ║
║   Ratio: Win rate HIGH, but profit/trade SMALL                           ║
║                                                                            ║
║ WHY IT WORKS:                                                              ║
║   2 correlated pairs temporarily diverge                                  ║
║   Divergence attracts arbitrage/correction                                ║
║   Spread reverts to equilibrium                                           ║
║   Trader exits with profit on both legs                                   ║
║                                                                            ║
║ WHEN IT FAILS:                                                             ║
║   ✗ Correlation breakdown (Brexit, policy divergence)                     ║
║   ✗ Trending regime (spread doesn't revert)                              ║
║   ✗ Overlap with major news (correlation unreliable)                      ║
║   ✗ Using equal volumes (should scale by hedge ratio)                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

if __name__ == '__main__':
    print(__doc__)
    print("""
═══════════════════════════════════════════════════════════════════════════════
READY TO TRADE?

Next Steps:
1. Read PART 1-3 (Understand the philosophy)
2. Study PART 4 (Learn why it works)
3. Code PART 6 (Implement with Python examples)
4. Check PART 7 (Avoid common pitfalls)
5. Monitor PART 9 (Track metrics, know when to exit)

Questions to ask yourself before trading:
- Is correlation > 0.7?
- Is spread cointegrated?
- Can I execute both legs simultaneously?
- Do I have proper stop loss discipline?
- Is volatility low enough?
- Do I understand the risk?

Remember:
  Mean reversion is NOT guaranteed
  Correlation can break without warning
  This is NOT a risk-free arbitrage
  Proper risk management is ESSENTIAL
  
═══════════════════════════════════════════════════════════════════════════════
    """)
