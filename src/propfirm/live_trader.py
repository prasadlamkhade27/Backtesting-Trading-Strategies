"""
Live Trading System
Handles real trading execution through various broker APIs
"""
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class TradeEvent:
    """Represents a trade event"""
    timestamp: str
    trade_id: str
    pair: str
    side: str
    entry_price: float
    lot_size: float
    stop_loss: float
    take_profit: float
    status: str  # "OPENED", "CLOSED", "PENDING"
    profit_loss: Optional[float] = None
    exit_price: Optional[float] = None
    duration_minutes: Optional[int] = None


class BaseLiveTrader:
    """Base class for live trading implementations"""
    
    def __init__(self, broker: str, credentials: Dict):
        """
        Initialize live trader
        
        Args:
            broker: Broker name
            credentials: Broker credentials dict
        """
        self.broker = broker
        self.credentials = credentials
        self.is_connected = False
        self.account_balance = 0.0
        self.open_trades = []
        self.closed_trades = []
        self.trades_log_file = Path(".streamlit_credentials/trades.json")
    
    def connect(self) -> bool:
        """Connect to broker API - override in subclass"""
        raise NotImplementedError()
    
    def disconnect(self) -> bool:
        """Disconnect from broker API"""
        self.is_connected = False
        return True
    
    def open_trade(
        self,
        pair: str,
        side: str,
        entry_price: float,
        lot_size: float,
        stop_loss: float,
        take_profit: float
    ) -> Optional[str]:
        """
        Open a new trade - override in subclass
        
        Returns:
            Trade ID or None if failed
        """
        raise NotImplementedError()
    
    def close_trade(self, trade_id: str) -> bool:
        """Close an open trade - override in subclass"""
        raise NotImplementedError()
    
    def get_account_info(self) -> Dict:
        """Get account information - override in subclass"""
        raise NotImplementedError()
    
    def log_trade(self, trade_event: TradeEvent) -> bool:
        """Log trade event to file"""
        try:
            self.trades_log_file.parent.mkdir(exist_ok=True)
            
            trades = []
            if self.trades_log_file.exists():
                with open(self.trades_log_file, 'r') as f:
                    trades = json.load(f)
            
            trades.append({
                'timestamp': trade_event.timestamp,
                'trade_id': trade_event.trade_id,
                'pair': trade_event.pair,
                'side': trade_event.side,
                'entry_price': trade_event.entry_price,
                'lot_size': trade_event.lot_size,
                'stop_loss': trade_event.stop_loss,
                'take_profit': trade_event.take_profit,
                'status': trade_event.status,
                'profit_loss': trade_event.profit_loss,
                'exit_price': trade_event.exit_price,
                'duration_minutes': trade_event.duration_minutes
            })
            
            with open(self.trades_log_file, 'w') as f:
                json.dump(trades, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error logging trade: {e}")
            return False
    
    def get_trade_history(self) -> list:
        """Get all logged trades"""
        try:
            if self.trades_log_file.exists():
                with open(self.trades_log_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []


class MT5LiveTrader(BaseLiveTrader):
    """MetaTrader 5 Live Trader Implementation"""
    
    def __init__(self, credentials: Dict):
        super().__init__("MetaTrader5", credentials)
        self.mt5 = None
    
    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            import MetaTrader5 as mt5
            
            account_id = int(self.credentials.get('account_id', 0))
            api_key = self.credentials.get('api_key', '')
            
            # Initialize MT5
            if not mt5.initialize():
                return False
            
            # Try to login
            authorized = mt5.login(account_id, password=api_key)
            if authorized:
                self.is_connected = True
                account_info = mt5.account_info()
                self.account_balance = account_info.balance if account_info else 0.0
                return True
            
            return False
        except ImportError:
            print("MetaTrader5 package not installed")
            return False
        except Exception as e:
            print(f"MT5 Connection error: {e}")
            return False
    
    def open_trade(
        self,
        pair: str,
        side: str,
        entry_price: float,
        lot_size: float,
        stop_loss: float,
        take_profit: float
    ) -> Optional[str]:
        """Open trade on MT5"""
        if not self.is_connected or not self.mt5:
            return None
        
        try:
            import MetaTrader5 as mt5
            
            # Normalize pair for MT5
            symbol = pair.replace(" ", "").upper()
            order_type = mt5.ORDER_BUY if side.upper() == "BUY" else mt5.ORDER_SELL
            
            # Prepare request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": entry_price,
                "sl": stop_loss,
                "tp": take_profit,
                "comment": "Python trading bot",
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            # Send order
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return None
            
            trade_id = str(result.order)
            return trade_id
        except Exception as e:
            print(f"Error opening trade: {e}")
            return None
    
    def close_trade(self, trade_id: str) -> bool:
        """Close trade on MT5"""
        if not self.is_connected or not self.mt5:
            return False
        
        try:
            import MetaTrader5 as mt5
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": int(trade_id),
                "type": mt5.ORDER_TYPE_CLOSE,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            return result.retcode == mt5.TRADE_RETCODE_DONE
        except Exception as e:
            print(f"Error closing trade: {e}")
            return False
    
    def get_account_info(self) -> Dict:
        """Get account info from MT5"""
        if not self.is_connected:
            return {}
        
        try:
            import MetaTrader5 as mt5
            
            info = mt5.account_info()
            if info:
                return {
                    "balance": info.balance,
                    "equity": info.equity,
                    "profit": info.profit,
                    "margin": info.margin,
                    "margin_free": info.margin_free,
                    "margin_level": info.margin_level
                }
        except Exception:
            pass
        
        return {}


class OandaLiveTrader(BaseLiveTrader):
    """Oanda Live Trader Implementation"""
    
    def __init__(self, credentials: Dict):
        super().__init__("Oanda", credentials)
        self.base_url = "https://api-fxpractice.oanda.com/v3"  # Demo environment
        # Use https://api-fxtrade.oanda.com/v3 for live trading
        self.headers = {
            "Authorization": f"Bearer {credentials.get('api_key', '')}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "UNIX"
        }
        self.account_id = credentials.get('account_id', '')
    
    def connect(self) -> bool:
        """Connect to Oanda API"""
        try:
            import requests
            
            # Test connection
            response = requests.get(
                f"{self.base_url}/accounts/{self.account_id}",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                account_data = response.json().get('account', {})
                self.account_balance = float(account_data.get('balance', 0))
                self.is_connected = True
                return True
            
            return False
        except ImportError:
            print("requests library not installed")
            return False
        except Exception as e:
            print(f"Oanda Connection error: {e}")
            return False
    
    def open_trade(
        self,
        pair: str,
        side: str,
        entry_price: float,
        lot_size: float,
        stop_loss: float,
        take_profit: float
    ) -> Optional[str]:
        """Open trade on Oanda"""
        if not self.is_connected:
            return None
        
        try:
            import requests
            
            # Normalize pair for Oanda (e.g., EURUSD for Oanda format)
            symbol = pair.replace(" ", "").replace("(", "").replace(")", "").upper()
            
            # Convert lot size to units (1 lot = 100,000 units)
            units = int(lot_size * 100000)
            if side.upper() == "SELL":
                units = -units
            
            order_data = {
                "order": {
                    "instrument": symbol,
                    "units": units,
                    "type": "MARKET",
                    "takeProfitOnFill": {
                        "price": str(take_profit)
                    },
                    "stopLossOnFill": {
                        "price": str(stop_loss)
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/accounts/{self.account_id}/orders",
                headers=self.headers,
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                trade_id = str(result.get('orderFillTransaction', {}).get('id', ''))
                
                if trade_id:
                    # Log trade
                    trade_event = TradeEvent(
                        timestamp=datetime.now().isoformat(),
                        trade_id=trade_id,
                        pair=pair,
                        side=side,
                        entry_price=entry_price,
                        lot_size=lot_size,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        status="OPENED"
                    )
                    self.log_trade(trade_event)
                    return trade_id
            
            return None
        except Exception as e:
            print(f"Error opening trade: {e}")
            return None
    
    def close_trade(self, trade_id: str) -> bool:
        """Close trade on Oanda"""
        if not self.is_connected:
            return False
        
        try:
            import requests
            
            response = requests.put(
                f"{self.base_url}/accounts/{self.account_id}/trades/{trade_id}/close",
                headers=self.headers,
                json={"units": "ALL"},
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            
            return False
        except Exception as e:
            print(f"Error closing trade: {e}")
            return False
    
    def get_account_info(self) -> Dict:
        """Get account info from Oanda"""
        if not self.is_connected:
            return {}
        
        try:
            import requests
            
            response = requests.get(
                f"{self.base_url}/accounts/{self.account_id}",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                account = response.json().get('account', {})
                return {
                    "balance": float(account.get('balance', 0)),
                    "equity": float(account.get('balance', 0)) + float(account.get('unrealizedPL', 0)),
                    "profit": float(account.get('unrealizedPL', 0)),
                    "margin": float(account.get('marginUsed', 0)),
                    "margin_free": float(account.get('marginAvailable', 0)),
                    "margin_level": (float(account.get('balance', 0)) + float(account.get('unrealizedPL', 0))) / max(float(account.get('marginUsed', 0)), 1) * 100
                }
        except Exception as e:
            print(f"Error getting account info: {e}")
        
        return {}


class SimulatedLiveTrader(BaseLiveTrader):
    """Simulated Live Trader for testing"""
    
    def __init__(self, credentials: Dict):
        super().__init__("Simulated", credentials)
        self.account_balance = 10000.0  # Default account size
    
    def connect(self) -> bool:
        """Simulate connection"""
        self.is_connected = True
        return True
    
    def open_trade(
        self,
        pair: str,
        side: str,
        entry_price: float,
        lot_size: float,
        stop_loss: float,
        take_profit: float
    ) -> Optional[str]:
        """Simulate opening trade"""
        if not self.is_connected:
            return None
        
        import uuid
        trade_id = str(uuid.uuid4())[:8]
        
        trade_event = TradeEvent(
            timestamp=datetime.now().isoformat(),
            trade_id=trade_id,
            pair=pair,
            side=side,
            entry_price=entry_price,
            lot_size=lot_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status="OPENED"
        )
        
        self.open_trades.append(trade_id)
        self.log_trade(trade_event)
        return trade_id
    
    def close_trade(self, trade_id: str, exit_price: float) -> bool:
        """Simulate closing trade"""
        if trade_id not in self.open_trades:
            return False
        
        try:
            trades = self.get_trade_history()
            for trade in trades:
                if trade['trade_id'] == trade_id and trade['status'] == 'OPENED':
                    profit_loss = (exit_price - trade['entry_price']) * trade['lot_size'] * 100000
                    trade['status'] = 'CLOSED'
                    trade['exit_price'] = exit_price
                    trade['profit_loss'] = profit_loss
                    
                    with open(self.trades_log_file, 'w') as f:
                        json.dump(trades, f, indent=2)
                    
                    self.open_trades.remove(trade_id)
                    self.account_balance += profit_loss
                    return True
        except Exception as e:
            print(f"Error closing trade: {e}")
        
        return False
    
    def get_account_info(self) -> Dict:
        """Get simulated account info"""
        trades = self.get_trade_history()
        open_count = sum(1 for t in trades if t.get('status') == 'OPENED')
        closed_count = sum(1 for t in trades if t.get('status') == 'CLOSED')
        
        open_profit_loss = sum(
            (t['entry_price'] - t['entry_price']) * t['lot_size'] * 100000
            for t in trades if t.get('status') == 'OPENED'
        )
        
        closed_profit_loss = sum(
            t.get('profit_loss', 0) for t in trades if t.get('status') == 'CLOSED'
        )
        
        total_profit_loss = open_profit_loss + closed_profit_loss
        
        return {
            "balance": self.account_balance,
            "equity": self.account_balance + open_profit_loss,
            "profit": total_profit_loss,
            "open_trades": open_count,
            "closed_trades": closed_count,
            "margin": 0,
            "margin_free": self.account_balance
        }


class LiveTraderFactory:
    """Factory to create appropriate live trader"""
    
    @staticmethod
    def create_trader(broker: str, credentials: Dict) -> Optional[BaseLiveTrader]:
        """
        Create trader instance based on broker
        
        Args:
            broker: Broker name
            credentials: Credentials dict
        
        Returns:
            Trader instance or None
        """
        if broker == "MetaTrader5":
            return MT5LiveTrader(credentials)
        elif broker == "Oanda":
            return OandaLiveTrader(credentials)
        elif broker == "Simulated":
            return SimulatedLiveTrader(credentials)
        else:
            # Default to simulated for now
            return SimulatedLiveTrader(credentials)
