//+------------------------------------------------------------------+
//|                   XAUUSD Pro Strategy Expert Advisor              |
//|         Market Structure + Pullback + Confluence Trading         |
//|                  Converted from Python HFT Strategy               |
//+------------------------------------------------------------------+
#property copyright "HFT System"
#property link      "https://github.com"
#property version   "1.0"
#property description "Professional XAUUSD Trading - Smart Money + Confluence Based"

#include <Trade\Trade.mqh>

//+------ INPUT PARAMETERS ------+

// Indicator Parameters
input int TrendEMA = 200;              // Trend filter period
input int PullbackEMA = 20;            // Pullback zone period
input int ATRPeriod = 14;              // Volatility period
input int RSIPeriod = 14;              // Momentum period
input int LookbackBars = 20;           // Swing detection period

// Risk Management
input double MinRRRatio = 2.0;         // Minimum Risk/Reward ratio (1:2)
input double RiskPercentage = 1.0;     // Risk per trade (% of account)
input double MaxDailyLossPercent = 3.0; // Max daily loss (% of account)
input double LotSize = 0.1;            // Fixed lot size (if not using auto-sizing)
input bool UseAutoLotSize = false;     // Auto-calculate lot based on SL

// Trade Management
input int MaxHoldingBars = 120;        // Max holding period (bars)
input int MaxOpenTrades = 2;           // Maximum concurrent positions
input bool UseTimeFilter = false;      // Use session filter
input int StartHour = 13;              // London Open (13:00 GMT)
input int EndHour = 21;                // NY Close (21:00 GMT)

// Thresholds
input double PullbackZonePercent = 2.0; // Zone around 20 EMA (%)
input double VolatilityHighMultiplier = 1.5; // High volatility threshold
input double VolatilityLowMultiplier = 0.7;  // Low volatility threshold
input double VolumeFilterRatio = 0.8;   // Minimum volume vs average

//+------ GLOBAL VARIABLES ------+
CTrade trade;
double DailyLoss = 0;
datetime LastDayCheck = 0;
double AccountStartEq = 0;

//+------ STRUCTURES ------+
struct MarketConditions {
    string trend;              // "UPTREND", "DOWNTREND", "MIXED"
    string volatility;         // "HIGH", "LOW", "NORMAL"
    double ema_200;
    double ema_20;
    double atr;
    double rsi;
    double swing_high;
    double swing_low;
};

struct TradeSetup {
    bool is_valid;
    double entry_price;
    double stop_loss;
    double target_price;
    double risk_reward_ratio;
    double position_size;
};

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    // Initialize trade object
    trade.SetExpertMagicNumber(54321);
    trade.SetDeviationInPoints(10);
    
    // Initialize daily loss tracking
    AccountStartEq = AccountInfoDouble(ACCOUNT_EQUITY);
    
    Print("═══════════════════════════════════════════════════════");
    Print("XAUUSD Pro Strategy EA Initialized");
    Print("═══════════════════════════════════════════════════════");
    PrintFormat("Trend EMA: %d | Pullback EMA: %d | ATR: %d | RSI: %d",
                TrendEMA, PullbackEMA, ATRPeriod, RSIPeriod);
    PrintFormat("Min RR: 1:%.1f | Risk: %.1f%% | Max Daily Loss: %.1f%%",
                MinRRRatio, RiskPercentage, MaxDailyLossPercent);
    Print("═══════════════════════════════════════════════════════");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Safety checks
    if (Ask <= 0 || Bid <= 0) return;  // No valid prices
    if (Close[0] <= 0) return;  // Invalid close
    
    // Update daily loss tracking
    UpdateDailyLossTracking();
    
    // Check if daily loss limit exceeded
    if (DailyLoss > MaxDailyLossPercent) {
        Print("Daily loss limit exceeded. No new trades.");
        return;
    }
    
    // Check position limit
    if (CountOpenTrades() >= MaxOpenTrades) {
        return;
    }
    
    // Check time filter if enabled
    if (UseTimeFilter && !IsTimeToTrade()) {
        return;
    }
    
    // Calculate market conditions
    MarketConditions market = CalculateMarketConditions();
    
    // Generate signals
    if (market.ema_200 > 0 && market.ema_20 > 0 && market.atr > 0) {
        CheckBuySignal(market);
        CheckSellSignal(market);
    }
    
    // Update trade management (trailing stops, partial closes, etc.)
    ManageOpenTrades();
}

//+------------------------------------------------------------------+
//| Calculate Market Conditions                                      |
//+------------------------------------------------------------------+
MarketConditions CalculateMarketConditions() {
    MarketConditions market;
    
    // Initialize defaults
    market.trend = "MIXED";
    market.volatility = "NORMAL";
    market.ema_200 = 0;
    market.ema_20 = 0;
    market.atr = 0;
    market.rsi = 50;  // Neutral
    market.swing_high = High[0];
    market.swing_low = Low[0];
    
    if (Bars(_Symbol, _Period) < TrendEMA + 50) {
        return market;
    }
    
    // Calculate EMAs
    market.ema_200 = CalculateEMA(TrendEMA, 0);
    market.ema_20 = CalculateEMA(PullbackEMA, 0);
    
    if (market.ema_200 <= 0 || market.ema_20 <= 0) return market;  // Safety check
    
    // Get current close
    double current_close = Close[0];
    if (current_close <= 0) return market;  // Safety check
    
    // Determine Trend
    if (current_close > market.ema_200) {
        market.trend = "UPTREND";
    } else if (current_close < market.ema_200) {
        market.trend = "DOWNTREND";
    } else {
        market.trend = "MIXED";
    }
    
    // Calculate ATR
    market.atr = CalculateATR(ATRPeriod);
    if (market.atr <= 0) market.atr = (High[0] - Low[0]);  // Fallback
    
    // Calculate RSI
    market.rsi = CalculateRSI(RSIPeriod);
    market.rsi = MathMax(0, MathMin(100, market.rsi));  // Bounds check
    
    // Determine Volatility Level
    double atr_avg = 0;
    int valid_count = 0;
    for (int i = 0; i < 20 && i < Bars(_Symbol, _Period); i++) {
        double atr_val = CalculateATR_At(ATRPeriod, i);
        if (atr_val > 0) {
            atr_avg += atr_val;
            valid_count++;
        }
    }
    
    if (valid_count > 0) {
        atr_avg /= valid_count;
        
        if (market.atr > atr_avg * VolatilityHighMultiplier) {
            market.volatility = "HIGH";
        } else if (market.atr < atr_avg * VolatilityLowMultiplier) {
            market.volatility = "LOW";
        } else {
            market.volatility = "NORMAL";
        }
    }
    
    // Swing Levels
    market.swing_high = FindSwingHigh(LookbackBars);
    market.swing_low = FindSwingLow(LookbackBars);
    
    return market;
}

//+------------------------------------------------------------------+
//| Check Buy Signal                                                 |
//+------------------------------------------------------------------+
void CheckBuySignal(MarketConditions &market) {
    // BUY Conditions:
    // 1. Uptrend (price > 200 EMA)
    // 2. Volatility NOT HIGH
    // 3. Price in pullback zone (20 EMA ±2%)
    // 4. Price above swing low
    // 5. RSI between 35-70 (not oversold, not overbought)
    // 6. Volume decent
    // 7. Good Risk/Reward
    
    double close_price = Close[0];
    if (close_price <= 0) return;  // Safety check
    
    long volume = Volume[0];
    if (volume <= 0) return;  // Safety check
    
    double volume_avg = CalculateVolumeAverage(20);
    if (volume_avg <= 0) return;  // Safety check
    
    // Check all conditions
    bool condition_trend = (StringCompare(market.trend, "UPTREND") == 0);
    bool condition_volatility = (StringCompare(market.volatility, "HIGH") != 0);
    
    // Pullback zone check (within 2% of 20 EMA)
    bool condition_pullback = (market.ema_20 > 0) &&
                              (close_price <= market.ema_20 * (1.0 + PullbackZonePercent / 100.0)) &&
                              (close_price >= market.ema_20 * (1.0 - PullbackZonePercent / 100.0));
    
    bool condition_support = (close_price >= market.swing_low && market.swing_low > 0);
    bool condition_rsi = (market.rsi >= 0 && market.rsi <= 100) && (market.rsi > 35) && (market.rsi < 70);
    bool condition_volume = (volume_avg > 0) && ((double)volume > volume_avg * VolumeFilterRatio);
    
    if (!condition_trend || !condition_volatility || !condition_pullback || 
        !condition_support || !condition_rsi || !condition_volume) {
        return;  // Not all conditions met
    }
    
    // Calculate Trade Setup
    TradeSetup setup;
    setup.is_valid = false;
    setup.entry_price = close_price;
    setup.stop_loss = market.swing_low - market.atr * 0.5;
    
    double risk = setup.entry_price - setup.stop_loss;
    if (risk <= 0 || setup.stop_loss <= 0) return;
    
    setup.target_price = setup.entry_price + risk * MinRRRatio;
    setup.risk_reward_ratio = (risk > 0) ? (setup.target_price - setup.entry_price) / risk : 0;
    setup.is_valid = true;
    
    // Check RR filter
    if (setup.risk_reward_ratio < MinRRRatio) {
        return;  // RR not good enough
    }
    
    // Calculate position size
    setup.position_size = CalculatePositionSize(risk);
    
    // Place BUY order
    ExecuteBuyTrade(setup, market);
}

//+------------------------------------------------------------------+
//| Check Sell Signal                                                |
//+------------------------------------------------------------------+
void CheckSellSignal(MarketConditions &market) {
    // SELL Conditions:
    // 1. Downtrend (price < 200 EMA)
    // 2. Volatility NOT HIGH
    // 3. Price in pullback zone (20 EMA ±2%)
    // 4. Price below swing high
    // 5. RSI between 30-65 (not oversold, not overbought)
    // 6. Volume decent
    // 7. Good Risk/Reward
    
    double close_price = Close[0];
    if (close_price <= 0) return;  // Safety check
    
    long volume = Volume[0];
    if (volume <= 0) return;  // Safety check
    
    double volume_avg = CalculateVolumeAverage(20);
    if (volume_avg <= 0) return;  // Safety check
    
    // Check all conditions
    bool condition_trend = (StringCompare(market.trend, "DOWNTREND") == 0);
    bool condition_volatility = (StringCompare(market.volatility, "HIGH") != 0);
    
    // Pullback zone check
    bool condition_pullback = (market.ema_20 > 0) &&
                              (close_price >= market.ema_20 * (1.0 - PullbackZonePercent / 100.0)) &&
                              (close_price <= market.ema_20 * (1.0 + PullbackZonePercent / 100.0));
    
    bool condition_resistance = (close_price <= market.swing_high && market.swing_high > 0);
    bool condition_rsi = (market.rsi >= 0 && market.rsi <= 100) && (market.rsi < 65) && (market.rsi > 30);
    bool condition_volume = (volume_avg > 0) && ((double)volume > volume_avg * VolumeFilterRatio);
    
    if (!condition_trend || !condition_volatility || !condition_pullback || 
        !condition_resistance || !condition_rsi || !condition_volume) {
        return;  // Not all conditions met
    }
    
    // Calculate Trade Setup
    TradeSetup setup;
    setup.is_valid = false;
    setup.entry_price = close_price;
    setup.stop_loss = market.swing_high + market.atr * 0.5;
    
    double risk = setup.stop_loss - setup.entry_price;
    if (risk <= 0 || setup.stop_loss <= 0) return;
    
    setup.target_price = setup.entry_price - risk * MinRRRatio;
    setup.risk_reward_ratio = (risk > 0) ? (setup.entry_price - setup.target_price) / risk : 0;
    setup.is_valid = true;
    
    // Check RR filter
    if (setup.risk_reward_ratio < MinRRRatio) {
        return;  // RR not good enough
    }
    
    // Calculate position size
    setup.position_size = CalculatePositionSize(risk);
    
    // Place SELL order
    ExecuteSellTrade(setup, market);
}

//+------------------------------------------------------------------+
//| Execute Buy Trade                                                |
//+------------------------------------------------------------------+
void ExecuteBuyTrade(TradeSetup &setup, MarketConditions &market) {
    if (!setup.is_valid || setup.position_size <= 0) return;
    if (!NoOpenBuyOrder()) return;
    if (setup.entry_price <= 0 || setup.stop_loss <= 0 || setup.target_price <= 0) return;
    
    double tp1 = setup.entry_price + (setup.entry_price - setup.stop_loss) * 1.0;
    double tp2 = setup.entry_price + (setup.entry_price - setup.stop_loss) * 2.0;
    double tp3 = setup.entry_price + (setup.entry_price - setup.stop_loss) * 3.0;
    
    if (Ask <= 0) return;  // Check valid market price
    
    if (trade.Buy(setup.position_size, _Symbol, Ask, setup.stop_loss, tp2, "XAUUSD BUY")) {
        PrintFormat("═ BUY SIGNAL ═ Price: %.2f | SL: %.2f | TP: %.2f | RR: %.2f",
                    setup.entry_price, setup.stop_loss, tp2, setup.risk_reward_ratio);
        PrintFormat("  Market: %s | Volatility: %s | RSI: %.1f",
                    market.trend, market.volatility, market.rsi);
    }
}

//+------------------------------------------------------------------+
//| Execute Sell Trade                                               |
//+------------------------------------------------------------------+
void ExecuteSellTrade(TradeSetup &setup, MarketConditions &market) {
    if (!setup.is_valid || setup.position_size <= 0) return;
    if (!NoOpenSellOrder()) return;
    if (setup.entry_price <= 0 || setup.stop_loss <= 0 || setup.target_price <= 0) return;
    
    double tp1 = setup.entry_price - (setup.stop_loss - setup.entry_price) * 1.0;
    double tp2 = setup.entry_price - (setup.stop_loss - setup.entry_price) * 2.0;
    double tp3 = setup.entry_price - (setup.stop_loss - setup.entry_price) * 3.0;
    
    if (Bid <= 0) return;  // Check valid market price
    
    if (trade.Sell(setup.position_size, _Symbol, Bid, setup.stop_loss, tp2, "XAUUSD SELL")) {
        PrintFormat("═ SELL SIGNAL ═ Price: %.2f | SL: %.2f | TP: %.2f | RR: %.2f",
                    setup.entry_price, setup.stop_loss, tp2, setup.risk_reward_ratio);
        PrintFormat("  Market: %s | Volatility: %s | RSI: %.1f",
                    market.trend, market.volatility, market.rsi);
    }


//+------------------------------------------------------------------+
//| Manage Open Trades                                               |
//+------------------------------------------------------------------+
void ManageOpenTrades() {
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        string symbol = PositionGetSymbol(i);
        if (symbol == _Symbol && PositionGetInteger(POSITION_MAGIC) == 54321) {
            // Check max holding time
            datetime pos_time = (datetime)PositionGetInteger(POSITION_TIME);
            if (TimeCurrent() - pos_time > MaxHoldingBars * PeriodSeconds(_Period)) {
                // Close on time stop-loss
                ulong ticket = PositionGetTicket(i);
                trade.PositionClose(ticket);
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Update Daily Loss Tracking                                       |
//+------------------------------------------------------------------+
void UpdateDailyLossTracking() {
    // Check if it's a new day
    if (LastDayCheck == 0 || TimeCurrent() - LastDayCheck > 86400) {  // 24 hours
        LastDayCheck = TimeCurrent();
        AccountStartEq = AccountInfoDouble(ACCOUNT_EQUITY);
        DailyLoss = 0;
    }
    
    double current_equity = AccountInfoDouble(ACCOUNT_EQUITY);
    if (AccountStartEq > 0) {
        double daily_change = (AccountStartEq - current_equity) / AccountStartEq * 100;
        DailyLoss = daily_change;
    }
}

//+------------------------------------------------------------------+
//| Calculate EMA                                                    |
//+------------------------------------------------------------------+
double CalculateEMA(int period, int shift) {
    double ema = 0;
    double multiplier = 2.0 / (period + 1);
    int bars = Bars(_Symbol, _Period);
    
    if (bars < shift + period) return 0;
    
    // Initialize with SMA
    for (int i = shift + period - 1; i >= shift; i--) {
        ema += Close[i];
    }
    ema /= period;
    
    // Calculate EMA
    for (int i = shift - 1; i >= 0; i--) {
        ema = Close[i] * multiplier + ema * (1 - multiplier);
    }
    
    return ema;
}

//+------------------------------------------------------------------+
//| Calculate ATR                                                    |
//+------------------------------------------------------------------+
double CalculateATR(int period) {
    double atr = 0;
    int bars = Bars(_Symbol, _Period);
    if (bars < period + 1) return 0;
    
    for (int i = 0; i < period && i < bars - 1; i++) {
        double tr = MathMax(High[i] - Low[i],
                 MathMax(MathAbs(High[i] - Close[i+1]), 
                         MathAbs(Low[i] - Close[i+1])));
        atr += tr;
    }
    return (period > 0) ? atr / period : 0;
}

//+------------------------------------------------------------------+
//| Calculate ATR at specific bar                                    |
//+------------------------------------------------------------------+
double CalculateATR_At(int period, int shift) {
    double atr = 0;
    int bars = Bars(_Symbol, _Period);
    int count = 0;
    
    for (int i = shift; i < shift + period && i < bars - 1; i++) {
        double tr = MathMax(High[i] - Low[i],
                 MathMax(MathAbs(High[i] - Close[i+1]), 
                         MathAbs(Low[i] - Close[i+1])));
        atr += tr;
        count++;
    }
    return (count > 0) ? atr / count : 0;
}

//+------------------------------------------------------------------+
//| Calculate RSI                                                    |
//+------------------------------------------------------------------+
double CalculateRSI(int period) {
    double up_sum = 0;
    double down_sum = 0;
    int bars = Bars(_Symbol, _Period);
    
    if (bars < period + 1) return 50;  // Return neutral RSI if not enough bars
    
    for (int i = 0; i < period && i < bars - 1; i++) {
        double change = Close[i] - Close[i+1];
        if (change > 0) {
            up_sum += change;
        } else {
            down_sum += MathAbs(change);
        }
    }
    
    double avg_up = (period > 0) ? up_sum / period : 0;
    double avg_down = (period > 0) ? down_sum / period : 0;
    
    if (avg_down <= 0) return 50;  // Return neutral RSI
    
    double rs = avg_up / avg_down;
    double rsi = 100 - (100 / (1 + rs));
    
    return MathMax(0, MathMin(100, rsi));  // Bounds check
}

//+------------------------------------------------------------------+
//| Find Swing High                                                  |
//+------------------------------------------------------------------+
double FindSwingHigh(int lookback) {
    if (lookback <= 0) return High[0];
    
    double swing_high = High[0];
    int bars = Bars(_Symbol, _Period);
    
    for (int i = 0; i < lookback && i < bars; i++) {
        if (High[i] > swing_high) {
            swing_high = High[i];
        }
    }
    return swing_high > 0 ? swing_high : High[0];
}

//+------------------------------------------------------------------+
//| Find Swing Low                                                   |
//+------------------------------------------------------------------+
double FindSwingLow(int lookback) {
    if (lookback <= 0) return Low[0];
    
    double swing_low = Low[0];
    int bars = Bars(_Symbol, _Period);
    
    for (int i = 0; i < lookback && i < bars; i++) {
        if (Low[i] < swing_low) {
            swing_low = Low[i];
        }
    }
    return swing_low > 0 ? swing_low : Low[0];
}

//+------------------------------------------------------------------+
//| Calculate Volume Average                                         |
//+------------------------------------------------------------------+
double CalculateVolumeAverage(int period) {
    if (period <= 0) return 0;
    
    double sum = 0;
    int bars = Bars(_Symbol, _Period);
    int count = 0;
    
    for (int i = 0; i < period && i < bars; i++) {
        sum += (double)Volume[i];  // Cast to double
        count++;
    }
    
    return (count > 0) ? sum / count : 0;
}

//+------------------------------------------------------------------+
//| Calculate Position Size                                          |
//+------------------------------------------------------------------+
double CalculatePositionSize(double risk_pips) {
    if (!UseAutoLotSize) {
        return LotSize;
    }
    
    if (risk_pips <= 0) return LotSize;
    
    double account_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if (account_balance <= 0) return LotSize;
    
    double risk_amount = account_balance * (RiskPercentage / 100.0);
    double risk_per_pip = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    
    if (risk_per_pip <= 0) return LotSize;  // Safety check
    
    double position_size = risk_amount / (risk_pips * risk_per_pip);
    position_size = MathMax(0.01, MathMin(100, position_size));  // Min 0.01, Max 100
    
    return NormalizeDouble(position_size, 2);
}

//+------------------------------------------------------------------+
//| Check No Open Buy Order                                          |
//+------------------------------------------------------------------+
bool NoOpenBuyOrder() {
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (i < 0) break;  // Safety check
        
        string symbol = PositionGetSymbol(i);
        if (symbol == _Symbol && PositionGetInteger(POSITION_MAGIC) == 54321) {
            if (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                return false;
            }
        }
    }
    return true;
}

//+------------------------------------------------------------------+
//| Check No Open Sell Order                                         |
//+------------------------------------------------------------------+
bool NoOpenSellOrder() {
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (i < 0) break;  // Safety check
        
        string symbol = PositionGetSymbol(i);
        if (symbol == _Symbol && PositionGetInteger(POSITION_MAGIC) == 54321) {
            if (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL) {
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
    for (int i = PositionsTotal() - 1; i >= 0; i--) {
        if (i < 0) break;  // Safety check
        
        string symbol = PositionGetSymbol(i);
        if (symbol == _Symbol && PositionGetInteger(POSITION_MAGIC) == 54321) {
            count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Check if it's time to trade                                      |
//+------------------------------------------------------------------+
bool IsTimeToTrade() {
    int current_hour = TimeHour(TimeCurrent());
    return (current_hour >= StartHour && current_hour < EndHour);
}

//+------------------------------------------------------------------+
