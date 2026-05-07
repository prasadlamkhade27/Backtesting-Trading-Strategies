"""
Strategy Builder Page - Clean UI Version
Allows users to create, test, and backtest trading strategies
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-2]))

from hft.utils.strategy_builder import StrategyBuilder, BacktestRunner
from hft.utils import DataLoader
from hft.strategies import AVAILABLE_STRATEGIES

# ====================== PAGE CONFIG ======================
st.set_page_config(layout="wide", page_title="Strategy Builder", initial_sidebar_state="expanded")

# ====================== CUSTOM STYLING ======================
st.markdown("""
<style>
    /* Main variables */
    :root {
        --primary: #2563EB;
        --primary-light: #3B82F6;
        --primary-dark: #1E40AF;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --bg: #0F172A;
        --bg-card: #1E293B;
        --border: #334155;
        --text: #F1F5F9;
        --text-muted: #94A3B8;
    }
    
    /* Main container */
    .main {
        background-color: var(--bg);
        padding: 20px;
    }
    
    /* Clean cards */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: var(--text);
        font-weight: 600;
    }
    
    h1 {
        font-size: 32px;
        margin-bottom: 8px;
    }
    
    h2 {
        font-size: 24px;
        margin-top: 20px;
        margin-bottom: 16px;
        color: var(--primary-light);
    }
    
    h3 {
        font-size: 18px;
        margin-top: 16px;
        color: var(--text);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.4);
    }
    
    /* Tabs */
    [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    [data-baseweb="tab"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-muted);
        padding: 12px 16px;
    }
    
    [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
        border-color: var(--primary) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background: var(--bg-card);
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px;
        padding: 10px 12px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        padding: 16px;
    }
    
    [data-testid="stSuccess"] {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid var(--success) !important;
        color: var(--success) !important;
    }
    
    [data-testid="stError"] {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid var(--error) !important;
        color: var(--error) !important;
    }
    
    [data-testid="stInfo"] {
        background: rgba(37, 99, 235, 0.1) !important;
        border: 1px solid var(--primary) !important;
        color: var(--primary-light) !important;
    }
    
    [data-testid="stWarning"] {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid var(--warning) !important;
        color: var(--warning) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-card);
    }
    
    /* Metric */
    .metric-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ====================== TITLE ======================
st.markdown("# 🚀 Strategy Builder")
st.markdown("**Create, test, and backtest your trading strategies**")
st.markdown("---")

# ====================== MODE SELECTION IN SIDEBAR ======================
st.sidebar.markdown("## 📊 Builder Modes")
builder_mode = st.sidebar.radio(
    "Select Mode",
    ["📈 Available Strategies", "✍️ Create Strategy", "🔬 Test Strategy", "💹 Backtest"],
    label_visibility="collapsed"
)

builder = StrategyBuilder()

# ====================== MODE 1: AVAILABLE STRATEGIES ======================
if builder_mode == "📈 Available Strategies":
    st.markdown("## Available Strategies")
    st.markdown("Active strategies in your system")
    
    if AVAILABLE_STRATEGIES:
        cols = st.columns(len(AVAILABLE_STRATEGIES))
        for idx, (strategy_name, strategy_class) in enumerate(AVAILABLE_STRATEGIES.items()):
            with cols[idx]:
                st.markdown(f"""
                <div class="card">
                    <h3 style="margin: 0 0 8px 0;">📊 {strategy_name}</h3>
                    <p style="margin: 0; color: var(--text-muted); font-size: 14px;">
                        {strategy_class.__name__}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No strategies loaded")

# ====================== MODE 2: CREATE STRATEGY ======================
elif builder_mode == "✍️ Create Strategy":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Strategy Details")
        strategy_name = st.text_input("Strategy Name", placeholder="e.g., My First Strategy", label_visibility="collapsed")
        strategy_description = st.text_area("Description", placeholder="Describe your strategy...", height=80, label_visibility="collapsed")
    
    with col2:
        st.markdown("### Template")
        template_type = st.selectbox(
            "Choose Template",
            ["Simple Moving Average", "Empty Template"],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    st.markdown("### Strategy Code")
    
    if template_type == "Simple Moving Average":
        default_code = builder.load_strategy_template()
    else:
        default_code = """import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class UserStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Your logic here
        return df
"""
    
    strategy_code = st.text_area("", value=default_code, height=300, label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Validate Code"):
            valid, message = builder.validate_strategy_code(strategy_code)
            if valid:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        if st.button("💾 Save Strategy"):
            if not strategy_name:
                st.error("Enter a strategy name")
            else:
                valid, msg = builder.validate_strategy_code(strategy_code)
                if valid:
                    success, message = builder.save_strategy_code(strategy_name, strategy_code)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error(f"Invalid code: {msg}")
    
    with col3:
        if st.button("📋 Load Template"):
            st.info("Template loaded above!")

# ====================== MODE 3: TEST STRATEGY ======================
elif builder_mode == "🔬 Test Strategy":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Select Strategy**")
        selected_strategy = st.selectbox(
            "Strategy",
            list(AVAILABLE_STRATEGIES.keys()),
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**Asset Symbol**")
        symbol = st.selectbox(
            "Symbol",
            ["EURUSD", "GBPUSD", "XAUUSD", "USDJPY"],
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("**Timeframe**")
        timeframe = st.selectbox(
            "TF",
            ["1h", "4h", "D", "W"],
            label_visibility="collapsed"
        )
    
    if st.button("📊 Load & Preview Data", use_container_width=True):
        try:
            days_back = {"1h": 30, "4h": 60, "D": 180, "W": 365}[timeframe]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            dates = pd.date_range(start=start_date, end=end_date, freq=timeframe)
            
            np.random.seed(42)
            prices = 100 * np.exp(np.cumsum(np.random.randn(len(dates)) * 0.01))
            
            df_preview = pd.DataFrame({
                'timestamp': dates,
                'open': prices + np.random.randn(len(prices)) * 0.5,
                'high': prices + abs(np.random.randn(len(prices)) * 1),
                'low': prices - abs(np.random.randn(len(prices)) * 1),
                'close': prices,
                'volume': np.random.randint(1000000, 5000000, len(prices))
            })
            
            st.success("✅ Data loaded successfully!")
            st.dataframe(df_preview.tail(15), use_container_width=True)
            st.session_state.test_data = df_preview
            st.session_state.selected_strategy = selected_strategy
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ====================== MODE 4: BACKTEST STRATEGY ======================
elif builder_mode == "💹 Backtest":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Strategy**")
        selected_strategy = st.selectbox(
            "Select",
            list(AVAILABLE_STRATEGIES.keys()),
            label_visibility="collapsed",
            key="bt_strategy"
        )
    
    with col2:
        st.markdown("**Capital**")
        initial_capital = st.number_input(
            "USD",
            value=10000,
            min_value=1000,
            step=1000,
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("**Position Size**")
        position_size = st.slider(
            "%",
            0.1, 100.0, 95.0,
            label_visibility="collapsed"
        ) / 100.0
    
    with col4:
        st.markdown("**Days Back**")
        days_back = st.number_input(
            "Days",
            value=180,
            min_value=30,
            step=30,
            label_visibility="collapsed"
        )
    
    if st.button("▶️ Run Backtest", use_container_width=True):
        try:
            with st.spinner("Running backtest..."):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                dates = pd.date_range(start=start_date, end=end_date, freq='1D')
                
                np.random.seed(42)
                prices = 1.0 * np.exp(np.cumsum(np.random.randn(len(dates)) * 0.01))
                
                df_data = pd.DataFrame({
                    'timestamp': dates,
                    'open': prices + np.random.randn(len(prices)) * 0.001,
                    'high': prices + abs(np.random.randn(len(prices)) * 0.002),
                    'low': prices - abs(np.random.randn(len(prices)) * 0.002),
                    'close': prices,
                    'volume': np.random.randint(1000000, 5000000, len(prices))
                })
                
                strategy_class = AVAILABLE_STRATEGIES[selected_strategy]
                strategy = strategy_class()
                
                results = BacktestRunner.run_backtest(
                    df_data,
                    strategy,
                    initial_capital=initial_capital,
                    position_size=position_size
                )
                
                if results['success']:
                    st.success("✅ Backtest completed!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Return",
                            f"{results['total_return']*100:.2f}%",
                        )
                    
                    with col2:
                        st.metric(
                            "Max DD",
                            f"{results['max_drawdown']*100:.2f}%",
                        )
                    
                    with col3:
                        st.metric(
                            "Sharpe",
                            f"{results['sharpe_ratio']:.2f}",
                        )
                    
                    with col4:
                        st.metric(
                            "Win Rate",
                            f"{results['win_rate']*100:.2f}%",
                        )
                    
                    if 'equity_curve' in results:
                        fig, ax = plt.subplots(figsize=(12, 4))
                        df_equity = results['equity_curve']
                        
                        ax.plot(df_equity.index, df_equity['equity'], linewidth=2, color='#2563EB', label='Equity')
                        ax.fill_between(df_equity.index, initial_capital, df_equity['equity'], alpha=0.2, color='#2563EB')
                        ax.axhline(y=initial_capital, color='#94A3B8', linestyle='--', linewidth=1, label='Initial')
                        
                        ax.set_facecolor('#0F172A')
                        fig.patch.set_facecolor('#0F172A')
                        ax.grid(True, alpha=0.1, color='white')
                        ax.set_xlabel('Date', color='#F1F5F9')
                        ax.set_ylabel('Equity ($)', color='#F1F5F9')
                        ax.tick_params(colors='#F1F5F9')
                        ax.spines['bottom'].set_color('#334155')
                        ax.spines['left'].set_color('#334155')
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        
                        st.pyplot(fig)
                else:
                    st.error(f"Backtest failed: {results['message']}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 40px;">
    🚀 Strategy Builder | Design. Test. Trade.
</div>
""", unsafe_allow_html=True)
