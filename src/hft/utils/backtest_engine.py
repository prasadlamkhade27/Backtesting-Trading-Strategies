"""
Backtest Engine - Core backtesting logic
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List


def run_backtest_phase(
    df: pd.DataFrame,
    initial_balance: float,
    phase_num: int,
    rules: Optional[object],
    sl: float,
    tp: float,
    risk_pct: float
) -> Tuple[List[Dict], List[float], float, Optional[str]]:
    """
    Run a complete backtest for a single phase
    
    Args:
        df: DataFrame with OHLC and BUY/SELL signals
        initial_balance: Starting account balance
        phase_num: Phase number (1 or 2)
        rules: PropFirm phase rules (None for standard backtest)
        sl: Stop loss in pips
        tp: Take profit in pips
        risk_pct: Risk per trade as decimal (0.01 = 1%)
    
    Returns:
        Tuple of (trades, equity, final_balance, fail_reason)
    """
    balance = initial_balance
    position = None
    entry_price = 0.0
    entry_index = 0
    position_size = 0.0
    
    trades: List[Dict] = []
    equity: List[float] = [balance]
    
    candles_per_day = 5
    current_day = 0
    daily_pnl = 0.0
    daily_trades = 0
    
    fail_reason: Optional[str] = None
    
    for i in range(len(df)):
        price = df['close'].iloc[i]
        
        # Daily reset
        if i % candles_per_day == 0:
            if current_day > 0 and rules:
                daily_pnl = 0.0
                daily_trades = 0
            current_day += 1
        
        # Entry logic
        if position is None:
            risk_amount = balance * risk_pct
            
            if df['BUY'].iloc[i]:
                position = "LONG"
                entry_price = price
                entry_index = i
                position_size = risk_amount / sl
            
            elif df['SELL'].iloc[i]:
                position = "SHORT"
                entry_price = price
                entry_index = i
                position_size = risk_amount / sl
        
        # LONG position exit logic
        elif position == "LONG":
            exit_price = None
            closed_reason = ""
            
            if price <= entry_price - sl:
                exit_price = entry_price - sl
                closed_reason = "SL Hit"
            elif price >= entry_price + tp:
                exit_price = entry_price + tp
                closed_reason = "TP Hit"
            elif df['SELL'].iloc[i]:
                exit_price = price
                closed_reason = "Signal"
            
            if exit_price is not None:
                profit = (exit_price - entry_price) * position_size
                balance += profit
                equity.append(balance)
                daily_pnl += profit
                daily_trades += 1
                
                trade_info = {
                    'trade_num': len(trades) + 1,
                    'type': 'LONG',
                    'entry_time': i,
                    'exit_time': i,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'sl_level': entry_price - sl,
                    'tp_level': entry_price + tp,
                    'position_size': position_size,
                    'profit': profit,
                    'profit_pct': (profit / (entry_price * position_size)) * 100 if entry_price != 0 else 0,
                    'closed_reason': closed_reason,
                    'candles_held': i - entry_index
                }
                trades.append(trade_info)
                
                # Check PropFirm rules
                if rules:
                    if daily_pnl < -abs(initial_balance * rules.daily_loss_limit):
                        fail_reason = f"Daily loss limit exceeded: ${abs(daily_pnl):.2f}"
                        return trades, equity, balance, fail_reason
                    
                    if (balance - initial_balance) < -abs(initial_balance * rules.max_loss_limit):
                        fail_reason = f"Max loss limit exceeded: ${abs(balance - initial_balance):.2f}"
                        return trades, equity, balance, fail_reason
                    
                    if daily_trades > rules.max_trades_per_day:
                        fail_reason = f"Max trades per day exceeded: {daily_trades}"
                        return trades, equity, balance, fail_reason
                
                position = None
        
        # SHORT position exit logic
        elif position == "SHORT":
            exit_price = None
            closed_reason = ""
            
            if price >= entry_price + sl:
                exit_price = entry_price + sl
                closed_reason = "SL Hit"
            elif price <= entry_price - tp:
                exit_price = entry_price - tp
                closed_reason = "TP Hit"
            elif df['BUY'].iloc[i]:
                exit_price = price
                closed_reason = "Signal"
            
            if exit_price is not None:
                profit = (entry_price - exit_price) * position_size
                balance += profit
                equity.append(balance)
                daily_pnl += profit
                daily_trades += 1
                
                trade_info = {
                    'trade_num': len(trades) + 1,
                    'type': 'SHORT',
                    'entry_time': i,
                    'exit_time': i,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'sl_level': entry_price + sl,
                    'tp_level': entry_price - tp,
                    'position_size': position_size,
                    'profit': profit,
                    'profit_pct': (profit / (entry_price * position_size)) * 100 if entry_price != 0 else 0,
                    'closed_reason': closed_reason,
                    'candles_held': i - entry_index
                }
                trades.append(trade_info)
                
                # Check PropFirm rules
                if rules:
                    if daily_pnl < -abs(initial_balance * rules.daily_loss_limit):
                        fail_reason = f"Daily loss limit exceeded: ${abs(daily_pnl):.2f}"
                        return trades, equity, balance, fail_reason
                    
                    if (balance - initial_balance) < -abs(initial_balance * rules.max_loss_limit):
                        fail_reason = f"Max loss limit exceeded: ${abs(balance - initial_balance):.2f}"
                        return trades, equity, balance, fail_reason
                    
                    if daily_trades > rules.max_trades_per_day:
                        fail_reason = f"Max trades per day exceeded: {daily_trades}"
                        return trades, equity, balance, fail_reason
                
                position = None
        
        # Check if target profit reached (for propfirm)
        if rules and len(trades) > 0:
            profit = balance - initial_balance
            trading_days = current_day
            if profit >= initial_balance * rules.profit_target:
                if trading_days >= rules.min_trading_days:
                    return trades, equity, balance, None
    
    return trades, equity, balance, fail_reason


def calculate_metrics(
    trades_list: List[Dict],
    starting_balance: float,
    ending_balance: float,
    equity_list: List[float]
) -> Dict:
    """
    Calculate comprehensive professional backtesting metrics
    
    Args:
        trades_list: List of trade dictionaries
        starting_balance: Initial account balance
        ending_balance: Final account balance
        equity_list: List of equity values over time
    
    Returns:
        Dictionary with professional-grade metrics
    """
    metrics = {}
    
    # Basic metrics
    total_trades = len(trades_list)
    wins = len([t for t in trades_list if t['profit'] > 0]) if trades_list else 0
    losses = len([t for t in trades_list if t['profit'] <= 0]) if trades_list else 0
    winrate = (wins / total_trades) * 100 if total_trades > 0 else 0
    
    net_profit = ending_balance - starting_balance
    net_profit_pct = (net_profit / starting_balance) * 100 if starting_balance > 0 else 0
    
    # Equity metrics
    equity_series = pd.Series(equity_list)
    drawdown = equity_series - equity_series.cummax()
    max_dd = drawdown.min()
    max_dd_pct = (max_dd / starting_balance) * 100 if starting_balance > 0 else 0
    
    # Trade analysis
    if trades_list:
        profits = [t['profit'] for t in trades_list]
        profit_pcts = [t['profit_pct'] for t in trades_list]
        candles_held = [t['candles_held'] for t in trades_list if 'candles_held' in t]
        
        avg_trade = np.mean(profits)
        avg_trade_pct = np.mean(profit_pcts)
        largest_win = max(profits)
        largest_loss = min(profits)
        largest_win_pct = max(profit_pcts) if profit_pcts else 0
        
        # Risk metrics
        winning_trades = [t['profit'] for t in trades_list if t['profit'] > 0]
        losing_trades = [t['profit'] for t in trades_list if t['profit'] <= 0]
        
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(winning_trades) if winning_trades else 0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (1.0 if gross_profit > 0 else 0.0)
        
        # Payoff ratio
        payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Consecutive metrics
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for trade in trades_list:
            if trade['profit'] > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        # Trade duration
        avg_trade_duration = np.mean(candles_held) if candles_held else 0
        
        # Sharpe Ratio (assuming 252 trading days)
        returns = np.diff(equity_list) / np.array(equity_list[:-1])
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        
        # Sortino Ratio (only downside volatility)
        downside_returns = returns[returns < 0]
        downside_volatility = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino_ratio = (np.mean(returns) / downside_volatility * np.sqrt(252)) if downside_volatility > 0 else 0
        
        # Calmar Ratio
        calmar_ratio = (net_profit_pct / abs(max_dd_pct)) if max_dd_pct != 0 else 0
        
        # Recovery Factor
        recovery_factor = net_profit / abs(max_dd) if max_dd != 0 and max_dd < 0 else 0
        
        # Win/Loss by type
        long_trades = len([t for t in trades_list if t['type'] == 'LONG'])
        short_trades = len([t for t in trades_list if t['type'] == 'SHORT'])
        long_wins = len([t for t in trades_list if t['type'] == 'LONG' and t['profit'] > 0])
        short_wins = len([t for t in trades_list if t['type'] == 'SHORT' and t['profit'] > 0])
        
    else:
        avg_trade = 0.0
        avg_trade_pct = 0.0
        largest_win = 0.0
        largest_loss = 0.0
        largest_win_pct = 0.0
        avg_win = 0.0
        avg_loss = 0.0
        profit_factor = 0.0
        payoff_ratio = 0.0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        avg_trade_duration = 0.0
        sharpe_ratio = 0.0
        sortino_ratio = 0.0
        calmar_ratio = 0.0
        recovery_factor = 0.0
        long_trades = 0
        short_trades = 0
        long_wins = 0
        short_wins = 0
    
    # Compile metrics
    metrics = {
        # Basic metrics
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'winrate': winrate,
        'net_profit': net_profit,
        'net_profit_pct': net_profit_pct,
        'max_dd': max_dd,
        'max_dd_pct': max_dd_pct,
        'ending_balance': ending_balance,
        
        # Trade metrics
        'avg_trade': avg_trade,
        'avg_trade_pct': avg_trade_pct,
        'largest_win': largest_win,
        'largest_loss': largest_loss,
        'largest_win_pct': largest_win_pct,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        
        # Performance metrics
        'profit_factor': profit_factor,
        'payoff_ratio': payoff_ratio,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'calmar_ratio': calmar_ratio,
        'recovery_factor': recovery_factor,
        
        # Consecutive metrics
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'avg_trade_duration': avg_trade_duration,
        
        # Trade type breakdown
        'long_trades': long_trades,
        'short_trades': short_trades,
        'long_wins': long_wins,
        'short_wins': short_wins,
    }
    
    return metrics


def calculate_daily_pnl(trades_list: List[Dict]) -> pd.DataFrame:
    """Calculate daily P&L from trades"""
    if not trades_list:
        return pd.DataFrame({'Date': [], 'PnL': [], 'Trades': []})
    
    trades_df = pd.DataFrame(trades_list)
    trades_df['day'] = trades_df['entry_time'] // 5  # Assuming 5 candles per day
    daily_pnl = trades_df.groupby('day').agg({
        'profit': 'sum',
        'trade_num': 'count'
    }).reset_index()
    daily_pnl.columns = ['Day', 'PnL', 'Trades']
    return daily_pnl


def calculate_trade_statistics(trades_list: List[Dict]) -> Dict:
    """Detailed trade statistics by type"""
    if not trades_list:
        return {}
    
    trades_df = pd.DataFrame(trades_list)
    
    stats = {}
    for trade_type in ['LONG', 'SHORT']:
        type_trades = trades_df[trades_df['type'] == trade_type]
        if len(type_trades) > 0:
            stats[trade_type] = {
                'total': len(type_trades),
                'wins': len(type_trades[type_trades['profit'] > 0]),
                'losses': len(type_trades[type_trades['profit'] <= 0]),
                'avg_profit': type_trades['profit'].mean(),
                'total_profit': type_trades['profit'].sum(),
                'winrate': (len(type_trades[type_trades['profit'] > 0]) / len(type_trades) * 100) if len(type_trades) > 0 else 0,
            }
    
    return stats


def calculate_drawdown_breakdown(equity_list: List[float]) -> Dict:
    """Calculate detailed drawdown statistics"""
    equity_series = pd.Series(equity_list)
    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max * 100
    
    return {
        'current_dd': drawdown.iloc[-1] if len(drawdown) > 0 else 0,
        'max_dd': drawdown.min(),
        'avg_dd': drawdown[drawdown < 0].mean() if any(drawdown < 0) else 0,
        'dd_duration': (drawdown < 0).sum(),  # Number of periods in drawdown
    }


def calculate_monthly_statistics(trades_list: List[Dict], start_time: int) -> pd.DataFrame:
    """Calculate monthly return statistics"""
    if not trades_list:
        return pd.DataFrame()
    
    trades_df = pd.DataFrame(trades_list)
    
    # Create month grouping (assuming 252 trading days per year, ~21 per month)
    trades_df['month'] = (trades_df['entry_time'] // (21 * 5)).astype(int)  # ~21 trading days * 5 candles
    
    monthly_stats = trades_df.groupby('month').agg({
        'profit': ['sum', 'count', 'mean'],
        'profit_pct': 'mean'
    }).reset_index()
    
    monthly_stats.columns = ['Month', 'Total_PnL', 'Trades', 'Avg_PnL', 'Avg_PnL_Pct']
    return monthly_stats
