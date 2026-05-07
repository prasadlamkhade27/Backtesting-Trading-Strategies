import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, List
from hft.utils.futures_specs import (
    get_contract_spec, calculate_profit_loss, calculate_position_size_futures,
    calculate_margin_requirement
)

def run_futures_backtest(df, initial_balance, contract_symbol, sl_points, tp_points, risk_pct=0.02, use_micro_contract=False):
    if use_micro_contract:
        micro_mapping = {'ES': 'MES', 'NQ': 'MNQ', 'YM': 'MYM', 'GC': 'MGC'}
        if contract_symbol in micro_mapping:
            contract_symbol = micro_mapping[contract_symbol]
    
    spec = get_contract_spec(contract_symbol)
    balance = initial_balance
    position = None
    entry_price = 0.0
    entry_index = 0
    contracts = 0
    trades = []
    equity = [balance]
    fail_reason = None
    
    for i in range(len(df)):
        price = df['close'].iloc[i]
        
        if position is not None:
            unrealized = calculate_profit_loss(entry_price, price, contracts, contract_symbol, position)
            current_balance = balance + unrealized
            margin_used = calculate_margin_requirement(contracts, contract_symbol, use_maintenance=True)
            if current_balance < margin_used:
                fail_reason = f"Margin Call at {price}"
                break
        
        if position is None:
            if df['BUY'].iloc[i]:
                sl_price = price - sl_points
                contracts, _, _ = calculate_position_size_futures(balance, risk_pct, price, sl_price, contract_symbol)
                margin_needed = calculate_margin_requirement(contracts, contract_symbol)
                if margin_needed <= balance:
                    position = "LONG"
                    entry_price = price
                    entry_index = i
            elif df['SELL'].iloc[i]:
                sl_price = price + sl_points
                contracts, _, _ = calculate_position_size_futures(balance, risk_pct, price, sl_price, contract_symbol)
                margin_needed = calculate_margin_requirement(contracts, contract_symbol)
                if margin_needed <= balance:
                    position = "SHORT"
                    entry_price = price
                    entry_index = i
        
        elif position == "LONG":
            exit_price = None
            if price <= entry_price - sl_points:
                exit_price = entry_price - sl_points
            elif price >= entry_price + tp_points:
                exit_price = entry_price + tp_points
            elif df['SELL'].iloc[i]:
                exit_price = price
            
            if exit_price:
                profit = calculate_profit_loss(entry_price, exit_price, contracts, contract_symbol, 'LONG')
                balance += profit
                equity.append(balance)
                trades.append({'trade_num': len(trades)+1, 'type': 'LONG', 'profit_loss': profit})
                position = None
                contracts = 0
        
        elif position == "SHORT":
            exit_price = None
            if price >= entry_price + sl_points:
                exit_price = entry_price + sl_points
            elif price <= entry_price - tp_points:
                exit_price = entry_price - tp_points
            elif df['BUY'].iloc[i]:
                exit_price = price
            
            if exit_price:
                profit = calculate_profit_loss(entry_price, exit_price, contracts, contract_symbol, 'SHORT')
                balance += profit
                equity.append(balance)
                trades.append({'trade_num': len(trades)+1, 'type': 'SHORT', 'profit_loss': profit})
                position = None
                contracts = 0
    
    return trades, equity, balance, fail_reason

def calculate_futures_metrics(trades, equity, initial_balance, contract_symbol):
    if not trades:
        return {'total_trades': 0, 'win_rate': 0, 'return_pct': 0, 'max_drawdown': 0}
    
    winning = len([t for t in trades if t['profit_loss'] > 0])
    net_profit = sum(t['profit_loss'] for t in trades)
    
    max_dd = 0
    max_bal = initial_balance
    for bal in equity:
        if bal > max_bal:
            max_bal = bal
        dd = ((max_bal - bal) / max_bal * 100) if max_bal > 0 else 0
        if dd > max_dd:
            max_dd = dd
    
    return {
        'total_trades': len(trades),
        'win_rate': (winning / len(trades) * 100) if trades else 0,
        'net_profit': net_profit,
        'return_pct': (net_profit / initial_balance * 100) if initial_balance > 0 else 0,
        'max_drawdown': max_dd,
        'final_balance': equity[-1] if equity else initial_balance
    }

def calculate_sharpe_ratio(equity_curve, risk_free_rate=0.02):
    if len(equity_curve) < 2:
        return 0
    returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve))]
    if not returns:
        return 0
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return 0
    return ((mean_return - (risk_free_rate / 252)) / std_return) * np.sqrt(252)
