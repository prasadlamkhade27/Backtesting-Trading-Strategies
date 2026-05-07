"""
PropFirm Account & Funding Rule Engine
═════════════════════════════════════════════════════════════════════════
Comprehensive data models for account lifecycle, phases, and evaluation rules.

Supports:
- One-step and two-step evaluations
- Fixed and trailing drawdown (intraday/EOD)
- Profit targets (absolute/percentage)
- Time limits and minimum trading days
- Phase transitions with rule breaches
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Literal
from enum import Enum


# ════════════════════════════════════════════════════════════════════════════
# ENUMS - Rule Types and Modes
# ════════════════════════════════════════════════════════════════════════════

class EvaluationType(Enum):
    """Type of evaluation process"""
    ONE_STEP = "one_step"  # Single phase (Apex, Lucid)
    TWO_STEP = "two_step"  # Two phases (Topstep)


class DrawdownType(Enum):
    """Type of drawdown calculation"""
    FIXED = "fixed"                    # Max loss from initial
    TRAILING = "trailing"              # Trailing from peak


class TrailMode(Enum):
    """When trailing drawdown threshold updates"""
    INTRADAY = "intraday"              # Real-time (strict, Apex-style)
    END_OF_DAY = "end_of_day"          # After market close (realistic)


class ProfitTargetType(Enum):
    """Type of profit target"""
    ABSOLUTE = "absolute"              # Fixed dollar amount
    PERCENTAGE = "percentage"          # Percentage of account


# ════════════════════════════════════════════════════════════════════════════
# PHASE RULES - Individual evaluation phase configuration
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class PhaseRules:
    """
    Configuration for a single evaluation phase
    
    Example (Lucid $50K):
        profit_target: 3000
        profit_target_pct: 6
        max_drawdown: 2500
        trailing_drawdown: true
        trail_mode: "end_of_day"
        min_days: 5
        max_days: None
    """
    
    # Profit Target
    profit_target: float = 3000.0                          # Absolute profit target in dollars
    profit_target_pct: float = 6.0                         # Percentage profit target (e.g., 6%)
    profit_target_type: ProfitTargetType = ProfitTargetType.ABSOLUTE
    
    # Drawdown Configuration
    drawdown_type: DrawdownType = DrawdownType.TRAILING    # Fixed vs Trailing
    max_drawdown: float = 2500.0                           # Max loss allowed (dollars)
    max_drawdown_pct: Optional[float] = None               # Alternative: as percentage
    
    # Trailing Drawdown Specifics
    trailing_drawdown: bool = True                         # Enable trailing?
    trail_mode: TrailMode = TrailMode.END_OF_DAY          # Intraday vs EOD update
    trail_offset: float = 2500.0                           # Amount below peak (dollars)
    trail_offset_pct: Optional[float] = None               # Alternative: as percentage
    
    # Time Requirements
    min_days: int = 5                                       # Minimum trading days
    max_days: Optional[int] = None                         # Max days to complete (None = unlimited)
    
    # Trading Day Definition
    min_trades_per_day: int = 1                            # At least 1 trade = trading day
    
    # Additional Rules
    max_consecutive_losses: Optional[int] = None           # Stop after N losses (optional)
    consistency_rule_pct: Optional[float] = None           # Best day ≤ X% of total profit


@dataclass
class AccountConfig:
    """
    Complete account configuration for a PropFirm challenge
    
    Example (Lucid $50K):
        initial_balance: 50000
        evaluation_type: ONE_STEP
        phases:
          - Phase 1 rules
    """
    
    # Account Identity
    account_id: str = "default"
    firm_name: str = "Custom"
    
    # Initial Funding
    initial_balance: float = 50000.0                       # Starting capital
    currency: str = "USD"
    
    # Evaluation Structure
    evaluation_type: EvaluationType = EvaluationType.ONE_STEP
    phases: List[PhaseRules] = field(default_factory=lambda: [PhaseRules()])
    
    # Account Status Thresholds
    phase_profit_hits: Dict[int, float] = field(default_factory=dict)  # Track when profit target hit
    phase_failure_reason: Optional[str] = None             # Why account failed
    phase_failure_time: Optional[int] = None               # When it failed
    
    def get_target_phase(self, phase_num: int) -> Optional[PhaseRules]:
        """Get rules for a specific phase (1-indexed)"""
        if 0 <= phase_num - 1 < len(self.phases):
            return self.phases[phase_num - 1]
        return None
    
    def get_current_phase(self) -> int:
        """Determine current phase based on profit hits"""
        if self.evaluation_type == EvaluationType.ONE_STEP:
            return 1
        
        # Two-step: check if phase 1 completed
        if 1 in self.phase_profit_hits:
            return 2
        return 1


# ════════════════════════════════════════════════════════════════════════════
# PRESET CONFIGURATIONS - Pre-built firm profiles with exact rules
# ════════════════════════════════════════════════════════════════════════════

def create_apex_preset(account_size: float = 50000) -> AccountConfig:
    """
    Apex - Industry Standard Challenge
    
    ✅ Intraday Trailing Drawdown (most strict)
    ✅ 1-step evaluation
    ✅ No minimum trading days
    ✅ No consistency rule
    ✅ No daily loss limit
    """
    
    profit_target = account_size * 0.06  # 6% profit target
    max_dd = account_size * 0.05  # 5% max drawdown
    
    return AccountConfig(
        account_id="apex",
        firm_name="Apex",
        initial_balance=account_size,
        evaluation_type=EvaluationType.ONE_STEP,
        phases=[
            PhaseRules(
                profit_target=profit_target,
                profit_target_pct=6,
                profit_target_type=ProfitTargetType.PERCENTAGE,
                
                drawdown_type=DrawdownType.TRAILING,
                max_drawdown=max_dd,
                max_drawdown_pct=5,
                trail_mode=TrailMode.INTRADAY,  # 🔴 REAL-TIME = STRICT
                trailing_drawdown=True,
                trail_offset=max_dd,
                trail_offset_pct=5,
                
                min_days=0,  # No minimum
                max_days=None,  # Unlimited
            )
        ]
    )


def create_lucid_preset(account_size: float = 50000) -> AccountConfig:
    """
    Lucid - Flexible Challenge
    
    ✅ End-of-Day Trailing Drawdown (more realistic)
    ✅ 1-step evaluation
    ✅ 5-day minimum trading requirement
    ✅ 50% consistency rule (best day ≤ 50% profit)
    ✅ No daily loss limit
    """
    
    profit_target = account_size * 0.06  # 6% profit target
    max_dd = account_size * 0.05  # 5% max drawdown
    
    return AccountConfig(
        account_id="lucid",
        firm_name="Lucid",
        initial_balance=account_size,
        evaluation_type=EvaluationType.ONE_STEP,
        phases=[
            PhaseRules(
                profit_target=profit_target,
                profit_target_pct=6,
                profit_target_type=ProfitTargetType.PERCENTAGE,
                
                drawdown_type=DrawdownType.TRAILING,
                max_drawdown=max_dd,
                max_drawdown_pct=5,
                trail_mode=TrailMode.END_OF_DAY,  # 🟢 EOD = REALISTIC
                trailing_drawdown=True,
                trail_offset=max_dd,
                trail_offset_pct=5,
                
                min_days=5,  # MUST trade 5+ days
                max_days=None,  # Unlimited
                consistency_rule_pct=50,  # Best day ≤ 50% of profit
            )
        ]
    )


def create_topstep_preset(account_size: float = 50000) -> AccountConfig:
    """
    Topstep - 2-Step Evaluation
    
    ✅ Two phases (Phase 1 → Phase 2)
    ✅ End-of-Day Trailing Drawdown
    ✅ Daily loss limit ($1000)
    ✅ Phase 1: $3000 profit, Phase 2: $2000 profit
    ✅ Phase transition: Hit profit target + no rule breach
    """
    
    phase1_target = account_size * 0.06  # 6%
    phase2_target = account_size * 0.04  # 4%
    max_dd = account_size * 0.05  # 5%
    
    return AccountConfig(
        account_id="topstep",
        firm_name="Topstep",
        initial_balance=account_size,
        evaluation_type=EvaluationType.TWO_STEP,
        phases=[
            PhaseRules(  # Phase 1
                profit_target=phase1_target,
                profit_target_pct=6,
                drawdown_type=DrawdownType.TRAILING,
                max_drawdown=max_dd,
                max_drawdown_pct=5,
                trail_mode=TrailMode.END_OF_DAY,
                min_days=5,
                max_days=None,
            ),
            PhaseRules(  # Phase 2
                profit_target=phase2_target,
                profit_target_pct=4,
                drawdown_type=DrawdownType.TRAILING,
                max_drawdown=max_dd,
                max_drawdown_pct=5,
                trail_mode=TrailMode.END_OF_DAY,
                min_days=5,
                max_days=None,
            ),
        ]
    )


# Preset registry
ACCOUNT_PRESETS = {
    "apex": create_apex_preset,
    "lucid": create_lucid_preset,
    "topstep": create_topstep_preset,
}
