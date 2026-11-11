"""
FoxTrader-Pro Live Data Feed & Multi-Broker Ingestion Engine
Streams live prices, ticks, and historical OHLCV data for all 224 F&O Indices & Stocks.
Connects with Fyers API v3, Zerodha, Angel One, and Live Fallback.
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from broker_gateway import BrokerGateway

UNIVERSE_FILE = os.path.join(os.path.dirname(__file__), "fno_universe.json")

class DataFeedManager:
    """Provides streaming real-time prices, historical bars, and multi-timeframe aggregations for all 224 F&O instruments."""

    def __init__(self):
        self.gateway = BrokerGateway()
        self.load_universe()
        self.historical_cache: Dict[str, pd.DataFrame] = {}
        self.extra_indices: Dict[str, Dict[str, Any]] = {}
        self._tick_cursor: int = 0
        self.last_live_sync_count: int = 0
        self.last_live_sync_time: Optional[str] = None
        self.initialize_market_state()

    def load_universe(self):
        if os.path.exists(UNIVERSE_FILE):
            with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
        else:
            raw_list = []

        self.universe_list = raw_list
        self.stocks = {s["symbol"]: dict(s) for s in raw_list}

    def initialize_market_state(self):
        """Initializes realistic baseline prices for all 224 instruments."""
        # Index baseline prices
        index_bases = {
            "NIFTY": 24150.0,
            "BANKNIFTY": 51600.0,
            "FINNIFTY": 23800.0,
            "MIDCPNIFTY": 12850.0,
            "NIFTYNXT50": 68500.0,
            "NIFTYFPI": 24200.0
        }
        
        # Stock specific realistic base prices
        stock_bases = {
            "RELIANCE": 2740.0, "TCS": 4120.0, "HDFCBANK": 1690.0, "ICICIBANK": 1210.0, "INFY": 1820.0,
            "SBIN": 820.0, "BHARTIARTL": 1580.0, "ITC": 465.0, "LT": 3480.0, "BAJFINANCE": 6950.0,
            "BAJAJFINSV": 1934.0, "CHAMBLFERT": 609.25, "HINDUNILVR": 2480.0, "TATASTEEL": 148.5,
            "AXISBANK": 1150.0, "KOTAKBANK": 1780.0, "TATAMOTORS": 980.0, "MARUTI": 11400.0,
            "SUNPHARMA": 1780.0, "DRREDDY": 6250.0, "CIPLA": 1490.0, "ADANIENT": 3120.0,
            "ADANIPORTS": 1390.0, "COALINDIA": 485.0, "NTPC": 410.0, "POWERGRID": 325.0,
            "TITAN": 3380.0, "ULTRACEMCO": 11200.0, "WIPRO": 540.0, "JIOFIN": 340.0,
            "ZOMATO": 265.0, "ETERNAL": 275.0, "BSE": 4500.0, "CDSL": 1450.0, "MCX": 5900.0,
            "HAL": 4350.0, "BEL": 290.0, "BDL": 1150.0, "RVNL": 460.0, "IRFC": 155.0,
            "SUZLON": 65.0, "IDEA": 9.5, "YESBANK": 22.0
        }

        for sym, data in self.stocks.items():
            is_idx = data.get("is_index", False)
            if is_idx and sym in index_bases:
                base = index_bases[sym]
            elif sym in stock_bases:
                base = stock_bases[sym]
            else:
                base = data.get("basePrice", 1250.0)

            # Fluctuations
            pcn = round(random.uniform(-2.2, 2.5), 2)
            ltp = round(base * (1 + pcn / 100.0), 2)
            open_p = round(base * (1 + random.uniform(-0.5, 0.5) / 100.0), 2)
            high_p = round(max(ltp, open_p) + base * random.uniform(0.05, 0.4) / 100.0, 2)
            low_p = round(min(ltp, open_p) - base * random.uniform(0.05, 0.4) / 100.0, 2)
            vol = random.randint(100000, 5000000) if not is_idx else random.randint(15000000, 50000000)

            data.update({
                "basePrice": base,
                "price": ltp,
                "ltp": ltp,
                "change": round(ltp - base, 2),
                "changePct": pcn,
                "pcn": pcn,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "prevClose": base,
                "volume": vol,
                "tickDir": 1 if pcn >= 0 else -1,
                "lastUpdate": datetime.now().strftime("%H:%M:%S"),
                "listed_at": datetime.now().strftime("%I:%M:%S %p IST")
            })

        # If a live broker token (e.g. Upstox) is configured, immediately sync real market quotes
        if self.gateway.has_live_upstox_token() or self.gateway.fyers_client:
            self.sync_all_live_quotes()

    def sync_all_live_quotes(self) -> int:
        """Synchronizes real-time quotes from active broker across all 224 instruments + SENSEX."""
        all_syms = list(self.stocks.keys()) + ["SENSEX"]
        quotes = self.gateway.fetch_live_quotes(all_syms)
        if not quotes:
            return 0

        now_str = datetime.now().strftime("%H:%M:%S")
        listed_ist = datetime.now().strftime("%I:%M:%S %p IST")
        updated_cnt = 0
        for sym, bq in quotes.items():
            if sym in self.stocks:
                stock = self.stocks[sym]
                bq_copy = dict(bq)
                bq_copy["tickDir"] = 1 if bq_copy.get("change", 0) >= 0 else -1
                bq_copy["lastUpdate"] = now_str
                bq_copy["listed_at"] = listed_ist
                if bq_copy.get("prevClose", 0) > 0:
                    bq_copy["basePrice"] = bq_copy["prevClose"]
                stock.update(bq_copy)
                updated_cnt += 1
            else:
                bq_copy = dict(bq)
                bq_copy["symbol"] = sym
                bq_copy["tickDir"] = 1 if bq_copy.get("change", 0) >= 0 else -1
                bq_copy["lastUpdate"] = now_str
                bq_copy["listed_at"] = listed_ist
                self.extra_indices[sym] = bq_copy
                updated_cnt += 1

        self.last_live_sync_count = updated_cnt
        self.last_live_sync_time = now_str
        return updated_cnt

    def get_live_snapshot(self, filter_type: str = "ALL") -> List[Dict[str, Any]]:
        """Returns the complete market watch array for all 224 instruments or filtered by sector."""
        all_items = list(self.stocks.values())
        if filter_type == "INDICES":
            return [s for s in all_items if s.get("is_index")]
        elif filter_type == "STOCKS":
            return [s for s in all_items if not s.get("is_index")]
        elif filter_type != "ALL":
            return [s for s in all_items if s.get("sector", "").upper() == filter_type.upper()]
        return all_items

    def update_ticks(self) -> List[Dict[str, Any]]:
        """
        Updates live prices:
        1. Polls active broker API (Upstox v2 / Fyers v3) across priority indices + rotating slices of all 224 stocks.
        2. Only falls back to micro-tick streamer simulation when no live broker feed is active.
        """
        updated = []
        priority_syms = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYNXT50", "SENSEX", "RELIANCE", "HDFCBANK", "ICICIBANK", "TCS"]
        pool = [s for s in self.stocks.keys() if s not in priority_syms]
        batch_size = 30
        if pool:
            end_idx = self._tick_cursor + batch_size
            slice_syms = pool[self._tick_cursor:end_idx]
            if len(slice_syms) < batch_size and len(pool) > batch_size:
                slice_syms += pool[:batch_size - len(slice_syms)]
            self._tick_cursor = end_idx % len(pool)
        else:
            slice_syms = []

        chosen = priority_syms + slice_syms

        # Try broker live quotes first
        broker_quotes = self.gateway.fetch_live_quotes(chosen)
        broker_live = self.gateway.has_live_upstox_token() or bool(self.gateway.fyers_client)
        now_str = datetime.now().strftime("%H:%M:%S")
        listed_ist = datetime.now().strftime("%I:%M:%S %p IST")

        if "SENSEX" in broker_quotes:
            sq = dict(broker_quotes["SENSEX"])
            sq["symbol"] = "SENSEX"
            sq["lastUpdate"] = now_str
            sq["listed_at"] = listed_ist
            self.extra_indices["SENSEX"] = sq

        for sym in chosen:
            if sym not in self.stocks:
                continue
            stock = self.stocks[sym]
            if sym in broker_quotes:
                bq = dict(broker_quotes[sym])
                new_price = bq["price"]
                pcn = bq["changePct"]
                tick_dir = 1 if bq["change"] >= 0 else -1
                stock.update(bq)
                stock["tickDir"] = tick_dir
                stock["lastUpdate"] = now_str
                stock["listed_at"] = listed_ist
            elif broker_live:
                # Preserve existing real broker quote without injecting simulated noise
                new_price = stock["price"]
                pcn = stock["pcn"]
                tick_dir = 0
                if "listed_at" not in stock:
                    stock["listed_at"] = listed_ist
            else:
                # Live micro tick oscillation fallback when broker token isn't configured
                volatility = 0.0006 if stock.get("is_index") else 0.0016
                delta = round(stock["price"] * random.uniform(-volatility, volatility), 2)
                new_price = max(1.0, round(stock["price"] + delta, 2))
                tick_dir = 1 if delta > 0 else (-1 if delta < 0 else 0)
                pcn = round((new_price - stock["prevClose"]) / stock["prevClose"] * 100.0, 2)
                
                stock["price"] = new_price
                stock["ltp"] = new_price
                stock["change"] = round(new_price - stock["prevClose"], 2)
                stock["changePct"] = pcn
                stock["pcn"] = pcn
                stock["high"] = max(stock["high"], new_price)
                stock["low"] = min(stock["low"], new_price)
                stock["volume"] += random.randint(15, 600)
                stock["tickDir"] = tick_dir
                stock["lastUpdate"] = now_str
                stock["listed_at"] = listed_ist

            updated.append({
                "symbol": sym,
                "price": new_price,
                "pcn": pcn,
                "tickDir": tick_dir,
                "volume": stock["volume"],
                "high": stock["high"],
                "low": stock["low"],
                "isIndex": stock.get("is_index", False),
                "sector": stock.get("sector", "F&O"),
                "time": stock["lastUpdate"],
                "listed_at": stock.get("listed_at", listed_ist)
            })

        return updated

    def get_historical_bars(self, symbol: str, timeframe: str = "5m", count: int = 120) -> pd.DataFrame:
        """Retrieves or generates historical OHLCV candles for any of the 224 instruments (Upstox API v2 / Vectorized NumPy)."""
        cache_key = f"{symbol}_{timeframe}_{count}"
        if cache_key in self.historical_cache:
            return self.historical_cache[cache_key].copy()

        # 1. Try real historical candles from Upstox API v2
        try:
            up_candles = self.gateway.fetch_upstox_historical_candles(symbol, timeframe, count)
            if up_candles and len(up_candles) >= 10:
                rows = []
                for c in reversed(up_candles):  # Upstox returns latest first
                    try:
                        ts = pd.to_datetime(c[0]).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    rows.append({
                        "timestamp": ts,
                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),
                        "volume": int(c[5] or 0)
                    })
                df = pd.DataFrame(rows)
                self.historical_cache[cache_key] = df
                return df.copy()
        except Exception:
            pass

        stock = self.stocks.get(symbol, {"basePrice": 1250.0})
        base = stock.get("basePrice", 1250.0)

        now = datetime.now()
        step_minutes = {
            "1m": 1, "5m": 5, "15m": 15, "30m": 30, "1H": 60, "Daily": 1440
        }.get(timeframe, 5)

        start_time = now - timedelta(minutes=step_minutes * count)
        times = [start_time + timedelta(minutes=step_minutes * i) for i in range(count)]

        # Ultra-fast vectorized NumPy series
        t = np.linspace(0, 4 * np.pi, count)
        trend = np.linspace(-0.015, 0.035, count)
        cycle = 0.012 * np.sin(t) + 0.006 * np.sin(2.2 * t)
        noise = np.random.normal(0, 0.003, count)
        returns = trend + cycle + noise
        prices = base * np.cumprod(1 + returns)

        bar_rng = prices * np.random.uniform(0.004, 0.012, count)
        opens = np.round(prices + np.random.uniform(-bar_rng * 0.3, bar_rng * 0.3), 2)
        closes = np.round(prices + np.random.uniform(-bar_rng * 0.3, bar_rng * 0.3), 2)
        highs = np.round(np.maximum(opens, closes) + np.random.uniform(0, bar_rng * 0.4), 2)
        lows = np.round(np.minimum(opens, closes) - np.random.uniform(0, bar_rng * 0.4), 2)
        volumes = np.random.randint(15000, 250000, count)

        df = pd.DataFrame({
            "timestamp": [t.strftime("%Y-%m-%d %H:%M") for t in times],
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes
        })

        self.historical_cache[cache_key] = df
        return df.copy()
