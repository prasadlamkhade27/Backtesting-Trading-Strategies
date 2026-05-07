"""
CSV Rules Processor - Process batch backtests from CSV
"""
import pandas as pd
from typing import List, Dict, Tuple
from dataclasses import asdict
from propfirm.config import PhaseRules


class CSVRulesProcessor:
    """Process CSV files containing PropFirm rules and parameters"""
    
    @staticmethod
    def parse_rules_csv(df: pd.DataFrame) -> List[Dict]:
        """
        Parse CSV with PropFirm parameters
        
        Expected columns:
        - propfirm_name: Name of the propfirm
        - daily_loss_limit: Daily loss limit (as %)
        - max_loss_limit: Max loss limit (as %)
        - profit_target: Profit target (as %)
        - min_trading_days: Minimum trading days
        - max_trades_per_day: Max trades per day
        - stop_loss: Stop loss level
        - take_profit: Take profit level
        - risk_percent: Risk per trade (as %)
        - account_size: Account size in $
        
        Returns:
            List of dictionaries with parsed parameters
        """
        required_columns = [
            'propfirm_name', 'daily_loss_limit', 'max_loss_limit',
            'profit_target', 'stop_loss', 'take_profit', 'risk_percent', 'account_size'
        ]
        
        # Check required columns
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        rules_list = []
        for idx, row in df.iterrows():
            rules_dict = {
                'propfirm_name': str(row['propfirm_name']),
                'daily_loss_limit': float(row['daily_loss_limit']) / 100,
                'max_loss_limit': float(row['max_loss_limit']) / 100,
                'profit_target': float(row['profit_target']) / 100,
                'min_trading_days': int(row.get('min_trading_days', 1)),
                'max_trades_per_day': int(row.get('max_trades_per_day', 999)),
                'stop_loss': float(row['stop_loss']),
                'take_profit': float(row['take_profit']),
                'risk_percent': float(row['risk_percent']) / 100,
                'account_size': float(row['account_size'])
            }
            rules_list.append(rules_dict)
        
        return rules_list
    
    @staticmethod
    def validate_rules(rules: Dict) -> Tuple[bool, str]:
        """
        Validate rules dictionary
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        validations = [
            (0 < rules['daily_loss_limit'] < 1, "Daily loss limit must be between 0-100%"),
            (0 < rules['max_loss_limit'] < 1, "Max loss limit must be between 0-100%"),
            (0 < rules['profit_target'] < 1, "Profit target must be between 0-100%"),
            (rules['max_loss_limit'] >= rules['daily_loss_limit'], "Max loss must be >= daily loss"),
            (rules['stop_loss'] > 0, "Stop loss must be positive"),
            (rules['take_profit'] > 0, "Take profit must be positive"),
            (0 < rules['risk_percent'] < 1, "Risk percent must be between 0-100%"),
            (rules['account_size'] > 0, "Account size must be positive"),
        ]
        
        for condition, message in validations:
            if not condition:
                return False, message
        
        return True, "Valid"
    
    @staticmethod
    def create_template_csv() -> str:
        """Create a template CSV string"""
        template_data = {
            'propfirm_name': ['FTMO', 'TradingView', 'MyForexFunds', 'Custom1'],
            'daily_loss_limit': [5, 8, 3, 5],
            'max_loss_limit': [10, 12, 8, 10],
            'profit_target': [10, 8, 8, 10],
            'min_trading_days': [1, 2, 3, 1],
            'max_trades_per_day': [999, 100, 50, 999],
            'stop_loss': [5, 10, 8, 5],
            'take_profit': [10, 15, 12, 10],
            'risk_percent': [1, 1.5, 1, 1],
            'account_size': [10000, 10000, 10000, 10000]
        }
        df = pd.DataFrame(template_data)
        return df.to_csv(index=False)
