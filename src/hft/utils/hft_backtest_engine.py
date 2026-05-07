"""
High-Frequency Trading (HFT) Backtesting Engine
Specialized backtesting for HFT strategies with focus on:
- Realistic execution modeling (slippage, latency)
- Tick-by-tick simulation
- Spread modeling
- Execution venue optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ExecutionVenue(Enum):
    """Trading venue types with different slippage profiles"""
    FOREX_ECN = "ECN"      # Low slippage, tight spreads
    FOREX_MM = "MM"        # Market maker, wider spreads
    FUTURES = "FUTURES"    # Minimal slippage, liquid
    CRYPTO = "CRYPTO"      # Variable slippage


@dataclass
class ExecutionParams:
    """Execution parameters for realistic trade simulation"""
    venue: ExecutionVenue
    base_spread_pips: float = 1.0          # Base bid-ask spread
    slippage_pips: float = 0.5             # Execution slippage
    latency_ms: int = 100                  # Order execution latency
    max_slippage_pips: float = 5.0         # Maximum allowed slippage
    
    def get_total_cost_pips(self) -> float:
        """Total cost of executing a trade in pips"""
        return self.base_spread_pips + self.slippage_pips


@dataclass
class HFTTrade:
    """Represents a single HFT trade"""
    entry_bar: int
    exit_bar: Optional[int]
    entry_price: float
    exit_price: Optional[float]
    direction: str  # 'LONG' or 'SHORT'
    lot_size: float
    stop_loss: float
    take_profit: float
    pnl: Optional[float]
    return_percent: Optional[float]
    trade_duration_bars: Optional[int]
    reason_entry: str
    reason_exit: Optional[str]
    status: str  # 'OPEN', 'CLOSED', 'STOPPED_OUT'


class HFTBacktestEngine:
    """
    Advanced backtesting engine optimized for HFT strategies
    """
    
    def __init__(
        self,
        initial_balance: float,
        execution_params: ExecutionParams,
        risk_percent_per_trade: float = 0.5,
        max_concurrent_positions: int = 3,
        use_realistic_execution: bool = True
    ):
        """
        Initialize HFT backtesting engine
        
        Args:
            initial_balance: Starting account balance
            execution_params: Execution parameter configuration
            risk_percent_per_trade: Risk as % of balance per trade
            max_concurrent_positions: Maximum simultaneous open positions
            use_realistic_execution: Apply realistic slippage/spread costs
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.execution_params = execution_params
        self.risk_percent_per_trade = risk_percent_per_trade
        self.max_concurrent_positions = max_concurrent_positions
        self.use_realistic_execution = use_realistic_execution
        
        # Trade tracking
        self.trades: List[HFTTrade] = []
        self.open_positions: List[HFTTrade] = []
        self.equity_curve: List[float] = [initial_balance]
        self.daily_returns: Dict = {}
        
        # Performance metrics
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.peak_equity = initial_balance
        
    def backtest(
        self,
        df: pd.DataFrame,
        strategy_signals: pd.DataFrame,
        symbol: str = "EURUSD"
    ) -> Dict:
        """
        Run HFT backtest on historical data
        
        Args:
            df: OHLC data
            strategy_signals: DataFrame with 'BUY' and 'SELL' signals
            symbol: Trading symbol
            
        Returns:
            Backtest results dictionary
        """
        df = df.copy()
        
        # Add strategy signals
        df['BUY'] = strategy_signals['BUY']
        df['SELL'] = strategy_signals['SELL']
        
        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume', 'BUY', 'SELL']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame missing required columns. Need: {required_cols}")
        
        # Main backtest loop
        for bar in range(len(df)):
            bar_data = df.iloc[bar]
            
            # Check for exits in existing positions
            self._process_exits(df, bar)
            
            # Process new entry signals
            if bar_data['BUY'] and len(self.open_positions) < self.max_concurrent_positions:
                self._execute_long(df, bar, bar_data['close'])
            
            if bar_data['SELL'] and len(self.open_positions) < self.max_concurrent_positions:
                self._execute_short(df, bar, bar_data['close'])
            
            # Update equity
            self._update_equity(bar_data['close'])
        
        # Close any remaining open positions at last bar price
        last_price = df['close'].iloc[-1]
        for trade in self.open_positions[:]:
            self._close_trade(trade, last_price, len(df) - 1, "Backtest End")
        
        # Calculate final statistics
        return self._calculate_statistics(df)
    
    def _execute_long(self, df: pd.DataFrame, bar: int, entry_price: float):
        """Execute a long entry"""
        if len(self.open_positions) >= self.max_concurrent_positions:
            return
        
        # Apply execution costs
        actual_entry = self._apply_execution_cost(entry_price, is_buy=True)
        
        # Calculate position size
        atr = self._estimate_atr(df, bar)
        stop_loss = actual_entry - (atr * 1.5)
        take_profit = actual_entry + (atr * 0.75)
        
        lot_size = self._calculate_lot_size(
            self.current_balance,
            actual_entry,
            stop_loss
        )
        
        trade = HFTTrade(
            entry_bar=bar,
            exit_bar=None,
            entry_price=actual_entry,
            exit_price=None,
            direction='LONG',
            lot_size=lot_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            pnl=None,
            return_percent=None,
            trade_duration_bars=None,
            reason_entry="HFT Signal Long",
            reason_exit=None,
            status='OPEN'
        )
        
        self.open_positions.append(trade)
    
    def _execute_short(self, df: pd.DataFrame, bar: int, entry_price: float):
        """Execute a short entry"""
        if len(self.open_positions) >= self.max_concurrent_positions:
            return
        
        # Apply execution costs
        actual_entry = self._apply_execution_cost(entry_price, is_buy=False)
        
        # Calculate position size
        atr = self._estimate_atr(df, bar)
        stop_loss = actual_entry + (atr * 1.5)
        take_profit = actual_entry - (atr * 0.75)
        
        lot_size = self._calculate_lot_size(
            self.current_balance,
            actual_entry,
            stop_loss
        )
        
        trade = HFTTrade(
            entry_bar=bar,
            exit_bar=None,
            entry_price=actual_entry,
            exit_price=None,
            direction='SHORT',
            lot_size=lot_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            pnl=None,
            return_percent=None,
            trade_duration_bars=None,
            reason_entry="HFT Signal Short",
            reason_exit=None,
            status='OPEN'
        )
        
        self.open_positions.append(trade)
    
    def _process_exits(self, df: pd.DataFrame, bar: int):
        """Check for stop loss / take profit hits"""
        bar_data = df.iloc[bar]
        high = bar_data['high']
        low = bar_data['low']
        close = bar_data['close']
        
        for trade in self.open_positions[:]:
            exit_executed = False
            exit_price = None
            exit_reason = ""
            
            if trade.direction == 'LONG':
                # Check take profit
                if high >= trade.take_profit:
                    exit_price = self._apply_execution_cost(trade.take_profit, is_buy=False)
                    exit_reason = "Take Profit"
                    exit_executed = True
                
                # Check stop loss
                elif low <= trade.stop_loss:
                    exit_price = self._apply_execution_cost(trade.stop_loss, is_buy=False)
                    exit_reason = "Stop Loss"
                    exit_executed = True
            
            elif trade.direction == 'SHORT':
                # Check take profit
                if low <= trade.take_profit:
                    exit_price = self._apply_execution_cost(trade.take_profit, is_buy=True)
                    exit_reason = "Take Profit"
                    exit_executed = True
                
                # Check stop loss
                elif high >= trade.stop_loss:
                    exit_price = self._apply_execution_cost(trade.stop_loss, is_buy=True)
                    exit_reason = "Stop Loss"
                    exit_executed = True
            
            if exit_executed and exit_price:
                self._close_trade(trade, exit_price, bar, exit_reason)
    
    def _close_trade(
        self,
        trade: HFTTrade,
        exit_price: float,
        exit_bar: int,
        reason: str
    ):
        """Close a trade and update statistics"""
        trade.exit_price = exit_price
        trade.exit_bar = exit_bar
        trade.status = 'CLOSED'
        trade.reason_exit = reason
        trade.trade_duration_bars = exit_bar - trade.entry_bar
        
        # Calculate P&L
        if trade.direction == 'LONG':
            pnl = (exit_price - trade.entry_price) * trade.lot_size * 100000
        else:  # SHORT
            pnl = (trade.entry_price - exit_price) * trade.lot_size * 100000
        
        # Apply execution costs
        execution_cost = self.execution_params.get_total_cost_pips() * trade.lot_size * 100000
        pnl -= execution_cost
        
        trade.pnl = pnl
        trade.return_percent = (pnl / self.current_balance) * 100
        
        # Update balance
        self.current_balance += pnl
        self.trades.append(trade)
        
        # Remove from open positions
        if trade in self.open_positions:
            self.open_positions.remove(trade)
    
    def _apply_execution_cost(self, price: float, is_buy: bool) -> float:
        """Apply spread and slippage to execution price"""
        if not self.use_realistic_execution:
            return price
        
        total_cost = self.execution_params.get_total_cost_pips() / 10000  # Convert to decimal
        
        if is_buy:
            return price + total_cost
        else:
            return price - total_cost
    
    def _update_equity(self, current_price: float):
        """Update equity and drawdown tracking"""
        # Calculate current equity including open P&L
        current_equity = self.current_balance
        
        for trade in self.open_positions:
            if trade.direction == 'LONG':
                unrealized_pnl = (current_price - trade.entry_price) * trade.lot_size * 100000
            else:
                unrealized_pnl = (trade.entry_price - current_price) * trade.lot_size * 100000
            
            current_equity += unrealized_pnl
        
        self.equity_curve.append(current_equity)
        
        # Update drawdown
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
    
    def _calculate_lot_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """Calculate position size based on risk"""
        risk_amount = balance * (self.risk_percent_per_trade / 100.0)
        loss_per_pip = abs(entry_price - stop_loss)
        
        if loss_per_pip == 0:
            return 0.01
        
        lot_size = risk_amount / (loss_per_pip * 100000)
        return max(0.01, min(lot_size, 10.0))
    
    @staticmethod
    def _estimate_atr(df: pd.DataFrame, bar: int, period: int = 14) -> float:
        """Estimate ATR for position sizing"""
        start = max(0, bar - period)
        end = bar + 1
        
        if end - start < 2:
            return 0.0010  # Default 10 pips
        
        subset = df.iloc[start:end]
        high_low = subset['high'] - subset['low']
        high_close = abs(subset['high'] - subset['close'].shift())
        low_close = abs(subset['low'] - subset['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.mean()
        
        return max(atr, 0.0005)
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive backtest statistics"""
        if not self.trades:
            return {
                'status': 'NO_TRADES',
                'message': 'No trades were executed'
            }
        
        trades = self.trades
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in trades)
        total_return = ((self.current_balance / self.initial_balance) - 1) * 100
        
        # Calculate metrics
        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        avg_trade_duration = np.mean([t.trade_duration_bars for t in trades if t.trade_duration_bars]) if trades else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Risk metrics
        sharpe_ratio = self._calculate_sharpe_ratio()
        sortino_ratio = self._calculate_sortino_ratio()
        
        return {
            'status': 'COMPLETED',
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': max(t.pnl for t in winning_trades) if winning_trades else 0,
            'largest_loss': min(t.pnl for t in losing_trades) if losing_trades else 0,
            'total_pnl': total_pnl,
            'total_return_percent': total_return,
            'profit_factor': profit_factor,
            'avg_trade_duration_bars': avg_trade_duration,
            'max_drawdown_percent': self.max_drawdown * 100,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'final_balance': self.current_balance,
            'consecutive_wins': self._calc_consecutive_wins(),
            'consecutive_losses': self._calc_consecutive_losses(),
        }
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe Ratio"""
        if len(self.equity_curve) < 2:
            return 0.0
        
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        return sharpe if not np.isnan(sharpe) else 0.0
    
    def _calculate_sortino_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino Ratio (downside deviation)"""
        if len(self.equity_curve) < 2:
            return 0.0
        
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        
        if len(returns) == 0:
            return 0.0
        
        negative_returns = returns[returns < 0]
        downside_dev = np.sqrt(np.mean(negative_returns ** 2)) if len(negative_returns) > 0 else 0
        
        if downside_dev == 0:
            return 0.0
        
        excess_returns = np.mean(returns) - (risk_free_rate / 252)
        sortino = excess_returns / downside_dev * np.sqrt(252)
        
        return sortino if not np.isnan(sortino) else 0.0
    
    def _calc_consecutive_wins(self) -> int:
        """Calculate longest consecutive winning trades"""
        max_streak = 0
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calc_consecutive_losses(self) -> int:
        """Calculate longest consecutive losing trades"""
        max_streak = 0
        current_streak = 0
        
        for trade in self.trades:
            if trade.pnl <= 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def get_trade_log(self) -> pd.DataFrame:
        """Export trade log as DataFrame"""
        data = []
        for trade in self.trades:
            data.append({
                'entry_bar': trade.entry_bar,
                'exit_bar': trade.exit_bar,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'direction': trade.direction,
                'lot_size': trade.lot_size,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit,
                'pnl': trade.pnl,
                'return_percent': trade.return_percent,
                'duration_bars': trade.trade_duration_bars,
                'entry_reason': trade.reason_entry,
                'exit_reason': trade.reason_exit,
            })
        
        return pd.DataFrame(data)


# ====================== HOW TO USE THIS ======================
# 1. Create execution parameters:
#
#    exec_params = ExecutionParams(
#        venue=ExecutionVenue.FOREX_ECN,
#        base_spread_pips=1.0,
#        slippage_pips=0.5
#    )
#
# 2. Initialize backtest engine:
#
#    engine = HFTBacktestEngine(
#        initial_balance=10000,
#        execution_params=exec_params,
#        risk_percent_per_trade=0.5
#    )
#
# 3. Run backtest:
#
#    results = engine.backtest(ohlc_data, signals_df)
#    print(results)
#
# 4. Export trade log:
#
#    trade_log = engine.get_trade_log()
#    trade_log.to_csv('hft_backtest_trades.csv', index=False)
