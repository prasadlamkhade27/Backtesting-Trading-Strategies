"""
Reporting & Analytics Engine
═════════════════════════════════════════════════════════════════════════
Comprehensive analytics, performance metrics, and reporting

Provides:
- Real-time performance metrics
- Compliance dashboards
- Profitability analysis
- Risk metrics and analysis
- Trade-by-trade validation logs
- Account pass/fail determination
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import statistics


@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics"""
    
    # Basic Stats
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate_pct: float = 0.0
    
    # P&L
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    expectancy_per_trade: float = 0.0
    
    # Drawdown
    max_drawdown_pct: float = 0.0
    current_drawdown_pct: float = 0.0
    
    # Consistency
    best_day_pnl: float = 0.0
    best_day_pct: float = 0.0
    worst_day_pnl: float = 0.0
    worst_day_pct: float = 0.0
    
    # Days
    trading_days: int = 0
    calendar_days: int = 0
    
    # Risk
    risk_reward_ratio: float = 0.0
    consecutive_losing_trades: int = 0
    max_consecutive_losses: int = 0


class ReportingEngine:
    """
    Analytics and reporting engine
    """
    
    def __init__(self, account_engine, compliance_engine, payout_rules):
        self.account_engine = account_engine
        self.compliance_engine = compliance_engine
        self.payout_rules = payout_rules
        self.account_config = account_engine.account_config
    
    # ════════════════════════════════════════════════════════════════════════
    # PERFORMANCE METRICS
    # ════════════════════════════════════════════════════════════════════════
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        metrics = PerformanceMetrics()
        trades = self.compliance_engine.trades_log
        
        if not trades:
            return metrics
        
        # ────────────────────────────────────────────────────────────────────
        # BASIC TRADE STATS
        # ────────────────────────────────────────────────────────────────────
        metrics.total_trades = len(trades)
        metrics.winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        metrics.losing_trades = len([t for t in trades if t.get('pnl', 0) < 0])
        
        if metrics.total_trades > 0:
            metrics.win_rate_pct = (metrics.winning_trades / metrics.total_trades) * 100
        
        # ────────────────────────────────────────────────────────────────────
        # P&L METRICS
        # ────────────────────────────────────────────────────────────────────
        metrics.total_pnl = self.account_engine.cumulative_pnl
        metrics.total_pnl_pct = self.account_engine.cumulative_pnl_pct
        
        wins = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        losses = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]
        
        if wins:
            metrics.average_win = sum(wins) / len(wins)
        if losses:
            metrics.average_loss = sum(losses) / len(losses)
        
        # Profit Factor = Gross Profit / Gross Loss
        if losses:
            gross_profit = sum(wins) if wins else 0
            gross_loss = abs(sum(losses))
            metrics.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
        if metrics.total_trades > 0:
            win_pct = metrics.win_rate_pct / 100
            loss_pct = (100 - metrics.win_rate_pct) / 100
            metrics.expectancy_per_trade = (win_pct * metrics.average_win) - (loss_pct * abs(metrics.average_loss))
        
        # ────────────────────────────────────────────────────────────────────
        # DRAWDOWN
        # ────────────────────────────────────────────────────────────────────
        metrics.max_drawdown_pct = self.account_engine.max_drawdown_hit_pct
        metrics.current_drawdown_pct = self.account_engine.current_drawdown_pct
        
        # ────────────────────────────────────────────────────────────────────
        # CONSISTENCY
        # ────────────────────────────────────────────────────────────────────
        daily_pnls = [r.daily_pnl for r in self.account_engine.daily_records]
        
        if daily_pnls:
            metrics.best_day_pnl = max(daily_pnls)
            metrics.worst_day_pnl = min(daily_pnls)
            
            if self.account_engine.cumulative_pnl > 0:
                metrics.best_day_pct = (metrics.best_day_pnl / self.account_engine.cumulative_pnl) * 100
        
        # ────────────────────────────────────────────────────────────────────
        # DAYS
        # ────────────────────────────────────────────────────────────────────
        metrics.trading_days = self.account_engine.trading_days_count
        
        if self.account_engine.account_open_time:
            calendar_days = (datetime.now() - self.account_engine.account_open_time).days
            metrics.calendar_days = max(1, calendar_days)
        
        # ────────────────────────────────────────────────────────────────────
        # CONSECUTIVE LOSSES
        # ────────────────────────────────────────────────────────────────────
        metrics.consecutive_losing_trades = self._count_consecutive_losses()
        metrics.max_consecutive_losses = self._find_max_consecutive_losses()
        
        return metrics
    
    def _count_consecutive_losses(self) -> int:
        """Current consecutive losses"""
        trades = self.compliance_engine.trades_log
        if not trades:
            return 0
        
        count = 0
        for trade in reversed(trades):
            if trade.get('pnl', 0) < 0:
                count += 1
            else:
                break
        return count
    
    def _find_max_consecutive_losses(self) -> int:
        """Maximum consecutive losses ever"""
        trades = self.compliance_engine.trades_log
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade.get('pnl', 0) < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    # ════════════════════════════════════════════════════════════════════════
    # COMPLIANCE & RULE CHECKING
    # ════════════════════════════════════════════════════════════════════════
    
    def determine_pass_fail(self) -> Tuple[bool, Optional[str]]:
        """
        Determine if account passes or fails
        
        Returns:
            (passed: bool, reason: str)
        """
        
        # 1. Check for critical breaches
        if self.compliance_engine.critical_breaches:
            reason = self.compliance_engine.critical_breaches[0].message
            return False, reason
        
        # 2. Check account status
        if self.account_engine.status.value == "failed":
            return False, self.account_engine.failure_reason or "Account failed"
        
        # 3. Check if profit target hit
        passed_phase, reason = self.account_engine.check_profit_target()
        
        if not passed_phase and self.account_engine.current_phase == 1:
            # For one-step, if not passed and phase ended, fail
            if self.account_engine.phase_rules.max_days:
                days_elapsed = (datetime.now() - self.account_engine.account_open_time).days
                if days_elapsed >= self.account_engine.phase_rules.max_days:
                    return False, f"Challenge expired without hitting profit target"
        
        # 4. Check minimum trading days
        if self.account_engine.trading_days_count < self.account_engine.phase_rules.min_days:
            return False, f"Insufficient trading days: {self.account_engine.trading_days_count} < {self.account_engine.phase_rules.min_days}"
        
        # 5. Check consistency rule
        if self.payout_rules.consistency.enabled:
            consistency_breach = self.compliance_engine._check_consistency_rule()
            if consistency_breach and self.payout_rules.consistency.violation_is_fatal:
                return False, consistency_breach.message
        
        # If all checks passed and profit target hit
        if passed_phase:
            return True, reason
        
        # Still in progress
        return None, "Account in progress"
    
    # ════════════════════════════════════════════════════════════════════════
    # DASHBOARDS & REPORTS
    # ════════════════════════════════════════════════════════════════════════
    
    def get_dashboard_summary(self) -> Dict:
        """Generate dashboard summary for UI"""
        
        metrics = self.calculate_metrics()
        passed, reason = self.determine_pass_fail()
        
        return {
            'account_status': {
                'account_id': self.account_config.account_id,
                'firm_name': self.account_config.firm_name,
                'phase': self.account_engine.current_phase,
                'status': self.account_engine.status.value,
                'passed': passed,
                'reason': reason,
            },
            'balance': {
                'initial': self.account_config.initial_balance,
                'current': self.account_engine.current_balance,
                'peak': self.account_engine.peak_balance,
                'cumulative_pnl': self.account_engine.cumulative_pnl,
                'cumulative_pnl_pct': f"{self.account_engine.cumulative_pnl_pct:.2f}%",
            },
            'drawdown': {
                'current': f"{self.account_engine.current_drawdown_pct:.2f}%" if self.account_engine.current_drawdown_pct is not None else "N/A",
                'max': f"{self.account_engine.max_drawdown_hit_pct:.2f}%" if self.account_engine.max_drawdown_hit_pct is not None else "N/A",
                'threshold': f"-{self.account_engine.phase_rules.max_drawdown_pct:.2f}%" if self.account_engine.phase_rules.max_drawdown_pct else f"-{self.account_engine.phase_rules.max_drawdown:.2f} points",
            },
            'profit_target': {
                'target': f"${self.account_engine.phase_profit_target:.2f}",
                'current_progress': f"${self.account_engine.cumulative_pnl:.2f}",
                'progress_pct': f"{(self.account_engine.cumulative_pnl / self.account_engine.phase_profit_target * 100):.1f}%" if self.account_engine.phase_profit_target and self.account_engine.phase_profit_target > 0 else "0%",
                'hit': self.account_engine.phase_profit_hit,
            },
            'trading': {
                'total_trades': metrics.total_trades,
                'winning_trades': metrics.winning_trades,
                'losing_trades': metrics.losing_trades,
                'win_rate': f"{metrics.win_rate_pct:.1f}%",
                'profit_factor': f"{metrics.profit_factor:.2f}",
                'best_day': f"${metrics.best_day_pnl:.2f}",
                'worst_day': f"${metrics.worst_day_pnl:.2f}",
            },
            'days': {
                'trading_days': metrics.trading_days,
                'min_required': self.account_engine.phase_rules.min_days,
                'days_remaining': None,  # Calculate based on max_days
            },
            'compliance': {
                'score': f"{self.compliance_engine.compliance_score:.0f}/100",
                'breaches': len(self.compliance_engine.breaches),
                'critical_breaches': len(self.compliance_engine.critical_breaches),
            },
        }
    
    def get_detailed_report(self) -> Dict:
        """Generate detailed performance report"""
        
        metrics = self.calculate_metrics()
        
        return {
            'summary': self.get_dashboard_summary(),
            'performance_metrics': {
                'total_pnl': f"${metrics.total_pnl:.2f}",
                'total_pnl_pct': f"{metrics.total_pnl_pct:.2f}%",
                'win_rate': f"{metrics.win_rate_pct:.1f}%",
                'profit_factor': f"{metrics.profit_factor:.2f}",
                'expectancy': f"${metrics.expectancy_per_trade:.2f}",
                'average_win': f"${metrics.average_win:.2f}",
                'average_loss': f"${metrics.average_loss:.2f}",
                'best_day': f"${metrics.best_day_pnl:.2f}",
                'best_day_pct_of_total': f"{metrics.best_day_pct:.1f}%",
                'worst_day': f"${metrics.worst_day_pnl:.2f}",
                'max_consecutive_losses': metrics.max_consecutive_losses,
            },
            'daily_records': [
                {
                    'date': r.date.isoformat(),
                    'open_balance': r.open_balance,
                    'close_balance': r.close_balance,
                    'daily_pnl': r.daily_pnl,
                    'trades': r.trades_count,
                    'is_trading_day': r.is_trading_day,
                }
                for r in self.account_engine.daily_records
            ],
            'trade_log': [
                {
                    'trade_num': t.get('trade_num'),
                    'symbol': t.get('symbol'),
                    'type': t.get('type'),
                    'entry_price': t.get('entry_price'),
                    'exit_price': t.get('exit_price'),
                    'pnl': t.get('pnl'),
                    'pnl_pct': t.get('pnl_pct'),
                    'risk_reward': t.get('rr_ratio'),
                    'entry_time': str(t.get('entry_time')),
                    'exit_time': str(t.get('exit_time')),
                    'reason': t.get('closed_reason'),
                }
                for t in self.compliance_engine.trades_log
            ],
            'compliance': self.compliance_engine.get_compliance_report(),
        }
    
    # ════════════════════════════════════════════════════════════════════════
    # EXPORT & FORMATTING
    # ════════════════════════════════════════════════════════════════════════
    
    def export_csv_summary(self) -> str:
        """Export summary as CSV"""
        
        summary = self.get_dashboard_summary()
        
        lines = [
            "PropFirm Backtest Report",
            f"Account: {summary['account_status']['account_id']}",
            f"Firm: {summary['account_status']['firm_name']}",
            f"Status: {summary['account_status']['status']}",
            f"Result: {'PASSED' if summary['account_status']['passed'] else 'FAILED'}",
            f"Reason: {summary['account_status']['reason']}",
            "",
            "BALANCE",
            f"Initial,{summary['balance']['initial']}",
            f"Current,{summary['balance']['current']}",
            f"Peak,{summary['balance']['peak']}",
            f"P&L,{summary['balance']['cumulative_pnl']}",
            f"P&L %,{summary['balance']['cumulative_pnl_pct']}",
            "",
            "DRAWDOWN",
            f"Current,{summary['drawdown']['current']}",
            f"Max,{summary['drawdown']['max']}",
            f"Threshold,{summary['drawdown']['threshold']}",
            "",
            "TRADING",
            f"Total Trades,{summary['trading']['total_trades']}",
            f"Wins,{summary['trading']['winning_trades']}",
            f"Losses,{summary['trading']['losing_trades']}",
            f"Win Rate,{summary['trading']['win_rate']}",
            f"Profit Factor,{summary['trading']['profit_factor']}",
        ]
        
        return "\\n".join(lines)
