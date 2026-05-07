"""
High-Frequency Trading (HFT) Scalping Strategy for Backtesting
Implements multiple HFT strategies: Scalping, Market Making, Trend Following

This module provides a Python version of the MT5 HFT EA that can be used
for backtesting historical data and optimizing parameters.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from hft.strategies.base_strategy import BaseStrategy


class HFTScalpingStrategy(BaseStrategy):
    """
    High-Frequency Trading Scalping Strategy
    
    Executes multiple small trades capturing bid-ask spreads and
    quick momentum moves. Optimized for rapid entry/exit with tight stops.
    """
    
    def __init__(
        self,
        strategy_type: str = "scalping",  # scalping, market_making, trend_following
        ma_fast: int = 5,
        ma_slow: int = 20,
        rsi_period: int = 14,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70,
        atr_period: int = 14,
        atr_sl_multiple: float = 1.5,
        atr_tp_multiple: float = 0.75,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9
    ):
        """
        Initialize HFT Scalping Strategy
        
        Args:
            strategy_type: Type of HFT strategy (scalping, market_making, trend_following)
            ma_fast: Fast moving average period (short-term trend)
            ma_slow: Slow moving average period (long-term trend)
            rsi_period: RSI indicator period
            rsi_oversold: RSI oversold threshold (0-100)
            rsi_overbought: RSI overbought threshold (0-100)
            atr_period: Average True Range period for volatility
            atr_sl_multiple: Stop loss multiplier of ATR
            atr_tp_multiple: Take profit multiplier of ATR
            macd_fast: MACD fast EMA period
            macd_slow: MACD slow EMA period
            macd_signal: MACD signal line period
        """
        description = f"HFT {strategy_type.capitalize()}: MA({ma_fast}x{ma_slow}) RSI({rsi_period})"
        super().__init__(
            name=f"HFT {strategy_type.capitalize()}",
            description=description
        )
        
        # Strategy configuration
        self.strategy_type = strategy_type.lower()
        
        # Technical indicators parameters
        self.ma_fast = ma_fast
        self.ma_slow = ma_slow
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.atr_period = atr_period
        self.atr_sl_multiple = atr_sl_multiple
        self.atr_tp_multiple = atr_tp_multiple
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        
        # Performance tracking
        self.trades_executed = []
        self.signals_generated = []
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate HFT trading signals
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with BUY/SELL signals and technical indicators
        """
        df = df.copy()
        
        # Calculate technical indicators
        df = self._calculate_indicators(df)
        
        # Generate signals based on strategy type
        if self.strategy_type == "scalping":
            df = self._generate_scalping_signals(df)
        elif self.strategy_type == "market_making":
            df = self._generate_market_making_signals(df)
        elif self.strategy_type == "trend_following":
            df = self._generate_trend_following_signals(df)
        else:
            df['BUY'] = False
            df['SELL'] = False
        
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        
        # Moving Averages (EMA for responsiveness)
        df['ma_fast'] = self._calculate_ema(df['close'], self.ma_fast)
        df['ma_slow'] = self._calculate_ema(df['close'], self.ma_slow)
        
        # RSI (Momentum)
        df['rsi'] = self._calculate_rsi(df['close'], self.rsi_period)
        
        # ATR (Volatility)
        df['atr'] = self._calculate_atr(df, self.atr_period)
        
        # MACD (Trend and Momentum)
        df['macd'], df['macd_signal'], df['macd_hist'] = self._calculate_macd(
            df['close'],
            self.macd_fast,
            self.macd_slow,
            self.macd_signal
        )
        
        # Bid-Ask Spread simulation (based on volatility)
        df['spread'] = df['atr'] * 0.2  # Spread = 0.2 * ATR
        
        # Volume confirmation
        df['volume_ma'] = df['volume'].rolling(self.ma_fast).mean()
        
        return df
    
    def _generate_scalping_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scalping Strategy: Tight entry/exit capturing small moves
        
        Rules:
        - BUY: Fast MA > Slow MA + RSI > 50 (not overbought) + MACD > 0
        - SELL: Fast MA < Slow MA + RSI < 50 (not oversold) + MACD < 0
        """
        
        df['BUY'] = False
        df['SELL'] = False
        
        for i in range(1, len(df)):
            # Buy conditions (uptrend +momentum without overbought)
            if (df['ma_fast'].iloc[i] > df['ma_slow'].iloc[i] and
                df['rsi'].iloc[i] > 50 and
                df['rsi'].iloc[i] < self.rsi_overbought and
                df['macd'].iloc[i] > 0 and
                df['volume'].iloc[i] > df['volume_ma'].iloc[i] * 1.2):
                
                # Only signal on crossover
                if (df['ma_fast'].iloc[i-1] <= df['ma_slow'].iloc[i-1] or
                    df['rsi'].iloc[i-1] <= 50):
                    df.loc[df.index[i], 'BUY'] = True
            
            # Sell conditions (downtrend + momentum without oversold)
            if (df['ma_fast'].iloc[i] < df['ma_slow'].iloc[i] and
                df['rsi'].iloc[i] < 50 and
                df['rsi'].iloc[i] > self.rsi_oversold and
                df['macd'].iloc[i] < 0 and
                df['volume'].iloc[i] > df['volume_ma'].iloc[i] * 1.2):
                
                # Only signal on crossover
                if (df['ma_fast'].iloc[i-1] >= df['ma_slow'].iloc[i-1] or
                    df['rsi'].iloc[i-1] >= 50):
                    df.loc[df.index[i], 'SELL'] = True
        
        df['signal_type'] = 'scalping'
        return df
    
    def _generate_market_making_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Market Making Strategy: Place orders on both sides
        
        Rules:
        - BUY: Price near support + favorable spread
        - SELL: Price near resistance + favorable spread
        """
        
        df['BUY'] = False
        df['SELL'] = False
        
        for i in range(1, len(df)):
            # Identify support/resistance using moving averages
            price = df['close'].iloc[i]
            ma_fast = df['ma_fast'].iloc[i]
            ma_slow = df['ma_slow'].iloc[i]
            spread = df['spread'].iloc[i]
            atr = df['atr'].iloc[i]
            
            # Support level (price pulling back to fast MA)
            if (price > ma_slow and  # In uptrend
                abs(price - ma_fast) < atr * 0.5 and  # Near fast MA
                spread < atr * 2):  # Good spread
                df.loc[df.index[i], 'BUY'] = True
            
            # Resistance level (price pulling back to fast MA)
            if (price < ma_slow and  # In downtrend
                abs(price - ma_fast) < atr * 0.5 and  # Near fast MA
                spread < atr * 2):  # Good spread
                df.loc[df.index[i], 'SELL'] = True
        
        df['signal_type'] = 'market_making'
        return df
    
    def _generate_trend_following_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trend Following Strategy: Rapid trend capture
        
        Rules:
        - BUY: Strong uptrend (Price > Fast MA > Slow MA) + RSI > 50
        - SELL: Strong downtrend (Price < Fast MA < Slow MA) + RSI < 50
        """
        
        df['BUY'] = False
        df['SELL'] = False
        
        for i in range(1, len(df)):
            price = df['close'].iloc[i]
            ma_fast = df['ma_fast'].iloc[i]
            ma_slow = df['ma_slow'].iloc[i]
            rsi = df['rsi'].iloc[i]
            
            # Strong uptrend with momentum
            if (price > ma_fast > ma_slow and
                rsi > 50 and
                df['macd'].iloc[i] > 0):
                df.loc[df.index[i], 'BUY'] = True
            
            # Strong downtrend with momentum
            if (price < ma_fast < ma_slow and
                rsi < 50 and
                df['macd'].iloc[i] < 0):
                df.loc[df.index[i], 'SELL'] = True
        
        df['signal_type'] = 'trend_following'
        return df
    
    # Technical Indicator Calculations
    
    @staticmethod
    def _calculate_ema(series: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def _calculate_rsi(series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        """
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Average True Range
        
        TR = max(High - Low, abs(High - Close[prev]), abs(Low - Close[prev]))
        """
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def _calculate_macd(
        series: pd.Series,
        fast: int,
        slow: int,
        signal: int
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        MACD = EMA(fast) - EMA(slow)
        Signal = EMA(MACD, signal)
        Histogram = MACD - Signal
        """
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd - macd_signal
        
        return macd, macd_signal, macd_histogram
    
    def get_parameters(self) -> dict:
        """Return strategy parameters for documentation"""
        return {
            'strategy': self.name,
            'strategy_type': self.strategy_type,
            'ma_fast': self.ma_fast,
            'ma_slow': self.ma_slow,
            'rsi_period': self.rsi_period,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'atr_period': self.atr_period,
            'atr_sl_multiple': self.atr_sl_multiple,
            'atr_tp_multiple': self.atr_tp_multiple,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
        }
    
    def get_trade_statistics(self) -> dict:
        """Return trading statistics"""
        return {
            'trades_executed': len(self.trades_executed),
            'total_pnl': sum(t.get('pnl', 0) for t in self.trades_executed),
            'winning_trades': len([t for t in self.trades_executed if t.get('pnl', 0) > 0]),
            'losing_trades': len([t for t in self.trades_executed if t.get('pnl', 0) < 0]),
        }
    
    def __repr__(self):
        return f"{self.name} ({self.strategy_type}): MA({self.ma_fast}x{self.ma_slow}) RSI({self.rsi_period})"


# Additional HFT-specific helpers

class HFTRiskManager:
    """
    Risk Management for High-Frequency Trading
    Handles position sizing, stop loss/take profit, and risk limits
    """
    
    def __init__(
        self,
        initial_balance: float,
        risk_percent_per_trade: float = 0.5,
        max_consecutive_losses: int = 5,
        max_daily_loss_percent: float = 5.0,
        atr_sl_multiple: float = 1.5,
        atr_tp_multiple: float = 0.75
    ):
        """
        Initialize HFT Risk Manager
        
        Args:
            initial_balance: Starting account balance
            risk_percent_per_trade: Risk as % of balance per trade
            max_consecutive_losses: Stop trading after N losing trades
            max_daily_loss_percent: Stop trading if daily loss exceeds this %
            atr_sl_multiple: Stop loss distance in ATR multiples
            atr_tp_multiple: Take profit distance in ATR multiples
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_percent_per_trade = risk_percent_per_trade
        self.max_consecutive_losses = max_consecutive_losses
        self.max_daily_loss_percent = max_daily_loss_percent
        self.atr_sl_multiple = atr_sl_multiple
        self.atr_tp_multiple = atr_tp_multiple
        
        # Tracking
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.daily_loss_limit = initial_balance * (max_daily_loss_percent / 100.0)
    
    def calculate_lot_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        account_balance: float
    ) -> float:
        """
        Calculate position size based on risk management rules
        
        Position Size = (Risk Amount) / (Loss per Pip × Pip Value)
        """
        risk_amount = account_balance * (self.risk_percent_per_trade / 100.0)
        
        # Calculate loss per pip
        loss_per_pip = abs(entry_price - stop_loss_price)
        
        if loss_per_pip == 0:
            return 0.01  # Minimum position
        
        lot_size = risk_amount / (loss_per_pip * 100000)  # Assuming 5-digit quote
        
        return max(0.01, min(lot_size, 10.0))  # Between 0.01 and 10.0 lots
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        is_long: bool
    ) -> float:
        """Calculate stop loss based on ATR"""
        if is_long:
            return entry_price - (atr * self.atr_sl_multiple)
        else:
            return entry_price + (atr * self.atr_sl_multiple)
    
    def calculate_take_profit(
        self,
        entry_price: float,
        atr: float,
        is_long: bool
    ) -> float:
        """Calculate take profit based on ATR"""
        if is_long:
            return entry_price + (atr * self.atr_tp_multiple)
        else:
            return entry_price - (atr * self.atr_tp_multiple)
    
    def check_daily_loss_limit(self, current_pnl: float) -> bool:
        """Check if daily loss limit has been exceeded"""
        return abs(current_pnl) > self.daily_loss_limit
    
    def check_consecutive_losses(self) -> bool:
        """Check if consecutive loss limit has been reached"""
        return self.consecutive_losses >= self.max_consecutive_losses
    
    def update_after_trade(self, pnl: float):
        """Update risk manager after a trade"""
        self.current_balance += pnl
        self.daily_pnl += pnl
        
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0


class HFTPerformanceAnalyzer:
    """
    Analyzes HFT strategy performance metrics
    """
    
    @staticmethod
    def calculate_metrics(trades_list: List[Dict]) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades_list: List of executed trades with entry/exit prices
            
        Returns:
            Dictionary with performance metrics
        """
        if not trades_list:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'total_pnl': 0.0,
                'profit_factor': 0.0,
                'consecutive_wins': 0,
                'consecutive_losses': 0,
            }
        
        total_trades = len(trades_list)
        winning_trades = len([t for t in trades_list if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in trades_list if t.get('pnl', 0) < 0])
        
        total_pnl = sum(t.get('pnl', 0) for t in trades_list)
        wins = [t.get('pnl', 0) for t in trades_list if t.get('pnl', 0) > 0]
        losses = [t.get('pnl', 0) for t in trades_list if t.get('pnl', 0) < 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        profit_factor = abs(sum(wins) / sum(losses)) if losses else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_pnl': total_pnl,
            'profit_factor': profit_factor,
            'consecutive_wins': HFTPerformanceAnalyzer._calc_consecutive(trades_list, True),
            'consecutive_losses': HFTPerformanceAnalyzer._calc_consecutive(trades_list, False),
        }
    
    @staticmethod
    def _calc_consecutive(trades_list: List[Dict], is_winning: bool) -> int:
        """Calculate longest consecutive wins or losses"""
        max_streak = 0
        current_streak = 0
        
        for trade in trades_list:
            pnl = trade.get('pnl', 0)
            is_win = pnl > 0
            
            if is_win == is_winning:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak


# ====================== HOW TO USE THIS ======================
# 1. Add this to strategies/__init__.py:
#
#    from strategies.hft_scalping_strategy import HFTScalpingStrategy, HFTRiskManager, HFTPerformanceAnalyzer
#
# 2. Basic usage:
#
#    strategy = HFTScalpingStrategy(strategy_type="scalping")
#    df = strategy.generate_signals(your_data)
#
# 3. Backtesting with risk management:
#
#    risk_mgr = HFTRiskManager(initial_balance=10000, risk_percent_per_trade=0.5)
#    analyzer = HFTPerformanceAnalyzer()
#
# 4. Different strategy types:
#    - "scalping": Tight spreads, rapid trades
#    - "market_making": Two-sided orders
#    - "trend_following": Momentum capture
#
# See /pages/04_Futures_Backtest.py for full example integration
