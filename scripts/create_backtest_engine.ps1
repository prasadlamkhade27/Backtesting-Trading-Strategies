@'
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List
from utils.futures_specs import (
    get_contract_spec,
    calculate_profit_loss,
    calculate_position_size_futures,
    calculate_margin_requirement
)


def run_futures_backtest(
    df: pd.DataFrame,
    initial_balance: float,
    contract_symbol: str,
    sl_points: float,
    tp_points: float,
    risk_pct: float = 0.02,
    use_micro_contract: bool = False
) -> Tuple[List[Dict], List[float], float, Optional[str]]:
    """
    Run futures backtest with proper margin handling
    
    Args:
        df: DataFrame with OHLC and BUY/SELL signals
        initial_balance: Starting account balance
        contract_symbol: Futures symbol (ES, NQ, YM, etc.)
        sl_points: Stop loss in points (not pips)
        tp_points: Take profit in points
        risk_pct: Risk per trade as percentage (0.02 = 2%)
        use_micro_contract: Use micro contract if available
    
    Returns:
        Tuple of (trades, equity_curve, final_balance, fail_reason)
    """
    
    # Adjust symbol if using micro
    if use_micro_contract:
        micro_mapping = {
            'ES': 'MES',
            'NQ': 'MNQ',
            'YM': 'MYM',
            'GC': 'MGC',
        }
        if contract_symbol in micro_mapping:
            contract_symbol = micro_mapping[contract_symbol]
    
    spec = get_contract_spec(contract_symbol)
    
    balance = initial_balance
    position = None
    entry_price = 0.0
    entry_index = 0
    contracts = 0
    
    trades: List[Dict] = []
    equity: List[float] = [balance]
    
    fail_reason: Optional[str] = None
    max_drawdown = 0.0
    max_balance = balance
    
    for i in range(len(df)):
        price = df['close'].iloc[i]
        
        # Calculate max drawdown
        if balance > max_balance:
            max_balance = balance
        current_dd = (1 - (balance / max_balance)) * 100 if max_balance > 0 else 0
        if current_dd > max_drawdown:
            max_drawdown = current_dd
        
        # Check if account is margin called
        if position is not None:
            # Calculate unrealized P&L
            if position == "LONG":
                unrealized_pnl = calculate_profit_loss(
                    entry_price, price, contracts, contract_symbol, 'LONG'
                )
            else:  # SHORT
                unrealized_pnl = calculate_profit_loss(
                    entry_price, price, contracts, contract_symbol, 'SHORT'
                )
            
            current_balance = balance + unrealized_pnl
            margin_used = calculate_margin_requirement(
                contracts, contract_symbol, use_maintenance=True
            )
            
            # Margin call if balance falls below margin requirement
            if current_balance < margin_used:
                fail_reason = f"Margin Call at {price} (used ${margin_used}, balance ${current_balance:.2f})"
                break
        
        # Entry logic
        if position is None:
            if df['BUY'].iloc[i]:
                # Calculate position size
                sl_price = price - sl_points
                contracts, risk_amount, _ = calculate_position_size_futures(
                    balance, risk_pct, price, sl_price, contract_symbol
                )
                
                # Check if we have enough margin
                margin_needed = calculate_margin_requirement(contracts, contract_symbol)
                if margin_needed <= balance:
                    position = "LONG"
                    entry_price = price
                    entry_index = i
            
            elif df['SELL'].iloc[i]:
                # Calculate position size
                sl_price = price + sl_points
                contracts, risk_amount, _ = calculate_position_size_futures(
                    balance, risk_pct, price, sl_price, contract_symbol
                )
                
                # Check if we have enough margin
                margin_needed = calculate_margin_requirement(contracts, contract_symbol)
                if margin_needed <= balance:
                    position = "SHORT"
                    entry_price = price
                    entry_index = i
        
        # LONG position exit logic
        elif position == "LONG":
            exit_price = None
            closed_reason = ""
            
            if price <= entry_price - sl_points:
                exit_price = entry_price - sl_points
                closed_reason = "SL Hit"
            elif price >= entry_price + tp_points:
                exit_price = entry_price + tp_points
                closed_reason = "TP Hit"
            elif df['SELL'].iloc[i]:
                exit_price = price
                closed_reason = "Signal"
            
            if exit_price is not None:
                profit = calculate_profit_loss(
                    entry_price, exit_price, contracts, contract_symbol, 'LONG'
                )
                balance += profit
                equity.append(balance)
                
                trade_info = {
                    'trade_num': len(trades) + 1,
                    'type': 'LONG',
                    'entry_time': entry_index,
                    'exit_time': i,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'contracts': contracts,
                    'points': exit_price - entry_price,
                    'profit_loss': profit,
                    'reason': closed_reason,
                    'balance_after': balance,
                }
                trades.append(trade_info)
                
                position = None
                contracts = 0
        
        # SHORT position exit logic
        elif position == "SHORT":
            exit_price = None
            closed_reason = ""
            
            if price >= entry_price + sl_points:
                exit_price = entry_price + sl_points
                closed_reason = "SL Hit"
            elif price <= entry_price - tp_points:
                exit_price = entry_price - tp_points
                closed_reason = "TP Hit"
            elif df['BUY'].iloc[i]:
                exit_price = price
                closed_reason = "Signal"
            
            if exit_price is not None:
                profit = calculate_profit_loss(
                    entry_price, exit_price, contracts, contract_symbol, 'SHORT'
                )
                balance += profit
                equity.append(balance)
                
                trade_info = {
                    'trade_num': len(trades) + 1,
                    'type': 'SHORT',
                    'entry_time': entry_index,
                    'exit_time': i,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'contracts': contracts,
                    'points': entry_price - exit_price,
                    'profit_loss': profit,
                    'reason': closed_reason,
                    'balance_after': balance,
                }
                trades.append(trade_info)
                
                position = None
                contracts = 0
    
    # Close any open position at end
    if position is not None and len(df) > 0:
        final_price = df['close'].iloc[-1]
        if position == "LONG":
            profit = calculate_profit_loss(
                entry_price, final_price, contracts, contract_symbol, 'LONG'
            )
        else:
            profit = calculate_profit_loss(
                entry_price, final_price, contracts, contract_symbol, 'SHORT'
            )
        balance += profit
        equity.append(balance)
    
    return trades, equity, balance, fail_reason


def calculate_futures_metrics(
    trades: List[Dict],
    equity: List[float],
    initial_balance: float,
    contract_symbol: str
) -> Dict:
    """Calculate performance metrics for futures trading"""
    
    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_profit': 0,
            'total_loss': 0,
            'net_profit': 0,
            'return_pct': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
        }
    
    total_profit = sum(t['profit_loss'] for t in trades if t['profit_loss'] > 0)
    total_loss = abs(sum(t['profit_loss'] for t in trades if t['profit_loss'] < 0))
    
    winning_trades = len([t for t in trades if t['profit_loss'] > 0])
    losing_trades = len([t for t in trades if t['profit_loss'] < 0])
    total_trades = len(trades)
    
    net_profit = sum(t['profit_loss'] for t in trades)
    return_pct = (net_profit / initial_balance) * 100 if initial_balance > 0 else 0
    
    # Max drawdown calculation
    max_dd = 0
    max_balance = initial_balance
    for bal in equity:
        if bal > max_balance:
            max_balance = bal
        dd = ((max_balance - bal) / max_balance) * 100 if max_balance > 0 else 0
        if dd > max_dd:
            max_dd = dd
    
    metrics = {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
        'total_profit': total_profit,
        'total_loss': total_loss,
        'net_profit': net_profit,
        'return_pct': return_pct,
        'avg_win': (total_profit / winning_trades) if winning_trades > 0 else 0,
        'avg_loss': (total_loss / losing_trades) if losing_trades > 0 else 0,
        'profit_factor': (total_profit / total_loss) if total_loss > 0 else 0,
        'max_drawdown': max_dd,
        'final_balance': equity[-1] if equity else initial_balance,
        'sharpe_ratio': calculate_sharpe_ratio(equity),
    }
    
    return metrics


def calculate_sharpe_ratio(equity_curve: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe Ratio"""
    if len(equity_curve) < 2:
        return 0
    
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] 
               for i in range(1, len(equity_curve))]
    
    if not returns:
        return 0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    # Annualized Sharpe (assuming ~252 trading days)
    sharpe = ((mean_return - (risk_free_rate / 252)) / std_return) * np.sqrt(252)
    return sharpe
"@ | Out-File -FilePath "utils\futures_backtest_engine.py" -Encoding UTF8
Write-Host "✓ Created futures_backtest_engine.py"
