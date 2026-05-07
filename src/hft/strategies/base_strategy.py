"""
Base Strategy Class - All strategies inherit from this
"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate BUY and SELL signals
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with 'BUY' and 'SELL' columns added
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> dict:
        """Return strategy parameters as dict"""
        pass
    
    def __repr__(self):
        return f"{self.name}: {self.description}"
