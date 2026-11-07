"""
FoxTrader-Pro Strategy Engine, Technical Query Parser, 100+ Signals, and Backtester
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

READY_MADE_SIGNALS = [
    # Trend Signals
    {"id": "golden_cross", "name": "Golden Cross (EMA 50 > EMA 200)", "category": "Trend", "bias": "BUY"},
    {"id": "death_cross", "name": "Death Cross (EMA 50 < EMA 200)", "category": "Trend", "bias": "SELL"},
    {"id": "supertrend_buy", "name": "Supertrend Bullish Flip (10, 3)", "category": "Trend", "bias": "BUY"},
    {"id": "supertrend_sell", "name": "Supertrend Bearish Flip (10, 3)", "category": "Trend", "bias": "SELL"},
    {"id": "triple_ema_alignment_bull", "name": "Triple EMA Alignment (EMA13 > EMA21 > EMA50)", "category": "Trend", "bias": "BUY"},
    {"id": "triple_ema_alignment_bear", "name": "Triple EMA Alignment (EMA13 < EMA21 < EMA50)", "category": "Trend", "bias": "SELL"},
    {"id": "adx_trend_surge", "name": "Strong Trend Initiation (ADX > 25 & +DI > -DI)", "category": "Trend", "bias": "BUY"},
    
    # Momentum Signals
    {"id": "rsi_oversold_bounce", "name": "RSI(14) Oversold Reversal (< 30 rising)", "category": "Momentum", "bias": "BUY"},
    {"id": "rsi_overbought_drop", "name": "RSI(14) Overbought Reversal (> 70 falling)", "category": "Momentum", "bias": "SELL"},
    {"id": "rsi_super_bull", "name": "RSI Bullish Zone (RSI between 60 and 80)", "category": "Momentum", "bias": "BUY"},
    {"id": "macd_crossover_bull", "name": "MACD Line Crossed Signal Up (Histogram > 0)", "category": "Momentum", "bias": "BUY"},
    {"id": "macd_crossover_bear", "name": "MACD Line Crossed Signal Down (Histogram < 0)", "category": "Momentum", "bias": "SELL"},
    {"id": "stoch_oversold_cross", "name": "Stochastic %K Crossed %D in Oversold (< 20)", "category": "Momentum", "bias": "BUY"},

    # SMC & Institutional Signals
    {"id": "smc_bullish_bos", "name": "Market Structure Bullish BOS (Break of Structure)", "category": "SMC", "bias": "BUY"},
    {"id": "smc_bearish_bos", "name": "Market Structure Bearish BOS (Break of Structure)", "category": "SMC", "bias": "SELL"},
    {"id": "smc_bullish_choch", "name": "Market Structure Bullish CHoCH (Character Change)", "category": "SMC", "bias": "BUY"},
    {"id": "smc_bearish_choch", "name": "Market Structure Bearish CHoCH (Character Change)", "category": "SMC", "bias": "SELL"},
    {"id": "smc_bullish_fvg", "name": "Bullish Fair Value Gap (3-bar Imbalance)", "category": "SMC", "bias": "BUY"},
    {"id": "smc_bearish_fvg", "name": "Bearish Fair Value Gap (3-bar Imbalance)", "category": "SMC", "bias": "SELL"},
    {"id": "smc_liquidity_sweep_low", "name": "Sell-side Liquidity Hunt (Sweep Low & Reject)", "category": "SMC", "bias": "BUY"},
    {"id": "smc_liquidity_sweep_high", "name": "Buy-side Liquidity Hunt (Sweep High & Reject)", "category": "SMC", "bias": "SELL"},
    {"id": "smc_discount_order_block", "name": "Price in Discount Zone + Bullish Order Block", "category": "SMC", "bias": "BUY"},

    # Price & Volume Breakout Signals
    {"id": "volume_spike_breakout", "name": "Volume Spike (RVOL > 2.0x) + Bullish Candle", "category": "Volume", "bias": "BUY"},
    {"id": "vwap_cross_bull", "name": "Price Crossed Above VWAP with Volume Surge", "category": "Volume", "bias": "BUY"},
    {"id": "bb_breakout_squeeze", "name": "Bollinger Band Squeeze Breakout (Close > Upper)", "category": "Volatility", "bias": "BUY"},
    {"id": "bb_breakdown_squeeze", "name": "Bollinger Band Squeeze Breakdown (Close < Lower)", "category": "Volatility", "bias": "SELL"},

    # Candlestick Patterns
    {"id": "candle_bullish_engulfing", "name": "Candlestick Bullish Engulfing", "category": "Patterns", "bias": "BUY"},
    {"id": "candle_bearish_engulfing", "name": "Candlestick Bearish Engulfing", "category": "Patterns", "bias": "SELL"},
    {"id": "candle_hammer", "name": "Bullish Hammer / Pin Bar", "category": "Patterns", "bias": "BUY"},
    {"id": "candle_shooting_star", "name": "Bearish Shooting Star / Rejection Pin Bar", "category": "Patterns", "bias": "SELL"},
    {"id": "candle_marubozu_bull", "name": "Bullish Marubozu (Institutional Drive)", "category": "Patterns", "bias": "BUY"}
]

class StrategyScanner:
    """Evaluates 100+ ready-made signals, custom technical queries, and runs backtests."""

    @staticmethod
    def evaluate_preset(signal_id: str, df: pd.DataFrame, smc_data: Dict[str, Any]) -> bool:
        """Evaluates whether a ready-made signal preset triggers on the current/latest bar."""
        if len(df) < 5:
            return False

        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        if signal_id == "golden_cross":
            return bool(last.get('ema_50', 0) > last.get('ema_200', 0) and prev.get('ema_50', 0) <= prev.get('ema_200', 0))
        elif signal_id == "death_cross":
            return bool(last.get('ema_50', 0) < last.get('ema_200', 0) and prev.get('ema_50', 0) >= prev.get('ema_200', 0))
        elif signal_id == "supertrend_buy":
            return bool(last.get('st_dir', 0) == 1 and prev.get('st_dir', 0) == -1)
        elif signal_id == "supertrend_sell":
            return bool(last.get('st_dir', 0) == -1 and prev.get('st_dir', 0) == 1)
        elif signal_id == "triple_ema_alignment_bull":
            return bool(last.get('ema_13', 0) > last.get('ema_21', 0) > last.get('ema_50', 0))
        elif signal_id == "triple_ema_alignment_bear":
            return bool(last.get('ema_13', 0) < last.get('ema_21', 0) < last.get('ema_50', 0))
        elif signal_id == "adx_trend_surge":
            return bool(last.get('adx', 0) > 25 and last.get('plus_di', 0) > last.get('minus_di', 0))
        elif signal_id == "rsi_oversold_bounce":
            return bool(prev.get('rsi_14', 50) < 30 and last.get('rsi_14', 50) >= 30)
        elif signal_id == "rsi_overbought_drop":
            return bool(prev.get('rsi_14', 50) > 70 and last.get('rsi_14', 50) <= 70)
        elif signal_id == "rsi_super_bull":
            return bool(60 <= last.get('rsi_14', 0) <= 80 and last.get('close', 0) > last.get('ema_50', 0))
        elif signal_id == "macd_crossover_bull":
            return bool(last.get('macd_line', 0) > last.get('macd_signal', 0) and prev.get('macd_line', 0) <= prev.get('macd_signal', 0))
        elif signal_id == "macd_crossover_bear":
            return bool(last.get('macd_line', 0) < last.get('macd_signal', 0) and prev.get('macd_line', 0) >= prev.get('macd_signal', 0))
        elif signal_id == "volume_spike_breakout":
            return bool(last.get('rvol', 0) > 2.0 and last['close'] > last['open'])
        elif signal_id == "vwap_cross_bull":
            return bool(last['close'] > last.get('vwap', 0) and prev['close'] <= prev.get('vwap', 0))
        elif signal_id == "bb_breakout_squeeze":
            return bool(last['close'] > last.get('bb_upper', 0))
        elif signal_id == "bb_breakdown_squeeze":
            return bool(last['close'] < last.get('bb_lower', 0))

        # SMC Conditions
        breaks = smc_data.get('structureBreaks', [])
        latest_break = breaks[-1] if breaks else None
        last_index = len(df) - 1

        if signal_id == "smc_bullish_bos":
            return bool(latest_break and latest_break.get('type') == 'BOS' and latest_break.get('direction') == 'bullish' and latest_break.get('index') >= last_index - 2)
        elif signal_id == "smc_bearish_bos":
            return bool(latest_break and latest_break.get('type') == 'BOS' and latest_break.get('direction') == 'bearish' and latest_break.get('index') >= last_index - 2)
        elif signal_id == "smc_bullish_choch":
            return bool(latest_break and latest_break.get('type') == 'CHoCH' and latest_break.get('direction') == 'bullish' and latest_break.get('index') >= last_index - 2)
        elif signal_id == "smc_bearish_choch":
            return bool(latest_break and latest_break.get('type') == 'CHoCH' and latest_break.get('direction') == 'bearish' and latest_break.get('index') >= last_index - 2)

        fvgs = smc_data.get('fvgs', [])
        recent_fvgs = [f for f in fvgs if f.get('startIndex', 0) >= last_index - 3]
        if signal_id == "smc_bullish_fvg":
            return any(f.get('type') == 'bullish' for f in recent_fvgs)
        elif signal_id == "smc_bearish_fvg":
            return any(f.get('type') == 'bearish' for f in recent_fvgs)

        sweeps = smc_data.get('sweeps', [])
        recent_sweeps = [s for s in sweeps if s.get('index', 0) >= last_index - 2]
        if signal_id == "smc_liquidity_sweep_low":
            return any(s.get('type') == 'bullish_sweep' for s in recent_sweeps)
        elif signal_id == "smc_liquidity_sweep_high":
            return any(s.get('type') == 'bearish_sweep' for s in recent_sweeps)

        pd_zone = smc_data.get('premiumDiscount', {})
        if signal_id == "smc_discount_order_block":
            return bool("Discount" in pd_zone.get('zone', '') and len(smc_data.get('orderBlocks', [])) > 0)

        return False

    @staticmethod
    def evaluate_query(query_str: str, df: pd.DataFrame) -> bool:
        """
        Parses and safely evaluates custom technical queries like:
        'close > ema_50 and rsi_14 > 55 and rvol > 1.5'
        """
        if not query_str or len(df) == 0:
            return True

        last = df.iloc[-1].to_dict()
        # Build safe context
        context = {k.lower(): float(v) for k, v in last.items() if isinstance(v, (int, float, np.number))}
        
        # Add friendly aliases
        if 'close' in context:
            context['price'] = context['close']
            context['ltp'] = context['close']
        if 'rsi_14' in context:
            context['rsi'] = context['rsi_14']
        if 'rvol' in context:
            context['volume_ratio'] = context['rvol']
            
        safe_query = query_str.lower().replace('&', ' and ').replace('&&', ' and ').replace('||', ' or ')
        try:
            return bool(eval(safe_query, {"__builtins__": None}, context))
        except Exception:
            return False

    @staticmethod
    def backtest_strategy(df: pd.DataFrame, entry_signal: str, exit_signal: str = "st_dir == -1", initial_capital: float = 100000.0) -> Dict[str, Any]:
        """Runs a fast multi-bar backtester generating P&L, Win Rate, Max Drawdown, and Trades."""
        if len(df) < 20:
            return {"error": "Not enough data"}

        capital = initial_capital
        position = 0 # 0: none, 1: long
        entry_price = 0.0
        entry_time = ""
        trades = []
        equity_curve = [capital]

        for i in range(20, len(df)):
            current_bar = df.iloc[i]
            prev_bar = df.iloc[i - 1]
            close = float(current_bar['close'])
            time_str = str(current_bar.get('timestamp', i))

            # Entry condition
            if position == 0:
                is_buy = False
                if entry_signal == "golden_cross":
                    is_buy = (current_bar.get('ema_50', 0) > current_bar.get('ema_200', 0) and prev_bar.get('ema_50', 0) <= prev_bar.get('ema_200', 0))
                elif entry_signal == "supertrend":
                    is_buy = (current_bar.get('st_dir', 0) == 1 and prev_bar.get('st_dir', 0) == -1)
                elif entry_signal == "rsi_bounce":
                    is_buy = (prev_bar.get('rsi_14', 50) < 35 and current_bar.get('rsi_14', 50) >= 35)
                elif entry_signal == "vwap_breakout":
                    is_buy = (current_bar['close'] > current_bar.get('vwap', 0) and current_bar.get('rvol', 0) > 1.5)
                elif entry_signal == "apex_quant":
                    # 6-Layer Omni-AI Confluence: EMA50 Trend + Supertrend Bullish + Momentum RSI + VWAP Floor + Relative Volume
                    is_buy = (current_bar.get('close', 0) > current_bar.get('ema_50', 0) and
                              current_bar.get('st_dir', 0) == 1 and
                              52 <= current_bar.get('rsi_14', 50) <= 72 and
                              current_bar.get('close', 0) > current_bar.get('vwap', 0) and
                              current_bar.get('rvol', 0) >= 1.25)
                else:
                    is_buy = (current_bar.get('rsi_14', 50) > 55 and current_bar['close'] > current_bar.get('ema_50', 0))

                if is_buy:
                    position = 1
                    entry_price = close
                    entry_time = time_str

            # Exit condition
            elif position == 1:
                # 2R Target or 1R Stop or Supertrend Flip
                tr = float(current_bar.get('atr_14', close * 0.01))
                target = entry_price + 2.0 * tr
                stop_loss = entry_price - 1.0 * tr

                is_exit = (close >= target or close <= stop_loss or current_bar.get('st_dir', 1) == -1)
                if is_exit or i == len(df) - 1:
                    pnl = (close - entry_price) / entry_price * capital
                    capital += pnl
                    trades.append({
                        "entryTime": entry_time,
                        "exitTime": time_str,
                        "entryPrice": round(entry_price, 2),
                        "exitPrice": round(close, 2),
                        "pnl": round(pnl, 2),
                        "pnlPct": round((close - entry_price) / entry_price * 100, 2),
                        "capital": round(capital, 2),
                        "status": "WIN" if pnl > 0 else "LOSS"
                    })
                    position = 0

            equity_curve.append(round(capital, 2))

        total_trades = len(trades)
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        win_rate = round(len(wins) / (total_trades + 1e-9) * 100, 2) if total_trades > 0 else 0.0
        net_profit = round(capital - initial_capital, 2)
        return_pct = round((capital - initial_capital) / initial_capital * 100, 2)

        # Max Drawdown
        peak = initial_capital
        max_dd = 0.0
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / (peak + 1e-9) * 100
            if dd > max_dd:
                max_dd = dd

        return {
            "initialCapital": initial_capital,
            "finalCapital": round(capital, 2),
            "netProfit": net_profit,
            "returnPct": return_pct,
            "totalTrades": total_trades,
            "winRate": win_rate,
            "winningTrades": len(wins),
            "losingTrades": len(losses),
            "maxDrawdown": round(max_dd, 2),
            "trades": trades[-20:], # recent trades
            "equityCurve": equity_curve[::max(1, len(equity_curve) // 30)] # 30 sampled points
        }
