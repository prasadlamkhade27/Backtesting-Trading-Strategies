import os
import importlib
import inspect
from hft.strategies.base_strategy import BaseStrategy
from hft.strategies.pivot_strategy import PivotStrategy
from hft.strategies.xauusd_pro_strategy import XAUUSDProStrategy
from hft.strategies.advanced_forex_strategy import AdvancedForexStrategy
from hft.strategies.base_futures_strategy import BaseFuturesStrategy
from hft.strategies.es_futures_strategy import ESFuturesStrategy
from hft.strategies.nq_futures_strategy import NQFuturesStrategy
from hft.strategies.ym_futures_strategy import YMFuturesStrategy
from hft.strategies.mql_king_1_strategy import MQLKing1Strategy

# Built-in strategies (core)
AVAILABLE_STRATEGIES = {
    'MQL King 1 - SMC HFT': MQLKing1Strategy,
    'Advanced Forex & Gold - RSI+Stochastic': AdvancedForexStrategy,
    'XAUUSD Pro Strategy': XAUUSDProStrategy,
    'Pivot Strategy': PivotStrategy,
    'ES Futures - Mean Reversion + Trend': ESFuturesStrategy,
    'NQ Futures - Momentum': NQFuturesStrategy,
    'YM Futures - Trend Following': YMFuturesStrategy,
}

# Auto-discover custom strategies
def _auto_discover_strategies():
    """
    Auto-discover all strategy classes from the strategies directory.
    Looks for files with classes that inherit from BaseStrategy.
    """
    strategies_dir = os.path.dirname(__file__)
    
    # Get all Python files in strategies directory
    for filename in os.listdir(strategies_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]  # Remove .py
            
            try:
                # Import the module
                full_module_name = f'hft.strategies.{module_name}'
                module = importlib.import_module(full_module_name)
                
                # Find all strategy classes
                for class_name, cls in inspect.getmembers(module, inspect.isclass):
                    # Check if it's a BaseStrategy subclass and not a base class itself
                    if (issubclass(cls, BaseStrategy) and 
                        cls not in [BaseStrategy, BaseFuturesStrategy] and
                        cls.__module__ == full_module_name):  # Only classes defined in this module
                        
                        # Skip if already in AVAILABLE_STRATEGIES
                        if cls in AVAILABLE_STRATEGIES.values():
                            continue
                        
                        # Try to get display name from the class
                        try:
                            # Instantiate with defaults to get the name
                            instance = cls()
                            display_name = instance.name
                        except:
                            # Convert class name to readable format
                            display_name = class_name.replace('Strategy', '').replace('_', ' ').strip()
                        
                        # Register the strategy
                        AVAILABLE_STRATEGIES[display_name] = cls
            except Exception as e:
                # Silent fail - module might not import or have issues
                pass

# Run auto-discovery
_auto_discover_strategies()

def get_strategy(strategy_name, **kwargs):
    """
    Get a strategy instance by name
    
    Args:
        strategy_name (str): Name of the strategy to retrieve
        **kwargs: Parameters to pass to the strategy constructor
        
    Returns:
        BaseStrategy: An instance of the requested strategy
        
    Raises:
        ValueError: If strategy not found
    """
    if strategy_name not in AVAILABLE_STRATEGIES:
        available = list(AVAILABLE_STRATEGIES.keys())
        raise ValueError(
            f"Strategy '{strategy_name}' not found.\n"
            f"Available strategies: {', '.join(available)}"
        )
    
    strategy_class = AVAILABLE_STRATEGIES[strategy_name]
    return strategy_class(**kwargs)

def get_available_strategies():
    """
    Get list of all available strategy names
    
    Returns:
        list: List of all registered strategy names
    """
    return sorted(list(AVAILABLE_STRATEGIES.keys()))

__all__ = [
    'BaseStrategy',
    'BaseFuturesStrategy',
    'PivotStrategy',
    'XAUUSDProStrategy',
    'AdvancedForexStrategy',
    'ESFuturesStrategy',
    'NQFuturesStrategy',
    'YMFuturesStrategy',
    'MQLKing1Strategy',
    'AVAILABLE_STRATEGIES',
    'get_strategy',
    'get_available_strategies'
]
