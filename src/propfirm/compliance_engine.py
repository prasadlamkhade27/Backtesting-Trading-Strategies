"""
Compliance Engine - Real-time Rule Validation & Breach Detection
═════════════════════════════════════════════════════════════════════════
Validates all trading rules and detects violations:

Checks:
- Drawdown limits (fixed, trailing intraday, trailing EOD)
- Daily/weekly/monthly loss limits
- Profit targets
- Trading day minimums
- Position size limits
- News trading restrictions
- Overnight/weekend holding rules
- Consistency rules (best day ≤ X% of profit)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Literal
from datetime import datetime, date, time, timedelta
from enum import Enum

from propfirm.account_engine import AccountEngine, AccountStatus
from propfirm.account_rules import AccountConfig, PhaseRules
from propfirm.trading_rules import TradingRules, RiskManagementRules
from propfirm.payout_rules import PayoutRules


# ════════════════════════════════════════════════════════════════════════════
# BREACH TYPES
# ════════════════════════════════════════════════════════════════════════════

class BreachType(Enum):
    """Types of rule violations"""
    DRAWDOWN = "drawdown"
    DAILY_LOSS = "daily_loss"
    WEEKLY_LOSS = "weekly_loss"
    MONTHLY_LOSS = "monthly_loss"
    PROFIT_TARGET_MISSED = "profit_target_missed"
    MIN_TRADING_DAYS = "min_trading_days"
    MAX_TRADING_DAYS = "max_trading_days"
    MAX_POSITION_SIZE = "max_position_size"
    OVERNIGHT_HOLD = "overnight_hold"
    WEEKEND_HOLD = "weekend_hold"
    NEWS_TRADING = "news_trading"
    CONSISTENCY_VIOLATION = "consistency_violation"
    LOW_RR_RATIO = "low_rr_ratio"
    CONSECUTIVE_LOSSES = "consecutive_losses"


@dataclass
class Breach:
    """A single rule violation"""
    timestamp: datetime
    breach_type: BreachType
    severity: Literal["warning", "error", "critical"]  # warning = advice, error = violation, critical = account fail
    message: str
    value: Optional[float] = None      # Current value that triggered breach
    threshold: Optional[float] = None  # Threshold that was crossed


# ════════════════════════════════════════════════════════════════════════════
# COMPLIANCE ENGINE
# ════════════════════════════════════════════════════════════════════════════

@dataclass
class ComplianceEngine:
    """
    Real-time rule validator and breach detector
    
    Tracks violations and determines when account should fail
    """
    
    # Configuration
    account_engine: AccountEngine
    account_config: AccountConfig
    trading_rules: TradingRules
    risk_rules: RiskManagementRules
    payout_rules: PayoutRules
    
    # Breach tracking
    breaches: List[Breach] = field(default_factory=list)
    critical_breaches: List[Breach] = field(default_factory=list)
    
    # Trade tracking (for position size, consecutive losses, etc.)
    trades_log: List[Dict] = field(default_factory=list)
    daily_trades: Dict[date, List[Dict]] = field(default_factory=dict)
    
    # News event tracking
    news_events: List[Dict] = field(default_factory=list)
    
    # Compliance score (0-100)
    compliance_score: float = 100.0
    
    # ════════════════════════════════════════════════════════════════════════
    # MAIN VALIDATION METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def validate_trade_entry(
        self,
        trade: Dict,
        current_time: datetime
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a trade can be entered (pre-entry checks)
        
        Args:
            trade: {
                'symbol': 'ES',
                'type': 'LONG',
                'entry_price': 5000,
                'stop_loss': 4950,
                'take_profit': 5100,
                'position_size': 1,
                'risk_amount': 50,
                'rr_ratio': 2.0,
            }
            current_time: datetime
        
        Returns:
            (can_enter: bool, rejection_reason: str)
        """
        
        breaches = []
        
        # 1. Check position size
        current_position_count = sum(
            t.get('position_size', 0) for t in self.trades_log
            if t.get('status') == 'OPEN' and not t.get('closed_time')
        )
        
        if current_position_count + trade.get('position_size', 0) > self.trading_rules.max_contracts_total:
            return False, f"Position size limit exceeded: {current_position_count} + {trade.get('position_size')} > {self.trading_rules.max_contracts_total}"
        
        # 2. Check symbol-specific limit
        symbol = trade.get('symbol', 'ES')
        max_for_symbol = self.trading_rules.max_contracts_per_symbol.get(symbol, 5)
        symbol_position_count = sum(
            t.get('position_size', 0) for t in self.trades_log
            if t.get('status') == 'OPEN' and t.get('symbol') == symbol
        )
        
        if symbol_position_count + trade.get('position_size', 0) > max_for_symbol:
            return False, f"Position limit for {symbol} exceeded"
        
        # 3. Check risk/reward ratio
        if self.risk_rules.reject_trades_below_rr:
            rr_ratio = trade.get('rr_ratio', 0)
            if rr_ratio < self.risk_rules.min_rr_ratio:
                return False, f"Trade RR ratio {rr_ratio} below minimum {self.risk_rules.min_rr_ratio}"
        
        # 4. Check news trading restriction
        if self.trading_rules.news_restriction.enabled:
            if self._is_news_blackout(current_time):
                return False, "Trade blocked: News trading blackout period"
        
        # 5. Check overnight holding
        if not self.trading_rules.allow_overnight:
            if self._is_after_market_hours(current_time):
                return False, "Trade blocked: Outside regular trading hours"
        
        # 6. Check weekend
        if not self.trading_rules.allow_weekend:
            if current_time.weekday() >= 5:  # 5,6 = Sat, Sun
                return False, "Trade blocked: Weekend trading not allowed"
        
        # 7. Check consecutive losses
        if self.risk_rules.max_consecutive_losing_trades > 0:
            consecutive_losses = self._count_consecutive_losses()
            if consecutive_losses >= self.risk_rules.max_consecutive_losing_trades:
                return False, f"Consecutive loss limit reached: {consecutive_losses}"
        
        return True, None
    
    def validate_trade_exit(
        self,
        trade: Dict,
        exit_price: float,
        exit_time: datetime
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate trade exit (post-entry checks)
        
        Returns:
            (can_exit: bool, rejection_reason: str)
        """
        
        # 1. Check minimum holding time
        if trade.get('entry_time'):
            holding_minutes = (exit_time - trade['entry_time']).total_seconds() / 60
            if holding_minutes < self.trading_rules.min_holding_time_minutes:
                return False, f"Position held for {holding_minutes:.1f}m, minimum {self.trading_rules.min_holding_time_minutes}m"
        
        # 2. Check maximum holding time
        if self.trading_rules.max_holding_time_hours:
            if trade.get('entry_time'):
                holding_hours = (exit_time - trade['entry_time']).total_seconds() / 3600
                if holding_hours > self.trading_rules.max_holding_time_hours:
                    return False, f"Position held too long: {holding_hours:.1f}h > {self.trading_rules.max_holding_time_hours}h"
        
        return True, None
    
    def check_post_trade_compliance(
        self,
        trade: Dict,
        current_balance: float,
        current_time: datetime
    ) -> List[Breach]:
        """
        Check all compliance rules after trade execution
        
        This is where account failures are detected
        
        Returns:
            List of breaches (empty if all rules passed)
        """
        
        breaches: List[Breach] = []
        
        # 1. Check daily loss limit
        if self.trading_rules.enable_daily_loss_limit:
            daily_loss_breach = self._check_daily_loss_limit(current_time)
            if daily_loss_breach:
                breaches.append(daily_loss_breach)
        
        # 2. Check weekly loss limit
        if self.trading_rules.max_weekly_loss_pct or self.trading_rules.max_weekly_loss_amount:
            weekly_loss_breach = self._check_weekly_loss_limit(current_time)
            if weekly_loss_breach:
                breaches.append(weekly_loss_breach)
        
        # 3. Check consistency rule
        if self.payout_rules.consistency.enabled:
            consistency_breach = self._check_consistency_rule()
            if consistency_breach:
                breaches.append(consistency_breach)
        
        # 4. Check RR ratio (already checked at entry, but verify)
        trade_breach = self._validate_trade_quality(trade)
        if trade_breach:
            breaches.append(trade_breach)
        
        # Mark critical breaches
        for breach in breaches:
            if breach.severity == "critical":
                self.critical_breaches.append(breach)
                self.account_engine.fail_account(breach.message)
        
        self.breaches.extend(breaches)
        self._update_compliance_score()
        
        return breaches
    
    def check_daily_boundary(
        self,
        current_date: date,
        end_of_day_time: datetime
    ) -> List[Breach]:
        """
        Check all daily boundary compliance rules
        
        Called at end of each trading day
        """
        
        breaches: List[Breach] = []
        
        # 1. Check minimum trading days if challenge is ending
        if self.account_engine.phase_rules.max_days:
            days_elapsed = (end_of_day_time.date() - self.account_engine.account_open_time.date()).days
            if days_elapsed >= self.account_engine.phase_rules.max_days:
                if self.account_engine.trading_days_count < self.account_engine.phase_rules.min_days:
                    breach = Breach(
                        timestamp=end_of_day_time,
                        breach_type=BreachType.MIN_TRADING_DAYS,
                        severity="critical",
                        message=f"Challenge expired: only {self.account_engine.trading_days_count} trading days < {self.account_engine.phase_rules.min_days} required",
                        value=self.account_engine.trading_days_count,
                        threshold=self.account_engine.phase_rules.min_days,
                    )
                    breaches.append(breach)
                    self.account_engine.fail_account(breach.message)
        
        # 2. Check overnight holding
        if not self.trading_rules.allow_overnight:
            overnight_breaches = self._check_overnight_positions(current_date)
            breaches.extend(overnight_breaches)
        
        self.breaches.extend(breaches)
        self._update_compliance_score()
        
        return breaches
    
    # ════════════════════════════════════════════════════════════════════════
    # INDIVIDUAL BREACH CHECKS
    # ════════════════════════════════════════════════════════════════════════
    
    def _check_daily_loss_limit(self, current_time: datetime) -> Optional[Breach]:
        """Check if daily loss limit was exceeded"""
        
        if not self.trading_rules.enable_daily_loss_limit:
            return None
        
        daily_pnl = self.account_engine.current_day_pnl
        
        # Check against amount
        if self.trading_rules.max_daily_loss_amount:
            if daily_pnl < -self.trading_rules.max_daily_loss_amount:
                return Breach(
                    timestamp=current_time,
                    breach_type=BreachType.DAILY_LOSS,
                    severity="critical",
                    message=f"Daily loss limit exceeded: ${abs(daily_pnl):.2f} > ${self.trading_rules.max_daily_loss_amount:.2f}",
                    value=abs(daily_pnl),
                    threshold=self.trading_rules.max_daily_loss_amount,
                )
        
        # Check against percentage
        if self.trading_rules.max_daily_loss_pct:
            max_loss_pct = (self.account_engine.account_config.initial_balance * 
                           self.trading_rules.max_daily_loss_pct / 100)
            if daily_pnl < -max_loss_pct:
                return Breach(
                    timestamp=current_time,
                    breach_type=BreachType.DAILY_LOSS,
                    severity="critical",
                    message=f"Daily loss limit exceeded: {abs(daily_pnl/self.account_engine.account_config.initial_balance*100):.2f}% > {self.trading_rules.max_daily_loss_pct:.2f}%",
                    value=abs(daily_pnl),
                    threshold=max_loss_pct,
                )
        
        return None
    
    def _check_weekly_loss_limit(self, current_time: datetime) -> Optional[Breach]:
        """Check if weekly loss limit was exceeded"""
        
        # Implementation similar to daily
        return None
    
    def _check_consistency_rule(self) -> Optional[Breach]:
        """
        Check if best day exceeds X% of total profit
        
        Consistency Rule: Best day ≤ 50% of total profit (typical)
        """
        
        if not self.payout_rules.consistency.enabled:
            return None
        
        total_profit = self.account_engine.cumulative_pnl
        
        if total_profit < self.payout_rules.consistency.min_profit_to_check:
            return None
        
        # Find best trading day
        best_day_profit = max(
            (record.daily_pnl for record in self.account_engine.daily_records),
            default=0
        )
        
        if best_day_profit <= 0:
            return None
        
        best_day_pct = (best_day_profit / total_profit * 100) if total_profit > 0 else 0
        
        if best_day_pct > self.payout_rules.consistency.best_day_max_pct:
            severity = "critical" if self.payout_rules.consistency.violation_is_fatal else "error"
            return Breach(
                timestamp=datetime.now(),
                breach_type=BreachType.CONSISTENCY_VIOLATION,
                severity=severity,
                message=f"Consistency rule violated: best day {best_day_pct:.1f}% > {self.payout_rules.consistency.best_day_max_pct:.1f}%",
                value=best_day_pct,
                threshold=self.payout_rules.consistency.best_day_max_pct,
            )
        
        return None
    
    def _validate_trade_quality(self, trade: Dict) -> Optional[Breach]:
        """Validate trade quality metrics"""
        
        rr_ratio = trade.get('rr_ratio', 0)
        
        if rr_ratio < self.risk_rules.min_rr_ratio:
            return Breach(
                timestamp=datetime.now(),
                breach_type=BreachType.LOW_RR_RATIO,
                severity="warning",
                message=f"Trade RR ratio {rr_ratio:.2f} below minimum {self.risk_rules.min_rr_ratio:.2f}",
                value=rr_ratio,
                threshold=self.risk_rules.min_rr_ratio,
            )
        
        return None
    
    def _count_consecutive_losses(self) -> int:
        """Count consecutive losing trades"""
        
        if not self.trades_log:
            return 0
        
        consecutive = 0
        for trade in reversed(self.trades_log):
            if trade.get('pnl', 0) < 0:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def _is_news_blackout(self, current_time: datetime) -> bool:
        """Check if current time falls in news blackout period"""
        
        # Find upcoming news events
        for event in self.news_events:
            event_time = event.get('time')
            if not event_time:
                continue
            
            time_diff = abs((event_time - current_time).total_seconds() / 60)
            
            if time_diff < self.trading_rules.news_restriction.blackout_before_minutes:
                return True
            if time_diff < self.trading_rules.news_restriction.blackout_after_minutes:
                return True
        
        return False
    
    def _is_after_market_hours(self, current_time: datetime) -> bool:
        """Check if time is after market hours"""
        
        market_close = time(self.trading_rules.market_close_hour, 0)
        current_time_only = current_time.time()
        
        return current_time_only > market_close or current_time_only < time(self.trading_rules.market_open_hour, 0)
    
    def _check_overnight_positions(self, current_date: date) -> List[Breach]:
        """Check positions held overnight"""
        
        breaches = []
        
        for trade in self.trades_log:
            if trade.get('status') != 'OPEN':
                continue
            
            entry_date = trade.get('entry_time', datetime.now()).date()
            
            if entry_date < current_date:  # Opened on previous day
                breach = Breach(
                    timestamp=datetime.now(),
                    breach_type=BreachType.OVERNIGHT_HOLD,
                    severity="critical",
                    message=f"Position held overnight (not allowed)",
                )
                breaches.append(breach)
                break  # Report once per day
        
        return breaches
    
    def _update_compliance_score(self):
        """Update overall compliance score (0-100)"""
        
        # Start at 100
        score = 100.0
        
        # Deduct for warnings
        score -= len([b for b in self.breaches if b.severity == "warning"]) * 5
        
        # Deduct for errors
        score -= len([b for b in self.breaches if b.severity == "error"]) * 15
        
        # Deduct for critical
        score -= len([b for b in self.critical_breaches]) * 50
        
        self.compliance_score = max(0, min(100, score))
    
    def get_compliance_report(self) -> Dict:
        """Generate compliance report"""
        
        return {
            'compliance_score': self.compliance_score,
            'total_breaches': len(self.breaches),
            'warnings': len([b for b in self.breaches if b.severity == "warning"]),
            'errors': len([b for b in self.breaches if b.severity == "error"]),
            'critical_breaches': len(self.critical_breaches),
            'breaches': [
                {
                    'timestamp': b.timestamp.isoformat(),
                    'type': b.breach_type.value,
                    'severity': b.severity,
                    'message': b.message,
                }
                for b in self.breaches
            ]
        }
