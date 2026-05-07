"""
Advanced Position & Lot Size Calculator
Handles lot size calculation and risk management for all forex pairs
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class PairConfig:
    """Configuration for each forex pair"""
    pair: str
    pip_size: float = 0.0001  # Default for most pairs
    contract_size: int = 100000  # Standard lot (1 lot = 100k units)
    min_lot: float = 0.01  # Minimum 0.01 lot (micro lot)
    max_lot: float = 100.0  # Maximum 100 lots
    account_risk_pct: float = 0.01  # 1% risk per trade
    
    @classmethod
    def get_pair_config(cls, pair: str) -> 'PairConfig':
        """Get configuration for a specific pair"""
        
        # JPY pairs have different pip sizes
        if 'JPY' in pair:
            pip_size = 0.01
        else:
            pip_size = 0.0001
        
        return cls(
            pair=pair,
            pip_size=pip_size,
            contract_size=100000,
            min_lot=0.01,
            max_lot=100.0,
            account_risk_pct=0.01
        )


class LotSizeCalculator:
    """Calculate lot sizes based on risk management principles"""
    
    def __init__(self, account_size: float):
        self.account_size = account_size
        self.pair_configs: Dict[str, PairConfig] = {}
    
    def calculate_lot_size(
        self,
        pair: str,
        entry_price: float,
        stop_loss_price: float,
        risk_pct: Optional[float] = None
    ) -> Tuple[float, float, Dict]:
        """
        Calculate optimal lot size for a trade.
        
        Formula:
        ────────────────────────────────────────────────
        Risk Amount = Account × Risk %
        Risk in Pips = |Entry - SL| / Pip Size
        Lot Size = Risk Amount / (Risk in Pips × Pip Value × Lot Size)
        ────────────────────────────────────────────────
        
        Args:
            pair: Currency pair (e.g., 'EURUSD')
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_pct: Risk percentage (default: 1% from config)
        
        Returns:
            Tuple of (lot_size, risk_amount, stats_dict)
        """
        
        # Get pair-specific config
        if pair not in self.pair_configs:
            self.pair_configs[pair] = PairConfig.get_pair_config(pair)
        
        config = self.pair_configs[pair]
        risk_pct = risk_pct or config.account_risk_pct
        
        # Calculate risk amount
        risk_amount = self.account_size * risk_pct
        
        # Calculate risk in pips
        risk_in_pips = abs(entry_price - stop_loss_price) / config.pip_size
        
        if risk_in_pips <= 0:
            raise ValueError(f"Invalid stop loss price for {pair}")
        
        # Calculate pip value per lot
        # For most pairs: 1 lot × 1 pip = $10
        # For JPY pairs: 1 lot × 1 pip = $1000
        if 'JPY' in pair:
            pip_value_per_lot = 1000
        else:
            pip_value_per_lot = 10
        
        # Calculate lot size
        lot_size = risk_amount / (risk_in_pips * pip_value_per_lot)
        
        # Apply constraints
        lot_size = max(lot_size, config.min_lot)
        lot_size = min(lot_size, config.max_lot)
        
        # Round to nearest micro lot (0.01)
        lot_size = round(lot_size, 2)
        
        # Recalculate actual risk with adjusted lot size
        actual_risk = lot_size * risk_in_pips * pip_value_per_lot
        
        stats = {
            'pair': pair,
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'risk_in_pips': risk_in_pips,
            'pip_size': config.pip_size,
            'pip_value_per_lot': pip_value_per_lot,
            'account_risk_pct': risk_pct,
            'risk_amount': risk_amount,
            'lot_size': lot_size,
            'actual_risk': actual_risk,
            'position_size_units': lot_size * config.contract_size
        }
        
        return lot_size, actual_risk, stats
    
    def calculate_take_profit_lot_profits(
        self,
        lot_size: float,
        pair: str,
        entry_price: float,
        take_profit_price: float
    ) -> Dict:
        """Calculate potential profit at take profit level"""
        
        config = PairConfig.get_pair_config(pair)
        
        profit_in_pips = abs(take_profit_price - entry_price) / config.pip_size
        
        if 'JPY' in pair:
            pip_value_per_lot = 1000
        else:
            pip_value_per_lot = 10
        
        profit_amount = lot_size * profit_in_pips * pip_value_per_lot
        profit_pct = (profit_amount / self.account_size) * 100
        
        return {
            'profit_in_pips': profit_in_pips,
            'profit_amount': profit_amount,
            'profit_pct': profit_pct,
            'rr_ratio': profit_in_pips / (abs(entry_price - entry_price) or 1)  # Will be calculated properly in usage
        }
    
    def display_lot_calculation(
        self,
        pair: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        lot_size: float
    ) -> str:
        """Format lot size calculation for display"""
        
        config = PairConfig.get_pair_config(pair)
        risk_in_pips = abs(entry_price - stop_loss) / config.pip_size
        reward_in_pips = abs(take_profit - entry_price) / config.pip_size
        
        if 'JPY' in pair:
            pip_value = 1000
        else:
            pip_value = 10
        
        risk_amount = lot_size * risk_in_pips * pip_value
        potential_profit = lot_size * reward_in_pips * pip_value
        
        output = f"""
        ╔══════════════════════════════════════════════════════╗
        ║               LOT SIZE CALCULATION                   ║
        ╚══════════════════════════════════════════════════════╝
        
        Pair:                {pair}
        Entry Price:         {entry_price:.5f}
        Stop Loss:           {stop_loss:.5f}
        Take Profit:         {take_profit:.5f}
        
        ─────────────────────────────────────────────────────
        Risk Distance:       {risk_in_pips:.1f} pips
        Reward Distance:     {reward_in_pips:.1f} pips
        Risk/Reward Ratio:   1:{reward_in_pips/risk_in_pips:.2f}
        
        ─────────────────────────────────────────────────────
        Lot Size:            {lot_size} lots ({lot_size * config.contract_size:,.0f} units)
        Risk Amount:         ${risk_amount:,.2f}
        Potential Profit:    ${potential_profit:,.2f}
        Risk/Account:        {(risk_amount/self.account_size)*100:.2f}%
        ─────────────────────────────────────────────────────
        """
        
        return output
