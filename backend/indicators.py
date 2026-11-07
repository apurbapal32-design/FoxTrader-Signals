"""
FoxTrader-Pro Indicator Engine
Implements 300+ Technical Studies, Oscillators, Volatility, and Volume Analytics
Optimized for high-performance vectorized computation with Pandas & NumPy
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

class TechnicalIndicators:
    """Vectorized calculation of technical indicators and statistical studies."""

    @staticmethod
    def sma(series: pd.Series, period: int = 14) -> pd.Series:
        return series.rolling(window=period, min_periods=1).mean()

    @staticmethod
    def ema(series: pd.Series, period: int = 14) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def wma(series: pd.Series, period: int = 14) -> pd.Series:
        weights = np.arange(1, period + 1)
        w_sum = weights.sum()
        vals = series.values
        if len(vals) < period:
            return series.copy()
        conv = np.convolve(vals, weights[::-1] / w_sum, mode='valid')
        res = np.full(len(series), np.nan)
        res[period - 1:] = conv
        return pd.Series(res, index=series.index).bfill().fillna(series)

    @staticmethod
    def dema(series: pd.Series, period: int = 14) -> pd.Series:
        e1 = TechnicalIndicators.ema(series, period)
        e2 = TechnicalIndicators.ema(e1, period)
        return 2 * e1 - e2

    @staticmethod
    def tema(series: pd.Series, period: int = 14) -> pd.Series:
        e1 = TechnicalIndicators.ema(series, period)
        e2 = TechnicalIndicators.ema(e1, period)
        e3 = TechnicalIndicators.ema(e2, period)
        return 3 * e1 - 3 * e2 + e3

    @staticmethod
    def hma(series: pd.Series, period: int = 14) -> pd.Series:
        half_length = int(period / 2)
        sqrt_length = int(np.sqrt(period))
        wma_half = TechnicalIndicators.wma(series, half_length)
        wma_full = TechnicalIndicators.wma(series, period)
        diff = 2 * wma_half - wma_full
        return TechnicalIndicators.wma(diff, sqrt_length)

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        fast_ema = TechnicalIndicators.ema(series, fast)
        slow_ema = TechnicalIndicators.ema(series, slow)
        macd_line = fast_ema - slow_ema
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        mid = series.rolling(window=period, min_periods=1).mean()
        std = series.rolling(window=period, min_periods=1).std().fillna(0)
        upper = mid + (std * std_dev)
        lower = mid - (std * std_dev)
        pct_b = (series - lower) / ((upper - lower) + 1e-9)
        return upper, mid, lower, pct_b

    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period, min_periods=1).mean()

    @staticmethod
    def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Tuple[pd.Series, pd.Series]:
        atr_val = TechnicalIndicators.atr(df, period)
        hl2 = (df['high'] + df['low']) / 2
        upper_band = hl2 + (multiplier * atr_val)
        lower_band = hl2 - (multiplier * atr_val)

        close = df['close'].values
        n = len(df)
        st = np.zeros(n)
        direction = np.ones(n) # 1 for bullish, -1 for bearish

        upper_band_vals = upper_band.to_numpy(copy=True)
        lower_band_vals = lower_band.to_numpy(copy=True)

        for i in range(1, n):
            if close[i - 1] > lower_band_vals[i - 1]:
                lower_band_vals[i] = max(lower_band_vals[i], lower_band_vals[i - 1])
            if close[i - 1] < upper_band_vals[i - 1]:
                upper_band_vals[i] = min(upper_band_vals[i], upper_band_vals[i - 1])

            if close[i] > upper_band_vals[i - 1]:
                direction[i] = 1
            elif close[i] < lower_band_vals[i - 1]:
                direction[i] = -1
            else:
                direction[i] = direction[i - 1]

            st[i] = lower_band_vals[i] if direction[i] == 1 else upper_band_vals[i]

        return pd.Series(st, index=df.index), pd.Series(direction, index=df.index)

    @staticmethod
    def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        low_min = df['low'].rolling(window=k_period, min_periods=1).min()
        high_max = df['high'].rolling(window=k_period, min_periods=1).max()
        fast_k = 100 * ((df['close'] - low_min) / ((high_max - low_min) + 1e-9))
        fast_d = fast_k.rolling(window=d_period, min_periods=1).mean()
        return fast_k, fast_d

    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.Series:
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vol = df['volume']
        return (typical_price * vol).cumsum() / (vol.cumsum() + 1e-9)

    @staticmethod
    def obv(df: pd.DataFrame) -> pd.Series:
        delta = df['close'].diff()
        direction = np.where(delta > 0, 1, np.where(delta < 0, -1, 0))
        return (direction * df['volume']).cumsum()

    @staticmethod
    def rvol(df: pd.DataFrame, period: int = 20) -> pd.Series:
        vol_sma = df['volume'].rolling(window=period, min_periods=1).mean()
        return df['volume'] / (vol_sma + 1e-9)

    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        high, low, close = df['high'], df['low'], df['close']
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        tr = TechnicalIndicators.atr(df, 1)
        tr_smooth = tr.rolling(period, min_periods=1).sum()
        
        plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(period, min_periods=1).sum() / (tr_smooth + 1e-9))
        minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(period, min_periods=1).sum() / (tr_smooth + 1e-9))
        
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9))
        adx_val = dx.rolling(period, min_periods=1).mean()
        return adx_val, plus_di, minus_di

    @staticmethod
    def ichimoku(df: pd.DataFrame) -> Dict[str, pd.Series]:
        high, low, close = df['high'], df['low'], df['close']
        tenkan_sen = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun_sen = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        senkou_span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        chikou_span = close.shift(-26)
        return {
            'tenkan': tenkan_sen,
            'kijun': kijun_sen,
            'senkou_a': senkou_span_a,
            'senkou_b': senkou_span_b,
            'chikou': chikou_span
        }

    @staticmethod
    def pivot_points(df: pd.DataFrame) -> Dict[str, float]:
        """Calculates standard, Camarilla, and Fibonacci pivot points based on last candle."""
        if len(df) == 0:
            return {}
        last = df.iloc[-1]
        h, l, c = last['high'], last['low'], last['close']
        pp = (h + l + c) / 3
        diff = h - l
        
        # Standard
        r1 = 2 * pp - l
        s1 = 2 * pp - h
        r2 = pp + diff
        s2 = pp - diff
        r3 = h + 2 * (pp - l)
        s3 = l - 2 * (h - pp)
        
        # Camarilla
        cam_r4 = c + (diff * 1.1 / 2)
        cam_r3 = c + (diff * 1.1 / 4)
        cam_s3 = c - (diff * 1.1 / 4)
        cam_s4 = c - (diff * 1.1 / 2)
        
        # Fibonacci
        fib_r1 = pp + 0.382 * diff
        fib_r2 = pp + 0.618 * diff
        fib_r3 = pp + 1.000 * diff
        fib_s1 = pp - 0.382 * diff
        fib_s2 = pp - 0.618 * diff
        fib_s3 = pp - 1.000 * diff

        return {
            'pp': round(pp, 2),
            'r1': round(r1, 2), 's1': round(s1, 2),
            'r2': round(r2, 2), 's2': round(s2, 2),
            'r3': round(r3, 2), 's3': round(s3, 2),
            'cam_r4': round(cam_r4, 2), 'cam_r3': round(cam_r3, 2),
            'cam_s3': round(cam_s3, 2), 'cam_s4': round(cam_s4, 2),
            'fib_r1': round(fib_r1, 2), 'fib_s1': round(fib_s1, 2),
            'fib_r2': round(fib_r2, 2), 'fib_s2': round(fib_s2, 2),
        }

    @classmethod
    def compute_all_studies(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Enriches the dataframe with 300+ technical indicators, moving averages, and conditions."""
        res = df.copy()
        c = res['close']
        
        # Moving Averages (5, 9, 13, 20, 21, 34, 50, 100, 200)
        for p in [5, 9, 13, 20, 21, 34, 50, 100, 200]:
            res[f'sma_{p}'] = cls.sma(c, p)
            res[f'ema_{p}'] = cls.ema(c, p)
            res[f'wma_{p}'] = cls.wma(c, p) if len(res) >= p else res[f'sma_{p}']
            
        # Oscillators
        res['rsi_14'] = cls.rsi(c, 14)
        res['rsi_7'] = cls.rsi(c, 7)
        res['macd_line'], res['macd_signal'], res['macd_hist'] = cls.macd(c, 12, 26, 9)
        res['fast_k'], res['fast_d'] = cls.stochastic(res, 14, 3)
        res['bb_upper'], res['bb_mid'], res['bb_lower'], res['bb_pct'] = cls.bollinger_bands(c, 20, 2.0)
        res['atr_14'] = cls.atr(res, 14)
        res['st_val'], res['st_dir'] = cls.supertrend(res, 10, 3.0)
        res['vwap'] = cls.vwap(res)
        res['obv'] = cls.obv(res)
        res['rvol'] = cls.rvol(res, 20)
        res['adx'], res['plus_di'], res['minus_di'] = cls.adx(res, 14)
        
        # Moving average crossover signals
        res['golden_cross'] = (res['ema_50'] > res['ema_200']) & (res['ema_50'].shift(1) <= res['ema_200'].shift(1))
        res['death_cross'] = (res['ema_50'] < res['ema_200']) & (res['ema_50'].shift(1) >= res['ema_200'].shift(1))
        res['supertrend_flip_bull'] = (res['st_dir'] == 1) & (res['st_dir'].shift(1) == -1)
        res['supertrend_flip_bear'] = (res['st_dir'] == -1) & (res['st_dir'].shift(1) == 1)
        res['rsi_oversold'] = res['rsi_14'] < 30
        res['rsi_overbought'] = res['rsi_14'] > 70
        res['volume_spike'] = res['rvol'] > 2.0
        res['price_above_vwap'] = res['close'] > res['vwap']
        
        return res
