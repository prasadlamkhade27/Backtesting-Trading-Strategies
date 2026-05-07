"""
Trading Restrictions & Risk Management Engine
═════════════════════════════════════════════════════════════════════════
Defines trading rules, position limits, session restrictions, and news trading rules.

Enforces:
- Position size limits per instrument
- Trading hour restrictions
- Overnight holding rules
- News trading blackout periods
- Holiday restrictions
- Daily/weekly/monthly loss limits
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from enum import Enum
from datetime import time, datetime


# ════════════════════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════════════════════

class PositionSizingType(Enum):
    """How position sizes are calculated"""
    FIXED = "fixed"                    # Fixed contracts (e.g., 1 contract)
    RISK_BASED = "risk_based"          # Based on account % risk


class CorrelationType(Enum):
    """How correlation limits are enforced"""
    DIRECTION = "direction"            # Long vs Short
    PRODUCT = "product"                # Related instruments
    SECTOR = "sector"                  # Industry correlation


# ════════════════════════════════════════════════════════════════════════════
# TRADING RESTRICTIONS - Session, Hours, News, Holidays
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class TradingSession:
    """Define a valid trading session"""
    name: str                                              # e.g., "CME_RTH"
    market: str                                            # e.g., "ES", "NQ"
    start_time: time = field(default_factory=lambda: time(9, 30))
    end_time: time = field(default_factory=lambda: time(16, 0))
    allow_trading: bool = True


@dataclass
class NewsRestriction:
    """Restrict trading around economic news events"""
    enabled: bool = True
    blackout_before_minutes: int = 2   # Don't trade N minutes before
    blackout_after_minutes: int = 2    # Don't trade N minutes after
    high_impact_only: bool = True      # Only for "High" impact events
    restricted_events: List[str] = field(default_factory=list)  # ["NFP", "FOMC", ...]


@dataclass
class TradingRules:
    """
    Complete trading restrictions and rules
    
    Example (Lucid):
        min_trading_days: 5
        max_contracts_per_symbol: {ES: 4, NQ: 3}
        allow_overnight: False
        allow_weekend: False
        max_daily_loss_pct: None
    """
    
    # ────────────────────────────────────────────────────────────────────────
    # TRADING DAYS & FREQUENCY
    # ────────────────────────────────────────────────────────────────────────
    min_trading_days: int = 5                              # Minimum trading days requirement
    max_trading_days: Optional[int] = None                 # Max days to complete (None = unlimited)
    
    # ────────────────────────────────────────────────────────────────────────
    # POSITION LIMITS
    # ────────────────────────────────────────────────────────────────────────
    max_contracts_total: int = 5                           # Total position limit
    max_contracts_per_symbol: Dict[str, int] = field(default_factory=lambda: {
        "ES": 4,
        "NQ": 3,
        "YM": 2,
        "RTY": 2,
        "CL": 2,
        "GC": 3,
        "XAUUSD": 5,
    })
    
    position_sizing_type: PositionSizingType = PositionSizingType.FIXED
    max_position_size_pct: float = 5.0                     # Max % of account per position
    
    # ────────────────────────────────────────────────────────────────────────
    # SESSION & HOURS RESTRICTIONS
    # ────────────────────────────────────────────────────────────────────────
    allow_regular_hours: bool = True                       # Standard market hours
    allow_pre_market: bool = False                         # Pre-market trading
    allow_after_hours: bool = False                        # After-hours trading
    allowed_sessions: List[str] = field(default_factory=lambda: ["CME_RTH"])
    
    # Trading hour windows (UTC, can override per session)
    market_open_hour: int = 9                              # e.g., 9 AM
    market_close_hour: int = 16                            # e.g., 4 PM
    
    # ────────────────────────────────────────────────────────────────────────
    # HOLDING RESTRICTIONS
    # ────────────────────────────────────────────────────────────────────────
    allow_overnight: bool = False                          # Can hold positions overnight
    allow_weekend: bool = False                            # Can hold over weekends
    max_holding_time_hours: Optional[int] = None           # Max hours to hold position
    min_holding_time_minutes: int = 1                      # Min time before exit
    
    # ────────────────────────────────────────────────────────────────────────
    # NEWS TRADING RULES
    # ────────────────────────────────────────────────────────────────────────
    news_restriction: NewsRestriction = field(default_factory=NewsRestriction)
    
    # ────────────────────────────────────────────────────────────────────────
    # HOLIDAY & MARKET CLOSURE
    # ────────────────────────────────────────────────────────────────────────
    trade_on_holidays: bool = False
    holiday_list: List[str] = field(default_factory=list)  # ["2024-12-25", "2024-01-01"]
    
    # ────────────────────────────────────────────────────────────────────────
    # CORRELATION LIMITS (Advanced)
    # ────────────────────────────────────────────────────────────────────────
    max_same_direction_positions: int = 3                  # Max concurrent long OR short
    correlation_type: CorrelationType = CorrelationType.DIRECTION
    
    # ────────────────────────────────────────────────────────────────────────
    # DAILY/WEEKLY/MONTHLY LOSS LIMITS
    # ────────────────────────────────────────────────────────────────────────
    enable_daily_loss_limit: bool = False                  # Some firms don't have this
    max_daily_loss_pct: Optional[float] = None             # e.g., 3% = $1500 on $50K
    max_daily_loss_amount: Optional[float] = None          # e.g., $1000 fixed
    
    max_weekly_loss_pct: Optional[float] = None
    max_weekly_loss_amount: Optional[float] = None
    
    max_monthly_loss_pct: Optional[float] = None
    max_monthly_loss_amount: Optional[float] = None


# ════════════════════════════════════════════════════════════════════════════
# RISK MANAGEMENT CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class RiskManagementRules:
    """
    Risk management and position sizing rules
    
    Example (Professional):
        risk_per_trade_pct: 1
        min_rr_ratio: 2
        max_account_drawdown: 20
    """
    
    # ────────────────────────────────────────────────────────────────────────
    # POSITION SIZING & RISK PER TRADE
    # ────────────────────────────────────────────────────────────────────────
    risk_per_trade_pct: float = 1.0                        # 1% of account per trade (standard)
    
    min_rr_ratio: float = 2.0                              # Minimum 1:2 Risk/Reward ratio
    min_win_rate_pct: float = 35.0                         # Minimum acceptable win rate
    
    # ────────────────────────────────────────────────────────────────────────
    # ACCOUNT DRAWDOWN LIMITS (may override phase rules)
    # ────────────────────────────────────────────────────────────────────────
    max_account_drawdown_pct: float = 20.0                 # Max 20% account drawdown
    max_consecutive_losing_trades: int = 5                 # Stop after N losses
    
    # ────────────────────────────────────────────────────────────────────────
    # TRADE QUALITY FILTERS
    # ────────────────────────────────────────────────────────────────────────
    min_volume_multiplier: float = 0.8                     # Min vol = 80% of average
    max_slippage_pips: float = 0.5                         # Max 0.5 pips slippage
    
    # ────────────────────────────────────────────────────────────────────────
    # TRADE REJECTION RULES
    # ────────────────────────────────────────────────────────────────────────
    reject_trades_below_rr: bool = True                    # Don't take low RR trades
    reject_countertrend_reversals: bool = False            # Don't go against trend
    reject_news_period_trades: bool = True                 # Don't trade news


# ════════════════════════════════════════════════════════════════════════════
# PRESET RULE CONFIGURATIONS
# ════════════════════════════════════════════════════════════════════════════

def create_apex_trading_rules() -> TradingRules:
    """Apex: Strict intraday rules"""
    return TradingRules(
        min_trading_days=0,              # No minimum
        max_contracts_total=5,
        allow_overnight=False,
        allow_weekend=False,
        trade_on_holidays=False,
        enable_daily_loss_limit=False,   # No daily loss limit
        news_restriction=NewsRestriction(enabled=False),  # Aggressive
    )


def create_lucid_trading_rules() -> TradingRules:
    """Lucid: Professional restrictions"""
    return TradingRules(
        min_trading_days=5,              # MUST trade 5+ days
        max_contracts_total=4,
        allow_overnight=False,
        allow_weekend=False,
        trade_on_holidays=False,
        enable_daily_loss_limit=False,   # No daily loss limit
        news_restriction=NewsRestriction(
            enabled=True,
            blackout_before_minutes=2,
            blackout_after_minutes=2,
        ),
    )


def create_topstep_trading_rules() -> TradingRules:
    """Topstep: Balanced restrictions"""
    return TradingRules(
        min_trading_days=5,
        max_contracts_total=6,
        allow_overnight=False,
        allow_weekend=False,
        trade_on_holidays=False,
        enable_daily_loss_limit=True,    # YES - has daily loss limit
        max_daily_loss_amount=1000,      # $1000 per day
        news_restriction=NewsRestriction(enabled=True),
    )


def create_risk_management_professional() -> RiskManagementRules:
    """Professional risk management - industry standard"""
    return RiskManagementRules(
        risk_per_trade_pct=1.0,
        min_rr_ratio=2.0,
        min_win_rate_pct=35.0,
        max_account_drawdown_pct=20.0,
        max_consecutive_losing_trades=5,
    )


def create_risk_management_conservative() -> RiskManagementRules:
    """Conservative risk management - for new traders"""
    return RiskManagementRules(
        risk_per_trade_pct=0.5,          # 0.5% per trade
        min_rr_ratio=3.0,                # Higher RR standard
        min_win_rate_pct=40.0,
        max_account_drawdown_pct=15.0,
        max_consecutive_losing_trades=3,
    )
