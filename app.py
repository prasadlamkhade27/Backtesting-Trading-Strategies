"""
Advanced Backtesting Tool with PropFirm Challenge
Refactored with modular architecture
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import custom modules
from hft.strategies import get_strategy, AVAILABLE_STRATEGIES
from hft.utils import run_backtest_phase, calculate_metrics, DataLoader, CSVRulesProcessor, calculate_drawdown_breakdown
from hft.utils.enhanced_backtest import EnhancedBacktestRunner
from propfirm import PROPFIRMS, DEFAULT_CUSTOM

# Import Unified Prop Firm Backtest System
from propfirm.unified_backtest import UnifiedPropFirmBacktest
from propfirm.account_rules import create_apex_preset, create_lucid_preset, create_topstep_preset
from propfirm.trading_rules import TradingRules, RiskManagementRules
from propfirm.payout_rules import PayoutRules

# ====================== PAGE CONFIG ======================
st.set_page_config(layout="wide", page_title="Advanced Backtester", initial_sidebar_state="expanded")

# ====================== CUSTOM CSS STYLING ======================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    :root {
        --primary: #2563EB;
        --primary-light: #3B82F6;
        --primary-dark: #1E40AF;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --text-dark: #1F2937;
        --text-light: #6B7280;
        --bg-white: #FFFFFF;
        --bg-gray: #F9FAFB;
        --border: #E5E7EB;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --text-dark: #F3F4F6;
            --text-light: #D1D5DB;
            --bg-white: #1F2937;
            --bg-gray: #111827;
            --border: #374151;
        }
    }
    
    .main {
        padding: 0 !important;
    }
    
    /* Header */
    h1 {
        color: var(--text-dark);
        text-align: center;
        padding: 40px 20px;
        font-size: 2.8em;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #2563EB, #1E40AF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: var(--text-dark);
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        font-size: 1.8em;
        font-weight: 700;
        border-bottom: 3px solid var(--primary);
    }
    
    h3 {
        color: var(--text-dark);
        margin: 20px 0 10px 0;
        font-size: 1.3em;
        font-weight: 600;
    }
    
    /* Page links (navigation) */
    .stPageLink > a {
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
        width: 100% !important;
        padding: 14px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #2563EB, #1E40AF) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
        text-decoration: none !important;
    }
    
    .stPageLink > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5) !important;
        background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #2563EB, #1E40AF) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Selectbox & Input */
    .stSelectbox > div > div > select,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        padding: 10px 12px !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        background-color: var(--bg-white) !important;
        color: var(--text-dark) !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div > select:focus,
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid var(--border);
        padding: 0 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px !important;
        font-weight: 600;
        color: var(--text-light) !important;
        background-color: transparent !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-gray);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 16px !important;
        font-weight: 600;
        color: var(--text-dark);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--border);
        border-color: var(--primary);
    }
    
    /* Metric */
    .stMetric {
        background-color: var(--bg-gray);
        padding: 16px !important;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
    }
    
    /* Radio */
    .stRadio > div {
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .stRadio > div label {
        padding: 10px 16px !important;
        background-color: var(--bg-gray) !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .stRadio > div label:hover {
        border-color: var(--primary) !important;
        background-color: rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Messages */
    .stSuccess, [data-testid="stSuccess"] {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid var(--success) !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
    }
    
    .stError, [data-testid="stError"] {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid var(--error) !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
    }
    
    .stWarning, [data-testid="stWarning"] {
        background-color: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid var(--warning) !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
    }
    
    .stInfo, [data-testid="stInfo"] {
        background-color: rgba(37, 99, 235, 0.1) !important;
        border-left: 4px solid var(--primary) !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    
    /* Strategy Card */
    .strategy-card {
        background: var(--bg-white);
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }
    
    .strategy-card:hover {
        border-color: var(--primary);
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.15);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: 20px 0 !important;
    }
    
    /* Columns */
    .stColumn {
        padding: 0 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-gray) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    [data-testid="stSidebarNav"] {
        padding-top: 20px !important;
    }
    
    /* Section container */
    .section-container {
        background-color: var(--bg-white);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        transition: all 0.3s ease;
    }
    
    .section-container:hover {
        border-color: var(--primary);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Advanced Backtesting Engine with PropFirm Challenge")

st.markdown("")

# ====================== STRATEGY BUILDER QUICK ACCESS ======================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("pages/01_Strategy_Builder.py", label="✨ Strategy Builder", icon="🚀")

st.markdown("---")

# ====================== SIDEBAR CONFIG ======================
st.sidebar.title("⚙️ Configuration Panel")
st.sidebar.markdown("---")

# Mode selection with better styling
st.sidebar.write("### 📋 Select Mode")
backtest_mode = st.sidebar.radio(
    "Backtesting Mode",
    ["Standard Backtest", "Strategy Comparison", "PropFirm 2-Phase Challenge", "Futures PropFirm", "Batch CSV Analysis"],
    help="Choose your backtesting mode",
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Current Mode:** {backtest_mode}", icon="ℹ️")

# ====================== STANDARD BACKTEST MODE ======================
if backtest_mode == "Standard Backtest":
    st.markdown("## 📊 Standard Backtesting Mode")
    st.markdown("Test a single strategy with custom parameters and analyze detailed results.")
    
    # Configuration Section
    with st.expander("⚙️ Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Strategy")
            strategy_name = st.selectbox(
                "Select Strategy",
                list(AVAILABLE_STRATEGIES.keys()),
                help="Choose a trading strategy",
                label_visibility="collapsed"
            )
            strategy = get_strategy(strategy_name)
            
            st.markdown("### 📈 Data Source")
            data_source = st.radio("Choose Data Source", ["Yahoo Finance", "CSV Upload"], label_visibility="collapsed")
        
        with col2:
            if data_source == "Yahoo Finance":
                st.markdown("### 🌐 Yahoo Finance Settings")
                symbol = st.selectbox("Symbol", list(DataLoader.SYMBOLS.keys()), label_visibility="collapsed", index=list(DataLoader.SYMBOLS.keys()).index("XAUUSD (Gold)"))
                interval = st.select_slider("Timeframe", ["1m", "5m", "15m", "1h", "1d"], value="1h")
                period = st.select_slider("Period", ["1d", "5d", "1mo", "3mo", "1y"], value="1mo")
                try:
                    with st.spinner("Loading data..."):
                        df = DataLoader.load_yfinance(symbol, interval, period)
                    st.success(f"✅ Loaded {len(df)} candles")
                except Exception as e:
                    st.error(f"❌ Error loading data: {e}")
                    st.stop()
            else:
                st.markdown("### 📁 CSV Upload")
                uploaded_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")
                if not uploaded_file:
                    st.info("📌 Please upload a CSV file")
                    st.stop()
                try:
                    with st.spinner("Loading CSV..."):
                        df = DataLoader.load_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} candles from CSV")
                except Exception as e:
                    st.error(f"❌ Error loading CSV: {e}")
                    st.stop()
        
        with col3:
            st.markdown("### 💰 Trading Parameters")
            stop_loss = st.slider("Stop Loss (pips)", 1, 100, 5, help="Stop loss distance in pips")
            take_profit = st.slider("Take Profit (pips)", 1, 200, 10, help="Take profit distance in pips")
            
            st.markdown("### 💎 Account Parameters")
            account_size = st.number_input("Account Size ($)", value=10000, min_value=1000, step=1000)
            risk_percent = st.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0, step=0.1, help="Percentage of account to risk per trade") / 100
    
    # Validation and Execution
    is_valid, msg = DataLoader.validate_data(df)
    if not is_valid:
        st.error(f"❌ Data validation failed: {msg}")
        st.stop()
    
    # Generate signals and run backtest
    with st.spinner("🔄 Running backtest..."):
        df = strategy.generate_signals(df)
        trades, equity, balance, fail_reason = run_backtest_phase(
            df, account_size, 0, None, stop_loss, take_profit, risk_percent
        )
        metrics = calculate_metrics(trades, account_size, balance, equity)
    
    st.markdown("---")
    
    # Results Section
    st.markdown("## 📊 Performance Results")
    
    # Key Metrics - First Row
    col1, col2, col3, col4 = st.columns(4)
    
    profit_color = "🟢" if metrics['net_profit'] >= 0 else "🔴"
    with col1:
        st.metric(
            "💰 Net Profit",
            f"${metrics['net_profit']:,.2f}",
            f"{metrics['net_profit_pct']:.2f}%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "📊 Win Rate",
            f"{metrics['winrate']:.2f}%",
            f"{metrics['wins']}/{metrics['total_trades']} wins"
        )
    
    with col3:
        st.metric(
            "📉 Max Drawdown",
            f"{metrics['max_dd_pct']:.2f}%",
            f"${metrics['max_dd']:,.2f}"
        )
    
    with col4:
        st.metric(
            "🎯 Final Balance",
            f"${balance:,.2f}",
            f"${balance - account_size:+,.2f}"
        )
    
    # Additional Metrics - Second Row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("📈 Total Trades", metrics['total_trades'])
    
    with col6:
        st.metric("📊 Avg Trade Profit", f"${metrics['avg_trade']:,.2f}")
    
    with col7:
        st.metric("🟢 Largest Win", f"${metrics['largest_win']:,.2f}")
    
    with col8:
        st.metric("🔴 Largest Loss", f"${metrics['largest_loss']:,.2f}")
    
    st.markdown("---")
    
    # Detailed Analysis with Multiple Tabs
    result_tabs = st.tabs([
        "📈 Equity Curve", 
        "📋 Trade History", 
        "🔬 Advanced Metrics",
        "📊 Trade Analysis",
        "📉 Drawdown Analysis",
        "🎯 Performance Charts"
    ])
    
    with result_tabs[0]:
        st.markdown("### Equity Curve Over Time")
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(equity, linewidth=2.5, label='Equity', color='#1f77b4')
        ax.axhline(y=account_size, color='green', linestyle='--', alpha=0.6, label='Starting Balance', linewidth=2)
        ax.fill_between(range(len(equity)), account_size, equity, 
                        where=(np.array(equity) >= account_size), alpha=0.2, color='green', label='Profit Zone')
        ax.fill_between(range(len(equity)), account_size, equity, 
                        where=(np.array(equity) < account_size), alpha=0.2, color='red', label='Loss Zone')
        ax.set_xlabel('Candles', fontsize=12)
        ax.set_ylabel('Balance ($)', fontsize=12)
        ax.set_title('Account Equity Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Drawdown chart
        st.markdown("### Drawdown Over Time")
        equity_series = pd.Series(equity)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.fill_between(range(len(drawdown)), 0, drawdown, color='#ef4444', alpha=0.3, label='Drawdown')
        ax.plot(drawdown, linewidth=2, color='#dc2626', label='Drawdown %')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Candles', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.set_title('Underwater Chart', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with result_tabs[1]:
        st.markdown("### Trade History - All Trades")
        if trades:
            trades_df = pd.DataFrame(trades)
            display_df = trades_df[['trade_num', 'type', 'entry_price', 'exit_price', 'profit', 'profit_pct', 'closed_reason', 'candles_held']].copy()
            display_df['entry_price'] = display_df['entry_price'].apply(lambda x: f"${x:.2f}")
            display_df['exit_price'] = display_df['exit_price'].apply(lambda x: f"${x:.2f}")
            display_df['profit'] = display_df['profit'].apply(lambda x: f"${x:.2f}" if x >= 0 else f"-${abs(x):.2f}")
            display_df['profit_pct'] = display_df['profit_pct'].apply(lambda x: f"{x:.2f}%")
            display_df.columns = ['#', 'Type', 'Entry', 'Exit', 'Profit', 'Profit %', 'Reason', 'Candles']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            csv = trades_df.to_csv(index=False)
            st.download_button(
                label="📥 Download All Trades as CSV",
                data=csv,
                file_name=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📌 No trades were executed in this backtest")
    
    with result_tabs[2]:
        st.markdown("### 🔬 Advanced Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}", help="Risk-adjusted returns")
        with col2:
            st.metric("📉 Sortino Ratio", f"{metrics['sortino_ratio']:.2f}", help="Downside-adjusted returns")
        with col3:
            st.metric("📈 Calmar Ratio", f"{metrics['calmar_ratio']:.2f}", help="Return vs Max Drawdown")
        with col4:
            st.metric("🎯 Recovery Factor", f"{metrics['recovery_factor']:.2f}", help="Recovery from drawdown")
        
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Profit Factor", f"{metrics['profit_factor']:.2f}", help="Gross Profit / Gross Loss")
        with col2:
            st.metric("📊 Payoff Ratio", f"{metrics['payoff_ratio']:.2f}", help="Avg Win / |Avg Loss|")
        with col3:
            st.metric("💵 Avg Win", f"${metrics['avg_win']:,.2f}")
        with col4:
            st.metric("💸 Avg Loss", f"${metrics['avg_loss']:,.2f}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Risk Analysis**")
            st.write(f"🔴 Max Loss Trade: ${metrics['largest_loss']:,.2f}")
            st.write(f"🟢 Largest Win: ${metrics['largest_win']:,.2f}")
            st.write(f"💔 Winning Trade Avg: ${metrics['avg_win']:,.2f}")
            st.write(f"📊 Losing Trade Avg: ${metrics['avg_loss']:,.2f}")
        
        with col2:
            st.markdown("**Return Analysis**")
            st.write(f"📈 Total Return: {metrics['net_profit_pct']:.2f}%")
            st.write(f"📊 Avg Trade Return: {metrics['avg_trade_pct']:.4f}%")
            st.write(f"⏱️ Avg Trade Duration: {metrics['avg_trade_duration']:.1f} candles")
            st.write(f"📋 Total Trades: {metrics['total_trades']}")
    
    with result_tabs[3]:
        st.markdown("### Trade Type Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**LONG Trades**")
            long_wr = (metrics['long_wins'] / metrics['long_trades'] * 100) if metrics['long_trades'] > 0 else 0
            st.write(f"Total: **{metrics['long_trades']}**")
            st.write(f"Wins: **{metrics['long_wins']}** | Losses: **{metrics['long_trades'] - metrics['long_wins']}**")
            st.write(f"Win Rate: **{long_wr:.1f}%**")
        
        with col2:
            st.markdown("**SHORT Trades**")
            short_wr = (metrics['short_wins'] / metrics['short_trades'] * 100) if metrics['short_trades'] > 0 else 0
            st.write(f"Total: **{metrics['short_trades']}**")
            st.write(f"Wins: **{metrics['short_wins']}** | Losses: **{metrics['short_trades'] - metrics['short_wins']}**")
            st.write(f"Win Rate: **{short_wr:.1f}%**")
        
        st.divider()
        
        # Trade breakdown pie chart
        if trades:
            col1, col2 = st.columns(2)
            
            with col1:
                fig, ax = plt.subplots(figsize=(8, 6))
                sizes = [metrics['wins'], metrics['losses']]
                colors = ['#10b981', '#ef4444']
                labels = [f"Wins ({metrics['wins']})", f"Losses ({metrics['losses']})"]
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
                ax.set_title('Win/Loss Distribution', fontsize=14, fontweight='bold')
                st.pyplot(fig)
            
            with col2:
                fig, ax = plt.subplots(figsize=(8, 6))
                long_cnt = metrics['long_trades']
                short_cnt = metrics['short_trades']
                sizes = [long_cnt, short_cnt]
                colors = ['#0066cc', '#ff9900']
                labels = [f"LONG ({long_cnt})", f"SHORT ({short_cnt})"]
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
                ax.set_title('Trade Type Distribution', fontsize=14, fontweight='bold')
                st.pyplot(fig)
        
        st.markdown("**Trade Exit Reasons**")
        if trades:
            trades_df = pd.DataFrame(trades)
            exit_reasons = trades_df['closed_reason'].value_counts()
            st.bar_chart(exit_reasons)
    
    with result_tabs[4]:
        st.markdown("### Drawdown Analysis")
        
        from hft.utils import calculate_drawdown_breakdown
        dd_stats = calculate_drawdown_breakdown(equity)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current DD", f"{dd_stats['current_dd']:.2f}%")
        col2.metric("Max Drawdown", f"{dd_stats['max_dd']:.2f}%")
        col3.metric("Avg DD", f"{dd_stats['avg_dd']:.2f}%")
        col4.metric("DD Duration", f"{dd_stats['dd_duration']:.0f} candles")
        
        st.divider()
        
        st.markdown("**Drawdown Details**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"🔴 Maximum Drawdown: **${metrics['max_dd']:,.2f}** ({metrics['max_dd_pct']:.2f}%)")
            st.write(f"📊 Starting Balance: **${account_size:,.2f}**")
            st.write(f"💰 Lowest Point: **${account_size + metrics['max_dd']:,.2f}**")
        with col2:
            equity_series = pd.Series(equity)
            recovery_time = (equity_series >= account_size).idxmax() if any(equity_series >= account_size) else 0
            st.write(f"⏱️ Candles to Recover: **{recovery_time}**")
            st.write(f"📈 Recovery Factor: **{metrics['recovery_factor']:.2f}x**")
            st.write(f"🎯 Most Efficient Phase: Phase with {max(metrics['winrate']) if isinstance(metrics['winrate'], (list, tuple)) else metrics['winrate']:.1f}% win rate")
    
    with result_tabs[5]:
        st.markdown("### Performance Distribution Charts")
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            profits = [t['profit'] for t in trades] if trades else []
            if profits:
                ax.hist(profits, bins=20, color='#1f77b4', edgecolor='black', alpha=0.7)
                ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Breakeven')
                ax.axvline(x=np.mean(profits), color='green', linestyle='--', linewidth=2, label=f'Mean: ${np.mean(profits):.2f}')
                ax.set_xlabel('Profit/Loss ($)', fontsize=12)
                ax.set_ylabel('Frequency', fontsize=12)
                ax.set_title('Profit/Loss Distribution', fontsize=14, fontweight='bold')
                ax.legend()
                st.pyplot(fig)
        
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            profit_pcts = [t['profit_pct'] for t in trades] if trades else []
            if profit_pcts:
                ax.hist(profit_pcts, bins=20, color='#ff7f0e', edgecolor='black', alpha=0.7)
                ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Breakeven')
                ax.axvline(x=np.mean(profit_pcts), color='green', linestyle='--', linewidth=2, label=f'Mean: {np.mean(profit_pcts):.2f}%')
                ax.set_xlabel('Profit/Loss (%)', fontsize=12)
                ax.set_ylabel('Frequency', fontsize=12)
                ax.set_title('Profit/Loss % Distribution', fontsize=14, fontweight='bold')
                ax.legend()
                st.pyplot(fig)

# ====================== STRATEGY COMPARISON MODE ======================
elif backtest_mode == "Strategy Comparison":
    st.markdown("## 📈 Strategy Comparison Mode")
    st.markdown("Compare multiple strategies side-by-side on the same data to find the best performer.")
    
    with st.expander("⚙️ Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 Data Source")
            data_source = st.radio("Choose Data Source", ["Yahoo Finance", "CSV Upload"], label_visibility="collapsed", key="comp_data")
            
            if data_source == "Yahoo Finance":
                st.markdown("### 🌐 Data Settings")
                symbol = st.selectbox("Symbol", list(DataLoader.SYMBOLS.keys()), key="comp_symbol", label_visibility="collapsed", index=list(DataLoader.SYMBOLS.keys()).index("XAUUSD (Gold)"))
                interval = st.select_slider("Timeframe", ["1m", "5m", "15m", "1h", "1d"], value="1h", key="comp_interval")
                period = st.select_slider("Period", ["1d", "5d", "1mo", "3mo", "1y"], value="1mo", key="comp_period")
            else:
                st.markdown("### 📁 CSV Upload")
                uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="comp_csv", label_visibility="collapsed")
        
        with col2:
            st.markdown("### 💰 Trading Parameters")
            sl = st.slider("Stop Loss (pips)", 1, 100, 20, key="comp_sl")
            tp = st.slider("Take Profit (pips)", 1, 200, 40, key="comp_tp")
            risk_pct = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0, key="comp_risk", help="Risk % per trade") / 100
        
        with col3:
            st.markdown("### 💎 Account Settings")
            account_size = st.number_input("Account Size ($)", 1000, step=500, key="comp_account", label_visibility="collapsed")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Strategy Selection")
    selected_strategies = st.multiselect(
        "Select Strategies to Compare",
        list(AVAILABLE_STRATEGIES.keys()),
        default=list(AVAILABLE_STRATEGIES.keys()) if len(list(AVAILABLE_STRATEGIES.keys())) <= 3 else list(AVAILABLE_STRATEGIES.keys())[:2],
        help="Choose one or more strategies to compare"
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        run_comparison = st.button("▶️ Run Comparison", key="comp_run", use_container_width=True)
    
    if run_comparison:
        try:
            with st.spinner("📊 Loading data and running comparison..."):
                # Load data
                if data_source == "Yahoo Finance":
                    df = DataLoader.load_yfinance(symbol, interval, period)
                    DataLoader.validate_data(df)
                else:
                    if uploaded_file:
                        df = DataLoader.load_csv(uploaded_file)
                        DataLoader.validate_data(df)
                    else:
                        st.error("❌ Please upload a CSV file")
                        df = None
                
                if df is not None and len(selected_strategies) > 0:
                    comparison_results = []
                    all_equities = {}
                    
                    progress_bar = st.progress(0)
                    for idx, strategy_name in enumerate(selected_strategies):
                        strategy = get_strategy(strategy_name)
                        df_with_signals = strategy.generate_signals(df.copy())
                        
                        trades, equity, final_balance, fail_reason = run_backtest_phase(
                            df_with_signals, account_size, 1, None, sl, tp, risk_pct
                        )
                        
                        metrics = calculate_metrics(trades, account_size, final_balance, equity)
                        
                        comparison_results.append({
                            "Strategy": strategy_name,
                            "Trades": metrics['total_trades'],
                            "Win Rate": f"{metrics['winrate']:.1f}%",
                            "Net Profit": f"${metrics['net_profit']:,.2f}",
                            "Profit %": f"{metrics['net_profit_pct']:.2f}%",
                            "Max Drawdown": f"{metrics['max_dd_pct']:.2f}%",
                            "Avg Trade": f"${metrics['avg_trade']:,.2f}",
                            "Final Balance": f"${final_balance:,.2f}"
                        })
                        
                        all_equities[strategy_name] = equity
                        progress_bar.progress((idx + 1) / len(selected_strategies))
                    
                    st.markdown("---")
                    st.markdown("## 📊 Comparison Results")
                    
                    # Results Table
                    st.markdown("### Detailed Comparison Table")
                    results_df = pd.DataFrame(comparison_results)
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    
                    # Equity Curves
                    st.markdown("### 📈 Equity Curves Comparison")
                    fig, ax = plt.subplots(figsize=(14, 6))
                    
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    for idx, (strategy_name, equity_curve) in enumerate(all_equities.items()):
                        ax.plot(range(len(equity_curve)), equity_curve, linewidth=2.5, 
                               label=strategy_name, marker='', color=colors[idx % len(colors)])
                    
                    ax.axhline(y=account_size, color='gray', linestyle='--', alpha=0.5, label='Starting Balance')
                    ax.set_xlabel('Candles', fontsize=12)
                    ax.set_ylabel('Account Balance ($)', fontsize=12)
                    ax.set_title('Strategy Comparison - Equity Curves', fontsize=14, fontweight='bold')
                    ax.legend(loc='best', fontsize=10)
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    st.markdown("---")
                    
                    # Ranking
                    st.markdown("### 🏅 Strategy Ranking (by Net Profit)")
                    ranked = sorted(comparison_results, 
                                  key=lambda x: float(x['Net Profit'].replace('$', '').replace(',', '')), 
                                  reverse=True)
                    
                    for idx, result in enumerate(ranked, 1):
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
                        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                        with col1:
                            st.write(f"{medal}")
                        with col2:
                            st.write(f"**{result['Strategy']}**")
                        with col3:
                            st.write(f"Net Profit: {result['Net Profit']}")
                        with col4:
                            st.write(f"({result['Profit %']}) | Win Rate: {result['Win Rate']}")
        
        except Exception as e:
            st.error(f"❌ Error in strategy comparison: {e}")

# ====================== PROPFIRM MODE ======================
elif backtest_mode == "PropFirm 2-Phase Challenge":
    st.markdown("## 🏆 PropFirm 2-Phase Challenge Mode")
    st.markdown("Test your strategy against PropFirm rules - each phase can start fresh or continue from previous phase!")
    
    with st.expander("⚙️ Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Strategy")
            strategy_name = st.selectbox(
                "Select Strategy",
                list(AVAILABLE_STRATEGIES.keys()),
                key="pf_strategy",
                label_visibility="collapsed"
            )
            strategy = get_strategy(strategy_name)
            
            st.markdown("### 🏢 PropFirm Selection")
            propfirm_name = st.selectbox(
                "Choose PropFirm",
                list(PROPFIRMS.keys()) + ["Custom"],
                key="pf_select",
                label_visibility="collapsed"
            )
            
            if propfirm_name == "Custom":
                propfirm = DEFAULT_CUSTOM.copy()
            else:
                propfirm = PROPFIRMS[propfirm_name].copy() if hasattr(PROPFIRMS[propfirm_name], 'copy') else PROPFIRMS[propfirm_name]
                # Make a copy of phase rules
                from propfirm import PhaseRules
                propfirm.phase1 = PhaseRules(
                    daily_loss_limit=PROPFIRMS[propfirm_name].phase1.daily_loss_limit,
                    max_loss_limit=PROPFIRMS[propfirm_name].phase1.max_loss_limit,
                    profit_target=PROPFIRMS[propfirm_name].phase1.profit_target,
                    min_trading_days=PROPFIRMS[propfirm_name].phase1.min_trading_days,
                    max_trades_per_day=PROPFIRMS[propfirm_name].phase1.max_trades_per_day
                )
                propfirm.phase2 = PhaseRules(
                    daily_loss_limit=PROPFIRMS[propfirm_name].phase2.daily_loss_limit,
                    max_loss_limit=PROPFIRMS[propfirm_name].phase2.max_loss_limit,
                    profit_target=PROPFIRMS[propfirm_name].phase2.profit_target,
                    min_trading_days=PROPFIRMS[propfirm_name].phase2.min_trading_days,
                    max_trades_per_day=PROPFIRMS[propfirm_name].phase2.max_trades_per_day
                )
            
            st.markdown("### 🎛️ Phase 1 Rules")
            p1_daily = st.slider("Daily Loss %", 1, 20, int(propfirm.phase1.daily_loss_limit*100), key="p1_daily") / 100
            p1_max = st.slider("Max Loss %", 5, 40, int(propfirm.phase1.max_loss_limit*100), key="p1_max") / 100
            p1_profit = st.slider("Profit Target %", 5, 50, int(propfirm.phase1.profit_target*100), key="p1_profit") / 100
            
            propfirm.phase1.daily_loss_limit = p1_daily
            propfirm.phase1.max_loss_limit = p1_max
            propfirm.phase1.profit_target = p1_profit
            
            st.markdown("### 🎛️ Phase 2 Rules")
            p2_daily = st.slider("Daily Loss %", 1, 20, int(propfirm.phase2.daily_loss_limit*100), key="p2_daily") / 100
            p2_max = st.slider("Max Loss %", 5, 40, int(propfirm.phase2.max_loss_limit*100), key="p2_max") / 100
            p2_profit = st.slider("Profit Target %", 5, 50, int(propfirm.phase2.profit_target*100), key="p2_profit") / 100
            
            propfirm.phase2.daily_loss_limit = p2_daily
            propfirm.phase2.max_loss_limit = p2_max
            propfirm.phase2.profit_target = p2_profit
            
            st.markdown("### ⚙️ Phase Logic")
            phase_logic = st.radio(
                "How should phases run?",
                ["Phase 2 Uses Phase 1 Profits", "Each Phase Starts Fresh"],
                help="Independent: Both phases start with fresh account balance\nAfter: Phase 2 uses Phase 1 ending balance",
                key="pf_phase_logic",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("### 📈 Data Source")
            data_source = st.radio("Choose Data Source", ["Yahoo Finance", "CSV Upload"], label_visibility="collapsed", key="pf_data")
            
            if data_source == "Yahoo Finance":
                st.markdown("### 🌐 Yahoo Finance")
                symbol = st.selectbox("Symbol", list(DataLoader.SYMBOLS.keys()), key="pf_symbol", label_visibility="collapsed", index=list(DataLoader.SYMBOLS.keys()).index("XAUUSD (Gold)"))
                interval = st.select_slider("Timeframe", ["1m", "5m", "15m", "1h", "1d"], value="1h", key="pf_interval")
                period = st.select_slider("Period", ["1d", "5d", "1mo", "3mo", "1y"], value="1mo", key="pf_period")
                try:
                    with st.spinner("📊 Loading data..."):
                        df = DataLoader.load_yfinance(symbol, interval, period)
                    st.success(f"✅ Loaded {len(df)} candles")
                except Exception as e:
                    st.error(f"❌ Error loading data: {e}")
                    st.stop()
            else:
                st.markdown("### 📁 CSV Upload")
                uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="pf_csv", label_visibility="collapsed")
                if not uploaded_file:
                    st.info("📌 Please upload a CSV file")
                    st.stop()
                try:
                    with st.spinner("📊 Loading CSV..."):
                        df = DataLoader.load_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} candles")
                except Exception as e:
                    st.error(f"❌ Error loading CSV: {e}")
                    st.stop()
        
        with col3:
            st.markdown("### 💰 Trading Parameters")
            stop_loss = st.slider("Stop Loss (pips)", 1, 100, 5, key="pf_sl")
            take_profit = st.slider("Take Profit (pips)", 1, 200, 10, key="pf_tp")
            
            st.markdown("### 💎 Account Parameters")
            account_size = st.number_input("Account Size ($)", value=10000, min_value=1000, step=1000, key="pf_account", label_visibility="collapsed")
            risk_percent = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0, step=0.1, key="pf_risk", help="% risk per trade") / 100
    
    st.markdown("---")
    
    # Validate data
    is_valid, msg = DataLoader.validate_data(df)
    if not is_valid:
        st.error(f"❌ Data validation failed: {msg}")
        st.stop()
    
    # Run backtests
    with st.spinner("🔄 Running Phase 1..."):
        df = strategy.generate_signals(df)
        
        # Phase 1 - Always starts with fresh account
        phase1_trades, phase1_equity, phase1_balance, phase1_fail = run_backtest_phase(
            df, account_size, 1, propfirm.phase1, stop_loss, take_profit, risk_percent
        )
        
        phase1_metrics = calculate_metrics(phase1_trades, account_size, phase1_balance, phase1_equity)
        
        # Phase 2 - Depends on phase logic
        phase2_trades, phase2_equity, phase2_balance, phase2_fail = [], [account_size if phase_logic == "Each Phase Starts Fresh" else phase1_balance], account_size if phase_logic == "Each Phase Starts Fresh" else phase1_balance, None
        phase2_metrics = None
        phase2_starting_balance = None
        
        if phase1_fail is None:
            # Determine Phase 2 starting balance based on logic
            if phase_logic == "Each Phase Starts Fresh":
                phase2_starting = account_size
                phase2_starting_balance = account_size
            else:
                phase2_starting = phase1_balance
                phase2_starting_balance = phase1_balance
            
            phase2_trades, phase2_equity, phase2_balance, phase2_fail = run_backtest_phase(
                df, phase2_starting, 2, propfirm.phase2, stop_loss, take_profit, risk_percent
            )
            phase2_metrics = calculate_metrics(phase2_trades, phase2_starting, phase2_balance, phase2_equity)
    
    st.markdown("---")
    st.markdown("## 🎯 Challenge Results")
    
    # Status Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if phase1_fail:
            st.markdown(f"""
            <div style="background-color: #fecaca; padding: 20px; border-radius: 10px; border-left: 5px solid #dc2626;">
                <h3 style="color: #991b1b; margin: 0;">❌ Phase 1 FAILED</h3>
                <p style="margin: 10px 0 0 0; font-size: 14px;"><strong>Reason:</strong> {phase1_fail}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #dbeafe; padding: 20px; border-radius: 10px; border-left: 5px solid #0284c7;">
                <h3 style="color: #0c4a6e; margin: 0;">✅ Phase 1 PASSED</h3>
                <p style="margin: 10px 0 0 0; font-size: 14px;"><strong>Balance:</strong> ${phase1_balance:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if phase1_fail:
            st.markdown(f"""
            <div style="background-color: #f3e8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #a855f7;">
                <h3 style="color: #6b21a8; margin: 0;">⏸️ Phase 2 BLOCKED</h3>
                <p style="margin: 10px 0 0 0; font-size: 14px;"><strong>Reason:</strong> Phase 1 not passed</p>
            </div>
            """, unsafe_allow_html=True)
        elif phase2_fail:
            st.markdown(f"""
            <div style="background-color: #fecaca; padding: 20px; border-radius: 10px; border-left: 5px solid #dc2626;">
                <h3 style="color: #991b1b; margin: 0;">❌ Phase 2 FAILED</h3>
                <p style="margin: 10px 0 0 0; font-size: 14px;"><strong>Reason:</strong> {phase2_fail}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #dcfce7; padding: 20px; border-radius: 10px; border-left: 5px solid #16a34a;">
                <h3 style="color: #15803d; margin: 0;">✅ Phase 2 PASSED</h3>
                <p style="margin: 10px 0 0 0; font-size: 14px;"><strong>Balance:</strong> ${phase2_balance:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if phase_logic == "Each Phase Starts Fresh":
            # When fresh: Phase 1 profit + Phase 2 profit = total
            total_profit = (phase1_balance - account_size) + (phase2_balance - account_size if not phase1_fail else 0)
            total_profit_pct = (total_profit / account_size) * 100
        else:
            # When continuing: Final balance - original = profit
            total_profit = phase2_balance - account_size
            total_profit_pct = (total_profit / account_size) * 100
        
        if total_profit >= 0:
            bg_color = "#fef3c7"
            border_color = "#f59e0b"
            text_color = "#92400e"
        else:
            bg_color = "#fecaca"
            border_color = "#dc2626"
            text_color = "#991b1b"
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border-left: 5px solid {border_color};">
            <h3 style="color: {text_color}; margin: 0;">💰 Total Profit</h3>
            <p style="margin: 10px 0 0 0; font-size: 18px; font-weight: bold; color: {text_color};"><strong>${total_profit:,.2f} ({total_profit_pct:.2f}%)</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Comparison of phase logic
    st.markdown("### 📊 Phase Logic Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Phase 1 Results**")
        st.write(f"Starting Balance: ${account_size:,.2f}")
        st.write(f"Ending Balance: ${phase1_balance:,.2f}")
        st.write(f"Profit: ${phase1_balance - account_size:,.2f} ({((phase1_balance - account_size) / account_size * 100):.2f}%)")
    
    with col2:
        st.markdown(f"**Phase 2 Results**")
        if phase_logic == "Each Phase Starts Fresh":
            st.write(f"Starting Balance: ${account_size:,.2f} (FRESH)")
            phase2_profit = phase2_balance - account_size if not phase1_fail else 0
            phase2_profit_pct = (phase2_profit / account_size * 100) if not phase1_fail else 0
        else:
            st.write(f"Starting Balance: ${phase1_balance:,.2f} (from Phase 1)")
            phase2_profit = phase2_balance - phase1_balance if not phase1_fail else 0
            phase2_profit_pct = (phase2_profit / phase1_balance * 100) if (not phase1_fail and phase1_balance > 0) else 0
        
        st.write(f"Ending Balance: ${phase2_balance:,.2f}")
        st.write(f"Profit: ${phase2_profit:,.2f} ({phase2_profit_pct:.2f}%)" if not phase1_fail else "Blocked (Phase 1 failed)")
    
    st.markdown("---")
    
    # Show Real Account scenario
    st.markdown("### 💎 Real Account Trading Scenario")
    st.markdown("If you pass both phases, you get a real account. Starting fresh with original account size:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Scenario: Real Account (Fresh $)**")
        real_account_profit = phase2_balance - account_size if not phase1_fail else "N/A"
        st.write(f"Starting: ${account_size:,.2f}")
        if not phase1_fail:
            st.write(f"Expected: ${phase2_balance:,.2f}")
            st.write(f"Profit: ${real_account_profit:,.2f}")
        else:
            st.write(f"Status: Cannot reach real account (Phase 1 failed)")
    
    with col2:
        st.markdown("**Your Edge Analysis**")
        if not phase1_fail and phase2_metrics:
            st.write(f"Win Rate: {phase2_metrics['winrate']:.1f}%")
            st.write(f"Profit Factor: {phase2_metrics['profit_factor']:.2f}x")
            st.write(f"Sharpe Ratio: {phase2_metrics['sharpe_ratio']:.2f}")
        else:
            st.write("Complete both phases to see edge analysis")
    
    # Detailed Results Tabs
    result_tabs = st.tabs(["📊 Phase 1", "📊 Phase 2", "📈 Comparison", "🔍 Analysis"])
    
    with result_tabs[0]:
        st.markdown("### Phase 1 Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", phase1_metrics['total_trades'])
        col2.metric("Win Rate", f"{phase1_metrics['winrate']:.2f}%")
        col3.metric("Net Profit", f"${phase1_metrics['net_profit']:,.2f}")
        col4.metric("Max Drawdown", f"{phase1_metrics['max_dd_pct']:.2f}%")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(phase1_equity, linewidth=2.5, label='Phase 1 Equity', color='#1f77b4')
        ax.axhline(y=account_size, color='green', linestyle='--', alpha=0.6, label='Starting Balance')
        ax.fill_between(range(len(phase1_equity)), account_size, phase1_equity, 
                        where=(np.array(phase1_equity) >= account_size), alpha=0.2, color='green')
        ax.fill_between(range(len(phase1_equity)), account_size, phase1_equity, 
                        where=(np.array(phase1_equity) < account_size), alpha=0.2, color='red')
        ax.set_xlabel('Candles')
        ax.set_ylabel('Balance ($)')
        ax.set_title('Phase 1 - Equity Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    with result_tabs[1]:
        if not phase1_fail and phase2_metrics:
            st.markdown("### Phase 2 Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Trades", phase2_metrics['total_trades'])
            col2.metric("Win Rate", f"{phase2_metrics['winrate']:.2f}%")
            col3.metric("Net Profit", f"${phase2_metrics['net_profit']:,.2f}")
            col4.metric("Max Drawdown", f"{phase2_metrics['max_dd_pct']:.2f}%")
            
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.plot(phase2_equity, linewidth=2.5, label='Phase 2 Equity', color='#ff7f0e')
            ax.axhline(y=phase1_balance, color='green', linestyle='--', alpha=0.6, label='Phase 1 Starting Balance')
            ax.fill_between(range(len(phase2_equity)), phase1_balance, phase2_equity, 
                            where=(np.array(phase2_equity) >= phase1_balance), alpha=0.2, color='green')
            ax.fill_between(range(len(phase2_equity)), phase1_balance, phase2_equity, 
                            where=(np.array(phase2_equity) < phase1_balance), alpha=0.2, color='red')
            ax.set_xlabel('Candles')
            ax.set_ylabel('Balance ($)')
            ax.set_title('Phase 2 - Equity Curve')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        else:
            st.info("⏸️ Phase 2 was not executed (Phase 1 did not pass)")
    
    with result_tabs[2]:
        if not phase1_fail and phase2_metrics:
            st.markdown("### Phase Comparison")
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.plot(phase1_equity, linewidth=2.5, label='Phase 1', color='#1f77b4')
            # Offset Phase 2 to start where Phase 1 ended
            phase2_equity_offset = np.array(phase2_equity) - phase1_balance + phase1_balance
            ax.plot(range(len(phase1_equity)-1, len(phase1_equity)-1+len(phase2_equity)), 
                   phase2_equity, linewidth=2.5, label='Phase 2', color='#ff7f0e')
            ax.set_xlabel('Candles')
            ax.set_ylabel('Balance ($)')
            ax.set_title('Phase 1 vs Phase 2 - Comparison')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
    
    with result_tabs[3]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📋 Phase 1 Summary")
            st.write(f"**Trades:** {phase1_metrics['total_trades']}")
            st.write(f"**Wins:** {phase1_metrics['wins']}")
            st.write(f"**Losses:** {phase1_metrics['losses']}")
            st.write(f"**Net Profit:** ${phase1_metrics['net_profit']:,.2f}")
        with col2:
            st.markdown("### 📋 Phase 2 Summary")
            if phase2_metrics:
                st.write(f"**Trades:** {phase2_metrics['total_trades']}")
                st.write(f"**Wins:** {phase2_metrics['wins']}")
                st.write(f"**Losses:** {phase2_metrics['losses']}")
                st.write(f"**Net Profit:** ${phase2_metrics['net_profit']:,.2f}")
            else:
                st.write("Not executed")

# ====================== FUTURES PROPFIRM MODE ======================
elif backtest_mode == "Futures PropFirm":
    st.markdown("## 🚀 Futures PropFirm Backtest")
    st.markdown("Test your futures strategy against prop firm rules with real-time compliance checking.")
    
    with st.expander("⚙️ Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🏢 Select Firm Preset")
            firm_preset = st.selectbox(
                "Prop Firm Rules",
                ["APEX", "LUCID", "TOPSTEP", "Custom"],
                label_visibility="collapsed",
                key="futures_firm"
            )
            
            if firm_preset == "APEX":
                account_config = create_apex_preset(50000)
            elif firm_preset == "LUCID":
                account_config = create_lucid_preset(50000)
            elif firm_preset == "TOPSTEP":
                account_config = create_topstep_preset(50000)
            else:
                st.markdown("### 📝 Custom Rules")
                profit_target = st.number_input("Profit Target ($)", 1000, 50000, 3000, key="futures_profit_target")
                max_drawdown = st.slider("Max Drawdown (%)", 1, 20, 5, key="futures_max_dd") / 100
                daily_loss = st.slider("Daily Loss Limit (%)", 1, 20, 3, key="futures_daily_loss") / 100
                account_config = create_apex_preset(50000)
                account_config.phase1.profit_target = profit_target / 50000
                account_config.phase1.max_loss_limit = max_drawdown
                account_config.phase1.daily_loss_limit = daily_loss
        
        with col2:
            st.markdown("### 📈 Futures Contract")
            futures_symbol = st.selectbox(
                "Select Futures",
                ["ES", "NQ", "YM", "CL", "GC"],
                label_visibility="collapsed",
                key="futures_symbol"
            )
            
            st.markdown("### 📊 Data Settings")
            start_date = st.date_input("Start Date", key="futures_start_date")
            end_date = st.date_input("End Date", key="futures_end_date")
            
            st.markdown("### 💰 Account Settings")
            initial_balance = st.number_input("Initial Balance ($)", 10000, 500000, 50000, step=5000, label_visibility="collapsed", key="futures_balance")
        
        with col3:
            st.markdown("### 📍 Trading Parameters")
            sl_pips = st.slider("Stop Loss (pips)", 1, 100, 20, key="futures_sl")
            tp_pips = st.slider("Take Profit (pips)", 1, 200, 40, key="futures_tp")
            
            st.markdown("### 🎯 Strategy Selection")
            strategy_name = st.selectbox(
                "Select Strategy",
                list(AVAILABLE_STRATEGIES.keys()),
                label_visibility="collapsed",
                key="futures_strategy"
            )
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        run_futures_backtest = st.button("▶️ Run Backtest", use_container_width=True, key="run_futures_btn")
    
    if run_futures_backtest:
        with st.spinner("🔄 Loading data and running backtest..."):
            try:
                # Validate dates
                if start_date >= end_date:
                    st.error("❌ Start date must be before end date!")
                    st.stop()
                
                # Generate sample data for futures
                date_range = pd.date_range(start=start_date, end=end_date, freq='1H')
                
                if len(date_range) < 10:
                    st.error("❌ Date range must span at least 10 hours to generate meaningful data!")
                    st.stop()
                
                np.random.seed(42)
                price_data = 4500 + np.cumsum(np.random.randn(len(date_range)) * 5)
                
                df = pd.DataFrame({
                    'timestamp': date_range,
                    'open': price_data + np.random.randn(len(date_range)) * 2,
                    'high': price_data + abs(np.random.randn(len(date_range)) * 3),
                    'low': price_data - abs(np.random.randn(len(date_range)) * 3),
                    'close': price_data,
                    'volume': np.random.randint(10000, 100000, len(date_range))
                })
                
                df = df.set_index('timestamp')
                
                # Generate signals using strategy
                strategy = get_strategy(strategy_name)
                df = strategy.generate_signals(df)
                
                # Count signals
                buy_signals = (df.get('BUY', 0) == 1).sum()
                sell_signals = (df.get('SELL', 0) == 1).sum()
                
                st.success(f"✅ Loaded {len(df)} candles | {buy_signals} BUY signals | {sell_signals} SELL signals")
                
                st.markdown("---")
                st.markdown("### 🔄 Running PropFirm Backtest...")
                
                # Create unified backtest
                backtest = UnifiedPropFirmBacktest(
                    account_config=account_config,
                    trading_rules=TradingRules(),
                    risk_rules=RiskManagementRules(),
                    payout_rules=PayoutRules()
                )
                
                # Run backtest
                result = backtest.run(
                    data=df,
                    symbol=futures_symbol,
                    entry_col='BUY',
                    exit_col='SELL',
                    sl_pips=sl_pips,
                    tp_pips=tp_pips,
                    init_time=df.index[0] if len(df) > 0 else None
                )
                
                # Validate result
                if result is None or not isinstance(result, dict):
                    st.error("❌ Backtest returned invalid result")
                    st.stop()
                
                st.markdown("---")
                st.markdown("## 📊 Backtest Results")
                
                # Status
                if result.get('passed'):
                    st.success("✅ PASSED - Account Challenge Completed!")
                else:
                    st.error(f"❌ FAILED - {result.get('reason', 'Unknown reason')}")
                
                # Key Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                summary = result.get('summary', {})
                if summary is None:
                    summary = {}
                
                col1.metric("💰 Final Balance", f"${summary.get('final_balance', 0):,.2f}", f"+${summary.get('pnl', 0):,.2f}")
                col2.metric("📊 Win Rate", f"{summary.get('win_rate', 0):.1f}%", f"{summary.get('winning_trades', 0)}/{summary.get('total_trades', 0)} wins")
                col3.metric("📉 Max Drawdown", f"{summary.get('max_drawdown_pct', 0):.2f}%", f"${summary.get('max_drawdown', 0):,.2f}")
                col4.metric("📈 Total Trades", summary.get('total_trades', 0))
                
                st.divider()
                
                # Dashboard Summary
                if result.get('detailed_report') and isinstance(result.get('detailed_report'), dict):
                    dashboard = result['detailed_report'].get('dashboard_summary', {})
                    
                    if dashboard:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 📊 Account Status")
                            st.write(f"**Starting Balance:** ${dashboard.get('initial_balance', 0):,.2f}")
                            st.write(f"**Current Balance:** ${dashboard.get('current_balance', 0):,.2f}")
                            st.write(f"**Peak Balance:** ${dashboard.get('peak_balance', 0):,.2f}")
                            st.write(f"**P&L:** ${dashboard.get('pnl', 0):,.2f} ({dashboard.get('pnl_pct', 0):.2f}%)")
                        
                        with col2:
                            st.markdown("### 🎯 Target Progress")
                            st.write(f"**Target:** ${dashboard.get('target', 0):,.2f}")
                            st.write(f"**Progress:** ${dashboard.get('progress', 0):,.2f}")
                            st.write(f"**Achievement:** {dashboard.get('achievement', 0):.1f}%")
                            st.write(f"**Status:** {dashboard.get('status', 'In Progress')}")
                        
                        st.divider()
                        
                        st.markdown("### ✅ Compliance Score")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Score", f"{dashboard.get('compliance_score', 0)}/100")
                        col2.metric("Breaches", dashboard.get('breaches', 0))
                        col3.metric("Critical", dashboard.get('critical_breaches', 0))
                    else:
                        st.info("ℹ️ Dashboard data not available")
                
                # Advanced Backtesting Analysis
                st.markdown("---")
                st.markdown("### 🔬 Advanced Analysis")
                
                if result.get('detailed_report') and isinstance(result.get('detailed_report'), dict):
                    report = result['detailed_report']
                    
                    # Advanced tabs
                    advanced_tabs = st.tabs([
                        "📈 Performance", 
                        "📊 Risk Analysis", 
                        "📋 Trade Details", 
                        "🔍 Compliance", 
                        "📉 Drawdown", 
                        "💹 Strategy Comparison"
                    ])
                    
                    # Tab 1: Performance Metrics
                    with advanced_tabs[0]:
                        st.markdown("### 📈 Performance Metrics")
                        metrics = report.get('performance_metrics', {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        if 'win_rate' in metrics:
                            col1.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
                        if 'profit_factor' in metrics:
                            col2.metric("Profit Factor", f"{metrics.get('profit_factor', 0):.2f}x")
                        if 'sharpe_ratio' in metrics:
                            col3.metric("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}")
                        if 'sortino_ratio' in metrics:
                            col4.metric("Sortino Ratio", f"{metrics.get('sortino_ratio', 0):.2f}")
                        
                        st.divider()
                        
                        # Detailed metrics table
                        metrics_display = {
                            "Metric": list(metrics.keys()),
                            "Value": [f"{v:.4f}" if isinstance(v, float) else str(v) for v in metrics.values()]
                        }
                        metrics_df = pd.DataFrame(metrics_display)
                        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
                        
                        # Export metrics
                        csv_metrics = metrics_df.to_csv(index=False)
                        st.download_button(
                            "📥 Download Metrics as CSV",
                            csv_metrics,
                            "futures_metrics.csv",
                            "text/csv"
                        )
                    
                    # Tab 2: Risk Analysis
                    with advanced_tabs[1]:
                        st.markdown("### 📊 Risk Analysis")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Drawdown Analysis**")
                            if 'max_drawdown_pct' in summary:
                                st.write(f"Max Drawdown: **{summary['max_drawdown_pct']:.2f}%**")
                            if 'max_drawdown' in summary:
                                st.write(f"Max Drawdown ($): **${summary['max_drawdown']:,.2f}**")
                            if 'avg_drawdown' in summary:
                                st.write(f"Avg Drawdown: **{summary.get('avg_drawdown', 0):.2f}%**")
                        
                        with col2:
                            st.markdown("**Trade Risk**")
                            if 'avg_win' in metrics:
                                st.write(f"Avg Winner: **${metrics['avg_win']:,.2f}**")
                            if 'avg_loss' in metrics:
                                st.write(f"Avg Loser: **${metrics['avg_loss']:,.2f}**")
                            if 'largest_loss' in metrics:
                                st.write(f"Largest Loss: **${metrics['largest_loss']:,.2f}**")
                        
                        st.divider()
                        
                        # Risk/Reward ratio chart
                        if 'avg_win' in metrics and 'avg_loss' in metrics and metrics['avg_loss'] != 0:
                            rr_data = {
                                'Type': ['Average Win', 'Average Loss'],
                                'Amount': [abs(metrics['avg_win']), abs(metrics['avg_loss'])]
                            }
                            rr_df = pd.DataFrame(rr_data)
                            st.bar_chart(rr_df.set_index('Type'))
                    
                    # Tab 3: Trade Details
                    with advanced_tabs[2]:
                        st.markdown("### 📋 All Trades")
                        if report.get('trades'):
                            trades_df = pd.DataFrame(report['trades'])
                            
                            # Columns selection
                            st.markdown("**Trade Filters**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                trade_type_filter = st.multiselect("Trade Type", ["LONG", "SHORT"], default=["LONG", "SHORT"], key="futures_type_filter")
                            with col2:
                                show_profitable = st.checkbox("Profitable Only", False, key="futures_profitable")
                            with col3:
                                show_losing = st.checkbox("Losing Only", False, key="futures_losing")
                            
                            # Apply filters
                            filtered_trades = trades_df.copy()
                            if trade_type_filter:
                                filtered_trades = filtered_trades[filtered_trades.get('type', '').isin(trade_type_filter)]
                            if show_profitable:
                                filtered_trades = filtered_trades[filtered_trades.get('profit', 0) > 0]
                            if show_losing:
                                filtered_trades = filtered_trades[filtered_trades.get('profit', 0) < 0]
                            
                            st.dataframe(filtered_trades, use_container_width=True, hide_index=True)
                            
                            # Export trades
                            csv_trades = filtered_trades.to_csv(index=False)
                            st.download_button(
                                "📥 Download Trades as CSV",
                                csv_trades,
                                f"futures_trades.csv",
                                "text/csv",
                                key="futures_trades_download"
                            )
                        else:
                            st.info("No trades executed")
                    
                    # Tab 4: Compliance
                    with advanced_tabs[3]:
                        st.markdown("### 🔍 Compliance Report")
                        if report.get('breaches'):
                            breaches_df = pd.DataFrame(report['breaches'])
                            
                            # Breach summary
                            col1, col2 = st.columns(2)
                            with col1:
                                breach_counts = breaches_df['type'].value_counts()
                                st.markdown("**Breach Types**")
                                st.bar_chart(breach_counts)
                            
                            with col2:
                                breach_severity = breaches_df['severity'].value_counts() if 'severity' in breaches_df else None
                                if breach_severity is not None:
                                    st.markdown("**Breach Severity**")
                                    severity_colors = {'CRITICAL': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}
                                    for severity, count in breach_severity.items():
                                        st.write(f"{severity_colors.get(severity, '⚪')} {severity}: **{count}**")
                            
                            st.divider()
                            st.markdown("**All Breaches**")
                            st.dataframe(breaches_df, use_container_width=True, hide_index=True)
                            
                            csv_breaches = breaches_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Breaches as CSV",
                                csv_breaches,
                                "futures_breaches.csv",
                                "text/csv",
                                key="futures_breaches_download"
                            )
                        else:
                            st.success("✅ No compliance breaches detected!")
                    
                    # Tab 5: Drawdown Analysis
                    with advanced_tabs[4]:
                        st.markdown("### 📉 Drawdown Visualization")
                        
                        # Create equity curve for drawdown visualization
                        if report.get('trades'):
                            trades_list = report['trades']
                            equity_curve = [initial_balance]
                            for trade in trades_list:
                                equity_curve.append(equity_curve[-1] + trade.get('profit', 0))
                            
                            equity_series = pd.Series(equity_curve)
                            running_max = equity_series.cummax()
                            drawdown_pct = ((equity_series - running_max) / running_max * 100)
                            
                            fig, ax = plt.subplots(figsize=(14, 6))
                            ax.fill_between(range(len(drawdown_pct)), 0, drawdown_pct, color='#ef4444', alpha=0.3)
                            ax.plot(drawdown_pct, linewidth=2, color='#dc2626', label='Drawdown %')
                            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
                            ax.set_xlabel('Trade Number')
                            ax.set_ylabel('Drawdown (%)')
                            ax.set_title('Underwater Chart - Drawdown Over Trades')
                            ax.legend()
                            ax.grid(True, alpha=0.3)
                            st.pyplot(fig)
                            
                            # Drawdown stats
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Max Drawdown", f"{drawdown_pct.min():.2f}%")
                            col2.metric("Current Drawdown", f"{drawdown_pct.iloc[-1]:.2f}%")
                            col3.metric("Avg Drawdown", f"{drawdown_pct[drawdown_pct < 0].mean():.2f}%")
                    
                    # Tab 6: Strategy Comparison
                    with advanced_tabs[5]:
                        st.markdown("### 💹 Strategy Comparison & Optimization")
                        
                        st.info("💡 Tip: Run multiple backtests with different parameters to compare strategies!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Current Strategy Performance**")
                            st.write(f"Firm: **{firm_preset}**")
                            st.write(f"Contract: **{futures_symbol}**")
                            st.write(f"Strategy: **{strategy_name}**")
                            st.write(f"Result: **{'PASSED ✅' if result.get('passed') else 'FAILED ❌'}**")
                        
                        with col2:
                            st.markdown("**Recommendation**")
                            if result.get('passed'):
                                st.success(f"✅ Strategy passed the {firm_preset} challenge!")
                                st.write(f"**Ready for live trading** with this configuration.")
                            else:
                                st.warning(f"❌ Strategy needs optimization for {firm_preset}")
                                st.write(f"**Reason:** {result.get('reason', 'See detailed report above')}")
                        
                        st.divider()
                        
                        # Parameter tuning guide
                        st.markdown("**Parameter Tuning Guide**")
                        st.markdown("""
                        **To optimize your strategy:**
                        
                        1. **Stop Loss**: Try values between 5-50 pips (smaller = stricter risk control)
                        2. **Take Profit**: Try values between 20-100 pips (larger = patient profit-taking)
                        3. **Account Size**: Test with different initial balances to see scalability
                        4. **Firm Rules**: Switch between APEX, LUCID, TOPSTEP to find best fit
                        
                        **Track Results:** Download CSV exports and compare across runs
                        """)
                else:
                    st.info("ℹ️ No detailed report available")
            
            except Exception as e:
                st.error(f"❌ Error running backtest: {str(e)}")
                import traceback
                with st.expander("🔍 Debug Information"):
                    st.error(traceback.format_exc())

# ====================== BATCH CSV MODE ======================
elif backtest_mode == "Batch CSV Analysis":
    st.markdown("## 📋 Batch CSV Rule Analysis Mode")
    st.markdown("Upload a CSV with multiple PropFirm rule configurations to test them all at once!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download Template CSV", use_container_width=True):
            template = CSVRulesProcessor.create_template_csv()
            st.download_button(
                label="⬇️ Download Template",
                data=template,
                file_name="batch_rules_template.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        st.write("")
    
    with col3:
        st.write("")
    
    st.markdown("---")
    
    # CSV Upload
    st.markdown("### 📁 Upload Your Rules CSV")
    csv_file = st.file_uploader("Upload Rules CSV", type=['csv'], label_visibility="collapsed")
    
    if csv_file:
        try:
            with st.spinner("📊 Reading CSV..."):
                rules_df = pd.read_csv(csv_file)
            
            st.markdown("### 👁️ CSV Preview")
            st.dataframe(rules_df, use_container_width=True, hide_index=True)
            
            with st.expander("⚙️ Test Configuration", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📈 Test Data Source")
                    data_source = st.radio("Choose Data Source", ["Yahoo Finance", "CSV Upload"], label_visibility="collapsed", key="batch_data")
                    if data_source == "Yahoo Finance":
                        symbol = st.selectbox("Symbol", list(DataLoader.SYMBOLS.keys()), key="batch_symbol", label_visibility="collapsed", index=list(DataLoader.SYMBOLS.keys()).index("XAUUSD (Gold)"))
                        interval = st.select_slider("Timeframe", ["1m", "5m", "15m", "1h", "1d"], value="1h", key="batch_interval")
                        period = st.select_slider("Period", ["1d", "5d", "1mo", "3mo", "1y"], value="1mo", key="batch_period")
                        with st.spinner("📊 Loading data..."):
                            df = DataLoader.load_yfinance(symbol, interval, period)
                        st.success(f"✅ Loaded {len(df)} candles")
                    else:
                        test_csv = st.file_uploader("Upload Test Data CSV", type=['csv'], key="batch_test_csv", label_visibility="collapsed")
                        if test_csv:
                            with st.spinner("📊 Loading CSV..."):
                                df = DataLoader.load_csv(test_csv)
                            st.success(f"✅ Loaded {len(df)} candles")
                        else:
                            st.info("📌 Please upload test data CSV")
                            df = None
                
                with col2:
                    st.markdown("### 🎯 Strategy Selection")
                    strategy_name = st.selectbox("Choose Strategy", list(AVAILABLE_STRATEGIES.keys()), key="batch_strategy", label_visibility="collapsed")
                    strategy = get_strategy(strategy_name)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col3:
                run_batch = st.button("▶️ Run Batch Analysis", use_container_width=True)
            
            if run_batch and df is not None:
                with st.spinner("🔄 Running batch analysis..."):
                    rules_list = CSVRulesProcessor.parse_rules_csv(rules_df)
                    df_signals = strategy.generate_signals(df.copy())
                    
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, rules in enumerate(rules_list):
                        is_valid, msg = CSVRulesProcessor.validate_rules(rules)
                        if not is_valid:
                            results.append({
                                'Propfirm': rules['propfirm_name'],
                                'Status': '❌ Invalid',
                                'Message': msg,
                                'Trades': 0,
                                'Profit': 'N/A'
                            })
                            progress_bar.progress((idx + 1) / len(rules_list))
                            continue
                        
                        # Create rules object
                        from propfirm import PhaseRules
                        phase_rules = PhaseRules(
                            daily_loss_limit=rules['daily_loss_limit'],
                            max_loss_limit=rules['max_loss_limit'],
                            profit_target=rules['profit_target'],
                            min_trading_days=rules.get('min_trading_days', 1),
                            max_trades_per_day=rules.get('max_trades_per_day', 999)
                        )
                        
                        trades, equity, balance, fail_reason = run_backtest_phase(
                            df_signals.copy(), rules['account_size'], 1, phase_rules,
                            rules['stop_loss'], rules['take_profit'], rules['risk_percent']
                        )
                        
                        profit = balance - rules['account_size']
                        profit_pct = (profit / rules['account_size']) * 100
                        
                        if fail_reason:
                            results.append({
                                'Propfirm': rules['propfirm_name'],
                                'Status': '❌ Failed',
                                'Message': fail_reason,
                                'Trades': len(trades),
                                'Profit': f"${profit:,.2f}"
                            })
                        else:
                            results.append({
                                'Propfirm': rules['propfirm_name'],
                                'Status': '✅ Passed',
                                'Message': 'Challenge Completed',
                                'Trades': len(trades),
                                'Profit': f"${profit:,.2f} ({profit_pct:.2f}%)"
                            })
                        
                        progress_bar.progress((idx + 1) / len(rules_list))
                    
                    st.markdown("---")
                    st.markdown("## 📊 Batch Analysis Results")
                    
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                    
                    # Summary Stats
                    col1, col2, col3, col4 = st.columns(4)
                    passed = len([r for r in results if r['Status'] == '✅ Passed'])
                    failed = len([r for r in results if r['Status'] == '❌ Failed'])
                    invalid = len([r for r in results if r['Status'] == '❌ Invalid'])
                    
                    col1.metric("✅ Passed", passed)
                    col2.metric("❌ Failed", failed)
                    col3.metric("⚠️ Invalid", invalid)
                    col4.metric("📊 Total", len(results))
                    
                    # Download results
                    st.markdown("---")
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results CSV",
                        data=csv,
                        file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"Error processing CSV: {e}")
