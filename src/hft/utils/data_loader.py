"""
Data Loading Utilities
"""
import pandas as pd
import yfinance as yf
from typing import Optional


class DataLoader:
    """Load market data from Yahoo Finance - supports forex and commodities"""
    
    # Comprehensive symbol mapping for forex pairs and commodities
    SYMBOLS = {
        # Commodities
        "XAUUSD (Gold)": "GC=F",
        "XAGUSD (Silver)": "SI=F",
        "CLUSD (Oil)": "CL=F",
        "NGAS (Natural Gas)": "NG=F",
        
        # Major Forex Pairs
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "AUDUSD": "AUDUSD=X",
        "NZDUSD": "NZDUSD=X",
        "USDCAD": "USDCAD=X",
        "USDCHF": "USDCHF=X",
        
        # Cross Pairs
        "EURJPY": "EURJPY=X",
        "GBPJPY": "GBPJPY=X",
        "EURGBP": "EURGBP=X",
        "AUDJPY": "AUDJPY=X",
        "CADJPY": "CADJPY=X",
        "CHFJPY": "CHFJPY=X",
        
        # Crypto
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
    }
    
    @classmethod
    def get_all_pairs(cls) -> list:
        """Get all available trading pairs"""
        return list(cls.SYMBOLS.keys())
    
    @classmethod
    def get_forex_pairs(cls) -> list:
        """Get only forex pairs (exclude commodities and crypto)"""
        forex = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'USDCHF',
            'EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY', 'CADJPY', 'CHFJPY'
        ]
        return forex
    
    @classmethod
    def get_commodities(cls) -> list:
        """Get commodity pairs"""
        return ['XAUUSD (Gold)', 'XAGUSD (Silver)', 'CLUSD (Oil)', 'NGAS (Natural Gas)']
    
    @staticmethod
    def load_yfinance(symbol_key: str, interval: str, period: str) -> pd.DataFrame:
        """
        Load data from Yahoo Finance
        
        Args:
            symbol_key: Key from SYMBOLS dict
            interval: '1m', '5m', '15m', '1h', '1d'
            period: '1d', '5d', '1mo', '3mo', '1y'
        
        Returns:
            DataFrame with columns: time, open, high, low, close, volume
        """
        symbol = DataLoader.SYMBOLS.get(symbol_key)
        if not symbol:
            raise ValueError(f"Unknown symbol: {symbol_key}")
        
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        df = df.reset_index()
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        return df
    
    @staticmethod
    def load_csv(uploaded_file) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Expected columns (case-insensitive):
        - time/date
        - open
        - high
        - low
        - close
        - volume (optional)
        """
        df = pd.read_csv(uploaded_file)
        df.columns = [c.lower() for c in df.columns]
        
        # Rename common column name variations
        if 'date' in df.columns and 'time' not in df.columns:
            df = df.rename(columns={'date': 'time'})
        
        required_cols = ['time', 'open', 'high', 'low', 'close']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        if 'volume' not in df.columns:
            df['volume'] = 0
        
        return df[required_cols + ['volume']].copy()
    
    @staticmethod
    def validate_data(df: pd.DataFrame) -> tuple:
        """
        Validate data quality
        
        Returns:
            Tuple of (is_valid, message)
        """
        if len(df) < 10:
            return False, "Need at least 10 candles"
        
        if df['close'].isna().any():
            return False, "Data contains NaN values"
        
        if (df['high'] < df['low']).any():
            return False, "High price < Low price (data error)"
        
        return True, "Data valid"
