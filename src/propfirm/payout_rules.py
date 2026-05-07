"""
Payout & Earnings Engine
═════════════════════════════════════════════════════════════════════════
Manages profit splits, consistency rules, scaling plans, and payouts.

Handles:
- Profit splitting between trader and firm
- Consistency rule validation (best day ≤ X% of profit)
- Withdrawal rules and minimum payout thresholds
- Scaling plans (scale up after hitting profits)
- Account reset fees and recovery rules
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from enum import Enum


# ════════════════════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════════════════════

class PayoutFrequency(Enum):
    """When payouts are released"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


class ScalingType(Enum):
    """How account scaling works"""
    LINEAR = "linear"                  # Scale increases linearly
    EXPONENTIAL = "exponential"        # Scale increases exponentially
    MILESTONE = "milestone"            # Scale at specific profit targets


# ════════════════════════════════════════════════════════════════════════════
# CONSISTENCY RULES
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class ConsistencyRule:
    """
    Consistency validation - most profitable day must be ≤ X% of total profit
    
    Prevents: Taking one huge win and calling it a strategy
    Ensures: Consistent, repeatable trading
    
    Example:
        50% consistency rule on $5000 profit:
        - Best day can be at most $2500
        - Prevents: Best day = $4999 (90% of profit)
    """
    enabled: bool = True
    best_day_max_pct: float = 50.0                         # Best day ≤ 50% of total
    min_profit_to_check: float = 100.0                     # Only check if profit > $100
    violation_is_fatal: bool = True                        # Fail account if violated?


# ════════════════════════════════════════════════════════════════════════════
# WITHDRAWAL & PAYOUT RULES
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class WithdrawalRules:
    """Restrictions on how/when traders can withdraw profits"""
    
    min_account_age_days: int = 5                          # Can't withdraw for N days
    min_payout_amount: float = 500.0                       # Minimum withdrawal
    max_payout_amount: Optional[float] = None              # Maximum withdrawal (None = unlimited)
    
    payout_frequency: PayoutFrequency = PayoutFrequency.WEEKLY
    payouts_per_month: int = 4                             # 4 payouts per month
    
    processing_days: int = 1                               # Days to process payout
    
    # Special rules
    first_payout_requires_consistency: bool = True         # Must pass consistency first
    payout_requires_profit_target_hit: bool = False        # Must hit full profit target


# ════════════════════════════════════════════════════════════════════════════
# PROFIT SPLITTING
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class ProfitSplitTier:
    """Tiered profit split (e.g., 90% up to $50K, then 95%)"""
    
    cumulative_profit_threshold: float = 0.0               # Split applies after this profit
    trader_split_pct: float = 90.0                         # Trader keeps X%
    firm_split_pct: float = 10.0                           # Firm keeps (100-X)%
    
    def validate(self):
        """Ensure split adds to 100%"""
        if abs(self.trader_split_pct + self.firm_split_pct - 100.0) > 0.01:
            raise ValueError("Profit split must sum to 100%")


@dataclass
class ProfitSplitRules:
    """
    Rules for how profits are split between trader and firm
    
    Example (Apex - flat 90%):
        tiers: [ProfitSplitTier(0, 90, 10)]
    
    Example (Lucid - escalating):
        tiers: [
            ProfitSplitTier(0, 80, 20),         # First $25K: 80%
            ProfitSplitTier(25000, 90, 10),    # After $25K: 90%
            ProfitSplitTier(100000, 95, 5),   # After $100K: 95%
        ]
    """
    
    flat_split_pct: float = 90.0                           # Simple flat split
    use_tiers: bool = False                                # Use tiered splits instead?
    tiers: List[ProfitSplitTier] = field(default_factory=lambda: [
        ProfitSplitTier(cumulative_profit_threshold=0.0, trader_split_pct=90.0, firm_split_pct=10.0)
    ])
    
    def calculate_trader_payout(self, gross_profit: float) -> Dict[str, float]:
        """
        Calculate trader's payout from gross profit
        
        Returns:
            {
                'gross_profit': 5000,
                'trader_payout': 4500,
                'firm_share': 500,
                'split_pct': 90
            }
        """
        if not self.use_tiers:
            # Simple flat split
            return {
                'gross_profit': gross_profit,
                'trader_payout': gross_profit * (self.flat_split_pct / 100),
                'firm_share': gross_profit * ((100 - self.flat_split_pct) / 100),
                'split_pct': self.flat_split_pct,
            }
        
        # Tiered logic
        total_trader_payout = 0.0
        remaining_profit = gross_profit
        last_threshold = 0.0
        
        for tier in sorted(self.tiers, key=lambda t: t.cumulative_profit_threshold):
            if tier.cumulative_profit_threshold <= remaining_profit:
                slice_amount = min(remaining_profit - last_threshold, 
                                  remaining_profit - tier.cumulative_profit_threshold)
                total_trader_payout += slice_amount * (tier.trader_split_pct / 100)
                last_threshold = tier.cumulative_profit_threshold
        
        return {
            'gross_profit': gross_profit,
            'trader_payout': total_trader_payout,
            'firm_share': gross_profit - total_trader_payout,
            'split_pct': (total_trader_payout / gross_profit * 100) if gross_profit > 0 else 0,
        }


# ════════════════════════════════════════════════════════════════════════════
# SCALING & ACCOUNT GROWTH
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class ScalingMilestone:
    """Trigger point for account scaling"""
    
    profit_threshold: float = 5000.0                       # Scale after $5K profit
    new_account_size: Optional[float] = None               # New account balance
    max_contracts_multiplier: float = 2.0                  # New contract limit = old × 2


@dataclass
class ScalingPlan:
    """
    Account scaling rules - increase capital and limits after proving performance
    
    Example (Apex scaling):
        After $5K profit → $50K becomes $100K
        After $10K profit → $100K becomes $150K
    """
    
    scaling_enabled: bool = True
    scaling_type: ScalingType = ScalingType.MILESTONE
    
    milestones: List[ScalingMilestone] = field(default_factory=lambda: [
        ScalingMilestone(profit_threshold=5000.0, new_account_size=100000, max_contracts_multiplier=2.0),
        ScalingMilestone(profit_threshold=15000.0, new_account_size=200000, max_contracts_multiplier=3.0),
        ScalingMilestone(profit_threshold=30000.0, new_account_size=300000, max_contracts_multiplier=4.0),
    ])
    
    def get_scaling_at_profit(self, cumulative_profit: float) -> Optional[ScalingMilestone]:
        """Find applicable scaling tier at this profit level"""
        applicable = [m for m in self.milestones if m.profit_threshold <= cumulative_profit]
        return max(applicable, key=lambda m: m.profit_threshold) if applicable else None


# ════════════════════════════════════════════════════════════════════════════
# RESET & RECOVERY RULES
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class ResetRules:
    """Rules for resetting a failed account"""
    
    allow_reset: bool = True                               # Can trader reset account?
    reset_fee: float = 100.0                               # Fee to reset (flat)
    reset_fee_pct: Optional[float] = None                  # Or percentage of account
    
    max_resets_per_month: int = 1                          # Limit resets
    max_total_resets: int = 10                             # Lifetime reset limit
    
    resets_before_escalation: int = 3                      # After 3 resets, increase fee
    escalation_fee_multiplier: float = 2.0                 # 3rd+ reset costs 2× more


# ════════════════════════════════════════════════════════════════════════════
# COMPLETE PAYOUT RULES
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class PayoutRules:
    """
    Complete ruleset for payouts, consistency, and account growth
    
    Combines all payout-related logic
    """
    
    # Consistency
    consistency: ConsistencyRule = field(default_factory=ConsistencyRule)
    
    # Withdrawals
    withdrawal: WithdrawalRules = field(default_factory=WithdrawalRules)
    
    # Profit Split
    profit_split: ProfitSplitRules = field(default_factory=ProfitSplitRules)
    
    # Scaling
    scaling: ScalingPlan = field(default_factory=ScalingPlan)
    
    # Reset/Recovery
    reset: ResetRules = field(default_factory=ResetRules)


# ════════════════════════════════════════════════════════════════════════════
# PRESET PAYOUT CONFIGURATIONS
# ════════════════════════════════════════════════════════════════════════════

def create_apex_payout_rules() -> PayoutRules:
    """Apex: Simple 90% flat split, strong consistency"""
    return PayoutRules(
        consistency=ConsistencyRule(
            enabled=False,  # Apex doesn't enforce consistency
            best_day_max_pct=50.0,
        ),
        withdrawal=WithdrawalRules(
            min_account_age_days=0,
            min_payout_amount=500.0,
            payout_frequency=PayoutFrequency.WEEKLY,
        ),
        profit_split=ProfitSplitRules(
            flat_split_pct=90.0,
            use_tiers=False,
        ),
        scaling=ScalingPlan(
            scaling_enabled=True,
            milestones=[
                ScalingMilestone(5000, 100000, 2.0),
                ScalingMilestone(15000, 200000, 3.0),
            ]
        ),
    )


def create_lucid_payout_rules() -> PayoutRules:
    """Lucid: 90% flat split, STRONG 50% consistency rule"""
    return PayoutRules(
        consistency=ConsistencyRule(
            enabled=True,  # ENFORCE
            best_day_max_pct=50.0,
            violation_is_fatal=True,  # Failed if violated
        ),
        withdrawal=WithdrawalRules(
            min_account_age_days=5,
            min_payout_amount=500.0,
            payout_frequency=PayoutFrequency.WEEKLY,
        ),
        profit_split=ProfitSplitRules(
            flat_split_pct=90.0,
            use_tiers=False,
        ),
        scaling=ScalingPlan(
            scaling_enabled=True,
            milestones=[
                ScalingMilestone(3000, 100000, 2.0),
                ScalingMilestone(10000, 200000, 3.0),
            ]
        ),
    )


def create_topstep_payout_rules() -> PayoutRules:
    """Topstep: 90% flat, optional consistency, 2-phase payouts"""
    return PayoutRules(
        consistency=ConsistencyRule(
            enabled=False,  # Optional for Topstep
            best_day_max_pct=50.0,
        ),
        withdrawal=WithdrawalRules(
            min_account_age_days=0,
            min_payout_amount=500.0,
            payout_frequency=PayoutFrequency.WEEKLY,
        ),
        profit_split=ProfitSplitRules(
            flat_split_pct=90.0,
            use_tiers=False,
        ),
        scaling=ScalingPlan(
            scaling_enabled=False,  # Topstep scales via phase 2
        ),
    )
