//+------------------------------------------------------------------+
//|                 High-Frequency Trading Scalping EA                |
//|              Market Making & Scalping Strategy                    |
//|                                                                    |
//| Strategy Types:                                                   |
//|  - Scalping: Multiple small trades capturing bid-ask spread       |
//|  - Market Making: Placing orders at support/resistance levels     |
//|  - Trend Following: Quick trend capture with tight stops          |
//|                                                                    |
//| Best Pairs: EURUSD, GBPUSD, Any liquid pair                      |
//| Timeframes: M1, M5, M15                                           |
//| Execution Speed: 50-500ms                                         |
//+------------------------------------------------------------------+

#property copyright "HFT Trading Solutions"
#property link      "https://hfttrading.pro"
#property version   "1.50"
#property strict
#property description "High-Frequency Trading Scalping EA with Risk Management"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <Trade\OrderInfo.mqh>

//--- Enum definitions
enum STRATEGY_TYPE {
    SCALPING = 1,           // Rapid short-term trades
    MARKET_MAKING = 2,      // Two-sided orders
    TREND_FOLLOWING = 3     // Trend with tight stops
};

enum RISK_MODE {
    CONSERVATIVE = 1,       // Small risk per trade
    MODERATE = 2,           // Medium risk
    AGGRESSIVE = 3          // Higher risk, higher reward
};

//+------------------------------------------------------------------+
//| Global Variables & Handles                                        |
//+------------------------------------------------------------------+
CTrade trade;
CPositionInfo posInfo;
CSymbolInfo symInfo;
COrderInfo ordInfo;

// Indicator handles
int handle_ma_fast = 0;
int handle_ma_slow = 0;
int handle_rsi = 0;
int handle_macd = 0;
int handle_atr = 0;

// Trading statistics
struct TradeStats {
    int total_trades;
    int winning_trades;
    int losing_trades;
    double total_pnl;
    double daily_pnl;
    double max_loss;
    int consecutive_losses;
    datetime last_trade_time;
};

TradeStats stats;

// Trade history for logging
struct TradeLog {
    datetime entry_time;
    double entry_price;
    double exit_price;
    double profit;
    string reason;
};

TradeLog last_trades[];

//+------------------------------------------------------------------+
//| Input Parameters - Strategy Configuration                         |
//+------------------------------------------------------------------+

// General Settings
input string EA_NAME = "HFT Scalping EA";
input STRATEGY_TYPE strategy_type = SCALPING;
input RISK_MODE risk_mode = MODERATE;
input bool use_news_filter = true;

// Risk Management
input double risk_percent_per_trade = 0.5;        // Risk % per trade (HFT uses small risk)
input int max_consecutive_losses = 5;              // Max losing trades before pause
input double max_daily_loss_percent = 5.0;         // Max daily loss % then close trades
input double max_drawdown_percent = 10.0;          // Max account drawdown %
input bool use_risk_control = true;

// Position Management
input int max_open_positions = 3;                  // Max simultaneous positions
input int max_trades_per_hour = 20;                // Rate limiting
input int min_bars_between_trades = 2;             // Minimum bars between entries
input bool close_on_session_end = true;            // Close at market close

// Entry Conditions
input int ma_fast_period = 5;                      // Fast MA for trend
input int ma_slow_period = 20;                     // Slow MA for trend confirmation
input int rsi_period = 14;                         // RSI for momentum
input int rsi_oversold = 30;                       // RSI oversold level
input int rsi_overbought = 70;                     // RSI overbought level
input int macd_fast = 12;
input int macd_slow = 26;
input int macd_signal = 9;

// Stop Loss & Take Profit
input int fixed_sl_pips = 0;                       // 0 = auto (1.5x ATR)
input int fixed_tp_pips = 0;                       // 0 = auto (0.5-1x ATR based on strategy)
input int atr_period = 14;                         // ATR period for dynamic SL/TP
input double atr_sl_multiple = 1.5;                // SL distance in ATR multiples
input double atr_tp_multiple = 0.75;               // TP distance in ATR multiples (tight for scalping)

// Lot Sizing
input bool use_fixed_lot = false;                  // Use fixed lot instead of risk-based
input double fixed_lot_size = 0.01;                // Fixed lot if enabled
input double max_lot_size = 1.0;                   // Maximum position size

// Time Filters
input bool use_time_filter = true;
input int start_hour = 8;                          // Start trading at 8 AM
input int end_hour = 16;                           // Stop trading at 4 PM
input bool avoid_news = true;                      // Avoid news events

// Performance Optimization
input int max_bars_to_analyze = 1000;              // Limit bar analysis for speed
input bool optimize_for_speed = true;              // Skip non-essential calculations

//+------------------------------------------------------------------+
//| Expert Initialization                                             |
//+------------------------------------------------------------------+
int OnInit() {
    // Print strategy configuration
    PrintLine("=== HFT Scalping EA Initialized ===");
    PrintLine("Strategy Type: ", EnumToString(strategy_type));
    PrintLine("Risk Mode: ", EnumToString(risk_mode));
    PrintLine("Risk per Trade: ", risk_percent_per_trade, "%");
    PrintLine("Max Concurrent Positions: ", max_open_positions);
    
    // Set trade parameters
    trade.SetExpertMagicNumber(123456);
    trade.SetDeviationInPoints(5);  // Slippage tolerance for HFT
    
    // Create indicator handles
    handle_ma_fast = iMA(Symbol(), Period(), ma_fast_period, 0, MODE_EMA, PRICE_CLOSE);
    if (handle_ma_fast == INVALID_HANDLE) {
        PrintLine("ERROR: Failed to create Fast MA indicator");
        return INIT_FAILED;
    }
    
    handle_ma_slow = iMA(Symbol(), Period(), ma_slow_period, 0, MODE_EMA, PRICE_CLOSE);
    if (handle_ma_slow == INVALID_HANDLE) {
        PrintLine("ERROR: Failed to create Slow MA indicator");
        return INIT_FAILED;
    }
    
    handle_rsi = iRSI(Symbol(), Period(), rsi_period, PRICE_CLOSE);
    if (handle_rsi == INVALID_HANDLE) {
        PrintLine("ERROR: Failed to create RSI indicator");
        return INIT_FAILED;
    }
    
    handle_macd = iMACD(Symbol(), Period(), macd_fast, macd_slow, macd_signal, PRICE_CLOSE);
    if (handle_macd == INVALID_HANDLE) {
        PrintLine("ERROR: Failed to create MACD indicator");
        return INIT_FAILED;
    }
    
    handle_atr = iATR(Symbol(), Period(), atr_period);
    if (handle_atr == INVALID_HANDLE) {
        PrintLine("ERROR: Failed to create ATR indicator");
        return INIT_FAILED;
    }
    
    // Initialize stats
    stats.total_trades = 0;
    stats.winning_trades = 0;
    stats.losing_trades = 0;
    stats.total_pnl = 0;
    stats.daily_pnl = 0;
    stats.consecutive_losses = 0;
    
    PrintLine("All indicators initialized successfully");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                           |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    // Print final statistics
    PrintLine("\n=== HFT Scalping EA Finalized ===");
    PrintLine("Total Trades: ", stats.total_trades);
    PrintLine("Winning Trades: ", stats.winning_trades);
    PrintLine("Losing Trades: ", stats.losing_trades);
    PrintLine("Total P&L: $", stats.total_pnl);
    PrintLine("Win Rate: ", (stats.total_trades > 0 ? (stats.winning_trades * 100.0 / stats.total_trades) : 0), "%");
    
    // Release indicator handles
    IndicatorRelease(handle_ma_fast);
    IndicatorRelease(handle_ma_slow);
    IndicatorRelease(handle_rsi);
    IndicatorRelease(handle_macd);
    IndicatorRelease(handle_atr);
    
    PrintLine("Deinitialization complete: ", GetDeinitReasonText(reason));
}

//+------------------------------------------------------------------+
//| Expert Tick Function - Main Trading Logic                         |
//+------------------------------------------------------------------+
void OnTick() {
    // Security checks
    if (!IsConnected()) {
        PrintLine("WARNING: Not connected to server");
        return;
    }
    
    if (Symbol() == "") {
        PrintLine("ERROR: No symbol selected");
        return;
    }
    
    // Apply filters
    if (!CheckTimeFilter()) return;
    if (!CheckRiskLimits()) return;
    
    // Get current price data
    double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
    double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
    
    // Check for open positions
    int open_positions = CountOpenPositions();
    
    // Main strategy logic based on type
    switch (strategy_type) {
        case SCALPING:
            ProcessScalpingStrategy(bid, ask, open_positions);
            break;
        case MARKET_MAKING:
            ProcessMarketMakingStrategy(bid, ask, open_positions);
            break;
        case TREND_FOLLOWING:
            ProcessTrendFollowingStrategy(bid, ask, open_positions);
            break;
    }
    
    // Manage existing positions
    ManagePositions(bid, ask);
    
    // Update statistics
    UpdateStats();
}

//+------------------------------------------------------------------+
//| Scalping Strategy - Tight entry/exit on bid-ask spread           |
//+------------------------------------------------------------------+
void ProcessScalpingStrategy(double bid, double ask, int open_positions) {
    // Check if we can take more positions
    if (open_positions >= max_open_positions) return;
    
    // Get indicator values
    double ma_fast = GetIndicatorValue(handle_ma_fast, 0);
    double ma_slow = GetIndicatorValue(handle_ma_slow, 0);
    double rsi = GetIndicatorValue(handle_rsi, 0);
    double atr = GetIndicatorValue(handle_atr, 0);
    
    if (ma_fast == 0 || ma_slow == 0 || rsi == 0 || atr == 0) return;
    
    // Scalping Entry Logic
    bool buy_signal = false;
    bool sell_signal = false;
    
    // Buy: Fast MA > Slow MA + RSI > 50 (not yet overbought) + MACD positive
    double macd_main = GetIndicatorValue(handle_macd, 0);
    if (ma_fast > ma_slow && rsi > 50 && rsi < rsi_overbought && macd_main > 0) {
        buy_signal = true;
    }
    
    // Sell: Fast MA < Slow MA + RSI < 50 (not yet oversold) + MACD negative
    if (ma_fast < ma_slow && rsi < 50 && rsi > rsi_oversold && macd_main < 0) {
        sell_signal = true;
    }
    
    // Calculate position size and SL/TP
    if (buy_signal) {
        double tp = 0, sl = 0;
        double lot = CalculateLotSize(ask, fixed_tp_pips, fixed_sl_pips);
        CalculateStopLevels(ask, atr, tp, sl, true);  // true = buy
        
        ExecuteTrade(ORDER_TYPE_BUY, ask, sl, tp, lot, "HFT Scalping BUY");
    }
    
    if (sell_signal) {
        double tp = 0, sl = 0;
        double lot = CalculateLotSize(bid, fixed_tp_pips, fixed_sl_pips);
        CalculateStopLevels(bid, atr, tp, sl, false);  // false = sell
        
        ExecuteTrade(ORDER_TYPE_SELL, bid, sl, tp, lot, "HFT Scalping SELL");
    }
}

//+------------------------------------------------------------------+
//| Market Making Strategy - Orders on both sides                    |
//+------------------------------------------------------------------+
void ProcessMarketMakingStrategy(double bid, double ask, int open_positions) {
    if (open_positions >= max_open_positions) return;
    
    double spread = ask - bid;
    double atr = GetIndicatorValue(handle_atr, 0);
    
    if (atr == 0) return;
    
    // Market making: Place buy order at bid support, sell at ask resistance
    if (spread < atr * 2) {  // Only when spread is favorable
        // Buy order slightly below bid
        double buy_price = bid - (atr * 0.25);
        double buy_tp = buy_price + (atr * atr_tp_multiple);
        double buy_sl = buy_price - (atr * atr_sl_multiple);
        double lot = CalculateLotSize(buy_price, 0, 0);
        
        ExecuteTrade(ORDER_TYPE_BUY, buy_price, buy_sl, buy_tp, lot, "HFT MarketMaking BUY");
        
        // Sell order slightly above ask
        double sell_price = ask + (atr * 0.25);
        double sell_tp = sell_price - (atr * atr_tp_multiple);
        double sell_sl = sell_price + (atr * atr_sl_multiple);
        
        ExecuteTrade(ORDER_TYPE_SELL, sell_price, sell_sl, sell_tp, lot, "HFT MarketMaking SELL");
    }
}

//+------------------------------------------------------------------+
//| Trend Following Strategy - Rapid trend capture                   |
//+------------------------------------------------------------------+
void ProcessTrendFollowingStrategy(double bid, double ask, int open_positions) {
    if (open_positions >= max_open_positions) return;
    
    double ma_fast = GetIndicatorValue(handle_ma_fast, 0);
    double ma_slow = GetIndicatorValue(handle_ma_slow, 0);
    double rsi = GetIndicatorValue(handle_rsi, 0);
    double atr = GetIndicatorValue(handle_atr, 0);
    
    if (ma_fast == 0 || ma_slow == 0 || atr == 0) return;
    
    // Uptrend: Strong MA alignment + RSI momentum
    if (ma_fast > ma_slow && Close[0] > ma_fast && rsi > 50) {
        double lot = CalculateLotSize(ask, 0, 0);
        double tp = ask + (atr * atr_tp_multiple * 2);
        double sl = ask - (atr * atr_sl_multiple);
        
        ExecuteTrade(ORDER_TYPE_BUY, ask, sl, tp, lot, "HFT Trend UP");
    }
    
    // Downtrend: Strong MA alignment + RSI momentum
    if (ma_fast < ma_slow && Close[0] < ma_fast && rsi < 50) {
        double lot = CalculateLotSize(bid, 0, 0);
        double tp = bid - (atr * atr_tp_multiple * 2);
        double sl = bid + (atr * atr_sl_multiple);
        
        ExecuteTrade(ORDER_TYPE_SELL, bid, sl, tp, lot, "HFT Trend DOWN");
    }
}

//+------------------------------------------------------------------+
//| Position Management - Trailing stops, breakeven                  |
//+------------------------------------------------------------------+
void ManagePositions(double bid, double ask) {
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (!posInfo.SelectByIndex(i)) continue;
        if (posInfo.Magic() != trade.GetExpertMagicNumber()) continue;
        
        double current_profit = posInfo.Profit();
        double entry_price = posInfo.PriceOpen();
        
        // Trailing stop logic
        if (current_profit > 0) {
            double trailing_amount = SymbolInfoDouble(Symbol(), SYMBOL_POINT) * 10;  // 10 pips
            
            if (posInfo.PositionType() == POSITION_TYPE_BUY) {
                double new_sl = bid - trailing_amount;
                if (new_sl > posInfo.StopLoss()) {
                    trade.PositionModify(posInfo.Ticket(), new_sl, posInfo.TakeProfit());
                }
            } else if (posInfo.PositionType() == POSITION_TYPE_SELL) {
                double new_sl = ask + trailing_amount;
                if (new_sl < posInfo.StopLoss()) {
                    trade.PositionModify(posInfo.Ticket(), new_sl, posInfo.TakeProfit());
                }
            }
        }
        
        // Breakeven stop after 5 pips profit
        if (current_profit > SymbolInfoDouble(Symbol(), SYMBOL_POINT) * 50) {
            if (posInfo.PositionType() == POSITION_TYPE_BUY) {
                if (posInfo.StopLoss() < entry_price) {
                    trade.PositionModify(posInfo.Ticket(), entry_price, posInfo.TakeProfit());
                }
            } else if (posInfo.PositionType() == POSITION_TYPE_SELL) {
                if (posInfo.StopLoss() > entry_price) {
                    trade.PositionModify(posInfo.Ticket(), entry_price, posInfo.TakeProfit());
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Helper Functions - Core Calculations                             |
//+------------------------------------------------------------------+

// Get indicator value safely
double GetIndicatorValue(int handle, int index) {
    double buffer[];
    if (CopyBuffer(handle, 0, index, 1, buffer) > 0) {
        return buffer[0];
    }
    return 0;
}

// Calculate lot size based on risk
double CalculateLotSize(double entry_price, int tp_pips, int sl_pips) {
    if (use_fixed_lot) return fmin(fixed_lot_size, max_lot_size);
    
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = balance * (risk_percent_per_trade / 100.0);
    
    if (sl_pips == 0) {
        double atr = GetIndicatorValue(handle_atr, 0);
        sl_pips = (int)(atr / SymbolInfoDouble(Symbol(), SYMBOL_POINT));
    }
    
    double point_value = SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    double loss_per_pip = (sl_pips * point_value * 100000) / 100000;
    
    double lot = fmin(risk_amount / (loss_per_pip * 100), max_lot_size);
    return NormalizeDouble(lot, 2);
}

// Calculate Stop Loss and Take Profit
void CalculateStopLevels(double entry_price, double atr, double &tp, double &sl, bool is_buy) {
    double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);
    
    if (is_buy) {
        sl = entry_price - (atr * atr_sl_multiple);
        tp = entry_price + (atr * atr_tp_multiple);
    } else {
        sl = entry_price + (atr * atr_sl_multiple);
        tp = entry_price - (atr * atr_tp_multiple);
    }
}

// Execute a trade
void ExecuteTrade(ENUM_ORDER_TYPE order_type, double price, double sl, double tp, double lot, string comment) {
    if (lot <= 0) {
        PrintLine("ERROR: Invalid lot size ", lot);
        return;
    }
    
    // Check volume limits
    if (!CheckVolumeLimit(lot)) return;
    
    trade.SetExpertMagicNumber(123456);
    trade.SetDeviationInPoints(5);
    
    bool result = false;
    
    if (order_type == ORDER_TYPE_BUY) {
        result = trade.Buy(lot, Symbol(), price, sl, tp, comment);
    } else if (order_type == ORDER_TYPE_SELL) {
        result = trade.Sell(lot, Symbol(), price, sl, tp, comment);
    }
    
    if (result) {
        PrintLine("Trade executed: ", comment, " Lot: ", lot, " Price: ", price, " SL: ", sl, " TP: ", tp);
        stats.total_trades++;
    } else {
        PrintLine("ERROR: Trade failed - ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
    }
}

// Count open positions
int CountOpenPositions() {
    int count = 0;
    for (int i = 0; i < PositionsTotal(); i++) {
        if (posInfo.SelectByIndex(i)) {
            if (posInfo.Magic() == trade.GetExpertMagicNumber()) {
                count++;
            }
        }
    }
    return count;
}

// Check volume limits
bool CheckVolumeLimit(double requested_volume) {
    double symbol_min = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MIN);
    double symbol_max = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MAX);
    double symbol_step = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_STEP);
    
    if (requested_volume < symbol_min || requested_volume > symbol_max) {
        return false;
    }
    return true;
}

//+------------------------------------------------------------------+
//| Risk & Filter Functions                                           |
//+------------------------------------------------------------------+

// Check time filters
bool CheckTimeFilter() {
    if (!use_time_filter) return true;
    
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    
    if (dt.hour < start_hour || dt.hour >= end_hour) {
        return false;
    }
    
    return true;
}

// Check risk limits
bool CheckRiskLimits() {
    if (!use_risk_control) return true;
    
    double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double account_equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double max_loss = account_balance * (max_daily_loss_percent / 100.0);
    
    // Stop trading if daily loss exceeded
    if (account_equity < (account_balance - max_loss)) {
        PrintLine("WARNING: Daily loss limit reached. Stopping new trades.");
        return false;
    }
    
    // Check consecutive losses
    if (stats.consecutive_losses >= max_consecutive_losses) {
        PrintLine("WARNING: Max consecutive losses reached (", stats.consecutive_losses, ")");
        return false;
    }
    
    return true;
}

// Update statistics
void UpdateStats() {
    // This would be called after each trade to update win rate
    // Implementation depends on your tracking system
}

//+------------------------------------------------------------------+
//| Utility Functions                                                 |
//+------------------------------------------------------------------+

// Print with formatting
void PrintLine(const string msg) {
    Print("[", TimeCurrent(), "] ", msg);
}

void PrintLine(const string msg1, const string msg2) {
    Print("[", TimeCurrent(), "] ", msg1, msg2);
}

void PrintLine(const string msg, double value) {
    Print("[", TimeCurrent(), "] ", msg, value);
}

void PrintLine(const string msg1, double value, const string msg2) {
    Print("[", TimeCurrent(), "] ", msg1, value, msg2);
}

void PrintLine(const string msg1, int value, const string msg2) {
    Print("[", TimeCurrent(), "] ", msg1, value, msg2);
}

void PrintLine(const string msg1, double value1, const string msg2, double value2) {
    Print("[", TimeCurrent(), "] ", msg1, value1, msg2, value2);
}

// Get deinit reason text
string GetDeinitReasonText(int reason) {
    switch (reason) {
        case REASON_ACCOUNT: return "Account was deleted";
        case REASON_CHARTCHANGE: return "Symbol or timeframe was changed";
        case REASON_CHARTCLOSE: return "Chart was closed";
        case REASON_PARAMETERS: return "EA parameters were changed";
        case REASON_RECOMPILE: return "EA was recompiled";
        case REASON_REMOVE: return "EA was removed from chart";
        case REASON_TEMPLATE: return "Template was changed";
        case REASON_INITFAILED: return "OnInit failed";
        case REASON_CLOSE: return "Terminal closed";
        default: return "Unknown reason";
    }
}

//+------------------------------------------------------------------+
// End of HFT Scalping EA
//+------------------------------------------------------------------+
