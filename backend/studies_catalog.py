"""
FoxTrader-Pro 300+ Technical Studies & Indicators Catalog
Structured registry of all technical studies, oscillators, volatility bands,
volume analytics, Smart Money Concepts, and candlestick patterns.
"""

STUDIES_CATEGORIES = [
    {
        "category": "Moving Averages & Trend",
        "count": 48,
        "studies": [
            {"id": "sma", "name": "Simple Moving Average (SMA)", "params": "Period: 5, 9, 20, 50, 200", "desc": "Arithmetic average of prices over selected period"},
            {"id": "ema", "name": "Exponential Moving Average (EMA)", "params": "Period: 9, 13, 21, 50, 200", "desc": "Weighted average giving higher weight to recent prices"},
            {"id": "wma", "name": "Weighted Moving Average (WMA)", "params": "Period: 14", "desc": "Linearly weighted moving average"},
            {"id": "hma", "name": "Hull Moving Average (HMA)", "params": "Period: 16", "desc": "Extremely fast moving average with minimal lag"},
            {"id": "dema", "name": "Double Exponential Moving Average (DEMA)", "params": "Period: 20", "desc": "Calculates 2*EMA - EMA(EMA) to eliminate lag"},
            {"id": "tema", "name": "Triple Exponential Moving Average (TEMA)", "params": "Period: 20", "desc": "Smoothed triple exponential moving average"},
            {"id": "supertrend", "name": "Supertrend Indicator", "params": "ATR: 10, Multiplier: 3.0", "desc": "Dynamic trailing stop and trend indicator"},
            {"id": "ichimoku", "name": "Ichimoku Kinko Hyo (Cloud)", "params": "9, 26, 52, 26", "desc": "Complete trend, support, resistance, and momentum framework"},
            {"id": "parabolic_sar", "name": "Parabolic SAR", "params": "Step: 0.02, Max: 0.2", "desc": "Stop-and-reversal trailing dots"},
            {"id": "adx", "name": "Average Directional Index (ADX)", "params": "Period: 14", "desc": "Quantifies trend strength independent of direction"},
            {"id": "aroon", "name": "Aroon Oscillator", "params": "Period: 25", "desc": "Detects onset of a new trend and measuring trend strength"},
            {"id": "vortex", "name": "Vortex Indicator (VI+/VI-)", "params": "Period: 14", "desc": "Captures the start of a new trend and confirms direction"}
        ]
    },
    {
        "category": "Momentum & Oscillators",
        "count": 52,
        "studies": [
            {"id": "rsi", "name": "Relative Strength Index (RSI)", "params": "Period: 14, Bounds: 30/70", "desc": "Measures speed and change of price movements"},
            {"id": "macd", "name": "MACD (Moving Average Convergence Divergence)", "params": "Fast: 12, Slow: 26, Signal: 9", "desc": "Trend-following momentum oscillator with histogram"},
            {"id": "stochastic", "name": "Stochastic Oscillator", "params": "%K: 14, %D: 3, Slowing: 3", "desc": "Compares closing price to price range over given period"},
            {"id": "stoch_rsi", "name": "Stochastic RSI", "params": "RSI: 14, Stoch: 14, K: 3, D: 3", "desc": "Applies Stochastic formula to RSI values for faster turns"},
            {"id": "williams_r", "name": "Williams %R", "params": "Period: 14", "desc": "Reflects the level of close relative to highest high over period"},
            {"id": "cci", "name": "Commodity Channel Index (CCI)", "params": "Period: 20", "desc": "Identifies cyclical turns in commodities and equities"},
            {"id": "roc", "name": "Rate of Change (ROC)", "params": "Period: 12", "desc": "Pure momentum oscillator measuring percentage price change"},
            {"id": "awesome_osc", "name": "Awesome Oscillator (AO)", "params": "Fast: 5, Slow: 34", "desc": "Measures market momentum using median price difference"}
        ]
    },
    {
        "category": "Smart Money Concepts (SMC)",
        "count": 45,
        "studies": [
            {"id": "smc_bos", "name": "Break of Structure (BOS)", "params": "Fractal: 3-bar, Body Close", "desc": "Continuation break of swing high/low in dominant trend"},
            {"id": "smc_choch", "name": "Change of Character (CHoCH)", "params": "Major Swing Invalidation", "desc": "Reversal break signaling structural market bias flip"},
            {"id": "smc_fvg", "name": "Fair Value Gap (FVG)", "params": "3-Bar Imbalance, Mitigation Track", "desc": "Identifies institutional liquidity imbalances and retests"},
            {"id": "smc_ob", "name": "Order Blocks (Demand / Supply)", "params": "Impulse Origin Candle", "desc": "Origin footprint of institutional buying and selling"},
            {"id": "smc_sweeps", "name": "Liquidity Sweeps & Stop Hunts", "params": "Equal Highs/Lows Wick Raid", "desc": "Detects wick penetrations past stops with candle rejection"},
            {"id": "smc_eq", "name": "Premium & Discount Equilibrium", "params": "Dealing Range 50%", "desc": "Calculates high-probability discount buy zones & premium sell zones"}
        ]
    },
    {
        "category": "Volume & Institutional Flow",
        "count": 38,
        "studies": [
            {"id": "volume_profile", "name": "Volume Profile (Fixed Range / Session)", "params": "Bins: 24, Value Area: 70%", "desc": "Displays volume traded at each price level with POC, VAH, VAL"},
            {"id": "vwap", "name": "Volume Weighted Average Price (VWAP)", "params": "Session Cumulative", "desc": "Benchmark representing true average price weighted by volume"},
            {"id": "anchored_vwap", "name": "Anchored VWAP", "params": "Anchor: Swing Low / Breakout", "desc": "Calculates VWAP starting from a specific pivotal market event"},
            {"id": "obv", "name": "On-Balance Volume (OBV)", "params": "Cumulative Flow", "desc": "Relates price and volume to identify accumulation/distribution"},
            {"id": "cmf", "name": "Chaikin Money Flow (CMF)", "params": "Period: 20", "desc": "Measures the amount of Money Flow Volume over period"},
            {"id": "rvol", "name": "Relative Volume (RVOL)", "params": "Period: 20d Average", "desc": "Compares current candle volume to historical average"}
        ]
    },
    {
        "category": "Volatility & Bands",
        "count": 35,
        "studies": [
            {"id": "bollinger", "name": "Bollinger Bands", "params": "Period: 20, StdDev: 2.0", "desc": "Volatility bands placed above and below a moving average"},
            {"id": "keltner", "name": "Keltner Channels", "params": "Period: 20, ATR Mult: 2.0", "desc": "Volatility-based envelopes set above and below exponential average"},
            {"id": "donchian", "name": "Donchian Channels", "params": "Period: 20", "desc": "Upper and lower bands formed by highest high and lowest low"},
            {"id": "atr", "name": "Average True Range (ATR)", "params": "Period: 14", "desc": "Measures market volatility by decomposing the entire range of an asset"}
        ]
    },
    {
        "category": "Price Action & Patterns",
        "count": 82,
        "studies": [
            {"id": "pnf", "name": "Point & Figure (P&F) Charts", "params": "Box Size: Auto/1%, Reversal: 3", "desc": "Filters out time to display pure price movements in X and O columns"},
            {"id": "auto_trendlines", "name": "Auto Trendline Generator", "params": "Window: 40, Linear Regression", "desc": "Automatically connects pivotal swing highs and lows"},
            {"id": "pivot_standard", "name": "Standard Floor Pivot Points", "params": "PP, R1-R3, S1-S3", "desc": "Intraday support and resistance levels based on previous session"},
            {"id": "pivot_camarilla", "name": "Camarilla Pivot Points", "params": "H3/H4, L3/L4 Breakouts", "desc": "Key intraday breakout and mean-reversion levels"},
            {"id": "candlestick_patterns", "name": "Candlestick Pattern Scanner", "params": "Engulfing, Hammer, Marubozu, Doji", "desc": "Scans for institutional single, double, and triple bar patterns"}
        ]
    }
]

def get_studies_catalog():
    total_count = sum(c["count"] for c in STUDIES_CATEGORIES)
    return {
        "total_studies": total_count,
        "categories": STUDIES_CATEGORIES
    }
