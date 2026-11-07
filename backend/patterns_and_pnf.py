"""
FoxTrader-Pro Patterns, Auto Trendlines, Point & Figure (P&F), and Options/Volume Profile
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple

class PatternAndChartEngines:
    """Computes Candlestick Patterns, Auto-Trendlines, P&F, and Options/Volume Profiles."""

    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Scans for institutional candlestick patterns across recent bars."""
        patterns = []
        n = len(df)
        if n < 3:
            return patterns

        times = df['timestamp'].tolist() if 'timestamp' in df else [str(i) for i in df.index]
        o, h, l, c = df['open'].values, df['high'].values, df['low'].values, df['close'].values

        for i in range(1, n):
            body = abs(c[i] - o[i])
            rng = h[i] - l[i] + 1e-9
            upper_shadow = h[i] - max(o[i], c[i])
            lower_shadow = min(o[i], c[i]) - l[i]
            
            # Doji
            if body / rng <= 0.1:
                patterns.append({
                    "time": times[i], "index": i, "pattern": "Doji",
                    "type": "neutral", "signal": "Indecision / Potential Reversal"
                })

            # Hammer (Bullish Reversal)
            elif lower_shadow >= 2 * body and upper_shadow <= 0.2 * body and c[i] > o[i]:
                patterns.append({
                    "time": times[i], "index": i, "pattern": "Bullish Hammer",
                    "type": "bullish", "signal": "Bullish Reversal Pin Bar"
                })

            # Shooting Star (Bearish Reversal)
            elif upper_shadow >= 2 * body and lower_shadow <= 0.2 * body and c[i] < o[i]:
                patterns.append({
                    "time": times[i], "index": i, "pattern": "Shooting Star",
                    "type": "bearish", "signal": "Bearish Rejection Pin Bar"
                })

            # Bullish Engulfing
            elif c[i-1] < o[i-1] and c[i] > o[i] and c[i] > o[i-1] and o[i] < c[i-1]:
                patterns.append({
                    "time": times[i], "index": i, "pattern": "Bullish Engulfing",
                    "type": "bullish", "signal": "Strong Bullish Momentum Surge"
                })

            # Bearish Engulfing
            elif c[i-1] > o[i-1] and c[i] < o[i] and c[i] < o[i-1] and o[i] > c[i-1]:
                patterns.append({
                    "time": times[i], "index": i, "pattern": "Bearish Engulfing",
                    "type": "bearish", "signal": "Strong Bearish Distribution Surge"
                })

            # Marubozu (Clean strong candle with tiny wicks)
            elif body / rng >= 0.85:
                p_type = "bullish" if c[i] > o[i] else "bearish"
                patterns.append({
                    "time": times[i], "index": i, "pattern": f"{p_type.capitalize()} Marubozu",
                    "type": p_type, "signal": "Uncontested Institutional Trend Expansion"
                })

        return patterns

    @staticmethod
    def compute_auto_trendlines(df: pd.DataFrame, window: int = 40) -> Dict[str, Any]:
        """Calculates upper resistance and lower support trendlines using linear regression on swing points."""
        if len(df) < 15:
            return {}

        subset = df.iloc[-window:] if len(df) >= window else df
        x = np.arange(len(subset))
        highs = subset['high'].values
        lows = subset['low'].values

        # Resistance line (upper boundary)
        slope_h, intercept_h = np.polyfit(x, highs, 1)
        # Support line (lower boundary)
        slope_l, intercept_l = np.polyfit(x, lows, 1)

        times = subset['timestamp'].tolist() if 'timestamp' in subset else [str(i) for i in subset.index]

        return {
            "resistance": {
                "start": {"x": 0, "y": round(float(intercept_h), 2), "time": times[0]},
                "end": {"x": len(subset) - 1, "y": round(float(slope_h * (len(subset) - 1) + intercept_h), 2), "time": times[-1]},
                "slope": round(float(slope_h), 4)
            },
            "support": {
                "start": {"x": 0, "y": round(float(intercept_l), 2), "time": times[0]},
                "end": {"x": len(subset) - 1, "y": round(float(slope_l * (len(subset) - 1) + intercept_l), 2), "time": times[-1]},
                "slope": round(float(slope_l), 4)
            }
        }

    @staticmethod
    def generate_point_and_figure(df: pd.DataFrame, box_size: float = None, reversal: int = 3) -> Dict[str, Any]:
        """Builds a classic Point & Figure (P&F) matrix of 'X' and 'O' columns."""
        if len(df) < 5:
            return {"columns": [], "boxSize": 1.0}

        close_prices = df['close'].values
        if box_size is None or box_size <= 0:
            # Auto box size based on 1% or ATR
            box_size = max(0.5, round(float(np.mean(close_prices)) * 0.005, 2))

        columns = []
        current_type = None  # 'X' or 'O'
        current_column = []

        for price in close_prices:
            box_price = round(price / box_size) * box_size

            if current_type is None:
                current_type = 'X'
                current_column = [box_price]
                continue

            if current_type == 'X':
                if box_price >= current_column[-1] + box_size:
                    # Continue rising
                    steps = int(round((box_price - current_column[-1]) / box_size))
                    for s in range(1, steps + 1):
                        current_column.append(round(current_column[-1] + box_size, 2))
                elif box_price <= current_column[-1] - (reversal * box_size):
                    # Reversal to 'O'
                    columns.append({"type": "X", "boxes": current_column})
                    current_type = 'O'
                    steps = int(round((current_column[-1] - box_price) / box_size))
                    current_column = [round(current_column[-1] - s * box_size, 2) for s in range(1, steps + 1)]

            elif current_type == 'O':
                if box_price <= current_column[-1] - box_size:
                    # Continue falling
                    steps = int(round((current_column[-1] - box_price) / box_size))
                    for s in range(1, steps + 1):
                        current_column.append(round(current_column[-1] - box_size, 2))
                elif box_price >= current_column[-1] + (reversal * box_size):
                    # Reversal to 'X'
                    columns.append({"type": "O", "boxes": current_column})
                    current_type = 'X'
                    steps = int(round((box_price - current_column[-1]) / box_size))
                    current_column = [round(current_column[-1] + s * box_size, 2) for s in range(1, steps + 1)]

        if current_column:
            columns.append({"type": current_type, "boxes": current_column})

        return {
            "boxSize": box_size,
            "reversal": reversal,
            "totalColumns": len(columns),
            "columns": columns[-30:] # return last 30 columns for display
        }

    @staticmethod
    def compute_volume_profile(df: pd.DataFrame, num_bins: int = 24) -> Dict[str, Any]:
        """Calculates Point of Control (POC), Value Area High (VAH), and Value Area Low (VAL)."""
        if len(df) == 0:
            return {}

        min_p = float(df['low'].min())
        max_p = float(df['high'].max())
        if max_p == min_p:
            max_p += 1.0

        bins = np.linspace(min_p, max_p, num_bins + 1)
        vol_profile = np.zeros(num_bins)

        for _, row in df.iterrows():
            typical = (row['high'] + row['low'] + row['close']) / 3
            b_idx = int((typical - min_p) / (max_p - min_p) * (num_bins - 1))
            b_idx = max(0, min(num_bins - 1, b_idx))
            vol_profile[b_idx] += row['volume']

        poc_idx = int(np.argmax(vol_profile))
        poc_price = (bins[poc_idx] + bins[poc_idx + 1]) / 2

        # 70% Value Area
        total_vol = np.sum(vol_profile)
        target_vol = 0.70 * total_vol
        sorted_indices = np.argsort(vol_profile)[::-1]
        
        va_indices = []
        accum = 0
        for idx in sorted_indices:
            accum += vol_profile[idx]
            va_indices.append(idx)
            if accum >= target_vol:
                break

        vah_idx = max(va_indices)
        val_idx = min(va_indices)
        vah_price = bins[vah_idx + 1]
        val_price = bins[val_idx]

        profile_rows = []
        for i in range(num_bins):
            p_mid = round(float((bins[i] + bins[i + 1]) / 2), 2)
            profile_rows.append({
                "price": p_mid,
                "volume": int(vol_profile[i]),
                "isPOC": bool(i == poc_idx),
                "isValueArea": bool(int(val_idx) <= i <= int(vah_idx))
            })

        return {
            "poc": round(float(poc_price), 2),
            "vah": round(float(vah_price), 2),
            "val": round(float(val_price), 2),
            "profile": profile_rows
        }

    @staticmethod
    def get_options_analytics(underlying_price: float) -> Dict[str, Any]:
        """Simulates/calculates live strike battlefields, PCR, Put Writing & Call Writing."""
        base_strike = round(underlying_price / 50.0) * 50
        strikes = [base_strike + i * 50 for i in range(-5, 6)]
        
        chain = []
        total_call_oi = 0
        total_put_oi = 0
        
        for s in strikes:
            dist = abs(s - underlying_price)
            # More OI near ATM
            call_oi = int(max(1000, 150000 - dist * 250 + (np.random.randint(-15000, 15000))))
            put_oi = int(max(1000, 140000 - dist * 240 + (np.random.randint(-15000, 15000))))
            total_call_oi += call_oi
            total_put_oi += put_oi
            
            chain.append({
                "strike": s,
                "callOI": call_oi,
                "putOI": put_oi,
                "callChange": int(np.random.randint(-8000, 18000)),
                "putChange": int(np.random.randint(-8000, 18000)),
                "isATM": bool(s == base_strike)
            })
            
        pcr = round(total_put_oi / (total_call_oi + 1e-9), 2)
        sentiment = "Strongly Bullish" if pcr > 1.25 else ("Mildly Bullish" if pcr > 1.0 else ("Bearish" if pcr < 0.8 else "Neutral"))
        
        return {
            "underlyingPrice": round(underlying_price, 2),
            "pcr": pcr,
            "sentiment": sentiment,
            "totalCallOI": total_call_oi,
            "totalPutOI": total_put_oi,
            "maxPain": base_strike,
            "chain": chain
        }
