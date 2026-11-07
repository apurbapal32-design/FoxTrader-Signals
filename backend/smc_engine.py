"""
FoxTrader-Pro Smart Money Concepts (SMC) & Institutional Price Action Engine
Calculates BOS, CHoCH, Order Blocks, Fair Value Gaps (FVG), Liquidity Sweeps,
Premium/Discount Equilibrium Zones, and Institutional Trade Setups.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple

class SMCEngine:
    """Smart Money Concepts (SMC) detector for multi-timeframe OHLCV data."""

    @staticmethod
    def detect_swings(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
        """Identifies Fractal Swing Highs and Swing Lows (pivot points)."""
        df = df.copy()
        highs = df['high'].values
        lows = df['low'].values
        n = len(df)
        
        swing_high = np.zeros(n, dtype=bool)
        swing_low = np.zeros(n, dtype=bool)
        
        for i in range(window, n - window):
            # Swing High
            is_sh = True
            for k in range(1, window + 1):
                if highs[i] <= highs[i - k] or highs[i] <= highs[i + k]:
                    is_sh = False
                    break
            swing_high[i] = is_sh
            
            # Swing Low
            is_sl = True
            for k in range(1, window + 1):
                if lows[i] >= lows[i - k] or lows[i] >= lows[i + k]:
                    is_sl = False
                    break
            swing_low[i] = is_sl
            
        df['swing_high'] = swing_high
        df['swing_low'] = swing_low
        return df

    @staticmethod
    def detect_fvg(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detects 3-candle Fair Value Gaps (FVG).
        Bullish FVG: Low[i] > High[i-2]
        Bearish FVG: High[i] < Low[i-2]
        """
        fvgs = []
        n = len(df)
        times = df['timestamp'].tolist() if 'timestamp' in df else [str(i) for i in df.index]
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values

        for i in range(2, n):
            # Bullish Imbalance
            if lows[i] > highs[i - 2]:
                top = float(lows[i])
                bottom = float(highs[i - 2])
                gap_size = top - bottom
                # Check mitigation
                mitigated = False
                for j in range(i + 1, n):
                    if lows[j] <= bottom:
                        mitigated = True
                        break
                fvgs.append({
                    "id": f"fvg_bull_{i}",
                    "type": "bullish",
                    "startIndex": i - 2,
                    "startTime": times[i - 2],
                    "endIndex": n - 1,
                    "endTime": times[-1],
                    "top": round(top, 2),
                    "bottom": round(bottom, 2),
                    "size": round(gap_size, 2),
                    "mitigated": mitigated
                })

            # Bearish Imbalance
            if highs[i] < lows[i - 2]:
                top = float(lows[i - 2])
                bottom = float(highs[i])
                gap_size = top - bottom
                mitigated = False
                for j in range(i + 1, n):
                    if highs[j] >= top:
                        mitigated = True
                        break
                fvgs.append({
                    "id": f"fvg_bear_{i}",
                    "type": "bearish",
                    "startIndex": i - 2,
                    "startTime": times[i - 2],
                    "endIndex": n - 1,
                    "endTime": times[-1],
                    "top": round(top, 2),
                    "bottom": round(bottom, 2),
                    "size": round(gap_size, 2),
                    "mitigated": mitigated
                })

        return fvgs

    @staticmethod
    def detect_market_structure(df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detects:
        - BOS (Break of Structure): Candle body breaks past previous structural swing point in trend direction
        - CHoCH (Change of Character): Reversal break of the opposing key swing point
        - Order Blocks (OB): Decisive origin candles of the impulsive breaks
        """
        df = SMCEngine.detect_swings(df, window=3)
        n = len(df)
        times = df['timestamp'].tolist() if 'timestamp' in df else [str(i) for i in df.index]
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        opens = df['open'].values

        structure_breaks = []
        order_blocks = []
        liquidity_sweeps = []

        last_swing_high = None
        last_swing_low = None
        current_trend = 0  # 1: Bullish, -1: Bearish

        for i in range(n):
            if df['swing_high'].iloc[i]:
                last_swing_high = {"index": i, "time": times[i], "price": float(highs[i])}
            if df['swing_low'].iloc[i]:
                last_swing_low = {"index": i, "time": times[i], "price": float(lows[i])}

            # Bullish Breakout
            if last_swing_high is not None and i > last_swing_high["index"]:
                # Liquidity Sweep Check: Wick exceeded, but close is below
                if highs[i] > last_swing_high["price"] and closes[i] <= last_swing_high["price"]:
                    liquidity_sweeps.append({
                        "type": "bearish_sweep",
                        "time": times[i],
                        "index": i,
                        "sweptPrice": round(last_swing_high["price"], 2),
                        "high": round(float(highs[i]), 2),
                        "name": "Buy-side Liquidity Hunt (Sweep High)"
                    })

                # Body close breaks structure
                elif closes[i] > last_swing_high["price"]:
                    is_choch = (current_trend == -1)
                    structure_breaks.append({
                        "type": "CHoCH" if is_choch else "BOS",
                        "direction": "bullish",
                        "time": times[i],
                        "index": i,
                        "breakPrice": round(last_swing_high["price"], 2),
                        "candleClose": round(float(closes[i]), 2)
                    })
                    current_trend = 1

                    # Identify Bullish Order Block (last bearish candle before breakout impulse)
                    lookback_start = max(0, i - 10)
                    for k in range(i - 1, lookback_start, -1):
                        if closes[k] < opens[k]: # Bearish candle
                            order_blocks.append({
                                "id": f"ob_bull_{k}",
                                "type": "bullish_demand",
                                "time": times[k],
                                "index": k,
                                "top": round(float(highs[k]), 2),
                                "bottom": round(float(lows[k]), 2),
                                "mitigated": False
                            })
                            break
                    last_swing_high = None

            # Bearish Breakout
            if last_swing_low is not None and i > last_swing_low["index"]:
                # Liquidity Sweep Check: Wick dipped, but close is above
                if lows[i] < last_swing_low["price"] and closes[i] >= last_swing_low["price"]:
                    liquidity_sweeps.append({
                        "type": "bullish_sweep",
                        "time": times[i],
                        "index": i,
                        "sweptPrice": round(last_swing_low["price"], 2),
                        "low": round(float(lows[i]), 2),
                        "name": "Sell-side Liquidity Hunt (Sweep Low)"
                    })

                elif closes[i] < last_swing_low["price"]:
                    is_choch = (current_trend == 1)
                    structure_breaks.append({
                        "type": "CHoCH" if is_choch else "BOS",
                        "direction": "bearish",
                        "time": times[i],
                        "index": i,
                        "breakPrice": round(last_swing_low["price"], 2),
                        "candleClose": round(float(closes[i]), 2)
                    })
                    current_trend = -1

                    # Identify Bearish Order Block (last bullish candle before downward break)
                    lookback_start = max(0, i - 10)
                    for k in range(i - 1, lookback_start, -1):
                        if closes[k] > opens[k]: # Bullish candle
                            order_blocks.append({
                                "id": f"ob_bear_{k}",
                                "type": "bearish_supply",
                                "time": times[k],
                                "index": k,
                                "top": round(float(highs[k]), 2),
                                "bottom": round(float(lows[k]), 2),
                                "mitigated": False
                            })
                            break
                    last_swing_low = None

        return structure_breaks, order_blocks, liquidity_sweeps

    @staticmethod
    def compute_premium_discount(df: pd.DataFrame, lookback: int = 50) -> Dict[str, Any]:
        """Calculates 50% Equilibrium, Premium (> 0.5) and Discount (< 0.5) zones."""
        if len(df) == 0:
            return {}
        subset = df.iloc[-lookback:] if len(df) >= lookback else df
        highest = float(subset['high'].max())
        lowest = float(subset['low'].min())
        equilibrium = (highest + lowest) / 2.0
        current_close = float(df['close'].iloc[-1])
        
        # Fibonacci Retracement Levels
        diff = highest - lowest
        fib_786 = highest - 0.786 * diff
        fib_618 = highest - 0.618 * diff
        fib_500 = equilibrium
        fib_382 = highest - 0.382 * diff

        zone = "Discount (Buy Zone)" if current_close < equilibrium else "Premium (Sell Zone)"
        
        return {
            "rangeHigh": round(highest, 2),
            "rangeLow": round(lowest, 2),
            "equilibrium": round(equilibrium, 2),
            "currentClose": round(current_close, 2),
            "zone": zone,
            "fib_786": round(fib_786, 2),
            "fib_618": round(fib_618, 2),
            "fib_500": round(fib_500, 2),
            "fib_382": round(fib_382, 2)
        }

    @staticmethod
    def calculate_trade_setup(df: pd.DataFrame, smc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates Potential Entry, Stop Loss, and 1R / 2R / 3R Targets."""
        if len(df) == 0:
            return {}
        
        current_close = float(df['close'].iloc[-1])
        # Approximate ATR
        recent = df.iloc[-14:]
        tr = (recent['high'] - recent['low']).mean()
        
        breaks = smc_data.get('structureBreaks', [])
        latest_break = breaks[-1] if breaks else None
        
        if latest_break and latest_break.get('direction') == 'bullish':
            entry = current_close
            sl = round(entry - 1.5 * tr, 2)
            risk = entry - sl
            t1 = round(entry + 1.0 * risk, 2)
            t2 = round(entry + 2.0 * risk, 2)
            t3 = round(entry + 3.0 * risk, 2)
            bias = "BULLISH (Long Setup)"
        else:
            entry = current_close
            sl = round(entry + 1.5 * tr, 2)
            risk = sl - entry
            t1 = round(entry - 1.0 * risk, 2)
            t2 = round(entry - 2.0 * risk, 2)
            t3 = round(entry - 3.0 * risk, 2)
            bias = "BEARISH (Short Setup)"

        return {
            "bias": bias,
            "entry": round(entry, 2),
            "stopLoss": sl,
            "target1": t1,
            "target2": t2,
            "target3": t3,
            "riskReward": "1:2.0+",
            "atr": round(tr, 2)
        }
