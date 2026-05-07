"""
Telegram Bot Notification System
Sends trade notifications and alerts to Telegram
"""
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class TelegramNotifier:
    """Handle Telegram notifications for trades and alerts"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token from @BotFather
            chat_id: Chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def test_connection(self) -> bool:
        """Test if Telegram connection is working"""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram connection error: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """
        Send plain text message
        
        Args:
            message: Message text
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def send_trade_opened(
        self,
        pair: str,
        side: str,
        entry_price: float,
        lot_size: float,
        stop_loss: float,
        take_profit: float,
        risk_amount: float
    ) -> bool:
        """
        Send trade opened notification with details
        
        Args:
            pair: Currency pair
            side: BUY or SELL
            entry_price: Entry price
            lot_size: Position size in lots
            stop_loss: Stop loss price
            take_profit: Take profit price
            risk_amount: Risk amount in dollars
        
        Returns:
            True if successful
        """
        side_emoji = "🟢 BUY" if side.upper() == "BUY" else "🔴 SELL"
        
        message = f"""
<b>🚀 TRADE OPENED</b>

<b>Pair:</b> {pair}
<b>Side:</b> {side_emoji}
<b>Entry Price:</b> {entry_price}
<b>Lot Size:</b> {lot_size}
<b>Stop Loss:</b> {stop_loss}
<b>Take Profit:</b> {take_profit}
<b>Risk Amount:</b> ${risk_amount:.2f}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return self.send_message(message)
    
    def send_trade_closed(
        self,
        pair: str,
        side: str,
        entry_price: float,
        exit_price: float,
        lot_size: float,
        profit_loss: float,
        profit_loss_pct: float,
        pips: float
    ) -> bool:
        """
        Send trade closed notification
        
        Args:
            pair: Currency pair
            side: BUY or SELL
            entry_price: Entry price
            exit_price: Exit price
            lot_size: Position size in lots
            profit_loss: Profit/loss in dollars
            profit_loss_pct: Profit/loss in percentage
            pips: Pips gained/lost
        
        Returns:
            True if successful
        """
        pl_emoji = "🟢" if profit_loss >= 0 else "🔴"
        pl_text = f"+${profit_loss:.2f}" if profit_loss >= 0 else f"-${abs(profit_loss):.2f}"
        pct_text = f"+{profit_loss_pct:.2f}%" if profit_loss >= 0 else f"{profit_loss_pct:.2f}%"
        pips_text = f"+{pips:.1f}" if pips >= 0 else f"{pips:.1f}"
        
        message = f"""
<b>🏁 TRADE CLOSED</b>

<b>Pair:</b> {pair}
<b>Side:</b> {'🟢 BUY' if side.upper() == 'BUY' else '🔴 SELL'}
<b>Entry Price:</b> {entry_price}
<b>Exit Price:</b> {exit_price}
<b>Lot Size:</b> {lot_size}

{pl_emoji} <b>P/L:</b> {pl_text} ({pct_text})
<b>Pips:</b> {pips_text}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return self.send_message(message)
    
    def send_alert(self, alert_type: str, message: str) -> bool:
        """
        Send alert notification
        
        Args:
            alert_type: Type of alert (WARNING, ERROR, INFO)
            message: Alert message
        
        Returns:
            True if successful
        """
        emoji_map = {
            "WARNING": "⚠️",
            "ERROR": "🚨",
            "INFO": "ℹ️",
            "SUCCESS": "✅"
        }
        emoji = emoji_map.get(alert_type, "📢")
        
        alert_message = f"""
<b>{emoji} {alert_type}</b>

{message}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return self.send_message(alert_message)
    
    def send_account_summary(
        self,
        account_size: float,
        balance: float,
        profit_loss: float,
        profit_loss_pct: float,
        open_trades: int,
        closed_trades: int,
        win_rate: float
    ) -> bool:
        """
        Send account summary
        
        Args:
            account_size: Initial account size
            balance: Current balance
            profit_loss: Total profit/loss
            profit_loss_pct: Profit/loss percentage
            open_trades: Number of open trades
            closed_trades: Number of closed trades
            win_rate: Win rate percentage
        
        Returns:
            True if successful
        """
        pl_emoji = "🟢" if profit_loss >= 0 else "🔴"
        
        message = f"""
<b>📊 ACCOUNT SUMMARY</b>

<b>Account Size:</b> ${account_size:,.2f}
<b>Current Balance:</b> ${balance:,.2f}
{pl_emoji} <b>P/L:</b> ${profit_loss:,.2f} ({profit_loss_pct:.2f}%)

<b>Open Trades:</b> {open_trades}
<b>Closed Trades:</b> {closed_trades}
<b>Win Rate:</b> {win_rate:.2f}%

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return self.send_message(message)
    
    def send_daily_report(
        self,
        date: str,
        trades_today: int,
        daily_profit_loss: float,
        daily_pips: float,
        best_trade: Dict[str, Any],
        worst_trade: Dict[str, Any]
    ) -> bool:
        """
        Send daily trading report
        
        Args:
            date: Report date
            trades_today: Number of trades today
            daily_profit_loss: Daily profit/loss
            daily_pips: Daily pips
            best_trade: Best trade details
            worst_trade: Worst trade details
        
        Returns:
            True if successful
        """
        pl_emoji = "🟢" if daily_profit_loss >= 0 else "🔴"
        pips_emoji = "📈" if daily_pips >= 0 else "📉"
        
        best_trade_str = f"{best_trade.get('pair', 'N/A')} - ${best_trade.get('profit_loss', 0):.2f}"
        worst_trade_str = f"{worst_trade.get('pair', 'N/A')} - ${worst_trade.get('profit_loss', 0):.2f}"
        
        message = f"""
<b>📈 DAILY REPORT - {date}</b>

<b>Trades Today:</b> {trades_today}
{pl_emoji} <b>P/L:</b> ${daily_profit_loss:,.2f}
{pips_emoji} <b>Pips:</b> {daily_pips:.1f}

<b>🥇 Best Trade:</b> {best_trade_str}
<b>🥉 Worst Trade:</b> {worst_trade_str}

<i>Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        return self.send_message(message)
