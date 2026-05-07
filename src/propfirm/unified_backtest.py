"""
Unified PropFirm Backtest Engine
═════════════════════════════════════════════════════════════════════════
MASTER ENGINE that integrates 3 layers:

1. MARKET ENGINE - Executes trades, calculates P&L
2. ACCOUNT ENGINE - Tracks balance, drawdown, phases
3. COMPLIANCE ENGINE - Validates rules, detects breaches

This is the main interface for running comprehensive prop firm backtests
with real account lifecycle simulation.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import traceback

from propfirm.account_rules import (
    AccountConfig, PhaseRules, EvaluationType,
    ACCOUNT_PRESETS
)
from propfirm.trading_rules import TradingRules, RiskManagementRules
from propfirm.payout_rules import PayoutRules
from propfirm.account_engine import AccountEngine, AccountStatus
from propfirm.compliance_engine import ComplianceEngine, BreachType
from propfirm.reporting_engine import ReportingEngine


class UnifiedPropFirmBacktest:
    """
    Master backtest engine combining all three layers
    
    Usage:
        backtest = UnifiedPropFirmBacktest(
            account_config=create_lucid_preset(50000),
            trading_rules=create_lucid_trading_rules(),
            risk_rules=create_risk_management_professional(),
            payout_rules=create_lucid_payout_rules(),
        )
        
        result = backtest.run(
            data=df_with_signals,
            symbol='ES',
            entry_col='BUY',
            exit_col='SELL',
        )
    """
    
    def __init__(
        self,
        account_config: AccountConfig,
        trading_rules: TradingRules,
        risk_rules: RiskManagementRules,
        payout_rules: PayoutRules,
    ):
        
        self.account_config = account_config
        self.trading_rules = trading_rules
        self.risk_rules = risk_rules
        self.payout_rules = payout_rules
        
        # Initialize engines
        self.account_engine = AccountEngine(account_config)
        self.compliance_engine = ComplianceEngine(
            account_engine=self.account_engine,
            account_config=account_config,
            trading_rules=trading_rules,
            risk_rules=risk_rules,
            payout_rules=payout_rules,
        )
        self.reporting_engine = ReportingEngine(
            account_engine=self.account_engine,
            compliance_engine=self.compliance_engine,
            payout_rules=payout_rules,
        )
        
        # Execution tracking
        self.current_position = None
        self.entry_price = 0.0
        self.entry_candle_idx = 0
        self.sl_level = 0.0
        self.tp_level = 0.0
        self.position_size = 0.0
        
        # State tracking
        self.execution_log = []
        self.current_date = None
        self.last_update_time = None
    
    # ════════════════════════════════════════════════════════════════════════
    # MAIN EXECUTION
    # ════════════════════════════════════════════════════════════════════════
    
    def run(
        self,
        data: pd.DataFrame,
        symbol: str = 'ES',
        entry_col: str = 'BUY',
        exit_col: str = 'SELL',
        sl_pips: float = 50,
        tp_pips: float = 100,
        init_time: Optional[datetime] = None,
    ) -> Dict:
        """
        Run complete backtest with all three layers
        
        Args:
            data: DataFrame with OHLC + signals
            symbol: Trading symbol (ES, NQ, YM, CL, GC, XAUUSD, etc.)
            entry_col: Column name for entry signals (BUY/SELL)
            exit_col: Column name for exit signals
            sl_pips: Stop loss distance in pips
            tp_pips: Take profit distance in pips
            init_time: Initial timestamp (defaults to now)
        
        Returns:
            Complete backtest result with:
            {
                'passed': bool,
                'reason': str,
                'summary': {...},
                'trades': [...],
                'daily_records': [...],
                'compliance': {...},
                'metrics': {...},
            }
        """
        
        try:
            if init_time is None:
                init_time = datetime.now()
            
            self.current_date = init_time.date()
            self.last_update_time = init_time
            
            # Normalize entry/exit columns
            if entry_col not in data.columns:
                if 'buy' in data.columns:
                    entry_col = 'buy'
                elif 'signal' in data.columns:
                    entry_col = 'signal'
            
            # Main backtest loop
            for idx in range(len(data)):
                row = data.iloc[idx]
                
                # Create timestamp for this candle
                if isinstance(row.name, datetime):
                    candle_time = row['timestamp'] if 'timestamp' in row else row.name
                else:
                    candle_time = init_time + pd.Timedelta(minutes=idx*5)  # Assume 5-min candles
                
                if not isinstance(candle_time, datetime):
                    candle_time = datetime.combine(self.current_date, datetime.min.time())
                
                # Check for day boundary
                if candle_time.date() != self.current_date:
                    self._handle_day_boundary(candle_time.date() - pd.Timedelta(days=1))
                    self.current_date = candle_time.date()
                
                self.last_update_time = candle_time
                
                # ════════════════════════════════════════════════
                # ENTRY LOGIC
                # ════════════════════════════════════════════════
                
                if self.current_position is None:
                    # Check for entry signal
                    has_buy_signal = row.get(entry_col, 0) if entry_col in row.index else False
                    has_sell_signal = row.get(exit_col, 0) if exit_col in row.index else False
                    
                    if has_buy_signal or has_sell_signal:
                        # Pre-entry validation
                        trade_request = {
                            'symbol': symbol,
                            'type': 'LONG' if has_buy_signal else 'SHORT',
                            'entry_price': row['close'],
                            'stop_loss': row['close'] - (sl_pips if has_buy_signal else -sl_pips),
                            'take_profit': row['close'] + (tp_pips if has_buy_signal else -tp_pips),
                            'position_size': 1,  # Simplified for now
                            'rr_ratio': tp_pips / sl_pips,
                        }
                        
                        # Check if trade can be entered
                        can_enter, block_reason = self.compliance_engine.validate_trade_entry(
                            trade_request,
                            candle_time
                        )
                        
                        if can_enter:
                            # Enter position
                            self.current_position = trade_request['type']
                            self.entry_price = trade_request['entry_price']
                            self.entry_candle_idx = idx
                            self.sl_level = trade_request['stop_loss']
                            self.tp_level = trade_request['take_profit']
                            self.position_size = trade_request['position_size']
                            
                            # Log entry
                            trade_record = {
                                'trade_num': len(self.execution_log) + 1,
                                'symbol': symbol,
                                'type': self.current_position,
                                'entry_price': self.entry_price,
                                'entry_time': candle_time,
                                'entry_candle': idx,
                                'stop_loss': self.sl_level,
                                'take_profit': self.tp_level,
                                'position_size': self.position_size,
                                'rr_ratio': trade_request.get('rr_ratio'),
                                'status': 'OPEN',
                            }
                            self.compliance_engine.trades_log.append(trade_record)
                            self.compliance_engine.daily_trades[self.current_date] = \
                                self.compliance_engine.daily_trades.get(self.current_date, []) + [trade_record]
                        else:
                            # Record rejection
                            pass  # Optional logging
                
                # ════════════════════════════════════════════════
                # EXIT LOGIC
                # ════════════════════════════════════════════════
                
                elif self.current_position is not None:
                    exit_price = None
                    exit_reason = None
                    profit = 0.0
                    
                    # Check exit conditions
                    if self.current_position == 'LONG':
                        if row['low'] <= self.sl_level:
                            exit_price = self.sl_level
                            exit_reason = 'SL_HIT'
                        elif row['high'] >= self.tp_level:
                            exit_price = self.tp_level
                            exit_reason = 'TP_HIT'
                        elif row.get(exit_col, 0):
                            exit_price = row['close']
                            exit_reason = 'SIGNAL'
                    
                    elif self.current_position == 'SHORT':
                        if row['high'] >= self.sl_level:
                            exit_price = self.sl_level
                            exit_reason = 'SL_HIT'
                        elif row['low'] <= self.tp_level:
                            exit_price = self.tp_level
                            exit_reason = 'TP_HIT'
                        elif row.get(exit_col, 0):
                            exit_price = row['close']
                            exit_reason = 'SIGNAL'
                    
                    if exit_price is not None:
                        # Calculate P&L
                        if self.current_position == 'LONG':
                            profit = (exit_price - self.entry_price) * self.position_size
                        else:  # SHORT
                            profit = (self.entry_price - exit_price) * self.position_size
                        
                        # Get current trade record
                        current_trade = self.compliance_engine.trades_log[-1]
                        current_trade['exit_price'] = exit_price
                        current_trade['exit_time'] = candle_time
                        current_trade['exit_candle'] = idx
                        current_trade['pnl'] = profit
                        current_trade['pnl_pct'] = (profit / (self.entry_price * self.position_size)) * 100 if self.entry_price > 0 else 0
                        current_trade['closed_reason'] = exit_reason
                        current_trade['status'] = 'CLOSED'
                        current_trade['candles_held'] = idx - self.entry_candle_idx
                        
                        # Post-exit validation
                        can_exit, block_reason = self.compliance_engine.validate_trade_exit(
                            current_trade,
                            exit_price,
                            candle_time
                        )
                        
                        if can_exit or exit_reason in ['SL_HIT', 'TP_HIT']:
                            # Update account
                            self.account_engine.update_balance(profit, candle_time)
                            
                            # Check compliance
                            breaches = self.compliance_engine.check_post_trade_compliance(
                                current_trade,
                                self.account_engine.current_balance,
                                candle_time
                            )
                            
                            # Check profit target
                            passed_phase, phase_reason = self.account_engine.check_profit_target()
                            
                            if passed_phase and self.account_config.evaluation_type == EvaluationType.ONE_STEP:
                                # Account passed!
                                return self._finalize_backtest(passed=True, reason=phase_reason or "PASSED_ONE_STEP")
                            
                            # Close position
                            self.current_position = None
                            self.account_engine.current_day_trades += 1
                        else:
                            # Trade blocked from exit (unlikely but possible)
                            pass
            
            # ════════════════════════════════════════════════════════════════
            # BACKTEST COMPLETE - Handle final day
            # ════════════════════════════════════════════════════════════════
            
            self._handle_day_boundary(self.current_date)
            
            # Close any open position at market close
            if self.current_position is not None:
                last_price = data.iloc[-1]['close']
                profit = (last_price - self.entry_price) * self.position_size if self.current_position == 'LONG' \
                        else (self.entry_price - last_price) * self.position_size
                self.account_engine.update_balance(profit, self.last_update_time)
            
            # Final determination
            passed, reason = self.reporting_engine.determine_pass_fail()
            
            return self._finalize_backtest(passed=passed, reason=reason)
        
        except Exception as e:
            return {
                'passed': False,
                'reason': f'Backtest error: {str(e)}',
                'error': traceback.format_exc(),
                'summary': None,
            }
    
    # ════════════════════════════════════════════════════════════════════════
    # BOUNDARY & FINALIZATION
    # ════════════════════════════════════════════════════════════════════════
    
    def _handle_day_boundary(self, end_date: date):
        """Process end-of-day logic"""
        
        day_record = self.account_engine.close_trading_day(end_date)
        
        # Daily compliance checks
        daily_breaches = self.compliance_engine.check_daily_boundary(
            end_date,
            datetime.combine(end_date, datetime.max.time())
        )
    
    def _finalize_backtest(self, passed: Optional[bool], reason: str) -> Dict:
        """Generate final backtest result"""
        
        return {
            'passed': passed,
            'reason': reason,
            'summary': self.reporting_engine.get_dashboard_summary(),
            'detailed_report': self.reporting_engine.get_detailed_report(),
            'trades': len(self.compliance_engine.trades_log),
            'daily_records': len(self.account_engine.daily_records),
            'compliance_score': self.compliance_engine.compliance_score,
        }
    
    # ════════════════════════════════════════════════════════════════════════
    # GETTERS & STATUS
    # ════════════════════════════════════════════════════════════════════════
    
    def get_live_status(self) -> Dict:
        """Get real-time account status"""
        return self.reporting_engine.get_dashboard_summary()
    
    def get_account_status_summary(self) -> Dict:
        """Get full account status"""
        return self.account_engine.get_status_summary()
    
    def get_compliance_report(self) -> Dict:
        """Get compliance violations"""
        return self.compliance_engine.get_compliance_report()
