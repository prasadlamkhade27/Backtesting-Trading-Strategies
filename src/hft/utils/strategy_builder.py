"""
Strategy Builder Utility
Allows users to create, test, and backtest strategies from the frontend
"""
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any


class StrategyBuilder:
    """Helper class to manage user-created strategies"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.strategies_dir = Path(self.temp_dir) / "user_strategies"
        self.strategies_dir.mkdir(exist_ok=True)
    
    def save_strategy_code(self, strategy_name: str, code: str) -> Tuple[bool, str]:
        """
        Save strategy code to a temporary file
        
        Args:
            strategy_name: Name of the strategy
            code: Python code for the strategy
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Sanitize strategy name
            safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in strategy_name)
            file_path = self.strategies_dir / f"{safe_name}.py"
            
            # Write code to file
            with open(file_path, 'w') as f:
                f.write(code)
            
            return True, f"Strategy '{strategy_name}' saved successfully at {file_path}"
        except Exception as e:
            return False, f"Error saving strategy: {str(e)}"
    
    def validate_strategy_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate if strategy code is syntactically correct
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple[bool, str]: (valid, message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, "Code is syntactically valid"
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"
        except Exception as e:
            return False, f"Validation Error: {str(e)}"
    
    def load_strategy_template(self) -> str:
        """
        Return a template for creating new strategies
        
        Returns:
            str: Strategy template code
        """
        return '''"""
Generated Strategy Template
Implement your strategy logic below
"""
import pandas as pd
import numpy as np
from hft.strategies.base_strategy import BaseStrategy


class UserStrategy(BaseStrategy):
    """User-defined trading strategy"""
    
    def __init__(self, **kwargs):
        """Initialize strategy with parameters"""
        super().__init__(**kwargs)
        # Add your parameters here
        self.param1 = kwargs.get('param1', 20)
        self.param2 = kwargs.get('param2', 50)
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            pd.DataFrame: DataFrame with 'signal' column (-1, 0, 1)
        """
        df = df.copy()
        
        # Example: Simple Moving Average crossover
        df['sma_short'] = df['close'].rolling(self.param1).mean()
        df['sma_long'] = df['close'].rolling(self.param2).mean()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1   # Buy
        df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1  # Sell
        
        return df
    
    def execute_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute the strategy on data
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Dict with strategy results
        """
        df = self.calculate_signals(df)
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['signal'].shift(1) * df['returns']
        
        return {
            'signals': df['signal'],
            'returns': df['returns'],
            'strategy_returns': df['strategy_returns'],
            'cumulative_returns': (1 + df['strategy_returns']).cumprod() - 1
        }
'''
    
    def get_strategy_template_with_parameters(self) -> Dict[str, Any]:
        """
        Return strategy template with suggested parameters
        
        Returns:
            Dict: Template with parameters and example values
        """
        return {
            'template': self.load_strategy_template(),
            'suggested_parameters': {
                'sma_short': {
                    'default': 20,
                    'min': 5,
                    'max': 100,
                    'description': 'Short moving average period'
                },
                'sma_long': {
                    'default': 50,
                    'min': 20,
                    'max': 200,
                    'description': 'Long moving average period'
                },
                'risk_per_trade': {
                    'default': 0.02,
                    'min': 0.001,
                    'max': 0.1,
                    'description': 'Risk percentage per trade'
                }
            }
        }


class BacktestRunner:
    """Helper to run backtests on user strategies"""
    
    @staticmethod
    def run_backtest(
        data: pd.DataFrame,
        strategy_func,
        initial_capital: float = 10000,
        position_size: float = 0.95
    ) -> Dict[str, Any]:
        """
        Run backtest on strategy
        
        Args:
            data: OHLCV DataFrame
            strategy_func: Strategy function/class
            initial_capital: Starting capital
            position_size: Position size as fraction of capital
            
        Returns:
            Dict: Backtest results
        """
        try:
            df = data.copy()
            
            # Execute strategy
            results = strategy_func.execute_strategy(df) if hasattr(strategy_func, 'execute_strategy') else strategy_func(df)
            
            # Calculate P&L
            df['signal'] = results.get('strategy_returns', 0)
            df['returns'] = results.get('returns', df['close'].pct_change())
            
            # Calculate equity curve
            df['pnl'] = df['signal'] * df['returns'] * initial_capital * position_size
            df['equity'] = initial_capital + df['pnl'].cumsum()
            
            # Calculate metrics
            total_return = (df['equity'].iloc[-1] - initial_capital) / initial_capital
            max_drawdown = BacktestRunner._calculate_max_drawdown(df['equity'])
            sharpe_ratio = BacktestRunner._calculate_sharpe_ratio(df['returns'])
            win_rate = BacktestRunner._calculate_win_rate(df['pnl'])
            
            return {
                'success': True,
                'equity_curve': df[['close', 'equity']],
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'win_rate': win_rate,
                'trades': len(df[df['signal'] != 0]),
                'message': 'Backtest completed successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Backtest failed: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def _calculate_max_drawdown(equity: pd.Series) -> float:
        """Calculate maximum drawdown"""
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def _calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - (risk_free_rate / 252)
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    @staticmethod
    def _calculate_win_rate(pnl: pd.Series) -> float:
        """Calculate win rate"""
        winning_trades = (pnl > 0).sum()
        total_trades = (pnl != 0).sum()
        return winning_trades / total_trades if total_trades > 0 else 0
