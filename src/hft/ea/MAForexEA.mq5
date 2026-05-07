//+------------------------------------------------------------------+
//|                 Moving Average Crossover EA                       |
//|              Simple MA Crossover Strategy for MT5                 |
//|                                                                    |
//| Strategy: Fast MA crosses Slow MA                                 |
//| Best Pairs: All forex pairs, especially EURUSD, GBPUSD, XAUUSD    |
//| Timeframes: 1H, 4H, 1D                                            |
//+------------------------------------------------------------------+
#property copyright "Prop Firm Trading"
#property link      "https://propfirm.trading"
#property version   "1.00"
#property strict
#property description "Moving Average Crossover EA"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>

//--- Enum for trade direction
enum TRADE_DIRECTION
{
    BOTH_DIRECTIONS = 1,
    LONG_ONLY = 2,
    SHORT_ONLY = 3
};

//+------------------------------------------------------------------+
//| Input Parameters                                                  |
//+------------------------------------------------------------------+
input string EA_NAME = "MA Crossover EA";
input TRADE_DIRECTION tradeDirection = BOTH_DIRECTIONS;
input double riskPercent = 1.0;                    // Risk % per trade

// Moving Average Parameters
input int fast_ma_period = 5;                      // Fast MA Period
input int slow_ma_period = 20;                     // Slow MA Period
input ENUM_MA_METHOD ma_method = MODE_SMA;         // MA Method (SMA, EMA, etc)

// Stop Loss and Take Profit
input int sl_points = 0;                           // SL in points (0 = auto from ATR)
input int tp_points = 0;                           // TP in points (0 = auto 2x ATR)
input double atr_sl_multiplier = 1.5;              // ATR multiplier for SL
input double atr_tp_multiplier = 3.0;              // ATR multiplier for TP

// Money Management
input bool use_fixed_lot = false;                  // Use fixed lot size
input double fixed_lot_size = 0.1;                 // Fixed lot size (if use_fixed_lot = true)
input double max_dd_percent = 10.0;                // Max drawdown %

// Trading Hours (optional)
input bool use_trading_hours = false;
input int start_hour = 9;
input int end_hour = 17;

// Filter Settings
input bool filter_rsi = true;                      // Use RSI filter for entries
input int rsi_period = 14;                         // RSI Period for filter
input int rsi_overbought = 70;                     // RSI overbought level
input int rsi_oversold = 30;                       // RSI oversold level

//+------------------------------------------------------------------+
//| Global Variables                                                  |
//+------------------------------------------------------------------+
CTrade trade;
CPositionInfo position;
CSymbolInfo symbol;

int fast_ma_handle;
int slow_ma_handle;
int rsi_handle;

bool canTrade = true;
double account_balance;
double max_loss;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Create Moving Average handles for both fast and slow MAs
    fast_ma_handle = iMA(_Symbol, _Period, fast_ma_period, 0, ma_method, PRICE_CLOSE);
    slow_ma_handle = iMA(_Symbol, _Period, slow_ma_period, 0, ma_method, PRICE_CLOSE);
    
    if(fast_ma_handle == INVALID_HANDLE || slow_ma_handle == INVALID_HANDLE)
    {
        Alert("Failed to create MA indicator handles!");
        return INIT_FAILED;
    }
    
    // Create RSI handle if filter is enabled
    if(filter_rsi)
    {
        rsi_handle = iRSI(_Symbol, _Period, rsi_period, PRICE_CLOSE);
        if(rsi_handle == INVALID_HANDLE)
        {
            Alert("Failed to create RSI indicator handle!");
            return INIT_FAILED;
        }
    }
    
    // Set up trade object
    trade.SetExpertMagicNumber(789456);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(_Symbol);
    
    account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    max_loss = account_balance * (max_dd_percent / 100.0);
    
    Print("═══════════════════════════════════════════════════════");
    Print("EA initialized: ", EA_NAME);
    Print("Symbol: ", _Symbol, " | Period: ", _Period);
    Print("Fast MA: ", fast_ma_period, " | Slow MA: ", slow_ma_period);
    Print("Risk per trade: ", riskPercent, "%");
    Print("Magic Number: 789456");
    Print("═══════════════════════════════════════════════════════");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check if we can trade
    if(!canTrade) return;
    
    // Check trading hours
    if(use_trading_hours)
    {
        int current_hour = Hour();
        if(current_hour < start_hour || current_hour >= end_hour)
            return;
    }
    
    // Check maximum drawdown
    double current_dd = CalculateDrawdown();
    if(current_dd > max_loss)
    {
        Print("Max drawdown reached. Stopping all trades.");
        canTrade = false;
        return;
    }
    
    // Update symbol info
    if(!symbol.Refresh()) return;
    
    // Get latest MA values
    double fast_ma_current = GetMovingAverage(fast_ma_handle, 0);
    double fast_ma_previous = GetMovingAverage(fast_ma_handle, 1);
    double slow_ma_current = GetMovingAverage(slow_ma_handle, 0);
    double slow_ma_previous = GetMovingAverage(slow_ma_handle, 1);
    
    // Get current price
    double close_current = iClose(_Symbol, _Period, 0);
    double close_previous = iClose(_Symbol, _Period, 1);
    
    // Get ATR for SL and TP calculation
    double atr_value = CalculateATR(14);
    
    // Check for existing positions
    bool has_long = HasOpenPosition(1);
    bool has_short = HasOpenPosition(-1);
    
    // Check for RSI filter if enabled
    double rsi_value = 50;  // neutral
    if(filter_rsi)
    {
        rsi_value = GetRSI(0);
    }
    
    // ═══════════════════════════════════════════════════════════════
    // BULLISH CROSSOVER (Fast MA crosses above Slow MA) - BUY SIGNAL
    // ═══════════════════════════════════════════════════════════════
    bool bullish_crossover = (fast_ma_current > slow_ma_current) && 
                            (fast_ma_previous <= slow_ma_previous);
    
    // Optional: Close short positions when bullish crossover occurs
    if(bullish_crossover && has_short)
    {
        CloseAllPositions(-1);
    }
    
    // Enter BUY trade only if:
    // 1. Bullish crossover
    // 2. No long position already open
    // 3. Trade direction allows long trades
    // 4. RSI filter passed (if enabled)
    bool buy_signal = false;
    if(bullish_crossover && !has_long && 
       (tradeDirection == BOTH_DIRECTIONS || tradeDirection == LONG_ONLY))
    {
        if(!filter_rsi || (filter_rsi && rsi_value < rsi_overbought))
        {
            buy_signal = true;
        }
    }
    
    // ═══════════════════════════════════════════════════════════════
    // BEARISH CROSSOVER (Fast MA crosses below Slow MA) - SELL SIGNAL
    // ═══════════════════════════════════════════════════════════════
    bool bearish_crossover = (fast_ma_current < slow_ma_current) && 
                            (fast_ma_previous >= slow_ma_previous);
    
    // Optional: Close long positions when bearish crossover occurs
    if(bearish_crossover && has_long)
    {
        CloseAllPositions(1);
    }
    
    // Enter SELL trade only if:
    // 1. Bearish crossover
    // 2. No short position already open
    // 3. Trade direction allows short trades
    // 4. RSI filter passed (if enabled)
    bool sell_signal = false;
    if(bearish_crossover && !has_short && 
       (tradeDirection == BOTH_DIRECTIONS || tradeDirection == SHORT_ONLY))
    {
        if(!filter_rsi || (filter_rsi && rsi_value > rsi_oversold))
        {
            sell_signal = true;
        }
    }
    
    // Execute trades
    if(buy_signal)
        ExecuteTrade(1, atr_value);
    
    if(sell_signal)
        ExecuteTrade(-1, atr_value);
}

//+------------------------------------------------------------------+
//| Execute Trade                                                    |
//+------------------------------------------------------------------+
void ExecuteTrade(int direction, double atr)
{
    double bid = symbol.Bid();
    double ask = symbol.Ask();
    double point = symbol.Point();
    
    // Calculate lot size
    double lot = use_fixed_lot ? fixed_lot_size : CalculateLotSize(atr);
    
    // Validate lot size
    if(lot <= 0)
    {
        Print("Invalid lot size calculated: ", lot);
        return;
    }
    
    // Calculate SL and TP based on user settings
    double sl, tp;
    
    if(sl_points == 0)
        sl = atr * atr_sl_multiplier;  // Auto: ATR * multiplier
    else
        sl = sl_points * point;
    
    if(tp_points == 0)
        tp = atr * atr_tp_multiplier;  // Auto: ATR * multiplier
    else
        tp = tp_points * point;
    
    // BUY ORDER
    if(direction > 0)
    {
        double entry_price = ask;
        double stop_loss = entry_price - sl;
        double take_profit = entry_price + tp;
        
        string comment = "MA Crossover BUY | Fast MA: " + IntegerToString(fast_ma_period) + 
                        " | Slow MA: " + IntegerToString(slow_ma_period);
        
        if(!trade.Buy(lot, _Symbol, entry_price, stop_loss, take_profit, comment))
        {
            Print("BUY Order failed! RetCode: ", trade.ResultRetcode(), 
                  " Description: ", trade.ResultRetcodeDescription());
        }
        else
        {
            Print("✓ BUY Order placed successfully");
            Print("  Entry: ", DoubleToString(entry_price, _Digits));
            Print("  Stop Loss: ", DoubleToString(stop_loss, _Digits));
            Print("  Take Profit: ", DoubleToString(take_profit, _Digits));
            Print("  Lot Size: ", DoubleToString(lot, 2));
        }
    }
    
    // SELL ORDER
    if(direction < 0)
    {
        double entry_price = bid;
        double stop_loss = entry_price + sl;
        double take_profit = entry_price - tp;
        
        string comment = "MA Crossover SELL | Fast MA: " + IntegerToString(fast_ma_period) + 
                        " | Slow MA: " + IntegerToString(slow_ma_period);
        
        if(!trade.Sell(lot, _Symbol, entry_price, stop_loss, take_profit, comment))
        {
            Print("SELL Order failed! RetCode: ", trade.ResultRetcode(), 
                  " Description: ", trade.ResultRetcodeDescription());
        }
        else
        {
            Print("✓ SELL Order placed successfully");
            Print("  Entry: ", DoubleToString(entry_price, _Digits));
            Print("  Stop Loss: ", DoubleToString(stop_loss, _Digits));
            Print("  Take Profit: ", DoubleToString(take_profit, _Digits));
            Print("  Lot Size: ", DoubleToString(lot, 2));
        }
    }
}

//+------------------------------------------------------------------+
//| Calculate Lot Size Based on Risk                                 |
//+------------------------------------------------------------------+
double CalculateLotSize(double atr)
{
    double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = account_balance * (riskPercent / 100.0);
    
    double point = symbol.Point();
    double tick_value = symbol.TickValue();
    
    // Stop loss in points
    double sl_points = (atr * atr_sl_multiplier) / point;
    
    // Lot size = Risk Amount / (SL Points * Tick Value)
    double lot = NormalizeDouble(risk_amount / (sl_points * tick_value), 2);
    
    // Apply broker's lot size constraints
    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double step_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    lot = MathMax(lot, min_lot);
    lot = MathMin(lot, max_lot);
    lot = MathFloor(lot / step_lot) * step_lot;
    
    return lot;
}

//+------------------------------------------------------------------+
//| Calculate ATR (Average True Range)                               |
//+------------------------------------------------------------------+
double CalculateATR(int period)
{
    double tr1, tr2, tr3, tr;
    double atr = 0;
    
    for(int i = 0; i < period; i++)
    {
        tr1 = iHigh(_Symbol, _Period, i) - iLow(_Symbol, _Period, i);
        tr2 = MathAbs(iHigh(_Symbol, _Period, i) - iClose(_Symbol, _Period, i + 1));
        tr3 = MathAbs(iLow(_Symbol, _Period, i) - iClose(_Symbol, _Period, i + 1));
        
        tr = MathMax(tr1, MathMax(tr2, tr3));
        atr += tr;
    }
    
    return NormalizeDouble(atr / period, _Digits);
}

//+------------------------------------------------------------------+
//| Get Moving Average Value                                         |
//+------------------------------------------------------------------+
double GetMovingAverage(int handle, int shift)
{
    double ma_buffer[1];
    ArraySetAsSeries(ma_buffer, true);
    
    if(CopyBuffer(handle, 0, shift, 1, ma_buffer) <= 0)
    {
        Print("Error copying MA buffer! Error code: ", GetLastError());
        return 0;
    }
    
    return ma_buffer[0];
}

//+------------------------------------------------------------------+
//| Get RSI Value (for filter)                                       |
//+------------------------------------------------------------------+
double GetRSI(int shift)
{
    double rsi_buffer[1];
    ArraySetAsSeries(rsi_buffer, true);
    
    if(CopyBuffer(rsi_handle, 0, shift, 1, rsi_buffer) <= 0)
    {
        return 50;  // Return neutral value on error
    }
    
    return rsi_buffer[0];
}

//+------------------------------------------------------------------+
//| Check for Open Position                                          |
//+------------------------------------------------------------------+
bool HasOpenPosition(int direction)
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(position.SelectByIndex(i))
        {
            if(position.Symbol() == _Symbol && position.Magic() == 789456)
            {
                if(direction > 0 && position.PositionType() == POSITION_TYPE_BUY)
                    return true;
                if(direction < 0 && position.PositionType() == POSITION_TYPE_SELL)
                    return true;
            }
        }
    }
    return false;
}

//+------------------------------------------------------------------+
//| Close All Positions                                              |
//+------------------------------------------------------------------+
void CloseAllPositions(int direction)
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(position.SelectByIndex(i))
        {
            if(position.Symbol() == _Symbol && position.Magic() == 789456)
            {
                if((direction > 0 && position.PositionType() == POSITION_TYPE_BUY) ||
                   (direction < 0 && position.PositionType() == POSITION_TYPE_SELL))
                {
                    if(!trade.PositionClose(position.Ticket()))
                    {
                        Print("Close position failed: ", trade.ResultRetcodeDescription());
                    }
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Calculate Drawdown                                               |
//+------------------------------------------------------------------+
double CalculateDrawdown()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    if(equity < balance)
        return balance - equity;
    return 0;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Release indicator handles
    if(fast_ma_handle != INVALID_HANDLE)
        IndicatorRelease(fast_ma_handle);
    if(slow_ma_handle != INVALID_HANDLE)
        IndicatorRelease(slow_ma_handle);
    if(rsi_handle != INVALID_HANDLE)
        IndicatorRelease(rsi_handle);
    
    Print("═══════════════════════════════════════════════════════");
    Print("EA deinitialized - Reason code: ", reason);
    Print("═══════════════════════════════════════════════════════");
}
