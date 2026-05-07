"""
Risk Management Module - Professional Position Sizing & Trade Management
═════════════════════════════════════════════════════════════════════════

This module handles all risk calculations, position sizing, and trade management
according to professional trading standards and PropFirm requirements.

KEY CONCEPTS:
1. Fixed Risk Per Trade: 1% of account (NON-NEGOTIABLE)
2. Position Size: Calculated based on entry price, SL, and risk amount
3. Trade Filters: Reject trades that don't meet minimum RR or other criteria
4. Daily Loss Limit: Track cumulative losses, stop trading if exceeded
5. Account Equity Updates: Live P&L tracking
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class RiskConfig:
    """Professional risk management configuration"""
    
    # Fixed Risk Per Trade (as % of account)
    risk_per_trade: float = 0.01  # 1% = Professional standard
    
    # Daily/Session limits
    max_daily_loss: float = 0.03  # 3% per day (PropFirm safe)
    max_monthly_loss: float = 0.10  # 10% per month
    
    # Trade quality filters
    min_rr_ratio: float = 2.0  # Minimum 1:2 Risk/Reward
    min_win_rate: float = 0.35  # Minimum 35% win rate acceptable
    
    # Trade execution filters
    min_volume_multiplier: float = 0.8  # Min vol = 80% of average
    max_slippage: float = 0.0005  # Max 0.05% slippage
    
    # Drawdown limits
    max_account_drawdown: float = 0.20  # Max 20% account drawdown
    max_consecutive_losses: int = 5  # Stop after 5 losses in a row


class RiskManager:
    """
    Manages all aspects of trading risk - position sizing, P&L tracking, etc.
    """
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.trades_log = []  # Track all trades
        self.daily_pnl_log = {}  # Track daily P&L
        self.account_equity_log = []  # Track account equity over time
        
    def calculate_position_size(
        self,
        account_size: float,
        entry_price: float,
        stop_loss: float,
        risk_amount: Optional[float] = None,
        max_lot_size: float = 100.0  # Gold contracts typically max 5-100 lots
    ) -> Tuple[float, float]:
        """
        Calculate optimal position size based on risk management.
        
        This is THE most important function in trading. Done wrong = ruin.
        Done right = consistent profits.
        
        Formula:
        ───────────────────────────────────────────────────
        Risk Amount = Account Size × Risk % per trade
        
        Risk Distance = |Entry - Stop Loss|
        
        Position Size = Risk Amount / Risk Distance
        ───────────────────────────────────────────────────
        
        Args:
            account_size: Current account balance
            entry_price: Entry price for the trade
            stop_loss: Stop loss price
            risk_amount: Optional override for risk amount (uses config % if not provided)
            max_lot_size: Maximum allowable position size (contracts)
            
        Returns:
            Tuple: (position_size, risk_amount_value)
        """
        
        # Step 1: Calculate risk amount
        if risk_amount is None:
            risk_amount = account_size * self.config.risk_per_trade
        
        # Step 2: Calculate risk distance (points at risk)
        risk_distance = abs(entry_price - stop_loss)
        
        if risk_distance <= 0:
            raise ValueError("Stop loss must be different from entry price")
        
        # Step 3: Calculate position size
        position_size = risk_amount / risk_distance
        
        # Step 4: Apply max lot size constraint
        position_size = min(position_size, max_lot_size)
        
        return position_size, risk_amount
    
    def validate_trade(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        entry_type: str = 'BUY',
        current_volume: float = 100,
        avg_volume: float = 100
    ) -> Tuple[bool, str]:
        """
        Validate if a trade meets minimum quality standards.
        
        Returns:
            Tuple: (is_valid, reason_if_invalid)
        """
        
        # Check 1: Risk/Reward ratio
        if entry_type.upper() == 'BUY':
            risk_distance = entry_price - stop_loss
            reward_distance = take_profit - entry_price
        else:  # SELL
            risk_distance = stop_loss - entry_price
            reward_distance = entry_price - take_profit
        
        if risk_distance <= 0:
            return False, "Invalid SL placement"
        
        if reward_distance <= 0:
            return False, "Invalid TP placement"
        
        rr_ratio = reward_distance / risk_distance
        
        if rr_ratio < self.config.min_rr_ratio:
            return False, f"Poor RR ratio ({rr_ratio:.2f}:1, min {self.config.min_rr_ratio}:1)"
        
        # Check 2: Volume validation
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        if volume_ratio < self.config.min_volume_multiplier:
            return False, f"Insufficient volume ({volume_ratio:.2%} of average)"
        
        # Check 3: Minimum profit potential
        min_profitable_pips = (stop_loss - entry_price) if entry_type.upper() == 'BUY' else (entry_price - stop_loss)
        if abs(min_profitable_pips) < 0.01:
            return False, "Trade too small, pip distance insufficient"
        
        return True, "Valid trade"
    
    def calculate_pnl(
        self,
        entry_price: float,
        exit_price: float,
        position_size: float,
        entry_type: str = 'BUY',
        commission: float = 0.0
    ) -> Tuple[float, float]:
        """
        Calculate profit/loss for a completed trade.
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            position_size: Position size (contracts or units)
            entry_type: 'BUY' or 'SELL'
            commission: Trading commission/fees
            
        Returns:
            Tuple: (pnl_pips, pnl_value)
        """
        
        if entry_type.upper() == 'BUY':
            pnl_pips = exit_price - entry_price
        else:
            pnl_pips = entry_price - exit_price
        
        pnl_value = pnl_pips * position_size - commission
        
        return pnl_pips, pnl_value
    
    def calculate_drawdown(
        self,
        peak_equity: float,
        current_equity: float
    ) -> float:
        """
        Calculate current drawdown percentage.
        
        Formula:
        Drawdown % = (Peak Equity - Current Equity) / Peak Equity × 100
        """
        
        if peak_equity <= 0:
            return 0.0
        
        drawdown = (peak_equity - current_equity) / peak_equity
        return max(0, drawdown)  # Never negative
    
    def should_stop_trading(
        self,
        daily_pnl: float,
        total_pnl: float,
        account_size: float,
        consecutive_losses: int,
        peak_equity: float,
        current_equity: float
    ) -> Tuple[bool, str]:
        """
        Determine if trading should stop (circuit breaker).
        
        Returns:
            Tuple: (stop_trading, reason)
        """
        
        # Check 1: Daily loss limit
        if daily_pnl < -account_size * self.config.max_daily_loss:
            return True, "Daily loss limit exceeded"
        
        # Check 2: Monthly loss limit
        if total_pnl < -account_size * self.config.max_monthly_loss:
            return True, "Monthly loss limit exceeded"
        
        # Check 3: Consecutive losses
        if consecutive_losses >= self.config.max_consecutive_losses:
            return True, f"{self.config.max_consecutive_losses} consecutive losses - psychological reset needed"
        
        # Check 4: Account drawdown
        drawdown = self.calculate_drawdown(peak_equity, current_equity)
        if drawdown > self.config.max_account_drawdown:
            return True, f"Account drawdown ({drawdown:.2%}) exceeded limit"
        
        return False, "Trading allowed"
    
    def calculate_expected_value(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate strategy expectancy (mathematical edge).
        
        Formula:
        Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
        
        Positive expectancy = Profitable strategy long-term
        Negative expectancy = Losing strategy (don't trade!)
        """
        
        loss_rate = 1 - win_rate
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        
        return expectancy
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe Ratio for performance evaluation.
        
        Formula:
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        
        Sharpe > 1.0 = Good
        Sharpe > 2.0 = Excellent
        """
        
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Annualized to daily
        
        sharpe = excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        return sharpe * np.sqrt(252)  # Annualize
    
    def calculate_profit_factor(
        self,
        wins: pd.Series,
        losses: pd.Series
    ) -> float:
        """
        Calculate Profit Factor.
        
        Formula:
        Profit Factor = Gross Profit / Gross Loss
        
        > 1.5 = Good
        > 2.0 = Excellent
        < 1.0 = Don't trade!
        """
        
        gross_profit = wins.sum() if len(wins) > 0 else 0
        gross_loss = abs(losses.sum()) if len(losses) > 0 else 0
        
        if gross_loss <= 0:
            return 0.0
        
        return gross_profit / gross_loss
    
    def log_trade(self, trade_data: dict):
        """Log a completed trade for analysis"""
        self.trades_log.append(trade_data)
    
    def generate_report(self) -> dict:
        """
        Generate comprehensive trading performance report.
        """
        
        if not self.trades_log:
            return {"error": "No trades logged"}
        
        df = pd.DataFrame(self.trades_log)
        
        wins = df[df['pnl'] > 0]['pnl']
        losses = df[df['pnl'] <= 0]['pnl']
        
        report = {
            'total_trades': len(df),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(df) if len(df) > 0 else 0,
            'avg_win': wins.mean() if len(wins) > 0 else 0,
            'avg_loss': losses.mean() if len(losses) > 0 else 0,
            'largest_win': wins.max() if len(wins) > 0 else 0,
            'largest_loss': losses.min() if len(losses) > 0 else 0,
            'total_pnl': df['pnl'].sum(),
            'profit_factor': self.calculate_profit_factor(wins, losses),
            'expectancy': self.calculate_expected_value(
                len(wins) / len(df),
                wins.mean() if len(wins) > 0 else 0,
                abs(losses.mean()) if len(losses) > 0 else 0
            )
        }
        
        return report


# ═════════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL POSITION SIZING EXAMPLE
# ═════════════════════════════════════════════════════════════════════════════════
#
# Account Size: $10,000
# Risk per Trade: 1% = $100
# Entry Price: 2050.00
# Stop Loss: 2045.00
# Risk Distance: 5.00 points
#
# Position Size = $100 / 5.00 = 20 contracts
#
# If we hit TP at 2060.00:
# Profit = (2060.00 - 2050.00) × 20 = 200 pips × 20 = $200 profit
# Our 1:2 RR was achieved!
#
# New Account: $10,100 (paid 1% risk, made 2% profit)
#
# ═════════════════════════════════════════════════════════════════════════════════

