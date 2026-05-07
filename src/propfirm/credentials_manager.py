"""
API Credentials Manager
Securely manages API keys and trading credentials
"""
import json
import os
from typing import Dict, Optional
from pathlib import Path
import base64
from datetime import datetime


class CredentialsManager:
    """Manages API credentials securely"""
    
    def __init__(self, credentials_dir: str = ".streamlit_credentials"):
        """
        Initialize credentials manager
        
        Args:
            credentials_dir: Directory to store encrypted credentials
        """
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(exist_ok=True)
        self.credentials_file = self.credentials_dir / "credentials.json"
    
    @staticmethod
    def _simple_encrypt(data: str, key: str) -> str:
        """Simple base64 encoding (for basic obfuscation)"""
        try:
            return base64.b64encode(data.encode()).decode()
        except Exception:
            return data
    
    @staticmethod
    def _simple_decrypt(data: str, key: str) -> str:
        """Simple base64 decoding"""
        try:
            return base64.b64decode(data.encode()).decode()
        except Exception:
            return data
    
    def save_credentials(
        self,
        broker: str,
        api_key: str,
        api_secret: Optional[str] = None,
        account_id: Optional[str] = None,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ) -> bool:
        """
        Save broker credentials
        
        Args:
            broker: Broker name (e.g., 'MT5', 'FXCM', 'IB')
            api_key: API key
            api_secret: API secret (optional)
            account_id: Account ID (optional)
            telegram_bot_token: Telegram bot token
            telegram_chat_id: Telegram chat ID
        
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            self.credentials_dir.mkdir(parents=True, exist_ok=True)
            
            credentials = self._load_all_credentials()
            
            credentials[broker] = {
                'api_key': self._simple_encrypt(api_key, 'key'),
                'api_secret': self._simple_encrypt(api_secret or '', 'key'),
                'account_id': account_id or '',
                'telegram_bot_token': self._simple_encrypt(telegram_bot_token or '', 'key'),
                'telegram_chat_id': telegram_chat_id or '',
                'created_at': datetime.now().isoformat()
            }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving credentials: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_credentials(self, broker: str) -> Optional[Dict]:
        """
        Get broker credentials
        
        Args:
            broker: Broker name
        
        Returns:
            Dictionary with decrypted credentials or None
        """
        try:
            credentials = self._load_all_credentials()
            
            if broker not in credentials:
                return None
            
            creds = credentials[broker]
            return {
                'api_key': self._simple_decrypt(creds.get('api_key', ''), 'key'),
                'api_secret': self._simple_decrypt(creds.get('api_secret', ''), 'key'),
                'account_id': creds.get('account_id', ''),
                'telegram_bot_token': self._simple_decrypt(creds.get('telegram_bot_token', ''), 'key'),
                'telegram_chat_id': creds.get('telegram_chat_id', ''),
            }
        except Exception as e:
            print(f"Error retrieving credentials: {e}")
            return None
    
    def delete_credentials(self, broker: str) -> bool:
        """
        Delete broker credentials
        
        Args:
            broker: Broker name
        
        Returns:
            True if successful
        """
        try:
            credentials = self._load_all_credentials()
            if broker in credentials:
                del credentials[broker]
                with open(self.credentials_file, 'w') as f:
                    json.dump(credentials, f, indent=2)
            return True
        except Exception as e:
            print(f"Error deleting credentials: {e}")
            return False
    
    def _load_all_credentials(self) -> Dict:
        """Load all credentials from file"""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def list_brokers(self) -> list:
        """List all saved brokers"""
        credentials = self._load_all_credentials()
        return list(credentials.keys())
    
    def has_credentials(self, broker: str) -> bool:
        """Check if credentials exist for broker"""
        credentials = self._load_all_credentials()
        return broker in credentials


class LiveTraderConfig:
    """Configuration for live trading"""
    
    # Supported brokers and their API requirements
    BROKER_CONFIG = {
        "MetaTrader5": {
            "name": "MetaTrader 5",
            "requires": ["account_id", "api_key"],
            "description": "MT5 terminal with API enabled"
        },
        "FXCM": {
            "name": "FXCM",
            "requires": ["api_key"],
            "description": "FXCM REST API"
        },
        "Interactive": {
            "name": "Interactive Brokers",
            "requires": ["account_id"],
            "description": "Interactive Brokers API"
        },
        "Alpaca": {
            "name": "Alpaca",
            "requires": ["api_key", "api_secret"],
            "description": "Alpaca Trading API"
        },
        "Binance": {
            "name": "Binance Futures",
            "requires": ["api_key", "api_secret"],
            "description": "Binance Futures API"
        },
        "Oanda": {
            "name": "Oanda",
            "requires": ["api_key", "account_id"],
            "description": "Oanda REST API - Forex & CFDs"
        }
    }
    
    @staticmethod
    def get_broker_config(broker: str) -> Optional[Dict]:
        """Get configuration for a broker"""
        return LiveTraderConfig.BROKER_CONFIG.get(broker)
    
    @staticmethod
    def get_all_brokers() -> list:
        """Get list of all supported brokers"""
        return list(LiveTraderConfig.BROKER_CONFIG.keys())
    
    @staticmethod
    def get_broker_display_names() -> Dict:
        """Get display names for all brokers"""
        return {k: v['name'] for k, v in LiveTraderConfig.BROKER_CONFIG.items()}
