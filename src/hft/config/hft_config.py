"""
HFT Trading System - Configuration Presets
Pre-configured settings for different trading scenarios and risk profiles

Usage:
    from hft_config import CONFIG_PRESETS
    
    # Use conservative preset
    config = CONFIG_PRESETS['CONSERVATIVE_SCALPING']
    
    # Or create custom configuration
    custom_config = create_custom_config(
        strategy='scalping',
        risk_level='moderate',
        market_profile='liquid'
    )
"""

from typing import Dict, Any
import pandas as pd


class HFTConfiguration:
    """HFT Strategy configuration class"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any]):
        self.name = name
        self.description = description
        self.config = config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def to_dict(self) -> Dict:
        """Export as dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.config
        }
    
    def __repr__(self) -> str:
        return f"HFTConfiguration({self.name}): {self.description}"


# Configuration Presets
# ====================

CONFIG_PRESETS = {
    
    # ========== SCALPING STRATEGIES ==========
    
    'CONSERVATIVE_SCALPING': HFTConfiguration(
        name="Conservative Scalping",
        description="Tight stops, small profits, high win rate. Best for risk-averse traders.",
        config={
            # Strategy
            'strategy_type': 'scalping',
            'description': 'Conservative scalping with 0.3% risk per trade',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 20,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 1.5,
            'atr_tp_multiple': 0.5,  # Tight TP
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.3,
            'max_consecutive_losses': 3,
            'max_daily_loss_percent': 2.0,
            'max_drawdown_percent': 5.0,
            'max_open_positions': 2,
            'max_trades_per_hour': 15,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 0.1,
            
            # Targets
            'target_monthly_return': '1-2%',
            'target_win_rate': '60-70%',
            'target_profit_factor': '1.5-2.0',
            'best_for': 'Capital preservation, consistent small profits'
        }
    ),
    
    'MODERATE_SCALPING': HFTConfiguration(
        name="Moderate Scalping",
        description="Balanced risk/reward. Standard HFT scalping. Recommended for most traders.",
        config={
            # Strategy
            'strategy_type': 'scalping',
            'description': 'Moderate scalping with 0.5% risk per trade',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 20,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 1.5,
            'atr_tp_multiple': 0.75,  # Standard TP
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.5,
            'max_consecutive_losses': 5,
            'max_daily_loss_percent': 5.0,
            'max_drawdown_percent': 10.0,
            'max_open_positions': 3,
            'max_trades_per_hour': 20,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 0.5,
            
            # Targets
            'target_monthly_return': '3-5%',
            'target_win_rate': '55-65%',
            'target_profit_factor': '1.5-2.5',
            'best_for': 'Most traders, balanced approach'
        }
    ),
    
    'AGGRESSIVE_SCALPING': HFTConfiguration(
        name="Aggressive Scalping",
        description="Higher risk, higher expected returns. Requires experienced traders.",
        config={
            # Strategy
            'strategy_type': 'scalping',
            'description': 'Aggressive scalping with 1.0% risk per trade',
            
            # Technical Indicators
            'ma_fast_period': 4,
            'ma_slow_period': 15,
            'rsi_period': 12,
            'rsi_oversold': 25,
            'rsi_overbought': 75,
            'atr_period': 14,
            'atr_sl_multiple': 1.2,  # Tighter SL
            'atr_tp_multiple': 1.0,  # Wider TP
            'macd_fast': 10,
            'macd_slow': 24,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 1.0,
            'max_consecutive_losses': 10,
            'max_daily_loss_percent': 10.0,
            'max_drawdown_percent': 15.0,
            'max_open_positions': 5,
            'max_trades_per_hour': 30,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 1.0,
            
            # Targets
            'target_monthly_return': '5-10%',
            'target_win_rate': '50-60%',
            'target_profit_factor': '1.3-2.0',
            'best_for': 'Experienced traders, higher risk tolerance'
        }
    ),
    
    # ========== MARKET MAKING STRATEGIES ==========
    
    'CONSERVATIVE_MARKET_MAKING': HFTConfiguration(
        name="Conservative Market Making",
        description="Two-sided orders capturing spreads. Low risk approach.",
        config={
            # Strategy
            'strategy_type': 'market_making',
            'description': 'Conservative market making with spread capture',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 25,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 2.0,
            'atr_tp_multiple': 0.5,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.3,
            'max_consecutive_losses': 5,
            'max_daily_loss_percent': 3.0,
            'max_drawdown_percent': 5.0,
            'max_open_positions': 4,  # 2 long, 2 short
            'max_trades_per_hour': 10,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 0.2,
            
            # Targets
            'target_monthly_return': '2-3%',
            'target_win_rate': '65-75%',
            'target_profit_factor': '2.0-3.0',
            'best_for': 'Spread capture, consistent small profits'
        }
    ),
    
    'MODERATE_MARKET_MAKING': HFTConfiguration(
        name="Moderate Market Making",
        description="Balanced market making. Standard approach.",
        config={
            # Strategy
            'strategy_type': 'market_making',
            'description': 'Moderate market making strategy',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 20,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 1.5,
            'atr_tp_multiple': 0.75,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.5,
            'max_consecutive_losses': 7,
            'max_daily_loss_percent': 5.0,
            'max_drawdown_percent': 10.0,
            'max_open_positions': 6,
            'max_trades_per_hour': 15,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 0.5,
            
            # Targets
            'target_monthly_return': '3-5%',
            'target_win_rate': '60-70%',
            'target_profit_factor': '1.5-2.5',
            'best_for': 'Balanced market making approach'
        }
    ),
    
    # ========== TREND FOLLOWING STRATEGIES ==========
    
    'CONSERVATIVE_TREND_FOLLOWING': HFTConfiguration(
        name="Conservative Trend Following",
        description="Trend capture with tight stops. Lower trade frequency.",
        config={
            # Strategy
            'strategy_type': 'trend_following',
            'description': 'Conservative trend following with risk control',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 30,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 1.5,
            'atr_tp_multiple': 1.5,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.5,
            'max_consecutive_losses': 5,
            'max_daily_loss_percent': 5.0,
            'max_drawdown_percent': 10.0,
            'max_open_positions': 2,
            'max_trades_per_hour': 8,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 0.5,
            
            # Targets
            'target_monthly_return': '3-6%',
            'target_win_rate': '50-60%',
            'target_profit_factor': '1.5-2.5',
            'best_for': 'Steady trend capture with risk control'
        }
    ),
    
    'MODERATE_TREND_FOLLOWING': HFTConfiguration(
        name="Moderate Trend Following",
        description="Balanced trend following. Standard approach.",
        config={
            # Strategy
            'strategy_type': 'trend_following',
            'description': 'Moderate trend following strategy',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 25,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 1.5,
            'atr_tp_multiple': 2.0,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.75,
            'max_consecutive_losses': 6,
            'max_daily_loss_percent': 6.0,
            'max_drawdown_percent': 12.0,
            'max_open_positions': 3,
            'max_trades_per_hour': 10,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 1.0,
            
            # Targets
            'target_monthly_return': '5-8%',
            'target_win_rate': '48-58%',
            'target_profit_factor': '1.3-2.0',
            'best_for': 'Standard trend following'
        }
    ),
    
    'AGGRESSIVE_TREND_FOLLOWING': HFTConfiguration(
        name="Aggressive Trend Following",
        description="Trend capture with wider stops. Higher risk/reward.",
        config={
            # Strategy
            'strategy_type': 'trend_following',
            'description': 'Aggressive trend following strategy',
            
            # Technical Indicators
            'ma_fast_period': 4,
            'ma_slow_period': 20,
            'rsi_period': 12,
            'rsi_oversold': 25,
            'rsi_overbought': 75,
            'atr_period': 14,
            'atr_sl_multiple': 1.2,
            'atr_tp_multiple': 3.0,  # Larger TP targets
            'macd_fast': 10,
            'macd_slow': 24,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 1.0,
            'max_consecutive_losses': 8,
            'max_daily_loss_percent': 8.0,
            'max_drawdown_percent': 15.0,
            'max_open_positions': 5,
            'max_trades_per_hour': 15,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 2.0,
            
            # Targets
            'target_monthly_return': '8-15%',
            'target_win_rate': '45-55%',
            'target_profit_factor': '1.2-1.8',
            'best_for': 'Experienced traders, higher risk tolerance'
        }
    ),
    
    # ========== SPECIALIZED PRESETS ==========
    
    'NEWS_TRADER': HFTConfiguration(
        name="News Event Trader",
        description="High volatility strategy for news events. Very aggressive.",
        config={
            # Strategy
            'strategy_type': 'scalping',
            'description': 'Trades news events and high volatility',
            
            # Technical Indicators
            'ma_fast_period': 3,
            'ma_slow_period': 10,
            'rsi_period': 10,
            'rsi_oversold': 20,
            'rsi_overbought': 80,
            'atr_period': 7,
            'atr_sl_multiple': 1.0,
            'atr_tp_multiple': 2.0,
            'macd_fast': 5,
            'macd_slow': 13,
            'macd_signal': 5,
            
            # Risk Management
            'risk_percent_per_trade': 2.0,
            'max_consecutive_losses': 3,
            'max_daily_loss_percent': 5.0,
            'max_drawdown_percent': 10.0,
            'max_open_positions': 10,
            'max_trades_per_hour': 50,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 5.0,
            
            # Targets
            'target_monthly_return': '10-20%',
            'target_win_rate': '45-55%',
            'target_profit_factor': '1.0-1.5',
            'best_for': 'News event trading, high volatility capture'
        }
    ),
    
    'DEMO_ACCOUNT': HFTConfiguration(
        name="Demo Account Testing",
        description="Conservative settings for demo trading validation.",
        config={
            # Strategy
            'strategy_type': 'scalping',
            'description': 'Demo account with conservative settings',
            
            # Technical Indicators
            'ma_fast_period': 5,
            'ma_slow_period': 20,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_sl_multiple': 1.5,
            'atr_tp_multiple': 0.75,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # Risk Management
            'risk_percent_per_trade': 0.5,
            'max_consecutive_losses': 5,
            'max_daily_loss_percent': 5.0,
            'max_drawdown_percent': 10.0,
            'max_open_positions': 3,
            'max_trades_per_hour': 20,
            
            # Execution
            'use_fixed_lot': False,
            'max_lot_size': 0.5,
            
            # Targets
            'target_monthly_return': '3-5%',
            'target_win_rate': '55-65%',
            'target_profit_factor': '1.5-2.5',
            'best_for': 'Demo validation before live trading'
        }
    ),
}


def get_preset(name: str) -> HFTConfiguration:
    """
    Get a configuration preset by name
    
    Args:
        name: Preset name
        
    Returns:
        HFTConfiguration object
        
    Raises:
        ValueError: If preset not found
    """
    if name not in CONFIG_PRESETS:
        available = list(CONFIG_PRESETS.keys())
        raise ValueError(
            f"Preset '{name}' not found. Available presets:\n" +
            "\n".join(f"  - {p}" for p in available)
        )
    return CONFIG_PRESETS[name]


def list_presets() -> str:
    """Get formatted list of all presets"""
    output = "Available HFT Configuration Presets:\n"
    output += "=" * 70 + "\n\n"
    
    for name, config in CONFIG_PRESETS.items():
        output += f"📊 {name}\n"
        output += f"   {config.description}\n"
        output += f"   Risk: {config.get('risk_percent_per_trade')}% | "
        output += f"Max Positions: {config.get('max_open_positions')}\n"
        output += f"   Target Return: {config.get('target_monthly_return')} | "
        output += f"Target Win Rate: {config.get('target_win_rate')}\n\n"
    
    return output


def compare_presets(*preset_names: str) -> pd.DataFrame:
    """
    Compare multiple presets side by side
    
    Args:
        *preset_names: Names of presets to compare
        
    Returns:
        DataFrame with comparison
    """
    import pandas as pd
    
    comparison_keys = [
        'strategy_type',
        'risk_percent_per_trade',
        'max_consecutive_losses',
        'max_daily_loss_percent',
        'max_open_positions',
        'target_monthly_return',
        'target_win_rate',
        'target_profit_factor',
    ]
    
    data = {}
    for preset_name in preset_names:
        config = get_preset(preset_name)
        data[preset_name] = {
            key: config.get(key, 'N/A') for key in comparison_keys
        }
    
    return pd.DataFrame(data).T
