"""
Pairs Trading Backtest Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unlike regular backtests, pairs trading requires:
1. Trading BOTH pairs simultaneously
2. Calculating P&L on the SPREAD (relationship), not individual pairs
3. Proper hedging accounting
4. Correlation-based risk (when hedge breaks, both lose)

This engine tracks:
- Entry prices for both pairs
- Spread at entry
- Z-score progression
- Exit on Z-reversion or stop-loss trigger
- P&L from spread compression/expansion
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TradeDirection(Enum):
    """Direction of spread trade"""
    LONG_SPREAD = "long_spread"    # Long pair1, short pair2
    SHORT_SPREAD = "short_spread"  # Short pair1, long pair2


@dataclass
class PairsTrade:
    """Represents a single pairs trade (both legs)"""
    entry_bar: int
    exit_bar: Optional[int]
    direction: TradeDirection
    
    # Entry data
    pair1_entry_price: float
    pair2_entry_price: float
    entry_zscore: float
    entry_spread: float
    hedge_ratio: float
    
    # Position sizing
    pair1_volume: float  # In units
    pair2_volume: float
    
    # Exit data
    pair1_exit_price: Optional[float] = None
    pair2_exit_price: Optional[float] = None
    exit_zscore: Optional[float] = None
    exit_spread: Optional[float] = None
    exit_reason: str = ""
    
    # P&L
    pnl_pair1: float = 0.0
    pnl_pair2: float = 0.0
    total_pnl: float = 0.0
    pnl_pips: float = 0.0
    
    # Metadata
    duration_bars: int = 0
    max_adverse_zscore: Optional[float] = None
    max_favorable_zscore: Optional[float] = None
    
    def calculate_pnl(self, pip_size_pair1: float = 0.0001, pip_size_pair2: float = 0.0001):
        """Calculate profit/loss when trade is closed"""
        if self.pair1_exit_price is None or self.pair2_exit_price is None:
            return
        
        if self.direction == TradeDirection.LONG_SPREAD:
            # Long pair1, short pair2
            self.pnl_pair1 = (self.pair1_exit_price - self.pair1_entry_price) * self.pair1_volume
            self.pnl_pair2 = (self.pair2_entry_price - self.pair2_exit_price) * self.pair2_volume
        else:
            # Short pair1, long pair2
            self.pnl_pair1 = (self.pair1_entry_price - self.pair1_exit_price) * self.pair1_volume
            self.pnl_pair2 = (self.pair2_exit_price - self.pair2_entry_price) * self.pair2_volume
        
        self.total_pnl = self.pnl_pair1 + self.pnl_pair2
        
        # Calculate in pips (simplified, assumes pair volumes are equal notional)
        spread_pips_entry = (self.entry_spread) / pip_size_pair1
        spread_pips_exit = (self.exit_spread) / pip_size_pair1
        self.pnl_pips = abs(spread_pips_exit - spread_pips_entry)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return {
            'entry_bar': self.entry_bar,
            'exit_bar': self.exit_bar,
            'direction': self.direction.value,
            'pair1_entry': f"{self.pair1_entry_price:.5f}",
            'pair2_entry': f"{self.pair2_entry_price:.5f}",
            'entry_zscore': f"{self.entry_zscore:.2f}",
            'entry_spread': f"{self.entry_spread:.6f}",
            'exit_zscore': f"{self.exit_zscore:.2f}" if self.exit_zscore else "N/A",
            'exit_spread': f"{self.exit_spread:.6f}" if self.exit_spread else "N/A",
            'total_pnl': f"{self.total_pnl:.2f}",
            'pnl_pips': f"{self.pnl_pips:.1f}",
            'duration_bars': self.duration_bars,
            'exit_reason': self.exit_reason,
        }


class PairsBacktestEngine:
    """
    Backtest engine for pairs trading strategies
    
    Accounts for:
    - Simultaneous entry in both pairs
    - Spread-based P&L (not individual pair direction)
    - Stop loss at extreme Z-scores
    - Profit taking when spread reverts
    - Correlation breakdown risk
    
    Example:
        engine = PairsBacktestEngine(
            account_size=10000,
            risk_pct_per_trade=0.02
        )
        results = engine.backtest(signals_df1, signals_df2, df1, df2)
    """
    
    def __init__(
        self,
        account_size: float = 10000,
        risk_pct_per_trade: float = 0.02,
        pair1_pip_size: float = 0.0001,
        pair2_pip_size: float = 0.0001,
        pair1_name: str = 'PAIR1',
        pair2_name: str = 'PAIR2',
        slippage_pips: float = 0.5,
        commission_pct: float = 0.001,
    ):
        """
        Initialize backtest engine
        
        Args:
            account_size: Starting account balance
            risk_pct_per_trade: % of account to risk per trade
            pair1_pip_size: Pip size for pair1 (default 0.0001)
            pair2_pip_size: Pip size for pair2
            pair1_name: Name of pair1
            pair2_name: Name of pair2
            slippage_pips: Slippage to assume on entries/exits
            commission_pct: Commission as % of trade notional
        """
        self.account_size = account_size
        self.risk_pct = risk_pct_per_trade
        self.pair1_pip_size = pair1_pip_size
        self.pair2_pip_size = pair2_pip_size
        self.pair1_name = pair1_name
        self.pair2_name = pair2_name
        self.slippage_pips = slippage_pips
        self.commission_pct = commission_pct
        
        self.trades: List[PairsTrade] = []
        self.balance_curve = [account_size]
        self.equity_curve = [account_size]
        self.current_balance = account_size
        self.current_position: Optional[PairsTrade] = None
        
    def backtest(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        z_exit_threshold: float = 0.5,
        z_stop_threshold: float = 3.0,
    ) -> Dict:
        """
        Run full pairs trading backtest
        
        Args:
            df1: DataFrame with OHLC for pair1 (must have 'signal_pair1', 'zscore', 'spread' columns)
            df2: DataFrame with OHLC for pair2
            z_exit_threshold: Z-score to take profit (close to mean)
            z_stop_threshold: Z-score for hard stop loss
            
        Returns:
            Dictionary with backtest results and statistics
        """
        
        if len(df1) != len(df2):
            raise ValueError(f"DataFrames must have same length: {len(df1)} vs {len(df2)}")
        
        if 'signal_pair1' not in df1.columns:
            raise ValueError("df1 must have 'signal_pair1' column from strategy.generate_signals()")
        
        if 'zscore' not in df1.columns:
            raise ValueError("df1 must have 'zscore' column from strategy.generate_signals()")
        
        # Run backtest loop
        for i in range(len(df1)):
            signal = df1['signal_pair1'].iloc[i]
            zscore = df1['zscore'].iloc[i]
            spread = df1['spread'].iloc[i]
            
            pair1_price = df1['close'].iloc[i]
            pair2_price = df2['close'].iloc[i]
            hedge_ratio = df1.get('hedge_ratio', pd.Series(1.0)).iloc[i]
            
            # Check for exit conditions
            if self.current_position is not None:
                self.current_position.max_favorable_zscore = \
                    max(self.current_position.max_favorable_zscore or 0, abs(zscore))
                self.current_position.max_adverse_zscore = \
                    max(self.current_position.max_adverse_zscore or 0, abs(zscore))
                
                # Exit conditions
                should_exit = False
                exit_reason = ""
                
                if abs(zscore) > z_stop_threshold:
                    # Hard stop - correlation breakdown warning
                    should_exit = True
                    exit_reason = f"Hard Stop (Z={zscore:.2f})"
                
                elif abs(zscore) < z_exit_threshold:
                    # Profit taking - spread normalized
                    should_exit = True
                    exit_reason = f"Profit Taking (Z={zscore:.2f})"
                
                if should_exit:
                    self._close_position(i, pair1_price, pair2_price, spread, zscore, exit_reason)
            
            # Check for entry signals
            if self.current_position is None and signal != 0:
                direction = TradeDirection.LONG_SPREAD if signal == 1 else TradeDirection.SHORT_SPREAD
                self._open_position(i, direction, pair1_price, pair2_price, zscore, spread, hedge_ratio)
        
        # Close any remaining open position at end of data
        if self.current_position is not None:
            last_idx = len(df1) - 1
            self._close_position(
                last_idx,
                df1['close'].iloc[last_idx],
                df2['close'].iloc[last_idx],
                df1['spread'].iloc[last_idx],
                df1['zscore'].iloc[last_idx],
                "Backtest End"
            )
        
        # Calculate statistics
        return self._calculate_statistics()
    
    def _open_position(
        self,
        bar: int,
        direction: TradeDirection,
        pair1_price: float,
        pair2_price: float,
        zscore: float,
        spread: float,
        hedge_ratio: float,
    ):
        """Open a new pairs trade"""
        
        # Apply slippage
        if direction == TradeDirection.LONG_SPREAD:
            p1_entry = pair1_price * (1 + self.slippage_pips * self.pair1_pip_size)
            p2_entry = pair2_price * (1 - self.slippage_pips * self.pair2_pip_size)
        else:
            p1_entry = pair1_price * (1 - self.slippage_pips * self.pair1_pip_size)
            p2_entry = pair2_price * (1 + self.slippage_pips * self.pair2_pip_size)
        
        # Calculate position size based on risk
        risk_amount = self.current_balance * self.risk_pct
        
        # Assume equal notional exposure on both legs
        # Pair1 volume based on risk
        pair1_volume = risk_amount / (p1_entry * self.pair1_pip_size)
        
        # Pair2 volume scaled by hedge ratio to maintain balance
        pair2_volume = (pair1_volume * p1_entry) / (p2_entry * hedge_ratio)
        
        self.current_position = PairsTrade(
            entry_bar=bar,
            exit_bar=None,
            direction=direction,
            pair1_entry_price=p1_entry,
            pair2_entry_price=p2_entry,
            entry_zscore=zscore,
            entry_spread=spread,
            hedge_ratio=hedge_ratio,
            pair1_volume=pair1_volume,
            pair2_volume=pair2_volume,
        )
    
    def _close_position(
        self,
        bar: int,
        pair1_price: float,
        pair2_price: float,
        spread: float,
        zscore: float,
        exit_reason: str,
    ):
        """Close current pairs trade"""
        
        if self.current_position is None:
            return
        
        # Apply slippage on close (ideally tight on exits)
        p1_exit = pair1_price * (1 - self.slippage_pips * self.pair1_pip_size * 0.5)
        p2_exit = pair2_price * (1 + self.slippage_pips * self.pair2_pip_size * 0.5)
        
        self.current_position.exit_bar = bar
        self.current_position.pair1_exit_price = p1_exit
        self.current_position.pair2_exit_price = p2_exit
        self.current_position.exit_zscore = zscore
        self.current_position.exit_spread = spread
        self.current_position.exit_reason = exit_reason
        self.current_position.duration_bars = bar - self.current_position.entry_bar
        
        # Calculate P&L
        self.current_position.calculate_pnl(self.pair1_pip_size, self.pair2_pip_size)
        
        # Update account
        commission = abs(self.current_position.pnl_pair1) * self.commission_pct
        net_pnl = self.current_position.total_pnl - commission
        
        self.current_balance += net_pnl
        self.balance_curve.append(self.current_balance)
        
        # Record trade
        self.trades.append(self.current_position)
        self.current_position = None
    
    def _calculate_statistics(self) -> Dict:
        """Calculate backtest statistics"""
        
        # Close any open position (shouldn't happen if backtest run fully)
        if self.current_position is not None:
            self.trades.append(self.current_position)
        
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'return_pct': 0,
                'profit_trades': 0,
                'loss_trades': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
            }
        
        # Calculate metrics
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.total_pnl > 0]
        losing_trades = [t for t in self.trades if t.total_pnl < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.total_pnl for t in self.trades)
        avg_win = sum(t.total_pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.total_pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Drawdown
        cumulative_pnl = 0
        running_max = 0
        drawdowns = []
        for trade in self.trades:
            cumulative_pnl += trade.total_pnl
            running_max = max(running_max, cumulative_pnl)
            drawdown = (running_max - cumulative_pnl) / (running_max if running_max != 0 else 1)
            drawdowns.append(drawdown)
        
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        # Return
        return_pct = (total_pnl / self.account_size) * 100
        
        # Sharpe (simplified)
        pnls = [t.total_pnl for t in self.trades]
        if len(pnls) > 1 and np.std(pnls) > 0:
            sharpe = (np.mean(pnls) / np.std(pnls)) * np.sqrt(252)
        else:
            sharpe = 0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': f"{win_rate*100:.1f}%",
            'total_pnl': f"{total_pnl:.2f}",
            'return_pct': f"{return_pct:.2f}%",
            'avg_win': f"{avg_win:.2f}",
            'avg_loss': f"{abs(avg_loss):.2f}",
            'profitfactor': f"{abs(sum(t.total_pnl for t in winning_trades)) / abs(sum(t.total_pnl for t in losing_trades)):.2f}" if losing_trades else "N/A",
            'max_drawdown': f"{max_drawdown*100:.2f}%",
            'sharpe_ratio': f"{sharpe:.2f}",
            'avg_bars_per_trade': f"{np.mean([t.duration_bars for t in self.trades]):.0f}",
            'trades': [t.to_dict() for t in self.trades],
        }
