"""
MQL KING 1 - SMC HFT Backtesting Framework
Professional Smart Money Concepts Trading System
Backtester for XAUUSD M1 Strategy

This backtester implements the exact same logic as the MQL5 EA
to verify strategy performance before live trading.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES (Same as MQL5)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LiquidityLevel:
    """Liquidity level structure"""
    level: float
    time: int
    is_high: bool  # True = resistance, False = support

@dataclass
class OrderBlock:
    """Order Block structure"""
    high: float
    low: float
    time: int
    is_bullish: bool
    strength: float

@dataclass
class FairValueGap:
    """Fair Value Gap structure"""
    top: float
    bottom: float
    time: int
    is_bullish: bool

@dataclass
class Trade:
    """Trade record"""
    entry_time: int
    entry_price: float
    stop_loss: float
    take_profit: float
    side: str  # 'BUY' or 'SELL'
    position_size: float
    entry_reason: str
    exit_price: float = None
    exit_time: int = None
    exit_reason: str = None
    profit_loss: float = None
    profit_loss_percent: float = None
    win: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# BACKTESTER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class MQLKing1Backtester:
    """
    MQL King 1 Backtesting System
    Implements SMC-based HFT strategy for XAUUSD M1
    """
    
    def __init__(self, ohlc_data: pd.DataFrame, **kwargs):
        """
        Initialize backtester
        
        Args:
            ohlc_data: DataFrame with columns [open, high, low, close, volume, time]
            **kwargs: Strategy parameters
        """
        self.df = ohlc_data.copy().reset_index(drop=True)
        
        # Strategy Parameters
        self.structure_lookback = kwargs.get('structure_lookback', 10)
        self.min_structure_ratio = kwargs.get('min_structure_ratio', 1.2)
        self.order_block_lookback = kwargs.get('order_block_lookback', 5)
        self.order_block_threshold = kwargs.get('order_block_threshold', 0.5)
        self.liquidity_memory = kwargs.get('liquidity_memory', 50)
        self.fvg_min_gap_percent = kwargs.get('fvg_min_gap_percent', 0.01)
        self.fvg_lookback = kwargs.get('fvg_lookback', 5)
        self.displacement_threshold = kwargs.get('displacement_threshold', 2.0)
        self.displacement_bars = kwargs.get('displacement_bars', 3)
        
        # Risk Management
        self.risk_percent = kwargs.get('risk_percent', 0.5)
        self.max_rr_ratio = kwargs.get('max_rr_ratio', 3.0)
        self.min_rr_ratio = kwargs.get('min_rr_ratio', 1.5)
        self.max_trades_per_day = kwargs.get('max_trades_per_day', 5)
        self.max_consecutive_losses = kwargs.get('max_consecutive_losses', 3)
        self.max_open_trades = kwargs.get('max_open_trades', 1)
        self.atr_multiplier_stop = kwargs.get('atr_multiplier_stop', 1.5)
        self.atr_multiplier_target = kwargs.get('atr_multiplier_target', 3.0)
        self.atr_period = kwargs.get('atr_period', 14)
        
        # Session Filters
        self.use_session_filter = kwargs.get('use_session_filter', True)
        self.london_open_hour = kwargs.get('london_open_hour', 8)
        self.ny_open_hour = kwargs.get('ny_open_hour', 13)
        self.asian_dead_hour = kwargs.get('asian_dead_hour', 2)
        self.initial_balance = kwargs.get('initial_balance', 10000)
        
        # Calculate ATR for all bars
        self._calculate_atr()
        
        # Storage
        self.liquidity_zones: List[LiquidityLevel] = []
        self.order_blocks: List[OrderBlock] = []
        self.fair_value_gaps: List[FairValueGap] = []
        self.trades: List[Trade] = []
        
        # Statistics
        self.balance = self.initial_balance
        self.equity = self.initial_balance
        self.max_drawdown = 0
        self.current_drawdown = 0
        
    def _calculate_atr(self):
        """Calculate ATR for all bars"""
        self.df['tr'] = np.maximum(
            self.df['high'] - self.df['low'],
            np.maximum(
                np.abs(self.df['high'] - self.df['close'].shift(1)),
                np.abs(self.df['low'] - self.df['close'].shift(1))
            )
        )
        self.df['atr'] = self.df['tr'].rolling(self.atr_period).mean()
    
    def backtest(self):
        """Run the backtest"""
        print("\n" + "="*70)
        print("🧭 MQL KING 1 - BACKTESTING START")
        print("="*70)
        print(f"Data points: {len(self.df)}")
        print(f"Period: {self.df.iloc[0]['time']} to {self.df.iloc[-1]['time']}")
        print("="*70 + "\n")
        
        trades_today = 0
        consecutive_losses = 0
        current_day = None
        
        for i in range(self.structure_lookback + 50, len(self.df)):
            current_bar = self.df.iloc[i]
            current_time = current_bar['time']
            
            # Reset daily counters
            if pd.Timestamp(current_time).day != (pd.Timestamp(current_day).day if current_day else -1):
                trades_today = 0
                current_day = current_time
            
            # Check if we should trade
            if trades_today >= self.max_trades_per_day:
                continue
            
            if consecutive_losses >= self.max_consecutive_losses:
                continue
            
            if len([t for t in self.trades if t.exit_time is None]) >= self.max_open_trades:
                continue
            
            if self.use_session_filter and not self._is_good_trading_time(current_time):
                continue
            
            # ═── STEP 1: Detect Market Structure ───═
            trend = self._detect_market_structure(i)
            if trend == 0:
                continue
            
            # ═── STEP 2: Detect Break of Structure ───═
            bos_detected = self._detect_break_of_structure(i, trend)
            if not bos_detected:
                continue
            
            # ═── STEP 3: Update Liquidity Zones ───═
            self._update_liquidity_zones(i)
            
            # ═── STEP 4: Identify Order Blocks ───═
            self._update_order_blocks(i, trend)
            
            # ═── STEP 5: Detect Fair Value Gaps ───═
            self._update_fair_value_gaps(i)
            
            # ═── STEP 6: Detect Displacement ───═
            displacement = self._detect_displacement(i, trend)
            if not displacement:
                continue
            
            # ═── STEP 7: Find Trade Setup ───═
            setup = self._find_trade_setup(i, trend)
            if not setup:
                continue
            
            # ═── STEP 8: Execute Trade ───═
            entry_price = setup[0]
            stop_loss = setup[1]
            take_profit = setup[2]
            entry_reason = setup[3]
            position_size = setup[4]
            
            trade = Trade(
                entry_time=i,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                side='BUY' if trend == 1 else 'SELL',
                position_size=position_size,
                entry_reason=entry_reason
            )
            
            self.trades.append(trade)
            trades_today += 1
            
            print(f"[{pd.Timestamp(current_time)}] {trade.side} - {entry_reason}")
            print(f"  Entry: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")
        
        # Close remaining open trades at market close
        self._close_remaining_trades()
        
        # Calculate statistics
        self._calculate_statistics()
        
        print("\n" + "="*70)
        print("🧭 BACKTEST COMPLETE")
        print("="*70)
        self._print_results()
        
        return self.get_results()
    
    def _detect_market_structure(self, bar_idx) -> int:
        """Detect market structure (uptrend=1, downtrend=-1, no structure=0)"""
        if bar_idx < self.structure_lookback + 5:
            return 0
        
        # Find recent swings
        lookback_data = self.df.iloc[bar_idx - self.structure_lookback:bar_idx + 1]
        highest = lookback_data['high'].max()
        lowest = lookback_data['low'].min()
        
        lookback_data_prev = self.df.iloc[max(0, bar_idx - self.structure_lookback - 5):bar_idx - self.structure_lookback]
        if len(lookback_data_prev) == 0:
            return 0
        
        highest_prev = lookback_data_prev['high'].max()
        lowest_prev = lookback_data_prev['low'].min()
        
        atr = self.df.iloc[bar_idx]['atr']
        if pd.isna(atr) or atr == 0:
            return 0
        
        # UPTREND: HH + HL
        if highest > highest_prev and lowest > lowest_prev and (highest - lowest) > atr * self.min_structure_ratio:
            return 1
        
        # DOWNTREND: LH + LL
        if highest < highest_prev and lowest < lowest_prev and (highest - lowest) > atr * self.min_structure_ratio:
            return -1
        
        return 0
    
    def _detect_break_of_structure(self, bar_idx, trend) -> bool:
        """Detect break of structure"""
        if bar_idx < 20:
            return False
        
        current_close = self.df.iloc[bar_idx]['close']
        prev_close = self.df.iloc[bar_idx - 1]['close']
        
        if trend == 1:  # Uptrend
            resistance = self.df.iloc[max(0, bar_idx - self.structure_lookback - 5):bar_idx]['high'].max()
            return current_close > resistance and prev_close <= resistance
        else:  # Downtrend
            support = self.df.iloc[max(0, bar_idx - self.structure_lookback - 5):bar_idx]['low'].min()
            return current_close < support and prev_close >= support
    
    def _update_liquidity_zones(self, bar_idx):
        """Update liquidity zones"""
        # Check for equal highs
        current_high = self.df.iloc[bar_idx]['high']
        high_count = 0
        
        for i in range(1, min(self.liquidity_memory, bar_idx)):
            if abs(self.df.iloc[bar_idx - i]['high'] - current_high) < 0.05:  # 5 pips
                high_count += 1
                if high_count >= 2:
                    level = LiquidityLevel(current_high, bar_idx, True)
                    if not any(abs(lz.level - level.level) < 0.1 for lz in self.liquidity_zones):
                        self.liquidity_zones.append(level)
                    break
        
        # Check for equal lows
        current_low = self.df.iloc[bar_idx]['low']
        low_count = 0
        
        for i in range(1, min(self.liquidity_memory, bar_idx)):
            if abs(self.df.iloc[bar_idx - i]['low'] - current_low) < 0.05:  # 5 pips
                low_count += 1
                if low_count >= 2:
                    level = LiquidityLevel(current_low, bar_idx, False)
                    if not any(abs(lz.level - level.level) < 0.1 for lz in self.liquidity_zones):
                        self.liquidity_zones.append(level)
                    break
        
        # Remove old liquidity zones
        self.liquidity_zones = [
            lz for lz in self.liquidity_zones 
            if bar_idx - lz.time <= self.liquidity_memory
        ]
    
    def _update_order_blocks(self, bar_idx, trend):
        """Update order blocks"""
        if bar_idx < self.order_block_lookback + 5:
            return
        
        if trend == 1:  # Uptrend - look for bullish OB
            for i in range(1, self.order_block_lookback):
                if bar_idx - i < 0:
                    break
                
                is_bearish = self.df.iloc[bar_idx - i]['close'] < self.df.iloc[bar_idx - i]['open']
                next_is_bullish = self.df.iloc[bar_idx - i + 1]['close'] > self.df.iloc[bar_idx - i + 1]['open']
                
                if is_bearish and next_is_bullish:
                    ob = OrderBlock(
                        high=self.df.iloc[bar_idx - i]['high'],
                        low=self.df.iloc[bar_idx - i]['low'],
                        time=bar_idx - i,
                        is_bullish=True,
                        strength=abs(self.df.iloc[bar_idx - i]['close'] - self.df.iloc[bar_idx - i]['open'])
                    )
                    
                    if not any(abs(o.high - ob.high) < 0.1 for o in self.order_blocks):
                        self.order_blocks.append(ob)
                    break
        else:  # Downtrend - look for bearish OB
            for i in range(1, self.order_block_lookback):
                if bar_idx - i < 0:
                    break
                
                is_bullish = self.df.iloc[bar_idx - i]['close'] > self.df.iloc[bar_idx - i]['open']
                next_is_bearish = self.df.iloc[bar_idx - i + 1]['close'] < self.df.iloc[bar_idx - i + 1]['open']
                
                if is_bullish and next_is_bearish:
                    ob = OrderBlock(
                        high=self.df.iloc[bar_idx - i]['high'],
                        low=self.df.iloc[bar_idx - i]['low'],
                        time=bar_idx - i,
                        is_bullish=False,
                        strength=abs(self.df.iloc[bar_idx - i]['close'] - self.df.iloc[bar_idx - i]['open'])
                    )
                    
                    if not any(abs(o.high - ob.high) < 0.1 for o in self.order_blocks):
                        self.order_blocks.append(ob)
                    break
        
        # Remove old order blocks
        self.order_blocks = [
            ob for ob in self.order_blocks 
            if bar_idx - ob.time <= 200
        ]
    
    def _update_fair_value_gaps(self, bar_idx):
        """Update fair value gaps"""
        if bar_idx < self.fvg_lookback + 2:
            return
        
        for i in range(2, self.fvg_lookback):
            if bar_idx - i < 0 or bar_idx - i - 1 < 0:
                continue
            
            high_current = self.df.iloc[bar_idx - i]['high']
            low_current = self.df.iloc[bar_idx - i]['low']
            high_next = self.df.iloc[bar_idx - i - 1]['high']
            low_next = self.df.iloc[bar_idx - i - 1]['low']
            close_current = self.df.iloc[bar_idx - i]['close']
            
            # Bullish FVG
            if low_current > high_next:
                gap_size = low_current - high_next
                gap_percent = (gap_size / close_current) * 100
                
                if gap_percent >= self.fvg_min_gap_percent:
                    fvg = FairValueGap(
                        top=low_current,
                        bottom=high_next,
                        time=bar_idx - i,
                        is_bullish=True
                    )
                    if not any(abs(f.top - fvg.top) < 0.1 for f in self.fair_value_gaps):
                        self.fair_value_gaps.append(fvg)
            
            # Bearish FVG
            if high_current < low_next:
                gap_size = low_next - high_current
                gap_percent = (gap_size / close_current) * 100
                
                if gap_percent >= self.fvg_min_gap_percent:
                    fvg = FairValueGap(
                        top=low_next,
                        bottom=high_current,
                        time=bar_idx - i,
                        is_bullish=False
                    )
                    if not any(abs(f.top - fvg.top) < 0.1 for f in self.fair_value_gaps):
                        self.fair_value_gaps.append(fvg)
        
        # Remove old FVGs
        self.fair_value_gaps = [
            fvg for fvg in self.fair_value_gaps 
            if bar_idx - fvg.time <= 300
        ]
    
    def _detect_displacement(self, bar_idx, trend) -> bool:
        """Detect displacement (strong impulse)"""
        if bar_idx < self.displacement_bars + 5:
            return False
        
        atr = self.df.iloc[bar_idx]['atr']
        if pd.isna(atr):
            return False
        
        displacement_distance = atr * self.displacement_threshold
        
        if trend == 1:  # Uptrend
            for i in range(self.displacement_bars):
                if bar_idx - i < 0:
                    continue
                candle_size = self.df.iloc[bar_idx - i]['high'] - self.df.iloc[bar_idx - i]['low']
                candle_move = self.df.iloc[bar_idx - i]['close'] - self.df.iloc[bar_idx - i]['open']
                
                if candle_size >= displacement_distance and candle_move > 0:
                    return True
        else:  # Downtrend
            for i in range(self.displacement_bars):
                if bar_idx - i < 0:
                    continue
                candle_size = self.df.iloc[bar_idx - i]['high'] - self.df.iloc[bar_idx - i]['low']
                candle_move = self.df.iloc[bar_idx - i]['open'] - self.df.iloc[bar_idx - i]['close']
                
                if candle_size >= displacement_distance and candle_move > 0:
                    return True
        
        return False
    
    def _find_trade_setup(self, bar_idx, trend) -> Optional[Tuple]:
        """Find trade setup (entry signal)"""
        atr = self.df.iloc[bar_idx]['atr']
        if pd.isna(atr):
            return None
        
        current_price = self.df.iloc[bar_idx]['close']
        
        # Option 1: Order Block Retest
        if len(self.order_blocks) > 0:
            ob = self.order_blocks[0]
            
            if trend == 1 and ob.is_bullish:
                if current_price >= ob.low and current_price <= ob.high:
                    stop_loss = ob.low - atr * self.atr_multiplier_stop
                    take_profit = current_price + atr * self.atr_multiplier_target
                    
                    setup = self._validate_setup(current_price, stop_loss, take_profit, "Order Block Retest (Bullish)")
                    if setup:
                        return setup
            elif trend == -1 and not ob.is_bullish:
                if current_price >= ob.low and current_price <= ob.high:
                    stop_loss = ob.high + atr * self.atr_multiplier_stop
                    take_profit = current_price - atr * self.atr_multiplier_target
                    
                    setup = self._validate_setup(current_price, stop_loss, take_profit, "Order Block Retest (Bearish)")
                    if setup:
                        return setup
        
        # Option 2: FVG Fill
        if len(self.fair_value_gaps) > 0:
            fvg = self.fair_value_gaps[0]
            
            if trend == 1 and fvg.is_bullish:
                if current_price >= fvg.bottom and current_price <= fvg.top:
                    stop_loss = fvg.bottom - atr * self.atr_multiplier_stop
                    take_profit = current_price + atr * self.atr_multiplier_target
                    
                    setup = self._validate_setup(current_price, stop_loss, take_profit, "FVG Fill Entry (Bullish)")
                    if setup:
                        return setup
            elif trend == -1 and not fvg.is_bullish:
                if current_price >= fvg.bottom and current_price <= fvg.top:
                    stop_loss = fvg.top + atr * self.atr_multiplier_stop
                    take_profit = current_price - atr * self.atr_multiplier_target
                    
                    setup = self._validate_setup(current_price, stop_loss, take_profit, "FVG Fill Entry (Bearish)")
                    if setup:
                        return setup
        
        # Option 3: Liquidity Sweep + Reversal
        if len(self.liquidity_zones) > 0:
            liq = self.liquidity_zones[0]
            
            if trend == 1 and not liq.is_high:
                if current_price >= liq.level and current_price <= liq.level + atr:
                    stop_loss = liq.level - atr * self.atr_multiplier_stop
                    take_profit = current_price + atr * self.atr_multiplier_target
                    
                    setup = self._validate_setup(current_price, stop_loss, take_profit, "Liquidity Sweep + Reversal (Bullish)")
                    if setup:
                        return setup
            elif trend == -1 and liq.is_high:
                if current_price <= liq.level and current_price >= liq.level - atr:
                    stop_loss = liq.level + atr * self.atr_multiplier_stop
                    take_profit = current_price - atr * self.atr_multiplier_target
                    
                    setup = self._validate_setup(current_price, stop_loss, take_profit, "Liquidity Sweep + Reversal (Bearish)")
                    if setup:
                        return setup
        
        return None
    
    def _validate_setup(self, entry_price, stop_loss, take_profit, reason) -> Optional[Tuple]:
        """Validate trade setup (RR check)"""
        if stop_loss < entry_price:  # Buy
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:  # Sell
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        if risk <= 0 or reward <= 0:
            return None
        
        rr_ratio = reward / risk
        
        if rr_ratio < self.min_rr_ratio or rr_ratio > self.max_rr_ratio:
            return None
        
        # Calculate position size
        account_balance = self.balance
        risk_amount = account_balance * (self.risk_percent / 100.0)
        point_value = 1.0  # For backtesting purposes
        
        position_size = risk_amount / (risk * point_value)
        
        return (entry_price, stop_loss, take_profit, reason, position_size)
    
    def _close_remaining_trades(self):
        """Close all remaining open trades"""
        last_price = self.df.iloc[-1]['close']
        
        for trade in self.trades:
            if trade.exit_time is None:
                trade.exit_price = last_price
                trade.exit_time = len(self.df) - 1
                trade.exit_reason = "Market Close"
                
                if trade.side == 'BUY':
                    trade.profit_loss = (trade.exit_price - trade.entry_price) * trade.position_size
                else:
                    trade.profit_loss = (trade.entry_price - trade.exit_price) * trade.position_size
                
                trade.profit_loss_percent = (trade.profit_loss / (trade.entry_price * trade.position_size)) * 100
                trade.win = trade.profit_loss > 0
    
    def _calculate_statistics(self):
        """Calculate backtest statistics"""
        total_trades = len(self.trades)
        closed_trades = [t for t in self.trades if t.exit_time is not None]
        closed_count = len(closed_trades)
        
        if closed_count == 0:
            self.equity = self.balance
            return
        
        wins = sum(1 for t in closed_trades if t.win)
        losses = sum(1 for t in closed_trades if not t.win)
        win_rate = (wins / closed_count * 100) if closed_count > 0 else 0
        
        gross_profit = sum(t.profit_loss for t in closed_trades if t.win)
        gross_loss = abs(sum(t.profit_loss for t in closed_trades if not t.win))
        net_profit = sum(t.profit_loss for t in closed_trades)
        
        # Calculate drawdown
        balance_history = [self.initial_balance]
        for trade in closed_trades:
            balance_history.append(balance_history[-1] + trade.profit_loss)
        
        running_max = max(balance_history)
        for balance in balance_history:
            drawdown = (running_max - balance) / running_max * 100
            self.max_drawdown = max(self.max_drawdown, drawdown)
        
        self.equity = self.balance + net_profit
        
        # Store results
        self.results = {
            'total_trades': total_trades,
            'closed_trades': closed_count,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': win_rate,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'net_profit': net_profit,
            'max_drawdown': self.max_drawdown,
            'roi': (net_profit / self.initial_balance) * 100,
            'final_equity': self.equity,
        }
    
    def _print_results(self):
        """Print backtest results"""
        if not hasattr(self, 'results'):
            print("No trades executed.")
            return
        
        r = self.results
        
        print(f"\n{'═'*70}")
        print("📊 BACKTEST RESULTS")
        print(f"{'═'*70}")
        print(f"Total Trades:         {r['total_trades']}")
        print(f"Closed Trades:        {r['closed_trades']}")
        print(f"Winning Trades:       {r['winning_trades']} ({r['win_rate']:.2f}%)")
        print(f"Losing Trades:        {r['losing_trades']}")
        print(f"\n{'─'*70}")
        print(f"Gross Profit:         ${r['gross_profit']:.2f}")
        print(f"Gross Loss:          -${r['gross_loss']:.2f}")
        print(f"Net Profit:           ${r['net_profit']:.2f}")
        print(f"\n{'─'*70}")
        print(f"Initial Balance:      ${self.initial_balance:.2f}")
        print(f"Final Equity:         ${r['final_equity']:.2f}")
        print(f"ROI:                  {r['roi']:.2f}%")
        print(f"Max Drawdown:         {r['max_drawdown']:.2f}%")
        print(f"{'═'*70}\n")
    
    def _is_good_trading_time(self, timestamp) -> bool:
        """Check if it's good trading time"""
        dt = pd.Timestamp(timestamp)
        hour = dt.hour
        minute = dt.minute
        
        # Avoid Asian dead hours
        if hour >= self.asian_dead_hour and hour < self.asian_dead_hour + 2:
            return False
        
        # Trade London Open
        if hour == self.london_open_hour and minute < 30:
            return True
        
        # Trade NY Open
        if hour == self.ny_open_hour and minute < 30:
            return True
        
        # Trade throughout these hours
        if hour >= self.london_open_hour and hour <= self.ny_open_hour + 4:
            return True
        
        return False
    
    def get_results(self) -> dict:
        """Get results dictionary"""
        return getattr(self, 'results', {})
    
    def export_trades(self, filename='trades.csv'):
        """Export trades to CSV"""
        data = []
        for trade in self.trades:
            data.append({
                'entry_time': trade.entry_time,
                'entry_price': trade.entry_price,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit,
                'side': trade.side,
                'position_size': trade.position_size,
                'entry_reason': trade.entry_reason,
                'exit_time': trade.exit_time,
                'exit_price': trade.exit_price,
                'exit_reason': trade.exit_reason,
                'profit_loss': trade.profit_loss,
                'profit_loss_percent': trade.profit_loss_percent,
                'win': trade.win,
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"\n✅ Trades exported to {filename}")
    
    def plot_equity(self, filename='equity_curve.png'):
        """Plot equity curve"""
        balance_history = [self.initial_balance]
        
        for trade in self.trades:
            if trade.exit_time is not None:
                balance_history.append(balance_history[-1] + trade.profit_loss)
        
        plt.figure(figsize=(14, 6))
        plt.plot(balance_history, linewidth=2, label='Equity Curve')
        plt.axhline(y=self.initial_balance, color='r', linestyle='--', label='Initial Balance')
        plt.xlabel('Trade Number')
        plt.ylabel('Account Balance ($)')
        plt.title('MQL King 1 - Equity Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        print(f"✅ Equity curve saved as {filename}")
        plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

def run_backtest():
    """
    Example: Run backtest on sample data
    In production, load real XAUUSD M1 data
    """
    
    # Create sample data (replace with real data from your broker)
    dates = pd.date_range(start='2024-01-01', periods=10000, freq='1min')
    
    np.random.seed(42)
    returns = np.random.normal(0.0001, 0.002, 10000)
    close = 2000 * (1 + returns).cumprod()
    
    ohlc_data = pd.DataFrame({
        'time': dates,
        'open': close + np.random.uniform(-1, 1, 10000),
        'high': close + np.random.uniform(0, 2, 10000),
        'low': close + np.random.uniform(-2, 0, 10000),
        'close': close,
        'volume': np.random.uniform(100, 1000, 10000),
    })
    
    # Initialize backtester
    bt = MQLKing1Backtester(
        ohlc_data,
        structure_lookback=10,
        min_structure_ratio=1.2,
        risk_percent=0.5,
        min_rr_ratio=1.5,
        max_rr_ratio=3.0,
        displacement_threshold=2.0,
        initial_balance=10000
    )
    
    # Run backtest
    results = bt.backtest()
    
    # Export results
    bt.export_trades('mql_king_1_trades.csv')
    bt.plot_equity('mql_king_1_equity.png')
    
    return bt


if __name__ == "__main__":
    backtester = run_backtest()
