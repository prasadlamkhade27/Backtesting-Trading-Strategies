//+------------------------------------------------------------------+
//|                     Pivot Strategy Expert Advisor                |
//|                  Converted from Python HFT Strategy               |
//+------------------------------------------------------------------+
#property copyright "HFT System"
#property link      "https://github.com"
#property version   "1.0"
#property description "Pivot Point Strategy - Detects pivot highs/lows and trades breakouts"

#include <Trade\Trade.mqh>

//+------ INPUT PARAMETERS ------+
input int LeftBars = 5;                    // Number of bars for pivot detection
input double LotSize = 0.1;                // Trade volume
input int StopLossPips = 50;               // Stop loss in pips
input int TakeProfitPips = 100;            // Take profit in pips
input int MaxOpenTrades = 2;               // Maximum number of open trades
input bool UseTimeFilter = false;          // Use time filter for trading
input int StartHour = 9;                   // Start trading hour (24-hour format)
input int EndHour = 17;                    // End trading hour (24-hour format)

//+------ GLOBAL VARIABLES ------+
CTrade trade;
int OnInit_Counter = 0;

//+------ STRUCTURES FOR PIVOT DATA ------+
struct PivotData {
    double pivot_high;
    double pivot_low;
    int market_structure;  // 1=uptrend, -1=downtrend, 0=undefined
};

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    OnInit_Counter++;
    
    // Check for valid inputs
    if (LeftBars < 2) {
        PrintFormat("Error: LeftBars must be at least 2, got %d", LeftBars);
        return INIT_PARAMETERS_INCORRECT;
    }
    
    if (LotSize <= 0) {
        PrintFormat("Error: LotSize must be positive, got %.2f", LotSize);
        return INIT_PARAMETERS_INCORRECT;
    }
    
    // Initialize trade object
    trade.SetExpertMagicNumber(12345);
    trade.SetDeviationInPoints(10);
    
    Print("Expert Advisor initialized successfully");
    PrintFormat("Parameters - LeftBars: %d, LotSize: %.2f, SL: %d pips, TP: %d pips",
                LeftBars, LotSize, StopLossPips, TakeProfitPips);
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("Expert Advisor deinitialized");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Check time filter if enabled
    if (UseTimeFilter && !IsTimeToTrade()) {
        return;
    }
    
    // Check maximum trades limit
    if (CountOpenTrades() >= MaxOpenTrades) {
        return;
    }
    
    // Calculate pivot data
    PivotData pivot = CalculatePivotData();
    
    // Generate trading signals
    CheckBuySignal(pivot);
    CheckSellSignal(pivot);
    
    // Update market structure visualization (optional)
    UpdateChart(pivot);
}

//+------------------------------------------------------------------+
//| Calculate Pivot High/Low and Market Structure                    |
//+------------------------------------------------------------------+
PivotData CalculatePivotData() {
    PivotData data;
    data.pivot_high = 0;
    data.pivot_low = 0;
    data.market_structure = 0;
    
    int bars_needed = LeftBars * 2 + 2;  // Need enough bars for calculation
    
    if (Bars(_Symbol, _Period) < bars_needed) {
        return data;
    }
    
    // Find current pivot high and low
    double ph = FindPivotHigh(LeftBars);
    double pl = FindPivotLow(LeftBars);
    
    data.pivot_high = ph;
    data.pivot_low = pl;
    
    // Determine market structure
    double current_close = Close[0];
    
    if (current_close > ph && ph > 0) {
        data.market_structure = 1;  // Uptrend
    } else if (current_close < pl && pl > 0) {
        data.market_structure = -1;  // Downtrend
    } else {
        // Maintain previous structure if within bounds
        data.market_structure = GetPreviousMarketStructure();
    }
    
    return data;
}

//+------------------------------------------------------------------+
//| Find Pivot High                                                  |
//+------------------------------------------------------------------+
double FindPivotHigh(int left_bars) {
    // Look for the most recent pivot high
    // A pivot high is where: high[i-left] < high[i] and high[i+left] < high[i]
    
    int right_bars = 1;  // Only look 1 bar to the right (current bar)
    
    for (int i = left_bars + right_bars + 1; i < Bars(_Symbol, _Period); i++) {
        bool is_pivot = true;
        
        // Check left bars
        for (int j = 1; j <= left_bars; j++) {
            if (High[i + j] >= High[i]) {
                is_pivot = false;
                break;
            }
        }
        
        // Check right bars (only current bar status)
        if (is_pivot && right_bars > 0) {
            for (int j = 1; j <= right_bars; j++) {
                if (i >= j && High[i - j] >= High[i]) {
                    is_pivot = false;
                    break;
                }
            }
        }
        
        if (is_pivot) {
            return High[i];
        }
    }
    
    return 0;
}

//+------------------------------------------------------------------+
//| Find Pivot Low                                                   |
//+------------------------------------------------------------------+
double FindPivotLow(int left_bars) {
    // Look for the most recent pivot low
    // A pivot low is where: low[i-left] > low[i] and low[i+left] > low[i]
    
    int right_bars = 1;  // Only look 1 bar to the right (current bar)
    
    for (int i = left_bars + right_bars + 1; i < Bars(_Symbol, _Period); i++) {
        bool is_pivot = true;
        
        // Check left bars
        for (int j = 1; j <= left_bars; j++) {
            if (Low[i + j] <= Low[i]) {
                is_pivot = false;
                break;
            }
        }
        
        // Check right bars
        if (is_pivot && right_bars > 0) {
            for (int j = 1; j <= right_bars; j++) {
                if (i >= j && Low[i - j] <= Low[i]) {
                    is_pivot = false;
                    break;
                }
            }
        }
        
        if (is_pivot) {
            return Low[i];
        }
    }
    
    return 0;
}

//+------------------------------------------------------------------+
//| Get Previous Market Structure                                    |
//+------------------------------------------------------------------+
int GetPreviousMarketStructure() {
    // Look back through recent bars to find last defined structure
    for (int i = 1; i <= 10 && i < Bars(_Symbol, _Period); i++) {
        if (Close[i] > FindPivotHigh(LeftBars)) {
            return 1;  // Uptrend
        }
        if (Close[i] < FindPivotLow(LeftBars)) {
            return -1;  // Downtrend
        }
    }
    return 0;  // Undefined
}

//+------------------------------------------------------------------+
//| Check Buy Signal                                                 |
//+------------------------------------------------------------------+
void CheckBuySignal(PivotData &pivot) {
    // BUY when:
    // 1. Close > Pivot High
    // 2. Previous market structure was downtrend (-1)
    
    if (pivot.pivot_high <= 0) {
        return;  // Invalid pivot
    }
    
    double current_close = Close[0];
    int prev_structure = (Bars(_Symbol, _Period) > 1) ? GetMarketStructureAt(1) : 0;
    
    // Buy signal: breakout above pivot high after downtrend
    if (current_close > pivot.pivot_high && prev_structure == -1 && NoOpenBuyOrder()) {
        double entry_price = Ask;
        double stop_loss = entry_price - StopLossPips * Point();
        double take_profit = entry_price + TakeProfitPips * Point();
        
        if (trade.Buy(LotSize, _Symbol, entry_price, stop_loss, take_profit, "Pivot Buy")) {
            PrintFormat("BUY Signal - Price: %.5f, PH: %.5f, SL: %.5f, TP: %.5f",
                        entry_price, pivot.pivot_high, stop_loss, take_profit);
        } else {
            PrintFormat("Buy order failed - Error: %d", GetLastError());
        }
    }
}

//+------------------------------------------------------------------+
//| Check Sell Signal                                                |
//+------------------------------------------------------------------+
void CheckSellSignal(PivotData &pivot) {
    // SELL when:
    // 1. Close < Pivot Low
    // 2. Previous market structure was uptrend (1)
    
    if (pivot.pivot_low <= 0) {
        return;  // Invalid pivot
    }
    
    double current_close = Close[0];
    int prev_structure = (Bars(_Symbol, _Period) > 1) ? GetMarketStructureAt(1) : 0;
    
    // Sell signal: breakdown below pivot low after uptrend
    if (current_close < pivot.pivot_low && prev_structure == 1 && NoOpenSellOrder()) {
        double entry_price = Bid;
        double stop_loss = entry_price + StopLossPips * Point();
        double take_profit = entry_price - TakeProfitPips * Point();
        
        if (trade.Sell(LotSize, _Symbol, entry_price, stop_loss, take_profit, "Pivot Sell")) {
            PrintFormat("SELL Signal - Price: %.5f, PL: %.5f, SL: %.5f, TP: %.5f",
                        entry_price, pivot.pivot_low, stop_loss, take_profit);
        } else {
            PrintFormat("Sell order failed - Error: %d", GetLastError());
        }
    }
}

//+------------------------------------------------------------------+
//| Get Market Structure at specific bar                             |
//+------------------------------------------------------------------+
int GetMarketStructureAt(int bar) {
    if (bar >= Bars(_Symbol, _Period)) {
        return 0;
    }
    
    double ph = FindPivotHigh(LeftBars);
    double pl = FindPivotLow(LeftBars);
    
    if (Close[bar] > ph && ph > 0) {
        return 1;
    } else if (Close[bar] < pl && pl > 0) {
        return -1;
    }
    return 0;
}

//+------------------------------------------------------------------+
//| Check if there is no open Buy order                              |
//+------------------------------------------------------------------+
bool NoOpenBuyOrder() {
    for (int i = OrdersTotal() - 1; i >= 0; i--) {
        if (OrderSelect(i, SELECT_BY_POS)) {
            if (OrderType() == ORDER_TYPE_BUY && OrderSymbol() == _Symbol 
                && OrderMagicNumber() == 12345) {
                return false;
            }
        }
    }
    return true;
}

//+------------------------------------------------------------------+
//| Check if there is no open Sell order                             |
//+------------------------------------------------------------------+
bool NoOpenSellOrder() {
    for (int i = OrdersTotal() - 1; i >= 0; i--) {
        if (OrderSelect(i, SELECT_BY_POS)) {
            if (OrderType() == ORDER_TYPE_SELL && OrderSymbol() == _Symbol
                && OrderMagicNumber() == 12345) {
                return false;
            }
        }
    }
    return true;
}

//+------------------------------------------------------------------+
//| Count Open Trades                                                |
//+------------------------------------------------------------------+
int CountOpenTrades() {
    int count = 0;
    for (int i = OrdersTotal() - 1; i >= 0; i--) {
        if (OrderSelect(i, SELECT_BY_POS)) {
            if (OrderSymbol() == _Symbol && OrderMagicNumber() == 12345) {
                count++;
            }
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Check if it's time to trade                                      |
//+------------------------------------------------------------------+
bool IsTimeToTrade() {
    int current_hour = Hour();
    return (current_hour >= StartHour && current_hour < EndHour);
}

//+------------------------------------------------------------------+
//| Update Chart (draw pivot levels)                                 |
//+------------------------------------------------------------------+
void UpdateChart(PivotData &pivot) {
    // Optional: Draw pivot levels on chart
    // Uncomment to enable visualization
    
    /*
    string ph_name = "PivotHigh_" + IntegerToString(TimeCurrent());
    string pl_name = "PivotLow_" + IntegerToString(TimeCurrent());
    
    if (pivot.pivot_high > 0) {
        ObjectCreate(0, ph_name, OBJ_HLINE, 0, 0, pivot.pivot_high);
        ObjectSetInteger(0, ph_name, OBJPROP_COLOR, clrGreen);
    }
    
    if (pivot.pivot_low > 0) {
        ObjectCreate(0, pl_name, OBJ_HLINE, 0, 0, pivot.pivot_low);
        ObjectSetInteger(0, pl_name, OBJPROP_COLOR, clrRed);
    }
    */
}

//+------------------------------------------------------------------+
