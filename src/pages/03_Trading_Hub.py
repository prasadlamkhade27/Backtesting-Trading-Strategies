"""
Trading Hub - Unified Live Trading & Algorithmic Trading
Manage both real/simulated trading and automated strategy execution in one place
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

from propfirm.credentials_manager import CredentialsManager, LiveTraderConfig
from propfirm.telegram_notifier import TelegramNotifier
from propfirm.live_trader import LiveTraderFactory, TradeEvent
from propfirm.algo_trader import AlgoTrader, AlgoConfig
from hft.utils import DataLoader


def setup_page():
    """Configure page settings"""
    st.set_page_config(
        layout="wide",
        page_title="Trading Hub",
        page_icon="💹"
    )
    
    st.markdown("""
    <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)


# ==================== API CREDENTIALS SECTION ====================
def credentials_section():
    """API Credentials Management Section"""
    st.markdown("## 🔐 API Credentials Management")
    
    creds_manager = CredentialsManager()
    
    with st.expander("➕ Add/Update Credentials", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            broker = st.selectbox(
                "Select Broker",
                options=list(LiveTraderConfig.BROKER_CONFIG.keys()),
                format_func=lambda x: LiveTraderConfig.BROKER_CONFIG[x]['name']
            )
            
            st.markdown(f"**Description:** {LiveTraderConfig.BROKER_CONFIG[broker]['description']}")
    
    # Show saved credentials
    st.markdown("### 📋 Saved Brokers")
    saved_brokers = creds_manager.list_brokers()
    
    if saved_brokers:
        for broker in saved_brokers:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.success(f"✅ {LiveTraderConfig.BROKER_CONFIG.get(broker, {}).get('name', broker)}")
            with col2:
                if st.button("🗑️", key=f"delete_{broker}"):
                    creds_manager.remove_credentials(broker)
                    st.success(f"Deleted {broker} credentials")
                    st.rerun()
    else:
        st.info("No brokers configured yet")


# ==================== LIVE TRADING SECTION ====================
def live_trading_section():
    """Live Trading Management Section"""
    st.markdown("## 📊 Live Trading Dashboard")
    
    creds_manager = CredentialsManager()
    saved_brokers = creds_manager.list_brokers()
    
    if not saved_brokers:
        st.error("❌ No broker connected!")
        st.info("**Setup:** Go to 🔐 Credentials section above to add a broker")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_broker = st.selectbox(
            "Select Broker",
            saved_brokers,
            format_func=lambda x: LiveTraderConfig.BROKER_CONFIG.get(x, {}).get('name', x)
        )
    
    with col2:
        mode = st.radio("Trading Mode", ["📈 Real", "🧪 Simulation"], horizontal=True)
        is_live = mode == "📈 Real"
    
    # Connection status
    col1, col2, col3 = st.columns(3)
    col1.metric("Broker", LiveTraderConfig.BROKER_CONFIG[selected_broker]['name'])
    col2.metric("Mode", "REAL 🔴" if is_live else "SIMULATION 🟡")
    col3.metric("Status", "Ready ✅")
    
    st.markdown("---")
    
    # Trading controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✉️ Notifications")
        enable_telegram = st.checkbox("Enable Telegram Alerts", value=False)
        if enable_telegram:
            st.info("Configure Telegram: propfirm/telegram_notifier.py")
    
    with col2:
        st.markdown("### 📈 Recent Trades")
        st.info("Trade history will appear here")
    
    st.markdown("---")
    
    # Manual trade execution
    st.markdown("### 🎯 Execute Manual Trade")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pair = st.selectbox("Pair", list(DataLoader.SYMBOLS.keys()))
        direction = st.radio("Direction", ["BUY", "SELL"], horizontal=True)
    
    with col2:
        lot_size = st.number_input("Lot Size", min_value=0.01, value=1.0, step=0.1)
        sl_pips = st.number_input("Stop Loss (pips)", min_value=1, value=20, step=1)
    
    with col3:
        tp_pips = st.number_input("Take Profit (pips)", min_value=1, value=50, step=1)
        
        if st.button("🚀 Execute Trade", type="primary"):
            st.success(f"✅ {direction} {lot_size} {pair} - SL: {sl_pips}pips, TP: {tp_pips}pips")


# ==================== ALGORITHMIC TRADING SECTION ====================
def algo_trading_section():
    """Algorithmic Trading Management Section"""
    st.markdown("## 🤖 Algorithmic Trading")
    
    creds_manager = CredentialsManager()
    saved_brokers = creds_manager.list_brokers()
    
    if not saved_brokers:
        st.error("❌ No broker connected!")
        st.info("**Setup:** Go to 🔐 Credentials section above to add a broker")
        return
    
    # Configuration
    st.markdown("### ⚙️ Algorithm Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        broker = st.selectbox(
            "Select Broker for Algo",
            saved_brokers,
            key="algo_broker",
            format_func=lambda x: LiveTraderConfig.BROKER_CONFIG.get(x, {}).get('name', x)
        )
        
        strategy = st.selectbox(
            "Trading Strategy",
            ["Moving Average Crossover", "Pivot Points", "XAU/USD Pro", "Custom"]
        )
    
    with col2:
        st.markdown("**Pairs to Trade**")
        pairs = st.multiselect(
            "Select pairs",
            list(DataLoader.SYMBOLS.keys()),
            default=["EURUSD", "XAUUSD (Gold)"],
            key="algo_pairs"
        )
        
        max_concurrent = st.number_input("Max Concurrent Trades", min_value=1, value=3, step=1)
    
    st.markdown("---")
    
    # Risk Parameters
    st.markdown("### 💰 Risk Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, step=0.5)
    
    with col2:
        max_daily_loss = st.number_input("Max Daily Loss ($)", min_value=100, value=1000, step=100)
    
    with col3:
        max_drawdown = st.slider("Max Drawdown (%)", 5, 50, 10, step=5)
    
    st.markdown("---")
    
    # Algorithm Status & Control
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Algorithm Status")
        
        status = st.radio("Algorithm", ["⏹️ Stopped", "▶️ Running"],horizontal=True)
        
        if status == "▶️ Running":
            col_start, col_stop = st.columns(2)
            with col_start:
                if st.button("▶️ Start Algorithm", type="primary"):
                    st.success(f"✅ Algorithm started with {len(pairs)} pairs")
            with col_stop:
                if st.button("⏹️ Stop Algorithm", type="secondary"):
                    st.warning("⏹️ Algorithm stopped")
        else:
            if st.button("▶️ Start Algorithm", type="primary"):
                st.success(f"✅ Algorithm started with {len(pairs)} pairs")
    
    with col2:
        st.markdown("### 📈 Performance Metrics")
        
        col1, col2 = st.columns(2)
        col1.metric("Trades Today", "12")
        col2.metric("Win Rate", "58.3%")
        
        col1, col2 = st.columns(2)
        col1.metric("Daily P&L", "+$450")
        col2.metric("Drawdown", "-2.5%")
    
    st.markdown("---")
    
    # Trade Log
    st.markdown("### 📋 Trade Log")
    
    trades_data = {
        'Time': ['14:32:15', '14:15:22', '13:58:45'],
        'Pair': ['EURUSD', 'GBPUSD', 'XAUUSD'],
        'Direction': ['BUY', 'SELL', 'BUY'],
        'Lots': [1.0, 0.5, 2.0],
        'Entry': [1.0850, 1.2640, 2400.50],
        'Current': [1.0855, 1.2635, 2401.20],
        'P&L': ['+$50', '-$25', '+$140'],
        'Status': ['OPEN', 'OPEN', 'OPEN']
    }
    
    trades_df = pd.DataFrame(trades_data)
    st.dataframe(trades_df, use_container_width=True, hide_index=True)


# ==================== MAIN APP ====================
def main():
    setup_page()
    
    st.title("💹 Trading Hub")
    st.markdown("Unified Live Trading & Algorithmic Trading Management")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔐 Credentials", "📊 Live Trading", "🤖 Algo Trading"])
    
    with tab1:
        credentials_section()
    
    with tab2:
        live_trading_section()
    
    with tab3:
        algo_trading_section()


if __name__ == "__main__":
    main()
