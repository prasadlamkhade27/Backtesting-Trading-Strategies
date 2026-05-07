"""
PropFirm Challenge Configuration
Contains all PropFirm rules and challenge settings
"""
from dataclasses import dataclass


@dataclass
class PhaseRules:
    """Rules for each phase of propfirm challenge"""
    daily_loss_limit: float  # Max loss per day (as % of account)
    max_loss_limit: float    # Max loss since start (as % of account)
    profit_target: float     # Profit target to pass (as % of account)
    min_trading_days: int    # Minimum trading days
    max_trades_per_day: int  # Max trades allowed per day


@dataclass
class PropFirm:
    """PropFirm challenge configuration"""
    name: str
    phase1: PhaseRules
    phase2: PhaseRules


# Predefined PropFirms with real-world rules
PROPFIRMS = {
    "FTMO": PropFirm(
        name="FTMO",
        phase1=PhaseRules(
            daily_loss_limit=0.05,      # 5% daily loss limit
            max_loss_limit=0.10,        # 10% max loss
            profit_target=0.10,         # 10% profit target
            min_trading_days=1,
            max_trades_per_day=999
        ),
        phase2=PhaseRules(
            daily_loss_limit=0.05,
            max_loss_limit=0.10,
            profit_target=0.05,         # 5% profit target (lower for phase 2)
            min_trading_days=1,
            max_trades_per_day=999
        ),
    ),
    "TradingView": PropFirm(
        name="TradingView",
        phase1=PhaseRules(
            daily_loss_limit=0.08,
            max_loss_limit=0.12,
            profit_target=0.08,
            min_trading_days=2,
            max_trades_per_day=100
        ),
        phase2=PhaseRules(
            daily_loss_limit=0.08,
            max_loss_limit=0.12,
            profit_target=0.06,
            min_trading_days=2,
            max_trades_per_day=100
        ),
    ),
    "MyForexFunds": PropFirm(
        name="MyForexFunds",
        phase1=PhaseRules(
            daily_loss_limit=0.03,
            max_loss_limit=0.08,
            profit_target=0.08,
            min_trading_days=3,
            max_trades_per_day=50
        ),
        phase2=PhaseRules(
            daily_loss_limit=0.03,
            max_loss_limit=0.08,
            profit_target=0.05,
            min_trading_days=3,
            max_trades_per_day=50
        ),
    ),
}

# Default custom propfirm template
DEFAULT_CUSTOM = PropFirm(
    name="Custom",
    phase1=PhaseRules(
        daily_loss_limit=0.05,
        max_loss_limit=0.10,
        profit_target=0.10,
        min_trading_days=1,
        max_trades_per_day=999
    ),
    phase2=PhaseRules(
        daily_loss_limit=0.05,
        max_loss_limit=0.10,
        profit_target=0.05,
        min_trading_days=1,
        max_trades_per_day=999
    ),
)
