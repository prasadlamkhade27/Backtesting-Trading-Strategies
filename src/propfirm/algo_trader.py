"""
Algorithmic Trading Engine
Automated trading execution based on strategies with risk management
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import time
import pandas as pd
import numpy as np


@dataclass
class AlgoConfig:
    """Configuration for algorithm trading"""
    strategy_name: str
    pairs: List[str]
    timeframe: str  # '1m', '5m', '15m', '1h', '4h', '1d'
    account_size: float
    risk_per_trade: float  # 0.01 = 1%
    max_concurrent_trades: int
    max_daily_loss: float  # Stop if daily loss exceeds this
    use_telegram: bool = False
    status: str = "STOPPED"  # STOPPED, RUNNING, PAUSED


@dataclass
class SignalRecord:
    """Record of a trading signal"""
    timestamp: str
    pair: str
    signal_type: str  # "BUY", "SELL", "NEUTRAL"
    confidence: float  # 0-1
    price: float
    strength: int  # 1-10 signal strength
    indicators: Dict = field(default_factory=dict)


@dataclass
class AlgoTrade:
    """Record of an automated trade"""
    trade_id: str
    pair: str
    side: str  # BUY, SELL
    entry_price: float
    entry_time: str
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    lot_size: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    status: str = "OPEN"  # OPEN, CLOSED
    reason_closed: Optional[str] = None


class RiskManager:
    """Manage risk for algorithmic trading"""
    
    def __init__(self, account_size: float, risk_per_trade: float):
        self.account_size = account_size
        self.risk_per_trade = risk_per_trade
        self.trades: List[AlgoTrade] = []
        self.daily_loss = 0.0
        self.reset_date = datetime.now().date()
    
    def calculate_lot_size(
        self,
        entry_price: float,
        stop_loss: float,
        pip_size: float = 0.0001
    ) -> float:
        """
        Calculate lot size based on risk management
        
        Risk = Account Size × Risk %
        Risk in Pips = |Entry - SL| / Pip Size
        Lot Size = Risk Amount / (Risk in Pips × Pip Value × 1 Lot)
        """
        risk_amount = self.account_size * self.risk_per_trade
        
        # Calculate pips at risk
        pips_at_risk = abs(entry_price - stop_loss) / pip_size
        
        if pips_at_risk <= 0:
            return 0.01  # Minimum 0.01 lot
        
        # For most pairs: 1 lot × 1 pip = $10
        # For JPY pairs: 1 lot × 1 pip = $1000
        pip_value_per_lot = 10  # Will be overridden for JPY
        
        lot_size = risk_amount / (pips_at_risk * pip_value_per_lot)
        
        # Constraints
        lot_size = max(lot_size, 0.01)  # Minimum
        lot_size = min(lot_size, 100.0)  # Maximum
        lot_size = round(lot_size, 2)
        
        return lot_size
    
    def check_daily_loss_limit(self, max_daily_loss: float) -> bool:
        """Check if daily loss limit exceeded"""
        # Reset if new day
        if datetime.now().date() != self.reset_date:
            self.daily_loss = 0.0
            self.reset_date = datetime.now().date()
        
        return self.daily_loss < max_daily_loss
    
    def update_daily_loss(self, trade: AlgoTrade):
        """Update daily loss tracking"""
        if trade.profit_loss and trade.profit_loss < 0:
            self.daily_loss += abs(trade.profit_loss)
    
    def get_max_concurrent_trades(self, max_trades: int, current_open: int) -> int:
        """Get number of new trades allowed"""
        return max(0, max_trades - current_open)


class StrategySignalGenerator:
    """Generate trading signals from strategy indicators"""
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.signal_history: List[SignalRecord] = []
    
    def generate_signal(
        self,
        df: pd.DataFrame,
        pair: str,
        indicators: Dict
    ) -> Optional[SignalRecord]:
        """
        Generate trading signal based on indicators
        
        Args:
            df: OHLCV data
            pair: Currency pair
            indicators: Dict with strategy indicators
        
        Returns:
            SignalRecord or None
        """
        if df.empty or len(df) < 2:
            return None
        
        current_price = df['close'].iloc[-1]
        
        # Strategy-specific signal generation
        if self.strategy_name == "Moving Average":
            return self._moving_average_signal(df, pair, current_price, indicators)
        elif self.strategy_name == "RSI":
            return self._rsi_signal(df, pair, current_price, indicators)
        elif self.strategy_name == "MACD":
            return self._macd_signal(df, pair, current_price, indicators)
        elif self.strategy_name == "Bollinger Bands":
            return self._bollinger_signal(df, pair, current_price, indicators)
        elif self.strategy_name == "Pivot Points":
            return self._pivot_signal(df, pair, current_price, indicators)
        
        return None
    
    def _moving_average_signal(
        self,
        df: pd.DataFrame,
        pair: str,
        price: float,
        indicators: Dict
    ) -> Optional[SignalRecord]:
        """Moving Average crossover strategy"""
        try:
            if len(df) < 50:
                return None
            
            # Calculate MAs
            ma_fast = df['close'].tail(20).mean()  # 20-period MA
            ma_slow = df['close'].tail(50).mean()  # 50-period MA
            
            # Get previous values
            ma_fast_prev = df['close'].iloc[-21:-1].mean()
            ma_slow_prev = df['close'].iloc[-51:-1].mean()
            
            # Determine signal
            if ma_fast > ma_slow and ma_fast_prev <= ma_slow_prev:
                signal_type = "BUY"
                confidence = 0.7
                strength = 7
            elif ma_fast < ma_slow and ma_fast_prev >= ma_slow_prev:
                signal_type = "SELL"
                confidence = 0.7
                strength = 7
            else:
                signal_type = "NEUTRAL"
                confidence = 0.5
                strength = 3
            
            return SignalRecord(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal_type=signal_type,
                confidence=confidence,
                price=price,
                strength=strength,
                indicators={'ma_fast': ma_fast, 'ma_slow': ma_slow}
            )
        except Exception as e:
            print(f"Error in MA signal: {e}")
            return None
    
    def _rsi_signal(
        self,
        df: pd.DataFrame,
        pair: str,
        price: float,
        indicators: Dict
    ) -> Optional[SignalRecord]:
        """RSI strategy (Overbought/Oversold)"""
        try:
            if len(df) < 14:
                return None
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Determine signal
            if current_rsi < 30:
                signal_type = "BUY"
                confidence = 0.75
                strength = 8
            elif current_rsi > 70:
                signal_type = "SELL"
                confidence = 0.75
                strength = 8
            else:
                signal_type = "NEUTRAL"
                confidence = 0.5
                strength = 4
            
            return SignalRecord(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal_type=signal_type,
                confidence=confidence,
                price=price,
                strength=strength,
                indicators={'rsi': current_rsi}
            )
        except Exception as e:
            print(f"Error in RSI signal: {e}")
            return None
    
    def _macd_signal(
        self,
        df: pd.DataFrame,
        pair: str,
        price: float,
        indicators: Dict
    ) -> Optional[SignalRecord]:
        """MACD strategy"""
        try:
            if len(df) < 26:
                return None
            
            # Calculate MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            
            current_hist = histogram.iloc[-1]
            prev_hist = histogram.iloc[-2]
            
            # Determine signal
            if current_hist > 0 and prev_hist <= 0:
                signal_type = "BUY"
                confidence = 0.72
                strength = 7
            elif current_hist < 0 and prev_hist >= 0:
                signal_type = "SELL"
                confidence = 0.72
                strength = 7
            else:
                signal_type = "NEUTRAL"
                confidence = 0.5
                strength = 4
            
            return SignalRecord(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal_type=signal_type,
                confidence=confidence,
                price=price,
                strength=strength,
                indicators={'macd': float(macd.iloc[-1]), 'signal': float(signal.iloc[-1])}
            )
        except Exception as e:
            print(f"Error in MACD signal: {e}")
            return None
    
    def _bollinger_signal(
        self,
        df: pd.DataFrame,
        pair: str,
        price: float,
        indicators: Dict
    ) -> Optional[SignalRecord]:
        """Bollinger Bands strategy"""
        try:
            if len(df) < 20:
                return None
            
            # Calculate Bollinger Bands
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            upper = sma + (std * 2)
            lower = sma - (std * 2)
            
            current_price = df['close'].iloc[-1]
            current_upper = upper.iloc[-1]
            current_lower = lower.iloc[-1]
            
            # Determine signal
            if current_price < current_lower:
                signal_type = "BUY"
                confidence = 0.68
                strength = 7
            elif current_price > current_upper:
                signal_type = "SELL"
                confidence = 0.68
                strength = 7
            else:
                signal_type = "NEUTRAL"
                confidence = 0.5
                strength = 4
            
            return SignalRecord(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal_type=signal_type,
                confidence=confidence,
                price=price,
                strength=strength,
                indicators={'upper_band': float(current_upper), 'lower_band': float(current_lower)}
            )
        except Exception as e:
            print(f"Error in Bollinger signal: {e}")
            return None
    
    def _pivot_signal(
        self,
        df: pd.DataFrame,
        pair: str,
        price: float,
        indicators: Dict
    ) -> Optional[SignalRecord]:
        """Pivot Points strategy"""
        try:
            if len(df) < 1:
                return None
            
            # Calculate pivot points
            h = df['high'].iloc[-1]
            l = df['low'].iloc[-1]
            c = df['close'].iloc[-1]
            
            pivot = (h + l + c) / 3
            resistance1 = (2 * pivot) - l
            support1 = (2 * pivot) - h
            
            current_price = df['close'].iloc[-1]
            
            # Determine signal
            if current_price < support1:
                signal_type = "BUY"
                confidence = 0.65
                strength = 6
            elif current_price > resistance1:
                signal_type = "SELL"
                confidence = 0.65
                strength = 6
            else:
                signal_type = "NEUTRAL"
                confidence = 0.5
                strength = 3
            
            return SignalRecord(
                timestamp=datetime.now().isoformat(),
                pair=pair,
                signal_type=signal_type,
                confidence=confidence,
                price=price,
                strength=strength,
                indicators={'pivot': pivot, 'resistance': resistance1, 'support': support1}
            )
        except Exception as e:
            print(f"Error in Pivot signal: {e}")
            return None


class AlgoTrader:
    """Main algorithmic trading engine - enhanced with ML"""
    
    def __init__(
        self,
        config: AlgoConfig,
        live_trader,
        data_loader,
        telegram_notifier=None
    ):
        self.config = config
        self.live_trader = live_trader
        self.data_loader = data_loader
        self.telegram_notifier = telegram_notifier
        
        self.risk_manager = RiskManager(config.account_size, config.risk_per_trade)
        self.signal_generator = StrategySignalGenerator(config.strategy_name)
        
        self.open_trades: Dict[str, AlgoTrade] = {}
        self.closed_trades: List[AlgoTrade] = []
        self.signals: List[SignalRecord] = []
        
        self.is_running = False
        self.thread = None
        self.trades_log_file = Path(".streamlit_credentials/algo_trades.json")
    
    def start(self) -> bool:
        """Start algo trading"""
        try:
            if not self.live_trader.is_connected:
                print("Trader not connected!")
                return False
            
            self.config.status = "RUNNING"
            self.is_running = True
            
            # Start trading loop in background thread
            self.thread = threading.Thread(target=self._trading_loop, daemon=True)
            self.thread.start()
            
            self._send_notification("✅ Algo Trading Started", f"Strategy: {self.config.strategy_name}")
            return True
        except Exception as e:
            print(f"Error starting algo trader: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop algo trading"""
        try:
            self.is_running = False
            self.config.status = "STOPPED"
            
            # Close all open trades
            for pair, trade in list(self.open_trades.items()):
                self._close_trade_internal(trade, "Stop requested")
            
            self._send_notification("⏹️ Algo Trading Stopped", "All open trades will be closed")
            return True
        except Exception as e:
            print(f"Error stopping algo trader: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause algo trading (don't close trades)"""
        self.is_running = False
        self.config.status = "PAUSED"
        self._send_notification("⏸️ Algo Trading Paused", "No new trades will be opened")
        return True
    
    def resume(self) -> bool:
        """Resume algo trading"""
        if self.live_trader.is_connected:
            self.is_running = True
            self.config.status = "RUNNING"
            self._send_notification("▶️ Algo Trading Resumed", "Trading signals active")
            return True
        return False
    
    def _trading_loop(self):
        """Main trading loop (runs in background thread)"""
        while self.is_running:
            try:
                for pair in self.config.pairs:
                    if not self.is_running:
                        break
                    
                    # Get data
                    df = self.data_loader.load_yfinance(pair, self.config.timeframe, "1d")
                    if df is None or df.empty:
                        continue
                    
                    # Generate signal
                    signal = self.signal_generator.generate_signal(df, pair, {})
                    self.signals.append(signal) if signal else None
                    
                    # Check if we should trade
                    if signal and signal.signal_type != "NEUTRAL" and signal.confidence > 0.6:
                        # Check if already trading this pair
                        if pair not in self.open_trades:
                            # Check limits
                            if self.risk_manager.check_daily_loss_limit(
                                self.config.account_size * self.config.max_daily_loss
                            ):
                                max_new_trades = self.risk_manager.get_max_concurrent_trades(
                                    self.config.max_concurrent_trades,
                                    len(self.open_trades)
                                )
                                
                                if max_new_trades > 0:
                                    # Open trade
                                    self._open_trade(pair, signal, df)
                
                # Check open trades for exit signals
                self._update_open_trades()
                
                # Sleep to avoid API rate limiting
                time.sleep(60)  # Check every 60 seconds
            
            except Exception as e:
                print(f"Error in trading loop: {e}")
                time.sleep(10)
    
    def _open_trade(self, pair: str, signal: SignalRecord, df: pd.DataFrame):
        """Open a new trade based on signal - with ML filtering"""
        try:
            entry_price = signal.price
            
            # Extract features for ML analysis
            features = self._extract_trade_features(df, pair)
            
            # Skip trade - ML filtering is disabled
            skip_trade = False
            
            # Regime adaptation - disabled
            regime_adapted_risk = self.config.risk_per_trade
            adapted_tp_sl_ratio = None
            
            # Calculate TP/SL based on strategy and regime
            sl, tp = self._calculate_tp_sl(entry_price, signal.signal_type, df, adapted_tp_sl_ratio)
            
            # Calculate lot size with adapted risk
            lot_size = self.risk_manager.calculate_lot_size(entry_price, sl)
            
            # Execute trade
            trade_id = self.live_trader.open_trade(
                pair=pair,
                side=signal.signal_type,
                entry_price=entry_price,
                lot_size=lot_size,
                stop_loss=sl,
                take_profit=tp
            )
            
            if trade_id:
                # Record trade
                trade = AlgoTrade(
                    trade_id=trade_id,
                    pair=pair,
                    side=signal.signal_type,
                    entry_price=entry_price,
                    entry_time=datetime.now().isoformat(),
                    lot_size=lot_size,
                    stop_loss=sl,
                    take_profit=tp,
                    status="OPEN"
                )
                
                self.open_trades[pair] = trade
                
                # Log to both JSON and database
                self._log_trade(trade)
                self._log_trade_to_db(trade, signal, features)
                
                # Send notification
                risk_amount = abs(tp - sl) * lot_size * 100000
                notification_msg = (
                    f"{pair} {signal.signal_type}\n"
                    f"Entry: {entry_price:.5f}\nSL: {sl:.5f}\nTP: {tp:.5f}\n"
                    f"Risk: ${risk_amount:.2f}\n"
                    f"Signal: {signal.confidence*100:.0f}%"
                )
                
                self._send_notification(f"🚀 Trade Opened", notification_msg)
        
        except Exception as e:
            print(f"Error opening trade: {e}")
    
    def _extract_trade_features(self, df: pd.DataFrame, pair: str) -> Dict:
        """Extract ML features from OHLCV data"""
        try:
            if df is None or df.empty or len(df) < 14:
                return {}
            
            features = {}
            
            # Trend Indicators
            if len(df) >= 20:
                features['ema_20'] = float(df['close'].ewm(span=20).mean().iloc[-1])
            if len(df) >= 50:
                features['ema_50'] = float(df['close'].ewm(span=50).mean().iloc[-1])
            if len(df) >= 200:
                features['ema_200'] = float(df['close'].ewm(span=200).mean().iloc[-1])
            
            # Trend direction
            if 'ema_20' in features and 'ema_50' in features:
                features['ema_trend'] = 1 if features['ema_20'] > features['ema_50'] else -1
            
            # RSI
            if len(df) >= 14:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                features['rsi'] = float(rsi.iloc[-1])
                features['rsi_period'] = 14
            
            # MACD
            if len(df) >= 26:
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal_line = macd.ewm(span=9, adjust=False).mean()
                features['macd_value'] = float(macd.iloc[-1])
                features['macd_signal'] = float(signal_line.iloc[-1])
                features['macd_histogram'] = float((macd - signal_line).iloc[-1])
            
            # Volatility & ATR
            if len(df) >= 14:
                atr = (df['high'] - df['low']).rolling(14).mean()
                features['atr'] = float(atr.iloc[-1])
                features['volatility'] = float(df['close'].pct_change().rolling(14).std().iloc[-1])
            
            # Bollinger Bands
            if len(df) >= 20:
                sma = df['close'].rolling(20).mean()
                std = df['close'].rolling(20).std()
                features['bollinger_upper'] = float((sma + std * 2).iloc[-1])
                features['bollinger_middle'] = float(sma.iloc[-1])
                features['bollinger_lower'] = float((sma - std * 2).iloc[-1])
            
            # Bar position in range
            if len(df) >= 1:
                h = df['high'].iloc[-1]
                l = df['low'].iloc[-1]
                c = df['close'].iloc[-1]
                if h > l:
                    features['bar_close_position'] = (c - l) / (h - l)
                    features['wick_ratio'] = (h - c) / (h - l) if (h - l) > 0 else 0.5
            
            # Session & Time
            current_hour = datetime.now().hour
            if 8 <= current_hour < 12:
                features['session'] = 'london'
            elif 13 <= current_hour < 18:
                features['session'] = 'newyork'
            elif 0 <= current_hour < 6:
                features['session'] = 'tokyo'
            else:
                features['session'] = 'other'
            
            features['time_of_day'] = 'morning' if 6 <= current_hour < 12 else 'afternoon' if 12 <= current_hour < 18 else 'night'
            features['day_of_week'] = datetime.now().strftime('%A')
            
            return features
        
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {}
    
    def _log_trade_to_db(self, trade: AlgoTrade, signal: SignalRecord, features: Dict):
        """Log trade to database with features"""
        if not self.enable_ml:
            return
        
        try:
            trade_dict = {
                'trade_id': trade.trade_id,
                'pair': trade.pair,
                'broker': 'Oanda',  # TODO: Get from live_trader
                'strategy': self.config.strategy_name,
                'direction': trade.side,
                'entry_time': trade.entry_time,
                'entry_price': trade.entry_price,
                'entry_lot_size': trade.lot_size,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit,
                'status': 'OPEN',
                'features': features
            }
            
            self.db.add_trade(trade_dict)
        except Exception as e:
            print(f"Error logging trade to database: {e}")
    
    def _calculate_tp_sl(self, entry_price: float, side: str, df: pd.DataFrame) -> Tuple[float, float]:
        """Calculate take profit and stop loss levels"""
        try:
            # Use ATR for dynamic TP/SL
            high = df['high'].tail(14).mean()
            low = df['low'].tail(14).mean()
            atr = (high - low) / 2
            
            if side == "BUY":
                sl = entry_price - (atr * 1.5)
                tp = entry_price + (atr * 3.0)
            else:  # SELL
                sl = entry_price + (atr * 1.5)
                tp = entry_price - (atr * 3.0)
            
            return sl, tp
        except Exception:
            # Fallback to fixed pips
            pip_size = 0.0001
            if side == "BUY":
                return entry_price - (30 * pip_size), entry_price + (50 * pip_size)
            else:
                return entry_price + (30 * pip_size), entry_price - (50 * pip_size)
    
    def _update_open_trades(self):
        """Check open trades for exit signals"""
        for pair, trade in list(self.open_trades.items()):
            try:
                # Get current price
                df = self.data_loader.load_yfinance(pair, "1m", "1d")
                if df is not None and not df.empty:
                    current_price = df['close'].iloc[-1]
                    
                    # Check SL/TP
                    if trade.side == "BUY":
                        if current_price <= trade.stop_loss:
                            self._close_trade_internal(trade, "Stop Loss Hit")
                        elif current_price >= trade.take_profit:
                            self._close_trade_internal(trade, "Take Profit Hit")
                    else:  # SELL
                        if current_price >= trade.stop_loss:
                            self._close_trade_internal(trade, "Stop Loss Hit")
                        elif current_price <= trade.take_profit:
                            self._close_trade_internal(trade, "Take Profit Hit")
            
            except Exception as e:
                print(f"Error updating trade {pair}: {e}")
    
    def _close_trade_internal(self, trade: AlgoTrade, reason: str):
        """Close a trade internally - with ML logging"""
        try:
            if self.live_trader.close_trade(trade.trade_id):
                trade.status = "CLOSED"
                trade.exit_time = datetime.now().isoformat()
                trade.reason_closed = reason
                trade.exit_price = 0  # Would need to fetch from broker in real implementation
                
                # Calculate P/L
                if trade.exit_price:
                    if trade.side == "BUY":
                        pips = (trade.exit_price - trade.entry_price) / 0.0001
                    else:
                        pips = (trade.entry_price - trade.exit_price) / 0.0001
                    
                    trade.profit_loss = pips * trade.lot_size * 10
                    trade.profit_loss_pct = (trade.profit_loss / 10000) * 100
                
                # Determine outcome
                outcome = 1 if (trade.profit_loss and trade.profit_loss > 0) else 0
                mae = 0  # Max Adverse Excursion
                mfe = 0  # Max Favorable Excursion
                
                # Move to closed trades
                self.closed_trades.append(trade)
                if trade.pair in self.open_trades:
                    del self.open_trades[trade.pair]
                
                self.risk_manager.update_daily_loss(trade)
                self._log_trade(trade)
                
                # Update in database
                if self.enable_ml:
                    try:
                        self.db.close_trade(
                            trade_id=trade.trade_id,
                            exit_time=trade.exit_time,
                            exit_price=trade.exit_price or 0,
                            pnl=trade.profit_loss or 0,
                            pnl_pct=trade.profit_loss_pct or 0,
                            mae=mae,
                            mfe=mfe,
                            outcome=outcome
                        )
                        
                        self.ml_status['trades_since_training'] += 1
                        
                        # Auto-train if interval reached
                        if self.ml_status['trades_since_training'] >= self.auto_train_interval:
                            print(f"Auto-training models after {self.auto_train_interval} trades...")
                            self.train_ml_models()
                    
                    except Exception as e:
                        print(f"Error updating trade in database: {e}")
                
                # Send notification
                pl_emoji = "🟢" if trade.profit_loss and trade.profit_loss >= 0 else "🔴"
                self._send_notification(
                    f"🏁 Trade Closed",
                    f"{trade.pair} {trade.side}\n{pl_emoji} P/L: ${trade.profit_loss or 0:.2f}\nReason: {reason}"
                )
        
        except Exception as e:
            print(f"Error closing trade: {e}")
    
    def _log_trade(self, trade: AlgoTrade):
        """Log trade to file"""
        try:
            self.trades_log_file.parent.mkdir(exist_ok=True)
            
            trades = []
            if self.trades_log_file.exists():
                with open(self.trades_log_file, 'r') as f:
                    trades = json.load(f)
            
            trade_dict = {
                'trade_id': trade.trade_id,
                'pair': trade.pair,
                'side': trade.side,
                'entry_price': trade.entry_price,
                'entry_time': trade.entry_time,
                'exit_price': trade.exit_price,
                'exit_time': trade.exit_time,
                'lot_size': trade.lot_size,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit,
                'profit_loss': trade.profit_loss,
                'profit_loss_pct': trade.profit_loss_pct,
                'status': trade.status,
                'reason': trade.reason_closed
            }
            
            trades.append(trade_dict)
            
            with open(self.trades_log_file, 'w') as f:
                json.dump(trades, f, indent=2)
        
        except Exception as e:
            print(f"Error logging trade: {e}")
    
    def _send_notification(self, title: str, message: str):
        """Send Telegram notification if configured"""
        if self.telegram_notifier and self.config.use_telegram:
            self.telegram_notifier.send_alert("INFO", f"{title}\n{message}")
    
    def get_status(self) -> Dict:
        """Get current trading status with ML insights"""
        status = {
            'config': {
                'strategy': self.config.strategy_name,
                'pairs': self.config.pairs,
                'status': self.config.status,
                'risk_per_trade': f"{self.config.risk_per_trade*100:.1f}%"
            },
            'open_trades': len(self.open_trades),
            'closed_trades': len(self.closed_trades),
            'daily_loss': self.risk_manager.daily_loss,
            'recent_signal': self.signals[-1] if self.signals else None
        }
        
        # Add ML information
        if self.enable_ml:
            status['ml_system'] = {
                'enabled': True,
                'loss_model_trained': self.ml_status['loss_model_trained'],
                'meta_model_trained': self.ml_status['meta_model_trained'],
                'regime_model_trained': self.ml_status['regime_model_trained'],
                'current_regime': self.ml_status['current_regime'],
                'trades_since_training': self.ml_status['trades_since_training'],
                'last_training_time': self.ml_status['last_training_time'],
                'auto_train_interval': self.auto_train_interval
            }
            
            # Add detailed ML insights
            if self.ml_status['loss_model_trained']:
                try:
                    insights = self.loss_analyzer.get_insights()
                    status['ml_insights'] = {
                        'top_loss_features': dict(list(insights.get('feature_importance', {}).items())[:3]),
                        'session_analysis': insights.get('session_analysis', {}),
                        'volatility_analysis': insights.get('volatility_analysis', {})
                    }
                except Exception:
                    pass
        
        return status
    
    def get_ml_report(self) -> Dict:
        """Get comprehensive ML analysis report"""
        if not self.enable_ml:
            return {'error': 'ML disabled'}
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'training_status': self.ml_status,
            'total_trades': len(self.closed_trades) + len(self.open_trades),
            'closed_trades': len(self.closed_trades)
        }
        
        # Loss analyzer insights
        if self.ml_status['loss_model_trained']:
            try:
                report['loss_analysis'] = self.loss_analyzer.get_insights()
            except Exception as e:
                report['loss_analysis_error'] = str(e)
        
        # Regime info
        if self.ml_status['regime_model_trained']:
            try:
                report['regime_report'] = self.regime_detector.get_regime_report()
            except Exception as e:
                report['regime_error'] = str(e)
        
        # Meta-model status
        if self.ml_status['meta_model_trained']:
            report['meta_model'] = self.meta_model.get_status()
        
        return report
    
    def get_trades(self) -> Dict:
        """Get all trades (open and closed)"""
        open_list = [self._trade_to_dict(t) for t in self.open_trades.values()]
        closed_list = [self._trade_to_dict(t) for t in self.closed_trades]
        return {'open': open_list, 'closed': closed_list}
    
    @staticmethod
    def _trade_to_dict(trade: AlgoTrade) -> Dict:
        """Convert trade to dictionary"""
        return {
            'trade_id': trade.trade_id,
            'pair': trade.pair,
            'side': trade.side,
            'entry_price': trade.entry_price,
            'entry_time': trade.entry_time,
            'exit_price': trade.exit_price,
            'exit_time': trade.exit_time,
            'lot_size': trade.lot_size,
            'stop_loss': trade.stop_loss,
            'take_profit': trade.take_profit,
            'profit_loss': trade.profit_loss,
            'profit_loss_pct': trade.profit_loss_pct,
            'status': trade.status
        }
