"""
Pairs Trading Integration with Enhanced Backtest System
════════════════════════════════════════════════════════════════════════════

Integrates PairsTradingStrategy with the existing EnhancedBacktestRunner
for comprehensive pairs trading backtesting.

Usage:
    from hft.utils.pairs_backtest_integration import PairsBacktestIntegration
    
    integration = PairsBacktestIntegration(
        pair1='EURUSD',
        pair2='GBPUSD',
        account_size=10000,
        risk_pct=0.02,
    )
    
    results = integration.run_backtest(df1, df2, sl_pips=30, tp_pips=50)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from hft.strategies.pairs_trading_strategy import PairsTradingStrategy, PairsTradingAnalyzer
from hft.utils.pairs_backtest_engine import PairsBacktestEngine, TradeDirection


@dataclass
class PairsBacktestResult:
    """Complete backtest result for pairs trading"""
    
    # Trade statistics
    total_trades: int
    profitable_trades: int
    losing_trades: int
    win_rate: float
    
    # P&L metrics
    total_pnl: float
    return_pct: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    
    # Risk metrics
    max_drawdown: float
    sharpe_ratio: float
    
    # Additional info
    avg_trade_duration: float
    equity_curve: List[float]
    trades: List[Dict]
    strategy_params: Dict
    pair_analysis: Dict


class PairsBacktestIntegration:
    """
    Integrate pairs trading strategy with backtest system
    
    Provides:
    - Signal generation from pairs trading strategy
    - Comprehensive backtesting with both pairs
    - P&L calculation and statistics
    - Compatibility with existing backtest infrastructure
    """
    
    def __init__(
        self,
        pair1: str = 'EURUSD',
        pair2: str = 'GBPUSD',
        account_size: float = 10000,
        risk_pct: float = 0.02,
        lookback: int = 100,
        z_entry: float = 2.0,
        z_exit: float = 0.5,
        z_stop: float = 3.0,
        min_correlation: float = 0.70,
        volatility_threshold: float = 0.002,
    ):
        """
        Initialize pairs trading backtest
        
        Args:
            pair1: First currency pair
            pair2: Second currency pair
            account_size: Starting account size
            risk_pct: Risk percentage per trade
            lookback: Lookback window for calculations
            z_entry: Z-score entry threshold
            z_exit: Z-score exit threshold
            z_stop: Hard stop Z-score
            min_correlation: Minimum correlation threshold
            volatility_threshold: Volatility filter threshold
        """
        
        self.pair1_name = pair1
        self.pair2_name = pair2
        self.account_size = account_size
        self.risk_pct = risk_pct
        
        # Initialize strategy
        self.strategy = PairsTradingStrategy(
            pair1=pair1,
            pair2=pair2,
            lookback=lookback,
            z_entry=z_entry,
            z_exit=z_exit,
            z_stop=z_stop,
            min_correlation=min_correlation,
            volatility_threshold=volatility_threshold,
        )
        
        # Initialize analyzer
        self.analyzer = PairsTradingAnalyzer()
        
        # Initialize backtest engine
        self.backtest_engine = PairsBacktestEngine(
            account_size=account_size,
            risk_pct_per_trade=risk_pct,
            pair1_name=pair1,
            pair2_name=pair2,
        )
    
    def run_full_backtest(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        sl_pips: float = 30,
        tp_pips: float = 50,
        verbose: bool = True,
    ) -> PairsBacktestResult:
        """
        Run complete pairs trading backtest
        
        Args:
            df1: OHLCV DataFrame for pair1
            df2: OHLCV DataFrame for pair2
            sl_pips: Stop loss in pips (from entry extremes)
            tp_pips: Take profit in pips (for Z-score targets)
            verbose: Print progress information
            
        Returns:
            PairsBacktestResult with comprehensive metrics
        """
        
        if verbose:
            print("\n" + "="*80)
            print(f"PAIRS TRADING BACKTEST: {self.pair1_name} vs {self.pair2_name}")
            print("="*80)
            print(f"Account Size: ${self.account_size:,.2f}")
            print(f"Risk per Trade: {self.risk_pct*100:.1f}%")
            print(f"Strategy: {self.strategy.name}")
        
        # Step 1: Analyze pair relationship
        if verbose:
            print("\n[1/4] Analyzing pair relationship...")
        
        pair_analysis = self.analyzer.analyze_pair_relationship(df1, df2)
        
        if verbose:
            print(f"  Correlation: {pair_analysis['correlation']:.4f} {'✓' if pair_analysis['correlation'] > 0.7 else '✗'}")
            print(f"  Cointegrated: {pair_analysis['is_cointegrated']} (p={pair_analysis['cointegration_pvalue']:.4f})")
            print(f"  Hedge Ratio: {pair_analysis['hedge_ratio']:.4f}")
        
        # Check if suitable for trading
        if pair_analysis['correlation'] < 0.5:
            print(f"\n⚠️  WARNING: Low correlation ({pair_analysis['correlation']:.3f}), results may be poor")
        
        if not pair_analysis['is_cointegrated']:
            print(f"\n⚠️  WARNING: Not cointegrated (p={pair_analysis['cointegration_pvalue']:.3f}), relationship may not hold")
        
        # Step 2: Generate signals
        if verbose:
            print("\n[2/4] Generating trading signals...")
        
        signals_df = self.strategy.generate_signals(df1, df2)
        
        signal_count = (signals_df['BUY'] == 1).sum()
        if verbose:
            print(f"  Signals generated: {signal_count}")
            print(f"  Entry threshold (Z): ±{self.strategy.z_entry}")
            print(f"  Exit threshold (Z): ±{self.strategy.z_exit}")
        
        # Step 3: Run backtest
        if verbose:
            print("\n[3/4] Running backtest simulation...")
        
        backtest_results = self.backtest_engine.backtest(
            signals_df, df2,
            z_exit_threshold=self.strategy.z_exit,
            z_stop_threshold=self.strategy.z_stop,
        )
        
        # Step 4: Format and display results
        if verbose:
            print("\n[4/4] Compiling results...")
        
        # Create result object
        result = self._format_results(backtest_results, pair_analysis)
        
        if verbose:
            self._print_results(result)
        
        return result
    
    def _format_results(self, backtest_results: Dict, pair_analysis: Dict) -> PairsBacktestResult:
        """Format backtest results into unified structure"""
        
        # Parse results
        total_trades = backtest_results.get('total_trades', 0)
        profitable = backtest_results.get('profitable_trades', 0)
        losing = backtest_results.get('losing_trades', 0)
        
        # Extract metrics
        try:
            total_pnl = float(backtest_results.get('total_pnl', '0').split()[0])
        except:
            total_pnl = 0
        
        try:
            return_pct = float(backtest_results.get('return_pct', '0%').rstrip('%'))
        except:
            return_pct = 0
        
        try:
            avg_win = float(backtest_results.get('avg_win', '0'))
        except:
            avg_win = 0
        
        try:
            avg_loss = float(backtest_results.get('avg_loss', '0'))
        except:
            avg_loss = 0
        
        try:
            profit_factor = float(backtest_results.get('profitfactor', '0').rstrip(':1'))
        except:
            profit_factor = 0 if avg_loss == 0 else abs(avg_win * profitable) / abs(avg_loss * losing) if losing > 0 else 0
        
        try:
            max_dd = backtest_results.get('max_drawdown', '0%').rstrip('%')
            max_drawdown = float(max_dd) / 100
        except:
            max_drawdown = 0
        
        try:
            sharpe = float(backtest_results.get('sharpe_ratio', '0'))
        except:
            sharpe = 0
        
        try:
            avg_duration = float(backtest_results.get('avg_bars_per_trade', '0'))
        except:
            avg_duration = 0
        
        # Calculate win rate
        win_rate = (profitable / total_trades * 100) if total_trades > 0 else 0
        
        return PairsBacktestResult(
            total_trades=total_trades,
            profitable_trades=profitable,
            losing_trades=losing,
            win_rate=win_rate,
            total_pnl=total_pnl,
            return_pct=return_pct,
            avg_win=avg_win,
            avg_loss=abs(avg_loss),
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            avg_trade_duration=avg_duration,
            equity_curve=self.backtest_engine.balance_curve,
            trades=backtest_results.get('trades', []),
            strategy_params=self.strategy.get_parameters(),
            pair_analysis=pair_analysis,
        )
    
    def _print_results(self, result: PairsBacktestResult):
        """Print formatted backtest results"""
        
        print("\n" + "="*80)
        print("BACKTEST RESULTS")
        print("="*80)
        
        print(f"\n📊 Trade Statistics:")
        print(f"  Total Trades: {result.total_trades}")
        print(f"  Winning Trades: {result.profitable_trades}")
        print(f"  Losing Trades: {result.losing_trades}")
        print(f"  Win Rate: {result.win_rate:.1f}%")
        print(f"  Avg Trade Duration: {result.avg_trade_duration:.0f} bars")
        
        print(f"\n💰 Profit & Loss:")
        print(f"  Total P&L: ${result.total_pnl:,.2f}")
        print(f"  Return: {result.return_pct:.2f}%")
        print(f"  Avg Win: ${result.avg_win:,.2f}")
        print(f"  Avg Loss: ${result.avg_loss:,.2f}")
        print(f"  Profit Factor: {result.profit_factor:.2f}:1" if result.profit_factor > 0 else "  Profit Factor: N/A")
        
        print(f"\n📈 Risk Metrics:")
        print(f"  Max Drawdown: {result.max_drawdown*100:.2f}%")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        
        print(f"\n🔗 Pair Analysis:")
        print(f"  Correlation: {result.pair_analysis['correlation']:.4f}")
        print(f"  Hedge Ratio: {result.pair_analysis['hedge_ratio']:.4f}")
        print(f"  Cointegrated: {result.pair_analysis['is_cointegrated']}")
        
        # Quality assessment
        print(f"\n✅ Quality Assessment:")
        
        if result.win_rate > 55:
            print(f"  ✓ Win Rate: {result.win_rate:.1f}% (Good)")
        else:
            print(f"  ✗ Win Rate: {result.win_rate:.1f}% (Low)")
        
        if result.pair_analysis['correlation'] > 0.7:
            print(f"  ✓ Correlation: {result.pair_analysis['correlation']:.3f} (Suitable)")
        else:
            print(f"  ✗ Correlation: {result.pair_analysis['correlation']:.3f} (Low)")
        
        if result.pair_analysis['is_cointegrated']:
            print(f"  ✓ Cointegration: True (Valid relationship)")
        else:
            print(f"  ✗ Cointegration: False (Unreliable)")
        
        print("\n" + "="*80)
    
    def optimize_parameters(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        z_entry_range: Tuple[float, float, float] = (1.5, 2.5, 0.1),
        z_exit_range: Tuple[float, float, float] = (0.3, 0.7, 0.1),
        z_stop_range: Tuple[float, float, float] = (2.8, 3.5, 0.2),
    ) -> Dict:
        """
        Optimize strategy parameters via grid search
        
        Args:
            df1, df2: DataFrames with price data
            z_entry_range: (min, max, step) for entry Z-score
            z_exit_range: (min, max, step) for exit Z-score
            z_stop_range: (min, max, step) for stop Z-score
            
        Returns:
            Dictionary with optimization results
        """
        
        print("\n" + "="*80)
        print("OPTIMIZING STRATEGY PARAMETERS")
        print("="*80)
        
        results = []
        z_entry_vals = np.arange(*z_entry_range)
        z_exit_vals = np.arange(*z_exit_range)
        z_stop_vals = np.arange(*z_stop_range)
        
        total_combos = len(z_entry_vals) * len(z_exit_vals) * len(z_stop_vals)
        print(f"\nTesting {total_combos} parameter combinations...\n")
        
        combo_count = 0
        
        for z_entry in z_entry_vals:
            for z_exit in z_exit_vals:
                for z_stop in z_stop_vals:
                    combo_count += 1
                    
                    # Create new strategy with these parameters
                    temp_strategy = PairsTradingStrategy(
                        pair1=self.pair1_name,
                        pair2=self.pair2_name,
                        lookback=self.strategy.lookback,
                        z_entry=z_entry,
                        z_exit=z_exit,
                        z_stop=z_stop,
                    )
                    
                    # Generate signals
                    signals = temp_strategy.generate_signals(df1, df2)
                    
                    # Run backtest
                    temp_engine = PairsBacktestEngine(
                        account_size=self.account_size,
                        risk_pct_per_trade=self.risk_pct,
                    )
                    
                    bt_results = temp_engine.backtest(signals, df2, z_exit, z_stop)
                    
                    # Extract key metrics
                    trades = bt_results.get('total_trades', 0)
                    if trades > 0:
                        win_rate = bt_results.get('profitable_trades', 0) / trades * 100
                        try:
                            pnl = float(bt_results.get('total_pnl', '0').split()[0])
                        except:
                            pnl = 0
                        
                        results.append({
                            'z_entry': z_entry,
                            'z_exit': z_exit,
                            'z_stop': z_stop,
                            'trades': trades,
                            'win_rate': win_rate,
                            'total_pnl': pnl,
                            'return_pct': (pnl / self.account_size) * 100,
                        })
                    
                    # Progress bar
                    if combo_count % max(1, total_combos // 10) == 0:
                        print(f"  Progress: {combo_count}/{total_combos} ({combo_count/total_combos*100:.0f}%)")
        
        # Sort by win rate and profit
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            results_df = results_df.sort_values('win_rate', ascending=False)
            
            print(f"\nTop 5 Parameter Combinations:")
            print("-" * 80)
            print(results_df.head(5).to_string(index=False))
            
            best = results_df.iloc[0]
            print(f"\n✓ Best Configuration:")
            print(f"  Z-Entry: {best['z_entry']:.1f}")
            print(f"  Z-Exit: {best['z_exit']:.1f}")
            print(f"  Z-Stop: {best['z_stop']:.1f}")
            print(f"  Win Rate: {best['win_rate']:.1f}%")
            print(f"  Total P&L: ${best['total_pnl']:,.2f}")
        else:
            print("No results found")
        
        return {
            'all_results': results_df,
            'best_params': results_df.iloc[0].to_dict() if len(results_df) > 0 else None,
        }
    
    def export_results_to_csv(self, result: PairsBacktestResult, filename: str):
        """Export backtest results to CSV"""
        
        # Trade details
        trades_df = pd.DataFrame(result.trades)
        trades_df.to_csv(f"{filename}_trades.csv", index=False)
        
        # Equity curve
        equity_df = pd.DataFrame({
            'bar': range(len(result.equity_curve)),
            'equity': result.equity_curve,
        })
        equity_df.to_csv(f"{filename}_equity.csv", index=False)
        
        print(f"\n✓ Results exported to {filename}_trades.csv and {filename}_equity.csv")
