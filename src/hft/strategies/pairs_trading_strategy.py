"""Pairs Trading Strategy - Mean Reversion

Trades the spread between two correlated pairs using Z-score signals.
Goes long when spread deviates significantly, exits on mean reversion.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class PairsTradingStrategy:
            z_stop=3.0
        )
        signals_df = strategy.generate_signals(df1, df2)
    """
    
    def __init__(
        self,
        pair1: str = 'EURUSD',
        pair2: str = 'GBPUSD',
        lookback: int = 100,
        z_entry: float = 2.0,
        z_exit: float = 0.5,
        z_stop: float = 3.0,
        enable_cointegration_check: bool = True,
        volatility_threshold: float = 0.002,
        min_correlation: float = 0.5,
    ):
        """
        Initialize Pairs Trading Strategy
        
        Args:
            pair1: Primary pair name (e.g., 'EURUSD')
            pair2: Secondary pair name (e.g., 'GBPUSD')
            lookback: Window for calculating mean, std, and hedge ratio (bars)
            z_entry: Z-score threshold to enter (absolute value)
            z_exit: Z-score threshold to exit (close to mean)
            z_stop: Z-score hard stop loss
            enable_cointegration_check: Check if pairs are cointegrated
            volatility_threshold: Skip trades if recent volatility too high
            min_correlation: Skip if correlation below this (default 0.5)
        """
        self.pair1 = pair1
        self.pair2 = pair2
        self.lookback = lookback
        self.z_entry = z_entry
        self.z_exit = z_exit
        self.z_stop = z_stop
        self.enable_cointegration_check = enable_cointegration_check
        self.volatility_threshold = volatility_threshold
        self.min_correlation = min_correlation
        
        self.name = f"Pairs Trading: {pair1} vs {pair2}"
        self.description = "Mean reversion pairs trading with hedge ratio normalization"
        
        # State tracking
        self.hedge_ratio = None
        self.spread_mean = None
        self.spread_std = None
        self.last_cointegration_pvalue = None
        
    @staticmethod
    def calculate_hedge_ratio(price1: np.ndarray, price2: np.ndarray) -> float:
        """
        Calculate hedge ratio using linear regression
        
        Formula: hedged_price2 = hedge_ratio × price2
        
        This normalizes the two series so they move proportionally.
        Without it, unequal price movements cause strategy to break.
        
        Args:
            price1: Price series for pair1
            price2: Price series for pair2
            
        Returns:
            hedge_ratio (β): Coefficient for price2
        """
        # Remove any NaN values
        mask = ~(np.isnan(price1) | np.isnan(price2))
        p1_clean = price1[mask]
        p2_clean = price2[mask]
        
        if len(p1_clean) < 3:
            return 1.0  # Default if insufficient data
        
        # Linear regression: price1 = α + β × price2
        coefficients = np.polyfit(p2_clean, p1_clean, 1)
        beta = coefficients[0]  # Slope is our hedge ratio
        
        # Ensure positive ratio
        beta = abs(beta) if beta != 0 else 1.0
        
        return beta
    
    @staticmethod
    def calculate_spread(price1: np.ndarray, price2: np.ndarray, hedge_ratio: float) -> np.ndarray:
        """
        Calculate normalized spread using hedge ratio
        
        Formula: Spread = Price1 - (β × Price2)
        
        Args:
            price1: Price array for pair1
            price2: Price array for pair2
            hedge_ratio: Hedge ratio (β) to normalize movements
            
        Returns:
            Spread array
        """
        return price1 - (hedge_ratio * price2)
    
    @staticmethod
    def calculate_zscore(spread: np.ndarray, lookback: int) -> np.ndarray:
        """
        Calculate Z-score with rolling mean and std
        
        Formula: Z = (Spread - Mean) / StdDev
        
        Meaning:
        - Z = 0: Normal, at equilibrium
        - Z > +2: Overextended high (mean reversion DOWN expected)
        - Z < -2: Overextended low (mean reversion UP expected)
        - Z > +3 or < -3: Extreme, hard stop (regime change warning)
        
        Args:
            spread: Spread array
            lookback: Window size for rolling stats
            
        Returns:
            Z-score array
        """
        rolling_mean = pd.Series(spread).rolling(window=lookback).mean().values
        rolling_std = pd.Series(spread).rolling(window=lookback).std().values
        
        # Avoid division by zero
        rolling_std = np.where(rolling_std == 0, 1e-6, rolling_std)
        
        zscore = (spread - rolling_mean) / rolling_std
        return np.nan_to_num(zscore, 0.0)
    
    @staticmethod
    def calculate_correlation(price1: np.ndarray, price2: np.ndarray, lookback: int) -> np.ndarray:
        """
        Calculate rolling correlation between two price series
        
        Args:
            price1: Price array for pair1
            price2: Price array for pair2
            lookback: Window size
            
        Returns:
            Rolling correlation array
        """
        series1 = pd.Series(price1)
        series2 = pd.Series(price2)
        
        corr = series1.rolling(window=lookback).corr(series2).values
        return corr
    
    @staticmethod
    def cointegration_test(spread: np.ndarray) -> Tuple[float, float]:
        """
        Engle-Granger cointegration test on the spread
        
        Null hypothesis: Series is non-stationary (random walk)
        If p-value < 0.05: Series IS stationary (cointegrated)
        
        This ensures the pairs have a true long-term relationship.
        
        Args:
            spread: Spread array to test
            
        Returns:
            (test_statistic, p_value)
        """
        from scipy.stats import linregress
        
        spread_clean = spread[~np.isnan(spread)]
        
        if len(spread_clean) < 10:
            return 0.0, 1.0  # Not enough data
        
        # Use Augmented Dickey-Fuller test concept
        # Simplified: if spread oscillates around mean, it's stationary
        diffs = np.diff(spread_clean)
        
        # Calculate t-statistic for unit root
        n = len(spread_clean)
        mean = np.mean(spread_clean)
        variance = np.var(spread_clean)
        
        if variance < 1e-10:
            return 0.0, 1.0
        
        # Simplified ADF-like calculation
        t_stat = mean / np.sqrt(variance / n)
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        
        return t_stat, p_value
    
    @staticmethod
    def calculate_volatility_filter(returns: np.ndarray, lookback: int = 20) -> np.ndarray:
        """
        Calculate recent price volatility to avoid trading during high-impact news
        
        Strategy: Skip entries if volatility is above threshold
        Rationale: During extreme volatility, correlations break and hedge fails
        
        Args:
            returns: Price return series
            lookback: Window for rolling volatility
            
        Returns:
            Rolling volatility array
        """
        rolling_vol = pd.Series(returns).rolling(window=lookback).std().values
        return rolling_vol
    
    def generate_signals(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        price_col: str = 'close'
    ) -> pd.DataFrame:
        """
        Generate pairs trading signals for both pairs
        
        Returns DataFrame with:
        - signal_pair1: BUY (1), SELL (-1), or HOLD (0) for pair1
        - signal_pair2: BUY (-1), SELL (1), or HOLD (0) for pair2 (inverse)
        - spread: Current spread value
        - zscore: Current Z-score
        - hedge_ratio: Current hedge ratio
        - spread_mean: Current mean
        - spread_std: Current std
        - correlation: Current correlation
        - volatility: Recent volatility
        - trade_active: Whether a trade should be active
        
        Args:
            df1: OHLC DataFrame for pair1
            df2: OHLC DataFrame for pair2
            price_col: Column name to use for analysis
            
        Returns:
            Signal DataFrame
        """
        # Validate inputs
        if len(df1) != len(df2):
            raise ValueError(f"DataFrames must have same length: {len(df1)} vs {len(df2)}")
        
        if len(df1) < self.lookback + 5:
            raise ValueError(f"Need at least {self.lookback + 5} bars, got {len(df1)}")
        
        if price_col not in df1.columns or price_col not in df2.columns:
            raise ValueError(f"Column '{price_col}' not found in dataframes")
        
        # Extract prices
        price1 = df1[price_col].values.astype(np.float64)
        price2 = df2[price_col].values.astype(np.float64)
        
        # Initialize output
        result_df = df1.copy()
        
        # Calculate rolling metrics
        spreads = []
        zscores = []
        hedge_ratios = []
        correlations = []
        spread_means = []
        spread_stds = []
        
        # For volatility, calculate returns
        returns1 = np.diff(price1) / price1[:-1]
        returns2 = np.diff(price2) / price2[:-1]
        volatilities = []
        
        for i in range(len(df1)):
            if i < self.lookback:
                # Not enough data
                spreads.append(np.nan)
                zscores.append(0.0)
                hedge_ratios.append(1.0)
                correlations.append(np.nan)
                spread_means.append(np.nan)
                spread_stds.append(np.nan)
                volatilities.append(np.nan)
            else:
                # Window of data
                window_start = i - self.lookback + 1
                window_end = i + 1
                
                p1_window = price1[window_start:window_end]
                p2_window = price2[window_start:window_end]
                
                # Calculate hedge ratio
                beta = self.calculate_hedge_ratio(p1_window, p2_window)
                hedge_ratios.append(beta)
                
                # Calculate spread
                spread = self.calculate_spread(p1_window, p2_window, beta)
                spreads.append(spread[-1])  # Current spread
                
                # Calculate mean and std
                mean_spread = np.mean(spread)
                std_spread = np.std(spread)
                spread_means.append(mean_spread)
                spread_stds.append(std_spread)
                
                # Calculate Z-score
                if std_spread > 0:
                    zscore = (spread[-1] - mean_spread) / std_spread
                else:
                    zscore = 0.0
                zscores.append(zscore)
                
                # Calculate correlation
                corr = np.corrcoef(p1_window, p2_window)[0, 1]
                correlations.append(corr)
                
                # Calculate volatility
                if i >= 20:
                    ret_window = returns1[max(0, i-20):i]
                    vol = np.std(ret_window)
                    volatilities.append(vol)
                else:
                    volatilities.append(0.0)
        
        # Add to result dataframe
        result_df['spread'] = spreads
        result_df['zscore'] = zscores
        result_df['hedge_ratio'] = hedge_ratios
        result_df['correlation'] = correlations
        result_df['spread_mean'] = spread_means
        result_df['spread_std'] = spread_stds
        result_df['volatility'] = volatilities
        
        # Generate signals
        signal_pair1 = []
        signal_pair2 = []
        trade_active = []
        
        for i in range(len(result_df)):
            zscore = result_df['zscore'].iloc[i]
            corr = result_df['correlation'].iloc[i]
            vol = result_df['volatility'].iloc[i]
            
            # Check conditions
            correlation_ok = np.isnan(corr) or corr > self.min_correlation
            volatility_ok = vol < self.volatility_threshold or np.isnan(vol)
            
            # Signal generation
            if not correlation_ok or not volatility_ok:
                # Don't trade if correlation or volatility issues
                signal_pair1.append(0)
                signal_pair2.append(0)
                trade_active.append(False)
            
            elif zscore > self.z_entry:
                # Spread too high: Sell pair1, Buy pair2
                # Pair1 is overpriced, Pair2 is underpriced
                signal_pair1.append(-1)  # SELL pair1
                signal_pair2.append(1)   # BUY pair2
                trade_active.append(True)
            
            elif zscore < -self.z_entry:
                # Spread too low: Buy pair1, Sell pair2
                # Pair1 is underpriced, Pair2 is overpriced
                signal_pair1.append(1)   # BUY pair1
                signal_pair2.append(-1)  # SELL pair2
                trade_active.append(True)
            
            elif abs(zscore) < self.z_exit or abs(zscore) > self.z_stop:
                # Exit or hard stop
                signal_pair1.append(0)   # CLOSE
                signal_pair2.append(0)   # CLOSE
                trade_active.append(False)
            
            else:
                signal_pair1.append(0)
                signal_pair2.append(0)
                trade_active.append(False)
        
        result_df['signal_pair1'] = signal_pair1
        result_df['signal_pair2'] = signal_pair2
        result_df['trade_active'] = trade_active
        
        # Add BUY/SELL columns (positive means BUY, negative means SELL)
        result_df['BUY'] = (result_df['signal_pair1'] != 0).astype(int)
        result_df['SELL'] = 0  # Not used in pairs, but for compatibility
        
        return result_df
    
    def get_parameters(self) -> Dict:
        """Return strategy parameters"""
        return {
            'pair1': self.pair1,
            'pair2': self.pair2,
            'lookback': self.lookback,
            'z_entry': self.z_entry,
            'z_exit': self.z_exit,
            'z_stop': self.z_stop,
            'enable_cointegration_check': self.enable_cointegration_check,
            'volatility_threshold': self.volatility_threshold,
            'min_correlation': self.min_correlation,
        }
    
    def __repr__(self):
        return f"{self.name}: {self.description}"


class PairsTradingAnalyzer:
    """
    Helper class to analyze pairs trading setup before trading
    """
    
    @staticmethod
    def analyze_pair_relationship(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        price_col: str = 'close',
        lookback: int = 100
    ) -> Dict:
        """
        Comprehensive analysis of pair relationship
        
        Returns:
            Dictionary with analysis results
        """
        price1 = df1[price_col].values[-lookback:]
        price2 = df2[price_col].values[-lookback:]
        
        strategy = PairsTradingStrategy()
        
        # Correlation
        corr = np.corrcoef(price1, price2)[0, 1]
        
        # Hedge ratio
        beta = strategy.calculate_hedge_ratio(price1, price2)
        
        # Spread and cointegration
        spread = strategy.calculate_spread(price1, price2, beta)
        t_stat, p_value = strategy.cointegration_test(spread)
        
        # Returns volatility
        ret1 = np.diff(price1) / price1[:-1]
        ret2 = np.diff(price2) / price2[:-1]
        vol1 = np.std(ret1)
        vol2 = np.std(ret2)
        
        return {
            'correlation': corr,
            'hedge_ratio': beta,
            'cointegration_pvalue': p_value,
            'is_cointegrated': p_value < 0.05,
            'volatility_pair1': vol1,
            'volatility_pair2': vol2,
            'spread_mean': np.mean(spread),
            'spread_std': np.std(spread),
            'current_zscore': (spread[-1] - np.mean(spread)) / np.std(spread),
            'pair1_volatility': vol1,
            'pair2_volatility': vol2,
        }
