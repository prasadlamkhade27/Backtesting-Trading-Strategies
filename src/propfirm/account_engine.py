"""
Account Engine - Real-time Account Lifecycle Tracking
═════════════════════════════════════════════════════════════════════════
Core engine that tracks:
- Current balance, peak balance, drawdown
- Multiple drawdown types (fixed, intraday trailing, EOD trailing)
- Daily/weekly/monthly P&L
- Trading day count
- Phase transitions
- Account status and failure reasons
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from enum import Enum

from propfirm.account_rules import AccountConfig, PhaseRules, DrawdownType, TrailMode


# ════════════════════════════════════════════════════════════════════════════
# ENUMS
# ════════════════════════════════════════════════════════════════════════════

class AccountStatus(Enum):
    """Current account status"""
    ACTIVE = "active"                  # Trading, no violations
    FAILED = "failed"                  # Violated rules, account closed
    PASSED = "passed"                  # Hit profit target
    PENDING_PHASE_2 = "pending_phase_2"  # Completed phase 1, waiting for phase 2
    SUSPENDED = "suspended"            # Temporarily halted


# ════════════════════════════════════════════════════════════════════════════
# DAILY TRACKING
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class DailyRecord:
    """Track one trading day's activity"""
    
    date: date
    open_balance: float                 # Balance at start of day
    close_balance: float                # Balance at end of day
    daily_pnl: float = 0.0             # Profit/loss for the day
    trades_count: int = 0              # Number of trades
    is_trading_day: bool = False       # Meets min trades threshold?
    peak_balance: float = 0.0          # Highest balance during day
    intraday_drawdown: float = 0.0     # Lowest point in day


# ════════════════════════════════════════════════════════════════════════════
# ACCOUNT ENGINE - Main Class
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class AccountEngine:
    """
    Core account tracking engine
    
    Responsibilities:
    1. Real-time balance tracking
    2. Drawdown calculation (fixed, trailing intraday, trailing EOD)
    3. Peak balance management
    4. Daily/weekly/monthly P&L aggregation
    5. Trading day counting
    6. Phase transition logic
    7. Status and breach detection
    """
    
    # Configuration
    account_config: AccountConfig
    phase_rules: PhaseRules = field(default_factory=PhaseRules)
    
    # ────────────────────────────────────────────────────────────────────────
    # REAL-TIME BALANCES
    # ────────────────────────────────────────────────────────────────────────
    current_balance: float = 0.0       # Current account balance
    peak_balance: float = 0.0          # Highest balance ever reached
    peak_balance_date: Optional[date] = None  # When peak was set
    
    # Trailing peak (updates based on trail_mode)
    trailing_peak_balance: float = 0.0  # Peak for trailing DD calc
    trailing_peak_update_time: Optional[datetime] = None
    
    # ────────────────────────────────────────────────────────────────────────
    # DRAWDOWN TRACKING
    # ────────────────────────────────────────────────────────────────────────
    current_drawdown: float = 0.0      # Current loss from peak
    current_drawdown_pct: float = 0.0  # Drawdown as %
    max_drawdown_hit: float = 0.0      # Worst drawdown encountered
    max_drawdown_hit_pct: float = 0.0  # Max DD as %
    
    # Drawdown thresholds
    fixed_dd_threshold: float = 0.0    # Fixed: fixed amount below start
    trailing_dd_threshold: float = 0.0 # Trailing: peak - offset
    
    # ────────────────────────────────────────────────────────────────────────
    # P&L AGGREGATION
    # ────────────────────────────────────────────────────────────────────────
    cumulative_pnl: float = 0.0        # Total P&L from start
    cumulative_pnl_pct: float = 0.0    # As percentage
    
    # Daily tracking
    current_day_pnl: float = 0.0
    current_day_trades: int = 0
    daily_records: List[DailyRecord] = field(default_factory=list)
    
    # Weekly/Monthly
    current_week_pnl: float = 0.0
    current_month_pnl: float = 0.0
    
    # ────────────────────────────────────────────────────────────────────────
    # TRADING DAY COUNTING
    # ────────────────────────────────────────────────────────────────────────
    trading_days_count: int = 0        # # of days traded
    total_trades: int = 0              # # of total trades
    
    # ────────────────────────────────────────────────────────────────────────
    # PHASE & STATUS
    # ────────────────────────────────────────────────────────────────────────
    current_phase: int = 1             # Which phase are we in
    status: AccountStatus = AccountStatus.ACTIVE
    failure_reason: Optional[str] = None
    failure_timestamp: Optional[datetime] = None
    
    # Profit target progress
    phase_profit_target: float = 0.0   # Target for current phase
    phase_profit_hit: bool = False     # Hit target yet?
    
    # ────────────────────────────────────────────────────────────────────────
    # TIMESTAMPS
    # ────────────────────────────────────────────────────────────────────────
    account_open_time: Optional[datetime] = None
    last_trade_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize account engine"""
        self.current_balance = self.account_config.initial_balance
        self.peak_balance = self.account_config.initial_balance
        self.trailing_peak_balance = self.account_config.initial_balance
        
        # Set up phase
        self.phase_rules = self.account_config.get_target_phase(self.current_phase) or self.phase_rules
        
        # Calculate drawdown threshold
        if self.phase_rules.drawdown_type == DrawdownType.FIXED:
            self.fixed_dd_threshold = self.current_balance - self.phase_rules.max_drawdown
        elif self.phase_rules.drawdown_type == DrawdownType.TRAILING:
            self.trailing_dd_threshold = self.peak_balance - self.phase_rules.trail_offset
        
        # Set profit target
        if self.phase_rules.profit_target_type.value == "absolute":
            self.phase_profit_target = self.phase_rules.profit_target
        else:  # percentage
            self.phase_profit_target = self.current_balance * (self.phase_rules.profit_target_pct / 100)
        
        self.account_open_time = datetime.now()
    
    # ════════════════════════════════════════════════════════════════════════
    # BALANCE UPDATES
    # ════════════════════════════════════════════════════════════════════════
    
    def update_balance(self, pnl: float, trade_time: datetime) -> Dict[str, any]:
        """
        Update account balance after a trade
        
        Returns:
            {
                'new_balance': 50150,
                'current_dd': -150,
                'current_dd_pct': -0.3,
                'status': 'ACTIVE',
                'breach': None
            }
        """
        
        self.current_balance += pnl
        self.current_day_pnl += pnl
        self.current_day_trades += 1
        self.total_trades += 1
        self.cumulative_pnl = self.current_balance - self.account_config.initial_balance
        self.cumulative_pnl_pct = (self.cumulative_pnl / self.account_config.initial_balance) * 100
        
        # Check for new peak
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
            self.peak_balance_date = trade_time.date()
        
        self.last_trade_time = trade_time
        
        # Update drawdown based on type
        breach = self._update_drawdown(trade_time)
        
        return {
            'new_balance': self.current_balance,
            'current_dd': self.current_drawdown,
            'current_dd_pct': self.current_drawdown_pct,
            'status': self.status.value,
            'breach': breach,
        }
    
    def _update_drawdown(self, timestamp: datetime) -> Optional[str]:
        """
        Calculate current drawdown and check for threshold breach
        
        Returns:
            Reason for breach (if any)
        """
        
        if self.phase_rules.drawdown_type == DrawdownType.FIXED:
            # Fixed drawdown: loss from initial balance
            self.fixed_dd_threshold = self.account_config.initial_balance - self.phase_rules.max_drawdown
            self.current_drawdown = self.current_balance - self.account_config.initial_balance
            self.current_drawdown_pct = (self.current_drawdown / self.account_config.initial_balance) * 100
            
            if self.current_balance < self.fixed_dd_threshold:
                self.status = AccountStatus.FAILED
                return f"Fixed drawdown breach: ${abs(self.current_drawdown):.2f}"
        
        elif self.phase_rules.drawdown_type == DrawdownType.TRAILING:
            # Trailing drawdown
            if self.phase_rules.trail_mode == TrailMode.INTRADAY:
                # Update threshold EVERY trade (strict)
                if self.current_balance > self.trailing_peak_balance:
                    self.trailing_peak_balance = self.current_balance
                
                self.trailing_dd_threshold = self.trailing_peak_balance - self.phase_rules.trail_offset
                self.current_drawdown = self.current_balance - self.trailing_peak_balance
                self.current_drawdown_pct = (self.current_drawdown / self.trailing_peak_balance * 100) if self.trailing_peak_balance > 0 else 0
                
                if self.current_balance < self.trailing_dd_threshold:
                    self.status = AccountStatus.FAILED
                    return f"Intraday trailing DD breach: ${abs(self.current_drawdown):.2f} from peak ${self.trailing_peak_balance:.2f}"
            
            elif self.phase_rules.trail_mode == TrailMode.END_OF_DAY:
                # Update threshold only at day end (realistic)
                # For now, use peak as trailing peak (will be updated at day boundary)
                if self.current_balance > self.trailing_peak_balance:
                    self.trailing_peak_balance = self.current_balance
                
                self.trailing_dd_threshold = self.trailing_peak_balance - self.phase_rules.trail_offset
                self.current_drawdown = self.current_balance - self.trailing_peak_balance
                self.current_drawdown_pct = (self.current_drawdown / self.trailing_peak_balance * 100) if self.trailing_peak_balance > 0 else 0
                
                if self.current_balance < self.trailing_dd_threshold:
                    self.status = AccountStatus.FAILED
                    return f"EOD trailing DD breach: ${abs(self.current_drawdown):.2f} from peak ${self.trailing_peak_balance:.2f}"
        
        # Track max drawdown hit
        if abs(self.current_drawdown) > abs(self.max_drawdown_hit):
            self.max_drawdown_hit = self.current_drawdown
            self.max_drawdown_hit_pct = self.current_drawdown_pct
        
        return None
    
    # ════════════════════════════════════════════════════════════════════════
    # PROFIT TARGET & PHASE TRANSITIONS
    # ════════════════════════════════════════════════════════════════════════
    
    def check_profit_target(self) -> Tuple[bool, Optional[str]]:
        """
        Check if phase profit target was hit
        
        Returns:
            (target_hit: bool, reason_if_passed: str)
        """
        
        if self.cumulative_pnl >= self.phase_profit_target:
            self.phase_profit_hit = True
            
            if self.current_phase == 1:
                if self.account_config.evaluation_type.value == "one_step":
                    return True, "PASSED_ONE_STEP"
                else:  # two_step
                    return False, "PHASE_1_COMPLETE_MOVE_TO_PHASE_2"
            elif self.current_phase == 2:
                return True, "PASSED_TWO_STEP"
        
        return False, None
    
    def advance_to_phase_2(self):
        """
        Transition from Phase 1 to Phase 2
        
        Only valid for two-step evaluation
        """
        if self.account_config.evaluation_type.value != "two_step":
            raise ValueError("Can't advance to phase 2 in one-step evaluation")
        
        if not self.phase_profit_hit:
            raise ValueError("Must complete phase 1 profit target first")
        
        self.current_phase = 2
        self.phase_profit_hit = False
        self.current_day_pnl = 0.0  # Reset for phase 2
        
        # Get new phase rules
        self.phase_rules = self.account_config.get_target_phase(2)
        self.phase_profit_target = self.phase_rules.profit_target
        
        # Reset peak balance for new phase
        self.trailing_peak_balance = self.current_balance
    
    # ════════════════════════════════════════════════════════════════════════
    # DAILY BOUNDARY HANDLING
    # ════════════════════════════════════════════════════════════════════════
    
    def close_trading_day(self, current_date: date) -> DailyRecord:
        """
        Record end-of-day metrics
        
        Called at market close each day
        """
        
        daily_record = DailyRecord(
            date=current_date,
            open_balance=self.current_balance - self.current_day_pnl,
            close_balance=self.current_balance,
            daily_pnl=self.current_day_pnl,
            trades_count=self.current_day_trades,
            is_trading_day=(self.current_day_trades >= self.phase_rules.min_trades_per_day),
            peak_balance=self.peak_balance,
        )
        
        self.daily_records.append(daily_record)
        
        # Update trading day count
        if daily_record.is_trading_day:
            self.trading_days_count += 1
        
        # Update trailing peak for EOD mode
        if self.phase_rules.trail_mode == TrailMode.END_OF_DAY:
            # Peak becomes trailing peak at day end
            if self.peak_balance > self.trailing_peak_balance:
                self.trailing_peak_balance = self.peak_balance
        
        # Reset daily counters
        self.current_day_pnl = 0.0
        self.current_day_trades = 0
        
        # Update weekly/monthly
        self.current_week_pnl += daily_record.daily_pnl
        self.current_month_pnl += daily_record.daily_pnl
        
        return daily_record
    
    # ════════════════════════════════════════════════════════════════════════
    # BREACHES & STATUS
    # ════════════════════════════════════════════════════════════════════════
    
    def fail_account(self, reason: str):
        """Mark account as failed"""
        self.status = AccountStatus.FAILED
        self.failure_reason = reason
        self.failure_timestamp = datetime.now()
    
    def get_status_summary(self) -> Dict[str, any]:
        """Get comprehensive account status"""
        return {
            'account_id': self.account_config.account_id,
            'status': self.status.value,
            'current_phase': self.current_phase,
            'balance': self.current_balance,
            'peak_balance': self.peak_balance,
            'cumulative_pnl': self.cumulative_pnl,
            'cumulative_pnl_pct': f"{self.cumulative_pnl_pct:.2f}%",
            'current_drawdown': self.current_drawdown,
            'current_drawdown_pct': f"{self.current_drawdown_pct:.2f}%",
            'max_drawdown_hit': self.max_drawdown_hit,
            'max_drawdown_hit_pct': f"{self.max_drawdown_hit_pct:.2f}%",
            'phase_profit_target': self.phase_profit_target,
            'phase_profit_hit': self.phase_profit_hit,
            'profit_progress_pct': f"{(self.cumulative_pnl / self.phase_profit_target * 100):.2f}%" if self.phase_profit_target > 0 else "0%",
            'trading_days': self.trading_days_count,
            'total_trades': self.total_trades,
            'failure_reason': self.failure_reason,
        }
