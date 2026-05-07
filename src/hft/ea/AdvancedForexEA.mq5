//+------------------------------------------------------------------+
//|                   Advanced Forex Trading EA                       |
//|                  RSI + Stochastic Strategy                         |
//|                                                                    |
//| Strategy: Combines RSI + Stochastic + Support/Resistance          |
//| Best Pairs: XAUUSD, EURUSD, GBPUSD, USDJPY                       |
//| Timeframes: 1H, 4H, 1D                                            |
//+------------------------------------------------------------------+
#property copyright "Prop Firm Trading"
#property link      "https://propfirm.trading"
#property version   "1.00"
#property strict
#property description "Advanced Forex EA using RSI + Stochastic + Support/Resistance"

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
input string EA_NAME = "Advanced Forex EA";
input TRADE_DIRECTION tradeDirection = BOTH_DIRECTIONS;
input double riskPercent = 1.0;                    // Risk % per trade
input int slPoints = 0;                            // SL in points (0 = auto 1.5x ATR)
input int tpPoints = 0;                            // TP in points (0 = auto 2x ATR)

// RSI Parameters
input int rsi_period = 14;                         // RSI Period
input int rsi_oversold = 30;                       // RSI Oversold Level
input int rsi_overbought = 70;                     // RSI Overbought Level

// Stochastic Parameters
input int stoch_k_period = 14;                     // Stochastic K Period
input int stoch_d_period = 3;                      // Stochastic D Period
input int stoch_smooth = 3;                        // Stochastic Smooth

// Money Management
input bool use_fixed_lot = false;                  // Use fixed lot size
input double fixed_lot_size = 0.1;                 // Fixed lot size
input double max_dd_percent = 10.0;                // Max drawdown %

// Trading Hours (optional)
input bool use_trading_hours = false;
input int start_hour = 9;
input int end_hour = 17;

//+------------------------------------------------------------------+
//| Global Variables                                                  |
//+------------------------------------------------------------------+
CTrade trade;
CPositionInfo position;
CSymbolInfo symbol;

int rsi_handle;
int stoch_handle;

bool canTrade = true;
double account_balance;
double max_loss;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Create indicator handles
    rsi_handle = iRSI(_Symbol, _Period, rsi_period, PRICE_CLOSE);
    stoch_handle = iStochastic(_Symbol, _Period, stoch_k_period, stoch_d_period, stoch_smooth, 
                               MODE_SMA, STO_LOWHIGH);
    
    if(rsi_handle == INVALID_HANDLE || stoch_handle == INVALID_HANDLE)
    {
        Alert("Failed to create indicator handles!");
        return INIT_FAILED;
    }
    
    // Set up trade object
    trade.SetExpertMagicNumber(123456);
    trade.SetMarginMode();
    trade.SetTypeFillingBySymbol(_Symbol);
    
    account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    max_loss = account_balance * (max_dd_percent / 100.0);
    
    Print("EA initialized: ", EA_NAME);
    Print("Symbol: ", _Symbol, " | Period: ", _Period);
    Print("Magic Number: 123456");
    
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
        Print("Max drawdown reached. Stopping trades.");
        canTrade = false;
        return;
    }
    
    // Update symbol info
    if(!symbol.Refresh()) return;
    
    // Get latest indicator values
    double rsi_current = GetRSI(0);
    double stoch_k_current = GetStochasticK(0);
    double stoch_d_current = GetStochasticD(0);
    double stoch_k_previous = GetStochasticK(1);
    double stoch_d_previous = GetStochasticD(1);
    double atr_value = CalculateATR(14);
    
    // Check for existing positions
    bool has_long = HasOpenPosition(1);
    bool has_short = HasOpenPosition(-1);
    
    // Close positions if conditions are violated
    if(has_long && rsi_current > 70)
        CloseAllPositions(1);
    
    if(has_short && rsi_current < 30)
        CloseAllPositions(-1);
    
    // Stochastic crossover signals
    bool stoch_bullish_cross = (stoch_k_current > stoch_d_current) && 
                              (stoch_k_previous <= stoch_d_previous);
    bool stoch_bearish_cross = (stoch_k_current < stoch_d_current) && 
                              (stoch_k_previous >= stoch_d_previous);
    
    // Price action patterns
    double close_prev2 = iClose(_Symbol, _Period, 2);
    double close_prev1 = iClose(_Symbol, _Period, 1);
    double close_current = iClose(_Symbol, _Period, 0);
    double high_prev2 = iHigh(_Symbol, _Period, 2);
    double high_prev1 = iHigh(_Symbol, _Period, 1);
    double low_prev2 = iLow(_Symbol, _Period, 2);
    double low_prev1 = iLow(_Symbol, _Period, 1);
    
    bool higher_low = (low_prev1 > low_prev2) && (low_current() > low_prev1);
    bool lower_high = (high_prev1 < high_prev2) && (high_current() < high_prev1);
    
    // ═══════════════════════════════════════════════════════════════
    // BUY SIGNALS
    // ═══════════════════════════════════════════════════════════════
    bool buy_signal = false;
    
    if(!has_long && (tradeDirection == BOTH_DIRECTIONS || tradeDirection == LONG_ONLY))
    {
        // Condition 1: RSI oversold + Stochastic bullish cross + Higher low
        if(rsi_current < rsi_oversold && stoch_bullish_cross && higher_low)
            buy_signal = true;
        
        // Condition 2: RSI not overbought + Stochastic bullish cross + Stoch extreme
        if(rsi_current < 40 && stoch_bullish_cross && stoch_k_current < 20)
            buy_signal = true;
        
        // Condition 3: RSI rising + Stochastic cross
        if(rsi_current > rsi_oversold && stoch_bullish_cross && rsi_current < 50)
            buy_signal = true;
    }
    
    // ═══════════════════════════════════════════════════════════════
    // SELL SIGNALS
    // ═══════════════════════════════════════════════════════════════
    bool sell_signal = false;
    
    if(!has_short && (tradeDirection == BOTH_DIRECTIONS || tradeDirection == SHORT_ONLY))
    {
        // Condition 1: RSI overbought + Stochastic bearish cross + Lower high
        if(rsi_current > rsi_overbought && stoch_bearish_cross && lower_high)
            sell_signal = true;
        
        // Condition 2: RSI not oversold + Stochastic bearish cross + Stoch extreme
        if(rsi_current > 60 && stoch_bearish_cross && stoch_k_current > 80)
            sell_signal = true;
        
        // Condition 3: RSI falling + Stochastic cross
        if(rsi_current < rsi_overbought && stoch_bearish_cross && rsi_current > 50)
            sell_signal = true;
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
    double spread = ask - bid;
    
    // Calculate lot size
    double lot = use_fixed_lot ? fixed_lot_size : CalculateLotSize(atr);
    
    // Calculate SL and TP
    double sl, tp;
    
    if(slPoints == 0)
        sl = atr * 1.5;  // Auto: 1.5x ATR
    else
        sl = slPoints * point;
    
    if(tpPoints == 0)
        tp = atr * 3.0;  // Auto: 2x risk/reward
    else
        tp = tpPoints * point;
    
    // BUY
    if(direction > 0)
    {
        double entry_price = ask;
        double stop_loss = entry_price - sl;
        double take_profit = entry_price + tp;
        
        if(!trade.Buy(lot, _Symbol, entry_price, stop_loss, take_profit, "Advanced EA BUY"))
        {
            Print("BUY Order failed: ", trade.ResultRetcodeDescription());
        }
        else
        {
            Print("BUY Order placed at ", entry_price, " | SL: ", stop_loss, " | TP: ", take_profit);
        }
    }
    
    // SELL
    if(direction < 0)
    {
        double entry_price = bid;
        double stop_loss = entry_price + sl;
        double take_profit = entry_price - tp;
        
        if(!trade.Sell(lot, _Symbol, entry_price, stop_loss, take_profit, "Advanced EA SELL"))
        {
            Print("SELL Order failed: ", trade.ResultRetcodeDescription());
        }
        else
        {
            Print("SELL Order placed at ", entry_price, " | SL: ", stop_loss, " | TP: ", take_profit);
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
    
    // Risk in points = SL (1.5x ATR)
    double sl_points = atr / point;
    
    // Lot size = Risk Amount / (SL Points * Tick Value)
    double lot = risk_amount / (sl_points * tick_value);
    
    // Normalize lot to broker's specifications
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
    
    return atr / period;
}

//+------------------------------------------------------------------+
//| Get RSI Value                                                    |
//+------------------------------------------------------------------+
double GetRSI(int shift)
{
    double rsi_buffer[1];
    ArraySetAsSeries(rsi_buffer, true);
    
    if(CopyBuffer(rsi_handle, 0, shift, 1, rsi_buffer) <= 0)
        return 0;
    
    return rsi_buffer[0];
}

//+------------------------------------------------------------------+
//| Get Stochastic K Value                                           |
//+------------------------------------------------------------------+
double GetStochasticK(int shift)
{
    double stoch_buffer[1];
    ArraySetAsSeries(stoch_buffer, true);
    
    if(CopyBuffer(stoch_handle, 0, shift, 1, stoch_buffer) <= 0)
        return 0;
    
    return stoch_buffer[0];
}

//+------------------------------------------------------------------+
//| Get Stochastic D Value                                           |
//+------------------------------------------------------------------+
double GetStochasticD(int shift)
{
    double stoch_buffer[1];
    ArraySetAsSeries(stoch_buffer, true);
    
    if(CopyBuffer(stoch_handle, 1, shift, 1, stoch_buffer) <= 0)
        return 0;
    
    return stoch_buffer[0];
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
            if(position.Symbol() == _Symbol && position.Magic() == 123456)
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
            if(position.Symbol() == _Symbol && position.Magic() == 123456)
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
//| Get Current Low                                                  |
//+------------------------------------------------------------------+
double low_current()
{
    return iLow(_Symbol, _Period, 0);
}

//+------------------------------------------------------------------+
//| Get Current High                                                 |
//+------------------------------------------------------------------+
double high_current()
{
    return iHigh(_Symbol, _Period, 0);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Release indicator handles
    if(rsi_handle != INVALID_HANDLE)
        ReleaseIndicator(rsi_handle);
    if(stoch_handle != INVALID_HANDLE)
        ReleaseIndicator(stoch_handle);
    
    Print("EA deinitialized");
}

//+------------------------------------------------------------------+
//| Release Indicator                                                |
//+------------------------------------------------------------------+
void ReleaseIndicator(int handle)
{
    if(handle != INVALID_HANDLE)
        IndicatorRelease(handle);
}
