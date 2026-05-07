"""
Enhanced Backtest Engine - With Lot Size Tracking
Tracks all trades with lot sizes, pip values, and risk management
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List
from propfirm.lot_size_calculator import LotSizeCalculator, PairConfig


class EnhancedBacktestRunner:
    """
    Run backtests with detailed lot size tracking and risk management.
    Supports all forex pairs with pair-specific pip sizes and risk calculations.
    """
    
    def __init__(self, account_size: float, risk_pct: float = 0.01, pair: str = 'XAUUSD'):
        self.account_size = account_size
        self.risk_pct = risk_pct
        self.pair = pair
        self.lot_calculator = LotSizeCalculator(account_size)
        self.pair_config = PairConfig.get_pair_config(pair)
        
    def run_backtest_with_lots(
        self,
        df: pd.DataFrame,
        sl_pips: float,
        tp_pips: float
    ) -> Dict:
        """
        Run backtest tracking lot sizes for each trade.
        
        Args:
            df: DataFrame with OHLC and BUY/SELL signals
            sl_pips: Stop loss in pips
            tp_pips: Take profit in pips
        
        Returns:
            Dictionary with comprehensive trade results including lot sizes
        """
        
        balance = self.account_size
        equity_curve = [balance]
        trades = []
        position = None
        entry_price = 0.0
        entry_index = 0
        lot_size = 0.0
        entry_signal = None
        
        for i in range(len(df)):
            price = df['close'].iloc[i]
            
            # Entry logic
            if position is None:
                if df['BUY'].iloc[i]:
                    # Calculate stop loss and take profit prices
                    stop_loss_price = price - (sl_pips * self.pair_config.pip_size)
                    take_profit_price = price + (tp_pips * self.pair_config.pip_size)
                    
                    # Calculate lot size
                    lot_size, risk_amount, stats = self.lot_calculator.calculate_lot_size(
                        self.pair, price, stop_loss_price, self.risk_pct
                    )
                    
                    position = "LONG"
                    entry_price = price
                    entry_index = i
                    entry_signal = "BUY"
                    entry_sl = stop_loss_price
                    entry_tp = take_profit_price
                    entry_time = df.index[i] if hasattr(df, 'index') else i
                
                elif df['SELL'].iloc[i]:
                    # Calculate stop loss and take profit prices
                    stop_loss_price = price + (sl_pips * self.pair_config.pip_size)
                    take_profit_price = price - (tp_pips * self.pair_config.pip_size)
                    
                    # Calculate lot size
                    lot_size, risk_amount, stats = self.lot_calculator.calculate_lot_size(
                        self.pair, price, stop_loss_price, self.risk_pct
                    )
                    
                    position = "SHORT"
                    entry_price = price
                    entry_index = i
                    entry_signal = "SELL"
                    entry_sl = stop_loss_price
                    entry_tp = take_profit_price
                    entry_time = df.index[i] if hasattr(df, 'index') else i
            
            # Exit logic for LONG positions
            elif position == "LONG":
                exit_price = None
                exit_reason = ""
                
                if price <= entry_sl:
                    exit_price = entry_sl
                    exit_reason = "SL Hit"
                elif price >= entry_tp:
                    exit_price = entry_tp
                    exit_reason = "TP Hit"
                elif df['SELL'].iloc[i] if 'SELL' in df.columns else False:
                    exit_price = price
                    exit_reason = "Exit Signal"
                
                if exit_price is not None:
                    # Calculate P&L
                    risk_in_pips = (entry_price - entry_sl) / self.pair_config.pip_size
                    pnl_pips = (exit_price - entry_price) / self.pair_config.pip_size
                    
                    if 'JPY' in self.pair:
                        pip_value = 1000
                    else:
                        pip_value = 10
                    
                    pnl_amount = lot_size * pnl_pips * pip_value
                    balance += pnl_amount
                    equity_curve.append(balance)
                    
                    # Record trade
                    trades.append({
                        'trade_num': len(trades) + 1,
                        'type': 'LONG',
                        'entry_time': entry_index,
                        'exit_time': i,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'stop_loss': entry_sl,
                        'take_profit': entry_tp,
                        'lot_size': lot_size,
                        'position_units': lot_size * self.pair_config.contract_size,
                        'risk_pips': risk_in_pips,
                        'pnl_pips': pnl_pips,
                        'pnl_amount': pnl_amount,
                        'pnl_pct': (pnl_amount / self.account_size) * 100,
                        'exit_reason': exit_reason,
                        'balance': balance,
                    })
                    
                    position = None
            
            # Exit logic for SHORT positions
            elif position == "SHORT":
                exit_price = None
                exit_reason = ""
                
                if price >= entry_sl:
                    exit_price = entry_sl
                    exit_reason = "SL Hit"
                elif price <= entry_tp:
                    exit_price = entry_tp
                    exit_reason = "TP Hit"
                elif df['BUY'].iloc[i] if 'BUY' in df.columns else False:
                    exit_price = price
                    exit_reason = "Exit Signal"
                
                if exit_price is not None:
                    # Calculate P&L
                    risk_in_pips = (entry_sl - entry_price) / self.pair_config.pip_size
                    pnl_pips = (entry_price - exit_price) / self.pair_config.pip_size
                    
                    if 'JPY' in self.pair:
                        pip_value = 1000
                    else:
                        pip_value = 10
                    
                    pnl_amount = lot_size * pnl_pips * pip_value
                    balance += pnl_amount
                    equity_curve.append(balance)
                    
                    # Record trade
                    trades.append({
                        'trade_num': len(trades) + 1,
                        'type': 'SHORT',
                        'entry_time': entry_index,
                        'exit_time': i,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'stop_loss': entry_sl,
                        'take_profit': entry_tp,
                        'lot_size': lot_size,
                        'position_units': lot_size * self.pair_config.contract_size,
                        'risk_pips': risk_in_pips,
                        'pnl_pips': pnl_pips,
                        'pnl_amount': pnl_amount,
                        'pnl_pct': (pnl_amount / self.account_size) * 100,
                        'exit_reason': exit_reason,
                        'balance': balance,
                    })
                    
                    position = None
        
        # Calculate statistics
        if not trades:
            return {
                'pair': self.pair,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'account_size': self.account_size,
                'final_balance': balance,
                'total_return': 0,
                'total_pnl': 0,
                'total_return_pct': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_profit': 0,
                'max_loss': 0,
                'max_drawdown': 0,
                'avg_lot_size': 0,
                'max_lot_size': 0,
                'min_lot_size': 0,
                'trades': trades,
                'equity_curve': equity_curve,
                'message': 'No trades generated'
            }
        
        trades_df = pd.DataFrame(trades)
        winning_trades = trades_df[trades_df['pnl_amount'] > 0]
        losing_trades = trades_df[trades_df['pnl_amount'] <= 0]
        
        win_rate = len(winning_trades) / len(trades_df) if len(trades_df) > 0 else 0
        total_profit = trades_df['pnl_amount'].sum()
        total_return_pct = (total_profit / self.account_size) * 100
        
        avg_win = winning_trades['pnl_amount'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl_amount'].mean() if len(losing_trades) > 0 else 0
        
        max_profit_trade = trades_df['pnl_amount'].max()
        max_loss_trade = trades_df['pnl_amount'].min()
        
        equity_array = np.array(equity_curve)
        max_equity = np.maximum.accumulate(equity_array)
        drawdowns = (equity_array - max_equity) / max_equity
        max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
        
        avg_lot_size = trades_df['lot_size'].mean()
        max_lot_size = trades_df['lot_size'].max()
        min_lot_size = trades_df['lot_size'].min()
        
        return {
            'pair': self.pair,
            'account_size': self.account_size,
            'risk_pct': self.risk_pct,
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'final_balance': balance,
            'total_pnl': total_profit,
            'total_return_pct': total_return_pct,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_profit': max_profit_trade,
            'max_loss': max_loss_trade,
            'max_drawdown': max_drawdown,
            'avg_lot_size': avg_lot_size,
            'max_lot_size': max_lot_size,
            'min_lot_size': min_lot_size,
            'trades': trades,
            'trades_df': trades_df,
            'equity_curve': equity_curve,
        }
