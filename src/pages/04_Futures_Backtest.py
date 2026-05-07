import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from hft.strategies import get_strategy, AVAILABLE_STRATEGIES
from hft.utils.futures import (
    run_futures_backtest, calculate_futures_metrics, FUTURES_CONTRACTS, get_contract_spec,
)

st.set_page_config(layout="wide", page_title="Futures Backtester")
st.title(" Futures Trading Backtester")

with st.sidebar:
    st.header("Configuration")
    
    contracts = list(FUTURES_CONTRACTS.keys())
    contract = st.selectbox("Select Futures Contract", contracts)
    
    futures_strats = {k: v for k, v in AVAILABLE_STRATEGIES.items() if 'Futures' in k}
    strategy_name = st.selectbox("Select Strategy", list(futures_strats.keys()))
    
    strategy = get_strategy(strategy_name)
    
    initial_balance = st.number_input("Initial Balance", min_value=1000, value=25000, step=1000)
    risk_pct = st.slider("Risk Per Trade %", 0.1, 5.0, 2.0) / 100
    sl_points = st.number_input("Stop Loss Points", min_value=1, value=50)
    tp_points = st.number_input("Take Profit Points", min_value=1, value=100)

try:
    st.info("Generating sample data...")
    dates = pd.date_range(end=datetime.now(), periods=300, freq='1H')
    base = 5000
    prices = base * (1 + np.random.normal(0, 0.005, 300)).cumprod()
    
    df = pd.DataFrame({
        'open': prices + np.random.normal(0, 1, 300),
        'high': prices + np.abs(np.random.normal(0, 3, 300)),
        'low': prices - np.abs(np.random.normal(0, 3, 300)),
        'close': prices,
        'volume': np.random.randint(100000, 1000000, 300)
    })
    
    df = strategy.generate_signals(df)
    st.success(f"Generated {df['BUY'].sum()} BUY and {df['SELL'].sum()} SELL signals")
    
    trades, equity, final_balance, fail_reason = run_futures_backtest(
        df, initial_balance, contract, sl_points, tp_points, risk_pct
    )
    
    if fail_reason:
        st.error(f"Backtest failed: {fail_reason}")
    
    metrics = calculate_futures_metrics(trades, equity, initial_balance, contract)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Balance", f"${final_balance:,.0f}", f"${final_balance - initial_balance:,.0f}")
    col2.metric("Return", f"{metrics.get('return_pct', 0):.1f}%")
    col3.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
    col4.metric("Max DD", f"{metrics.get('max_drawdown', 0):.1f}%")
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(equity, linewidth=2)
    ax.fill_between(range(len(equity)), equity, alpha=0.2)
    ax.set_xlabel('Trade #')
    ax.set_ylabel('Balance ($)')
    st.pyplot(fig)
    
    if trades:
        st.dataframe(pd.DataFrame(trades))

except Exception as e:
    st.error(f"Error: {str(e)}")
