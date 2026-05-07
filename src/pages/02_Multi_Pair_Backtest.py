"""
Demo: Multi-Pair Backtesting with Lot Size Tracking
Shows how to use the EnhancedBacktestRunner to backtest multiple forex pairs
with intelligent lot sizing and risk management per pair
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from hft.utils import DataLoader, EnhancedBacktestRunner
from hft.strategies import get_strategy
from propfirm.lot_size_calculator import PairConfig


def format_currency(value):
    """Format value as currency"""
    if value >= 0:
        return f"🟢 ${value:,.2f}"
    else:
        return f"🔴 -${abs(value):,.2f}"


def run_multi_pair_backtest():
    """
    Streamlit app for multi-pair backtesting with lot sizes
    """
    st.set_page_config(layout="wide", page_title="Multi-Pair Backtester with Lot Sizes")
    
    st.title("🌍 Multi-Pair Backtest with Lot Size Tracking")
    st.markdown("""
    Test your trading strategy across multiple forex pairs simultaneously.
    Each pair gets intelligent lot sizing based on pip values and risk management.
    """)
    
    # ==================== Configuration ====================
    with st.expander("⚙️ Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Strategy & Pairs")
            strategy_name = st.selectbox("Strategy", list(get_strategy.__globals__.get('AVAILABLE_STRATEGIES', {}).keys()) or ["XAUUSD Pro"])
            
            # Get available pairs from DataLoader
            all_pairs = list(DataLoader.SYMBOLS.keys())
            pairs = st.multiselect(
                "Select Pairs to Test",
                all_pairs,
                default=["XAUUSD (Gold)", "EURUSD", "USDJPY"],
                help="Choose forex pairs to backtest"
            )
        
        with col2:
            st.markdown("### 📈 Data & Trading")
            period = st.select_slider("Data Period", ["1d", "5d", "1mo", "3mo", "1y"], value="1mo")
            interval = st.select_slider("Timeframe", ["1m", "5m", "15m", "1h", "1d"], value="1h")
            
            sl_pips = st.number_input("Stop Loss (pips)", 1, 100, 10)
            tp_pips = st.number_input("Take Profit (pips)", 1, 200, 20)
        
        with col3:
            st.markdown("### 💰 Account")
            account_size = st.number_input("Account Size ($)", 1000, 1000000, 10000, step=1000)
            risk_pct = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0) / 100
            
            if pairs:
                st.markdown(f"### 📊 Selected Pairs: {len(pairs)}")
                for pair in pairs:
                    config = PairConfig.get_pair_config(pair)
                    pip_value = 1000 if 'JPY' in pair else 10
                    st.caption(f"• {pair} - Pip: {config.pip_size}, Value: ${pip_value}/pip")
    
    if not pairs:
        st.warning("Please select at least one pair")
        return
    
    st.markdown("---")
    
    # ==================== Run Backtest ====================
    if st.button("▶️ Run Multi-Pair Backtest", use_container_width=True):
        progress_bar = st.progress(0)
        results = {}
        
        for idx, pair in enumerate(pairs):
            progress_bar.progress((idx + idx*0.5) / (len(pairs) * 1.5))
            
            with st.spinner(f"📊 Backtesting {pair}..."):
                try:
                    # Load data for pair
                    symbol_key = pair  # Already has description
                    df = DataLoader.load_yfinance(symbol_key, interval, period)
                    
                    # Get strategy and generate signals
                    strategy = get_strategy(strategy_name)
                    df_with_signals = strategy.generate_signals(df.copy())
                    
                    # Run enhanced backtest with lot sizes
                    runner = EnhancedBacktestRunner(account_size, risk_pct, symbol_key)
                    backtest_result = runner.run_backtest_with_lots(df_with_signals, sl_pips, tp_pips)
                    
                    results[pair] = backtest_result
                    
                except Exception as e:
                    st.error(f"Error backtesting {pair}: {e}")
                    continue
            
            progress_bar.progress((idx + 1) / len(pairs))
        
        progress_bar.empty()
        
        if results:
            st.markdown("---")
            st.markdown("## 📊 Results Summary")
            
            # ==================== Summary Table ====================
            summary_data = []
            for pair, result in results.items():
                summary_data.append({
                    'Pair': pair,
                    'Trades': result['total_trades'],
                    'Win %': f"{result['win_rate']*100:.1f}%",
                    'Net Profit': f"${result['total_pnl']:,.2f}",
                    'Return %': f"{result['total_return_pct']:.2f}%",
                    'Max DD %': f"{result['max_drawdown']*100:.2f}%",
                    'Avg Lot': f"{result['avg_lot_size']:.2f}",
                    'Final Balance': f"${result['final_balance']:,.2f}"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # ==================== Detailed Tabs ====================
            tabs = st.tabs([f"📈 {pair}" for pair in results.keys()] + ["🏆 Comparison", "📋 Trade Details"])
            
            for idx, pair in enumerate(results.keys()):
                with tabs[idx]:
                    backtest_result = results[pair]
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Trades", backtest_result['total_trades'])
                    col2.metric("Win Rate", f"{backtest_result['win_rate']*100:.1f}%")
                    col3.metric("Net Profit", f"${backtest_result['total_pnl']:,.2f}")
                    col4.metric("Return", f"{backtest_result['total_return_pct']:.2f}%")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Max Drawdown", f"{backtest_result['max_drawdown']*100:.2f}%")
                    col2.metric("Avg Lot Size", f"{backtest_result['avg_lot_size']:.2f}")
                    col3.metric("Max Lot", f"{backtest_result['max_lot_size']:.2f}")
                    col4.metric("Min Lot", f"{backtest_result['min_lot_size']:.2f}")
                    
                    # Equity Curve
                    st.markdown("### 📈 Equity Curve")
                    fig, ax = plt.subplots(figsize=(14, 6))
                    ax.plot(backtest_result['equity_curve'], linewidth=2.5, label='Equity', color='#1f77b4')
                    ax.axhline(y=account_size, color='green', linestyle='--', alpha=0.5, label='Starting Balance')
                    ax.fill_between(range(len(backtest_result['equity_curve'])), account_size, backtest_result['equity_curve'],
                                  where=(np.array(backtest_result['equity_curve']) >= account_size), alpha=0.2, color='green')
                    ax.fill_between(range(len(backtest_result['equity_curve'])), account_size, backtest_result['equity_curve'],
                                  where=(np.array(backtest_result['equity_curve']) < account_size), alpha=0.2, color='red')
                    ax.set_xlabel('Candles')
                    ax.set_ylabel('Balance ($)')
                    ax.set_title(f'{pair} - Equity Curve')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    
                    # Trade Details
                    st.markdown("### 📋 Recent Trades")
                    if backtest_result['trades']:
                        trades_df = backtest_result['trades_df'].copy()
                        display_cols = ['trade_num', 'type', 'entry_price', 'exit_price', 'lot_size', 'pnl_amount', 'pnl_pct', 'exit_reason']
                        if all(col in trades_df.columns for col in display_cols):
                            display_df = trades_df[display_cols].copy()
                            display_df.columns = ['#', 'Type', 'Entry', 'Exit', 'Lots', 'P&L', 'P&L%', 'Reason']
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No trades executed")
            
            # Comparison Tab
            with tabs[-2]:
                st.markdown("### 🏆 Pair Performance Comparison")
                
                # Equity curves comparison
                fig, ax = plt.subplots(figsize=(14, 6))
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                for idx, (pair, result) in enumerate(results.items()):
                    ax.plot(result['equity_curve'], linewidth=2, label=pair, color=colors[idx % len(colors)])
                ax.axhline(y=account_size, color='gray', linestyle='--', alpha=0.5)
                ax.set_xlabel('Candles')
                ax.set_ylabel('Balance ($)')
                ax.set_title('All Pairs - Equity Curves')
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
                
                # Performance ranking
                st.markdown("### 📊 Ranking by Net Profit")
                ranked = sorted(results.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
                for rank, (pair, result) in enumerate(ranked, 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
                    col1, col2, col3, col4, col5 = st.columns([0.5, 2, 1.5, 1.5, 1.5])
                    with col1:
                        st.write(medal)
                    with col2:
                        st.write(f"**{pair}**")
                    with col3:
                        st.write(f"${result['total_pnl']:,.2f}")
                    with col4:
                        st.write(f"{result['total_return_pct']:.2f}%")
                    with col5:
                        st.write(f"Win: {result['win_rate']*100:.1f}%")
            
            # Trade Details Tab
            with tabs[-1]:
                st.markdown("### 📋 Detailed Trade Analysis")
                selected_pair = st.selectbox("Select Pair for Details", list(results.keys()))
                
                if selected_pair in results:
                    backtest_result = results[selected_pair]
                    trades_df = backtest_result['trades_df']
                    
                    st.markdown(f"**{selected_pair}** - {len(trades_df)} Total Trades")
                    
                    # Show all trades
                    if not trades_df.empty:
                        st.dataframe(trades_df, use_container_width=True, height=400)
                        
                        # Download option
                        csv = trades_df.to_csv(index=False)
                        st.download_button(
                            "📥 Download Trades CSV",
                            csv,
                            f"{selected_pair}_trades.csv",
                            "text/csv"
                        )
                    else:
                        st.info("No trades for this pair")


if __name__ == "__main__":
    run_multi_pair_backtest()
