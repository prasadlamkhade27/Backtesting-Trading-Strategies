//+------------------------------------------------------------------+
//|                     MQL KING 1 - SMC HFT EA                        |
//|              Smart Money Concepts + Price Action + M1              |
//|                    Professional Trading System                    |
//+------------------------------------------------------------------+
#property copyright "MQL King Trading Systems"
#property link      "https://github.com"
#property version   "1.0"
#property description "Advanced SMC + Price Action HFT for XAUUSD M1"

#include <Trade\Trade.mqh>

//+------ INPUT PARAMETERS ------+

// Market Structure Detection
input int StructureLookback = 10;              // Bars for HH/HL/LH/LL detection
input double MinStructureRatio = 1.2;          // Minimum structure size (ATR ratio)

// Liquidity & Order Blocks
input int OrderBlockLookback = 5;              // Bars for OB detection
input double OrderBlockThreshold = 0.5;        // OB sensitivity (0-1)
input int LiquidityMemory = 50;                // Keep track of liquidity for N bars

// Fair Value Gap
input double FVGMinGapPercent = 0.01;          // Minimum FVG size (%)
input int FVGLookback = 5;                     // Bars to detect FVG

// Displacement & Entry
input double DisplacementThreshold = 2.0;      // Min momentum (ATR multiplier)
input int DisplacementBars = 3;                // Candles for displacement

// Risk Management
input double RiskPercent = 0.5;                // Risk per trade (%)
input double MaxRiskRewardRatio = 3.0;         // Max acceptable RR
input double MinRiskRewardRatio = 1.5;         // Minimum RR to trade
input int MaxTradesPerDay = 5;                 // Daily trade limit
input int MaxConsecutiveLosses = 3;            // Stop trading after N losses
input int MaxOpenTrades = 1;                   // Concurrent positions

// Session & Time Filters
input bool UseSessionFilter = true;
input int LondonOpenHour = 8;                  // 08:00 GMT = London Open
input int NYOpenHour = 13;                     // 13:00 GMT = NY Open
input int AsianDeadHour = 2;                   // 02:00-04:00 UTC - AVOID
input bool AvoidNews = true;

// Mathematical Model Parameters
input double ATRMultiplierStop = 1.5;          // ATR * X for stop loss
input double ATRMultiplierTarget = 3.0;        // ATR * X for take profit
input int ATRPeriod = 14;

//+------ GLOBAL VARIABLES ------+
CTrade trade;

struct LiquidityLevel {
    double level;
    datetime time;
    bool is_high;  // true = resistance, false = support
};

struct OrderBlock {
    double high;
    double low;
    datetime time;
    bool is_bullish;  // true = bullish OB, false = bearish OB
    double strength;
};

struct FairValueGap {
    double top;
    double bottom;
    datetime time;
    bool is_bullish;
};

// Arrays to store levels
LiquidityLevel liquidity_zones[];
OrderBlock order_blocks[];
FairValueGap fair_value_gaps[];

int trades_today = 0;
int consecutive_losses = 0;
datetime last_trade_time = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    trade.SetExpertMagicNumber(99999);
    trade.SetDeviationInPoints(20);
    
    ArrayResize(liquidity_zones, 0);
    ArrayResize(order_blocks, 0);
    ArrayResize(fair_value_gaps, 0);
    
    Print("═══════════════════════════════════════════════════════");
    Print("🧭 MQL KING 1 - SMC HFT EA INITIALIZED");
    Print("═══════════════════════════════════════════════════════");
    PrintFormat("Structure Lookback: %d | OB Lookback: %d | FVG Gap: %.2f%%",
                StructureLookback, OrderBlockLookback, FVGMinGapPercent);
    PrintFormat("Risk: %.1f%% | Min RR: %.1f | Max RR: %.1f",
                RiskPercent, MinRiskRewardRatio, MaxRiskRewardRatio);
    Print("Strategy: SMC Price Action on M1 Timeframe");
    Print("═══════════════════════════════════════════════════════");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Check session filter
    if (UseSessionFilter && !IsGoodTradingTime()) {
        return;
    }
    
    // Reset daily counters
    if (Hour() == 0 && Minute() < 5) {
        trades_today = 0;
    }
    
    // Check trade limits
    if (trades_today >= MaxTradesPerDay) {
        return;
    }
    
    if (consecutive_losses >= MaxConsecutiveLosses) {
        return;
    }
    
    if (CountOpenTrades() >= MaxOpenTrades) {
        ManageOpenTrades();
        return;
    }
    
    // ═══════════════════════════════════════════════════════
    // STEP 1: DETECT MARKET STRUCTURE (HH, HL, LH, LL)
    // ═══════════════════════════════════════════════════════
    
    int trend = DetectMarketStructure();
    
    if (trend == 0) {
        return;  // No clear structure
    }
    
    // ═══════════════════════════════════════════════════════
    // STEP 2: DETECT BREAK OF STRUCTURE (BOS)
    // ═══════════════════════════════════════════════════════
    
    bool bos_detected = DetectBreakOfStructure(trend);
    if (!bos_detected) {
        return;
    }
    
    // ═══════════════════════════════════════════════════════
    // STEP 3: MAP LIQUIDITY ZONES
    // ═══════════════════════════════════════════════════════
    
    UpdateLiquidityZones();
    
    // ═══════════════════════════════════════════════════════
    // STEP 4: IDENTIFY ORDER BLOCKS
    // ═══════════════════════════════════════════════════════
    
    UpdateOrderBlocks(trend);
    
    // ═══════════════════════════════════════════════════════
    // STEP 5: DETECT FAIR VALUE GAPS
    // ═══════════════════════════════════════════════════════
    
    UpdateFairValueGaps();
    
    // ═══════════════════════════════════════════════════════
    // STEP 6: DETECT DISPLACEMENT (CONFIRMATION)
    // ═══════════════════════════════════════════════════════
    
    bool displacement = DetectDisplacement(trend);
    if (!displacement) {
        return;
    }
    
    // ═══════════════════════════════════════════════════════
    // STEP 7: FIND ENTRY POINT (OB, FVG, or Breaker)
    // ═══════════════════════════════════════════════════════
    
    TradeSetup setup = FindTradeSetup(trend);
    if (!setup.is_valid) {
        return;
    }
    
    // ═══════════════════════════════════════════════════════
    // STEP 8: EXECUTE TRADE
    // ═══════════════════════════════════════════════════════
    
    ExecuteTrade(setup, trend);
}

//+------------------------------------------------------------------+
//| STEP 1: Detect Market Structure (HH, HL, LH, LL)                |
//+------------------------------------------------------------------+
int DetectMarketStructure() {
    if (Bars(_Symbol, _Period) < StructureLookback + 5) {
        return 0;
    }
    
    // Find recent swings
    double highest = High[iHighest(_Symbol, _Period, MODE_HIGH, StructureLookback, 0)];
    double lowest = Low[iLowest(_Symbol, _Period, MODE_LOW, StructureLookback, 0)];
    double highest_prev = High[iHighest(_Symbol, _Period, MODE_HIGH, StructureLookback, StructureLookback + 2)];
    double lowest_prev = Low[iLowest(_Symbol, _Period, MODE_LOW, StructureLookback, StructureLookback + 2)];
    
    double atr = CalculateATR(ATRPeriod);
    
    // UPTREND: HH + HL
    if (highest > highest_prev && lowest > lowest_prev && 
        (highest - lowest) > atr * MinStructureRatio) {
        return 1;  // Uptrend
    }
    
    // DOWNTREND: LH + LL
    if (highest < highest_prev && lowest < lowest_prev &&
        (highest - lowest) > atr * MinStructureRatio) {
        return -1;  // Downtrend
    }
    
    return 0;  // No clear structure
}

//+------------------------------------------------------------------+
//| STEP 2: Detect Break of Structure (BOS)                         |
//+------------------------------------------------------------------+
bool DetectBreakOfStructure(int trend) {
    if (Bars(_Symbol, _Period) < 20) {
        return false;
    }
    
    double close_current = Close[0];
    double close_prev = Close[1];
    
    if (trend == 1) {  // Uptrend
        // BOS in uptrend: Break above recent resistance
        double resistance = High[iHighest(_Symbol, _Period, MODE_HIGH, StructureLookback + 5, 1)];
        return (close_current > resistance && close_prev <= resistance);
    } else {  // Downtrend
        // BOS in downtrend: Break below recent support
        double support = Low[iLowest(_Symbol, _Period, MODE_LOW, StructureLookback + 5, 1)];
        return (close_current < support && close_prev >= support);
    }
}

//+------------------------------------------------------------------+
//| STEP 3: Update Liquidity Zones                                  |
//+------------------------------------------------------------------+
void UpdateLiquidityZones() {
    // Track equal highs and lows
    LiquidityLevel new_level;
    
    // Check for equal highs
    int high_count = 0;
    double current_high = High[0];
    
    for (int i = 1; i < LiquidityMemory && i < Bars(_Symbol, _Period); i++) {
        if (MathAbs(High[i] - current_high) < Point() * 5) {  // Within 5 pips
            high_count++;
            if (high_count >= 2) {
                new_level.level = current_high;
                new_level.time = TimeCurrent();
                new_level.is_high = true;
                AddLiquidityLevel(new_level);
                break;
            }
        }
    }
    
    // Check for equal lows
    int low_count = 0;
    double current_low = Low[0];
    
    for (int i = 1; i < LiquidityMemory && i < Bars(_Symbol, _Period); i++) {
        if (MathAbs(Low[i] - current_low) < Point() * 5) {  // Within 5 pips
            low_count++;
            if (low_count >= 2) {
                new_level.level = current_low;
                new_level.time = TimeCurrent();
                new_level.is_high = false;
                AddLiquidityLevel(new_level);
                break;
            }
        }
    }
    
    // Remove old levels
    for (int i = ArraySize(liquidity_zones) - 1; i >= 0; i--) {
        if (TimeCurrent() - liquidity_zones[i].time > LiquidityMemory * PeriodSeconds(_Period)) {
            ArrayRemove(liquidity_zones, i, 1);
        }
    }
}

//+------------------------------------------------------------------+
//| Add Liquidity Level                                              |
//+------------------------------------------------------------------+
void AddLiquidityLevel(LiquidityLevel level) {
    // Check if level already exists
    for (int i = 0; i < ArraySize(liquidity_zones); i++) {
        if (MathAbs(liquidity_zones[i].level - level.level) < Point() * 10) {
            return;  // Already exists
        }
    }
    
    int size = ArraySize(liquidity_zones);
    ArrayResize(liquidity_zones, size + 1);
    liquidity_zones[size] = level;
}

//+------------------------------------------------------------------+
//| STEP 4: Identify Order Blocks                                   |
//+------------------------------------------------------------------+
void UpdateOrderBlocks(int trend) {
    if (Bars(_Symbol, _Period) < OrderBlockLookback + 5) {
        return;
    }
    
    OrderBlock new_ob;
    
    if (trend == 1) {  // Uptrend - look for bullish OB (last bearish candle before move up)
        for (int i = 1; i < OrderBlockLookback; i++) {
            bool is_bearish = (Close[i] < Open[i]);
            bool next_is_bullish = (Close[i-1] > Open[i-1]);
            
            if (is_bearish && next_is_bullish) {
                new_ob.low = Low[i];
                new_ob.high = High[i];
                new_ob.time = iTime(_Symbol, _Period, i);
                new_ob.is_bullish = true;
                new_ob.strength = MathAbs(Close[i] - Open[i]);
                AddOrderBlock(new_ob);
                break;
            }
        }
    } else {  // Downtrend - look for bearish OB (last bullish candle before move down)
        for (int i = 1; i < OrderBlockLookback; i++) {
            bool is_bullish = (Close[i] > Open[i]);
            bool next_is_bearish = (Close[i-1] < Open[i-1]);
            
            if (is_bullish && next_is_bearish) {
                new_ob.low = Low[i];
                new_ob.high = High[i];
                new_ob.time = iTime(_Symbol, _Period, i);
                new_ob.is_bullish = false;
                new_ob.strength = MathAbs(Close[i] - Open[i]);
                AddOrderBlock(new_ob);
                break;
            }
        }
    }
    
    // Remove expired OBs
    for (int i = ArraySize(order_blocks) - 1; i >= 0; i--) {
        if (TimeCurrent() - order_blocks[i].time > 200 * PeriodSeconds(_Period)) {
            ArrayRemove(order_blocks, i, 1);
        }
    }
}

//+------------------------------------------------------------------+
//| Add Order Block                                                  |
//+------------------------------------------------------------------+
void AddOrderBlock(OrderBlock ob) {
    // Don't add if already exists
    for (int i = 0; i < ArraySize(order_blocks); i++) {
        if (MathAbs(order_blocks[i].high - ob.high) < Point() * 10) {
            return;
        }
    }
    
    int size = ArraySize(order_blocks);
    ArrayResize(order_blocks, size + 1);
    order_blocks[size] = ob;
}

//+------------------------------------------------------------------+
//| STEP 5: Detect Fair Value Gaps (FVG)                            |
//+------------------------------------------------------------------+
void UpdateFairValueGaps() {
    if (Bars(_Symbol, _Period) < FVGLookback + 2) {
        return;
    }
    
    // FVG = Gap between candles (imbalance)
    FairValueGap new_fvg;
    
    for (int i = 2; i < FVGLookback; i++) {
        // Bullish FVG: Low[i] > High[i+1] (gap up)
        if (Low[i] > High[i+1]) {
            double gap_size = Low[i] - High[i+1];
            double gap_percent = (gap_size / Close[i]) * 100;
            
            if (gap_percent >= FVGMinGapPercent) {
                new_fvg.bottom = High[i+1];
                new_fvg.top = Low[i];
                new_fvg.time = iTime(_Symbol, _Period, i);
                new_fvg.is_bullish = true;
                AddFVG(new_fvg);
            }
        }
        
        // Bearish FVG: High[i] < Low[i+1] (gap down)
        if (High[i] < Low[i+1]) {
            double gap_size = Low[i+1] - High[i];
            double gap_percent = (gap_size / Close[i]) * 100;
            
            if (gap_percent >= FVGMinGapPercent) {
                new_fvg.bottom = High[i];
                new_fvg.top = Low[i+1];
                new_fvg.time = iTime(_Symbol, _Period, i);
                new_fvg.is_bullish = false;
                AddFVG(new_fvg);
            }
        }
    }
    
    // Remove old FVGs
    for (int i = ArraySize(fair_value_gaps) - 1; i >= 0; i--) {
        if (TimeCurrent() - fair_value_gaps[i].time > 300 * PeriodSeconds(_Period)) {
            ArrayRemove(fair_value_gaps, i, 1);
        }
    }
}

//+------------------------------------------------------------------+
//| Add Fair Value Gap                                               |
//+------------------------------------------------------------------+
void AddFVG(FairValueGap fvg) {
    int size = ArraySize(fair_value_gaps);
    ArrayResize(fair_value_gaps, size + 1);
    fair_value_gaps[size] = fvg;
}

//+------------------------------------------------------------------+
//| STEP 6: Detect Displacement (Strong Impulse)                    |
//+------------------------------------------------------------------+
bool DetectDisplacement(int trend) {
    if (Bars(_Symbol, _Period) < DisplacementBars + 5) {
        return false;
    }
    
    double atr = CalculateATR(ATRPeriod);
    double displacement_distance = atr * DisplacementThreshold;
    
    if (trend == 1) {  // Uptrend - look for strong up candles
        for (int i = 0; i < DisplacementBars; i++) {
            double candle_size = High[i] - Low[i];
            double candle_move = Close[i] - Open[i];
            
            if (candle_size >= displacement_distance && candle_move > 0) {
                // Strong upward displacement
                return true;
            }
        }
    } else {  // Downtrend - look for strong down candles
        for (int i = 0; i < DisplacementBars; i++) {
            double candle_size = High[i] - Low[i];
            double candle_move = Open[i] - Close[i];
            
            if (candle_size >= displacement_distance && candle_move > 0) {
                // Strong downward displacement
                return true;
            }
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| STEP 7: Find Trade Setup (Entry Signal)                         |
//+------------------------------------------------------------------+
struct TradeSetup {
    bool is_valid;
    double entry_price;
    double stop_loss;
    double take_profit;
    string entry_reason;
    double position_size;
};

TradeSetup FindTradeSetup(int trend) {
    TradeSetup setup;
    setup.is_valid = false;
    
    double atr = CalculateATR(ATRPeriod);
    double current_price = Close[0];
    
    // ═── Option 1: Entry at Order Block Retest ───═
    if (ArraySize(order_blocks) > 0) {
        OrderBlock ob = order_blocks[0];
        
        if (trend == 1 && ob.is_bullish) {
            // Buy at bullish OB retest
            if (current_price >= ob.low && current_price <= ob.high) {
                setup.entry_price = current_price;
                setup.stop_loss = ob.low - atr * ATRMultiplierStop;
                setup.take_profit = current_price + atr * ATRMultiplierTarget;
                setup.entry_reason = "Order Block Retest (Bullish)";
                setup.is_valid = ValidateSetup(setup);
                return setup;
            }
        } else if (trend == -1 && !ob.is_bullish) {
            // Sell at bearish OB retest
            if (current_price >= ob.low && current_price <= ob.high) {
                setup.entry_price = current_price;
                setup.stop_loss = ob.high + atr * ATRMultiplierStop;
                setup.take_profit = current_price - atr * ATRMultiplierTarget;
                setup.entry_reason = "Order Block Retest (Bearish)";
                setup.is_valid = ValidateSetup(setup);
                return setup;
            }
        }
    }
    
    // ═── Option 2: Entry at FVG Fill ───═
    if (ArraySize(fair_value_gaps) > 0) {
        FairValueGap fvg = fair_value_gaps[0];
        
        if (trend == 1 && fvg.is_bullish) {
            // Price filling bullish FVG (buy entry)
            if (current_price >= fvg.bottom && current_price <= fvg.top) {
                setup.entry_price = current_price;
                setup.stop_loss = fvg.bottom - atr * ATRMultiplierStop;
                setup.take_profit = current_price + atr * ATRMultiplierTarget;
                setup.entry_reason = "FVG Fill Entry (Bullish)";
                setup.is_valid = ValidateSetup(setup);
                return setup;
            }
        } else if (trend == -1 && !fvg.is_bullish) {
            // Price filling bearish FVG (sell entry)
            if (current_price >= fvg.bottom && current_price <= fvg.top) {
                setup.entry_price = current_price;
                setup.stop_loss = fvg.top + atr * ATRMultiplierStop;
                setup.take_profit = current_price - atr * ATRMultiplierTarget;
                setup.entry_reason = "FVG Fill Entry (Bearish)";
                setup.is_valid = ValidateSetup(setup);
                return setup;
            }
        }
    }
    
    // ═── Option 3: Liquidity Sweep + Reversal ───═
    if (ArraySize(liquidity_zones) > 0) {
        LiquidityLevel liq = liquidity_zones[0];
        
        if (trend == 1 && !liq.is_high) {
            // Liquidity sweep touched support, now buy
            if (current_price >= liq.level && current_price <= liq.level + atr) {
                setup.entry_price = current_price;
                setup.stop_loss = liq.level - atr * ATRMultiplierStop;
                setup.take_profit = current_price + atr * ATRMultiplierTarget;
                setup.entry_reason = "Liquidity Sweep + Reversal (Bullish)";
                setup.is_valid = ValidateSetup(setup);
                return setup;
            }
        } else if (trend == -1 && liq.is_high) {
            // Liquidity sweep touched resistance, now sell
            if (current_price <= liq.level && current_price >= liq.level - atr) {
                setup.entry_price = current_price;
                setup.stop_loss = liq.level + atr * ATRMultiplierStop;
                setup.take_profit = current_price - atr * ATRMultiplierTarget;
                setup.entry_reason = "Liquidity Sweep + Reversal (Bearish)";
                setup.is_valid = ValidateSetup(setup);
                return setup;
            }
        }
    }
    
    return setup;
}

//+------------------------------------------------------------------+
//| Validate Trade Setup (Risk/Reward Check)                        |
//+------------------------------------------------------------------+
bool ValidateSetup(TradeSetup &setup) {
    if (!setup.is_valid) {
        return false;
    }
    
    double risk = 0;
    double reward = 0;
    
    if (setup.stop_loss < setup.entry_price) {
        // Buy trade
        risk = setup.entry_price - setup.stop_loss;
        reward = setup.take_profit - setup.entry_price;
    } else {
        // Sell trade
        risk = setup.stop_loss - setup.entry_price;
        reward = setup.entry_price - setup.take_profit;
    }
    
    if (risk <= 0 || reward <= 0) {
        return false;
    }
    
    double rr_ratio = reward / risk;
    
    // Check if RR is within acceptable range
    if (rr_ratio < MinRiskRewardRatio || rr_ratio > MaxRiskRewardRatio) {
        return false;
    }
    
    // Calculate position size
    double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = account_balance * (RiskPercent / 100.0);
    double point_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    
    setup.position_size = NormalizeDouble(risk_amount / (risk * point_value), 2);
    
    return true;
}

//+------------------------------------------------------------------+
//| STEP 8: Execute Trade                                           |
//+------------------------------------------------------------------+
void ExecuteTrade(TradeSetup &setup, int trend) {
    if (trend == 1) {  // BUY
        if (trade.Buy(setup.position_size, _Symbol, Ask, setup.stop_loss, 
                      setup.take_profit, "MQL King 1 - BUY: " + setup.entry_reason)) {
            PrintFormat("✅ BUY EXECUTED - %s", setup.entry_reason);
            PrintFormat("   Entry: %.2f | SL: %.2f | TP: %.2f | Size: %.2f",
                        setup.entry_price, setup.stop_loss, setup.take_profit, setup.position_size);
            trades_today++;
            consecutive_losses = 0;
        }
    } else if (trend == -1) {  // SELL
        if (trade.Sell(setup.position_size, _Symbol, Bid, setup.stop_loss,
                       setup.take_profit, "MQL King 1 - SELL: " + setup.entry_reason)) {
            PrintFormat("✅ SELL EXECUTED - %s", setup.entry_reason);
            PrintFormat("   Entry: %.2f | SL: %.2f | TP: %.2f | Size: %.2f",
                        setup.entry_price, setup.stop_loss, setup.take_profit, setup.position_size);
            trades_today++;
            consecutive_losses = 0;
        }
    }
}

//+------------------------------------------------------------------+
//| Manage Open Trades                                               |
//+------------------------------------------------------------------+
void ManageOpenTrades() {
    // Check for SL/TP hits and update trailing stops if needed
    // Can be extended for advanced position management
}

//+------------------------------------------------------------------+
//| Helper: Calculate ATR                                            |
//+------------------------------------------------------------------+
double CalculateATR(int period) {
    double atr = 0;
    
    for (int i = 0; i < period && i < Bars(_Symbol, _Period); i++) {
        double tr = MathMax(High[i] - Low[i],
                 MathMax(MathAbs(High[i] - Close[i+1]),
                         MathAbs(Low[i] - Close[i+1])));
        atr += tr;
    }
    
    return atr / period;
}

//+------------------------------------------------------------------+
//| Check Trading Time Filter                                        |
//+------------------------------------------------------------------+
bool IsGoodTradingTime() {
    int current_hour = Hour();
    int current_minute = Minute();
    
    // Avoid Asian dead hours
    if (current_hour >= AsianDeadHour && current_hour < AsianDeadHour + 2) {
        return false;
    }
    
    // Trade London Open (08:00 GMT)
    if (current_hour == LondonOpenHour && current_minute < 30) {
        return true;
    }
    
    // Trade NY Open (13:00 GMT)
    if (current_hour == NYOpenHour && current_minute < 30) {
        return true;
    }
    
    // Trade throughout these hours
    if (current_hour >= LondonOpenHour && current_hour <= NYOpenHour + 4) {
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Count Open Trades                                                |
//+------------------------------------------------------------------+
int CountOpenTrades() {
    int count = 0;
    for (int i = OrdersTotal() - 1; i >= 0; i--) {
        if (OrderSelect(i, SELECT_BY_POS)) {
            if (OrderSymbol() == _Symbol && OrderMagicNumber() == 99999) {
                count++;
            }
        }
    }
    return count;
}

//+------------------------------------------------------------------+
