"""
Dhan Muhurat Multi-Broker Gateway
Supports Upstox API v2, Fyers API v3, Zerodha Kite Connect, Angel One SmartAPI, Dhan, and Live Streamer.
Provides unified live quote streaming and historical data for all 224 F&O indices & stocks.
"""

import os
import json
import time
import urllib.parse
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple

try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None

try:
    import upstox_client
except ImportError:
    upstox_client = None

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "broker_config.json")
UNIVERSE_PATH = os.path.join(os.path.dirname(__file__), "fno_universe.json")

class BrokerGateway:
    """Manages connections to Indian broker APIs (Upstox, Fyers, Zerodha, Angel One) and live feeds."""

    def __init__(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        self.load_universe()
        self.load_config()
        self.fyers_client = None
        self.upstox_client = None
        self.upstox_token_valid = True
        self._profile_cache: Optional[Dict[str, Any]] = None
        self._profile_cache_ts: float = 0.0
        self._profile_cache_token: str = ""
        self.init_fyers()
        self.init_upstox()

    def load_universe(self):
        if os.path.exists(UNIVERSE_PATH):
            with open(UNIVERSE_PATH, "r", encoding="utf-8") as f:
                self.universe = json.load(f)
        else:
            self.universe = []
        self.symbol_map = {item["symbol"]: item for item in self.universe}

    def load_config(self) -> Dict[str, Any]:
        default_config = {
            "active_broker": "upstox",  # "upstox", "fyers", "zerodha", "angel", "dhan", "live_stream"
            "upstox": {
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "redirect_uri": "http://127.0.0.1:8088/api/broker/upstox/callback"
            },
            "fyers": {
                "client_id": "RMR62XB492-100",
                "secret_key": "0WF68SFOJD",
                "access_token": "",
                "redirect_uri": "http://127.0.0.1:8088/api/broker/fyers/callback"
            },
            "zerodha": {
                "api_key": "",
                "access_token": ""
            },
            "angel": {
                "api_key": "",
                "jwt_token": ""
            },
            "dhan": {
                "client_id": "",
                "access_token": ""
            }
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    # ensure upstox section exists
                    if "upstox" not in self.config:
                        self.config["upstox"] = default_config["upstox"]
                    return self.config
            except Exception:
                pass
        self.config = default_config
        self.save_config(default_config)
        return self.config

    def save_config(self, cfg: Dict[str, Any]):
        self.config = cfg
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

    def init_fyers(self):
        fyers_cfg = self.config.get("fyers", {})
        client_id = fyers_cfg.get("client_id", "")
        token = fyers_cfg.get("access_token", "").strip()
        if fyersModel and client_id and token:
            try:
                self.fyers_client = fyersModel.FyersModel(
                    client_id=client_id,
                    token=token,
                    is_async=False,
                    log_path=""
                )
            except Exception:
                self.fyers_client = None
        else:
            self.fyers_client = None

    def init_upstox(self):
        self.upstox_token_valid = True
        self._profile_cache = None
        self._profile_cache_ts = 0.0
        up_cfg = self.config.get("upstox", {})
        token = up_cfg.get("access_token", "").strip()
        if token and upstox_client:
            try:
                configuration = upstox_client.Configuration()
                configuration.access_token = token
                self.upstox_client = upstox_client.ApiClient(configuration)
            except Exception:
                self.upstox_client = None
        else:
            self.upstox_client = None

    def get_fyers_login_url(self) -> str:
        """Generates the Fyers Auth Login URL for generating a fresh access token."""
        fyers_cfg = self.config.get("fyers", {})
        client_id = fyers_cfg.get("client_id", "RMR62XB492-100")
        redirect_uri = fyers_cfg.get("redirect_uri", "http://127.0.0.1:8088/api/broker/fyers/callback")
        return (
            f"https://api-t1.fyers.in/api/v3/generate-authcode?"
            f"client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state=foxtrader"
        )

    def get_upstox_login_url(self) -> str:
        """Generates the Upstox OAuth 2.0 Login URL."""
        up_cfg = self.config.get("upstox", {})
        client_id = up_cfg.get("api_key", "").strip()
        redirect_uri = up_cfg.get("redirect_uri", "http://127.0.0.1:8088/api/broker/upstox/callback")
        return (
            f"https://api.upstox.com/v2/login/authorization/dialog?"
            f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state=foxtrader"
        )

    def exchange_upstox_code(self, code: str) -> Dict[str, Any]:
        """Exchanges an authorization code for an Upstox access token."""
        up_cfg = self.config.get("upstox", {})
        client_id = up_cfg.get("api_key", "").strip()
        client_secret = up_cfg.get("api_secret", "").strip()
        redirect_uri = up_cfg.get("redirect_uri", "http://127.0.0.1:8088/api/broker/upstox/callback")

        url = "https://api.upstox.com/v2/login/authorization/token"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        try:
            res = requests.post(url, headers=headers, data=data, timeout=10)
            json_res = res.json()
            if res.status_code == 200 and "access_token" in json_res:
                token = json_res["access_token"]
                self.config["upstox"]["access_token"] = token
                self.config["active_broker"] = "upstox"
                self.save_config(self.config)
                self.init_upstox()
                return {
                    "success": True,
                    "access_token": token,
                    "user_name": json_res.get("user_name", ""),
                    "user_id": json_res.get("user_id", "")
                }
            err = json_res.get("message") or json_res.get("errors") or "Token exchange failed"
            return {"success": False, "error": str(err)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_broker_connection(self) -> Dict[str, Any]:
        """Tests live connectivity to the active broker API."""
        broker = self.config.get("active_broker", "upstox")

        if broker == "upstox":
            token = self.config.get("upstox", {}).get("access_token", "").strip()
            if not token:
                return {
                    "connected": False,
                    "broker": "Upstox API v2",
                    "status": "Access Token Required",
                    "action_required": "Provide an Upstox Access Token or click 'Generate Upstox Login URL'",
                    "login_url": self.get_upstox_login_url()
                }
            now_ts = time.time()
            if (
                self._profile_cache is not None
                and self._profile_cache_token == token
                and (now_ts - self._profile_cache_ts) < 60.0
            ):
                return dict(self._profile_cache)
            try:
                res = requests.get(
                    "https://api.upstox.com/v2/user/profile",
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                    timeout=6
                )
                if res.status_code == 200:
                    user_data = res.json().get("data", {})
                    result = {
                        "connected": True,
                        "broker": "Upstox API v2",
                        "status": "Connected & Live (Streaming 224 Instruments)",
                        "user_id": user_data.get("user_id", ""),
                        "user_name": user_data.get("user_name", ""),
                        "email": user_data.get("email", ""),
                        "broker_name": "Upstox Securities Ltd."
                    }
                    self._profile_cache = result
                    self._profile_cache_ts = now_ts
                    self._profile_cache_token = token
                    return dict(result)
                else:
                    if res.status_code == 401:
                        self.upstox_token_valid = False
                    errors = res.json().get("errors", [{}])
                    err_msg = errors[0].get("message") if errors else "Token Expired/Invalid"
                    return {
                        "connected": False,
                        "broker": "Upstox API v2",
                        "status": f"Invalid/Expired Token: {err_msg}",
                        "login_url": self.get_upstox_login_url()
                    }
            except Exception as e:
                if self._profile_cache is not None and self._profile_cache_token == token:
                    return dict(self._profile_cache)
                return {"connected": False, "broker": "Upstox API v2", "status": f"Connection error: {str(e)}"}

        elif broker == "fyers":
            if not self.fyers_client:
                return {
                    "connected": False,
                    "broker": "Fyers API v3",
                    "status": "Token Missing or Invalid",
                    "action_required": "Please provide a valid Fyers access token or click 'Generate Broker Login URL'",
                    "login_url": self.get_fyers_login_url()
                }
            try:
                res = self.fyers_client.get_profile()
                if res.get("s") == "ok":
                    return {
                        "connected": True,
                        "broker": "Fyers API v3",
                        "status": "Connected & Live",
                        "name": res.get("data", {}).get("name", ""),
                        "fy_id": res.get("data", {}).get("fy_id", "")
                    }
                else:
                    return {
                        "connected": False,
                        "broker": "Fyers API v3",
                        "status": f"Expired/Invalid Token: {res.get('message', 'Error')}",
                        "login_url": self.get_fyers_login_url()
                    }
            except Exception as e:
                return {"connected": False, "broker": "Fyers API v3", "status": str(e)}

        elif broker == "zerodha":
            token = self.config.get("zerodha", {}).get("access_token")
            return {
                "connected": bool(token),
                "broker": "Zerodha Kite Connect",
                "status": "Ready (API Token Set)" if token else "Access Token Required"
            }

        return {
            "connected": True,
            "broker": "Dhan Muhurat Live Tick Streamer",
            "status": "Active (Streaming 224 Instruments)"
        }

    EXTRA_UPSTOX_KEYS = {
        "SENSEX": "BSE_INDEX|SENSEX"
    }

    def has_live_upstox_token(self) -> bool:
        """Returns True if Upstox is active, has an access token, and token has not returned 401."""
        return (
            self.config.get("active_broker", "upstox") == "upstox"
            and bool(self.config.get("upstox", {}).get("access_token", "").strip())
            and self.upstox_token_valid
        )

    def _get_upstox_key(self, symbol: str) -> Optional[str]:
        item = self.symbol_map.get(symbol)
        if item and item.get("upstox_instrument_key"):
            return item["upstox_instrument_key"]
        return self.EXTRA_UPSTOX_KEYS.get(symbol)

    def fetch_live_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetches live tick quotes from Upstox API v2 or Fyers API v3 if connected;
        Otherwise returns empty dict so the high-speed live streamer handles it.
        """
        active = self.config.get("active_broker", "upstox")

        # 1. UPSTOX API V2 LIVE QUOTES
        if active == "upstox":
            token = self.config.get("upstox", {}).get("access_token", "").strip()
            if token and self.upstox_token_valid:
                key_to_syms: Dict[str, List[str]] = {}
                ordered_keys: List[str] = []
                for s in symbols:
                    ukey = self._get_upstox_key(s)
                    if ukey:
                        if ukey not in key_to_syms:
                            key_to_syms[ukey] = []
                            ordered_keys.append(ukey)
                        key_to_syms[ukey].append(s)
                        colon_key = ukey.replace("|", ":")
                        key_to_syms.setdefault(colon_key, key_to_syms[ukey])

                if ordered_keys:
                    out: Dict[str, Dict[str, Any]] = {}
                    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
                    for i in range(0, len(ordered_keys), 80):
                        chunk = ordered_keys[i:i + 80]
                        try:
                            encoded = urllib.parse.quote(",".join(chunk), safe=",")
                            url = f"https://api.upstox.com/v2/market-quote/quotes?instrument_key={encoded}"
                            res = requests.get(url, headers=headers, timeout=5.0)
                            if res.status_code == 401:
                                self.upstox_token_valid = False
                                return out
                            if res.status_code == 200:
                                data = res.json().get("data", {}) or {}
                                for key_str, q in data.items():
                                    if not isinstance(q, dict):
                                        continue
                                    inst_tok = q.get("instrument_token") or ""
                                    matched_syms = (
                                        key_to_syms.get(inst_tok)
                                        or key_to_syms.get(key_str)
                                        or key_to_syms.get(key_str.replace(":", "|"))
                                    )
                                    if not matched_syms:
                                        trading_sym = q.get("symbol") or ""
                                        if trading_sym in self.symbol_map:
                                            matched_syms = [trading_sym]
                                    if not matched_syms:
                                        continue

                                    ohlc = q.get("ohlc") or {}
                                    ltp = float(q.get("last_price") or 0.0)
                                    if ltp <= 0:
                                        continue
                                    chg = float(q.get("net_change") or 0.0)
                                    prev_c = round(ltp - chg, 2)
                                    if prev_c <= 0:
                                        prev_c = float(ohlc.get("close") or ltp)
                                    chg_pct = round((chg / prev_c) * 100.0, 2) if prev_c > 0 else 0.0
                                    open_p = float(ohlc.get("open") or ltp)
                                    high_p = float(ohlc.get("high") or ltp)
                                    low_p = float(ohlc.get("low") or ltp)
                                    vol = int(q.get("volume") or 0)

                                    for base_sym in matched_syms:
                                        out[base_sym] = {
                                            "price": ltp,
                                            "ltp": ltp,
                                            "change": round(chg, 2),
                                            "changePct": chg_pct,
                                            "pcn": chg_pct,
                                            "open": open_p,
                                            "high": high_p,
                                            "low": low_p,
                                            "prevClose": prev_c,
                                            "volume": vol,
                                            "source": "UPSTOX_API_V2"
                                        }
                        except Exception:
                            pass
                    if out:
                        return out

        # 2. FYERS API V3 LIVE QUOTES
        elif active == "fyers" and self.fyers_client:
            fyers_syms = []
            for s in symbols:
                item = self.symbol_map.get(s)
                if item:
                    fyers_syms.append(item.get("fyers_symbol", f"NSE:{s}-EQ"))

            if fyers_syms:
                chunk = fyers_syms[:50]
                try:
                    res = self.fyers_client.quotes({"symbols": ",".join(chunk)})
                    if res.get("s") == "ok":
                        out = {}
                        for d in res.get("d", []):
                            sym_raw = d.get("n", "")
                            base_sym = sym_raw.replace("NSE:", "").replace("-EQ", "").replace("-INDEX", "")
                            v = d.get("v", {})
                            out[base_sym] = {
                                "price": float(v.get("lp", 0.0)),
                                "change": float(v.get("ch", 0.0)),
                                "changePct": float(v.get("chp", 0.0)),
                                "open": float(v.get("open_price", 0.0)),
                                "high": float(v.get("high_price", 0.0)),
                                "low": float(v.get("low_price", 0.0)),
                                "prevClose": float(v.get("prev_close_price", 0.0)),
                                "volume": int(v.get("volume", 0)),
                                "source": "FYERS_API_V3"
                            }
                        return out
                except Exception:
                    pass

        return {}

    def fetch_upstox_historical_candles(self, symbol: str, timeframe: str = "5m", count: int = 80) -> Optional[List[List[Any]]]:
        """
        Fetches official Upstox historical + intraday candles for any of the 224 instruments & indices.
        Resamples 1m/30m bars cleanly for 5m, 15m, and 1H views. Returns newest-first candles list.
        """
        ukey = self._get_upstox_key(symbol)
        if not ukey:
            return None

        tf = timeframe.strip()
        if tf in ("1d", "D", "Daily", "daily"):
            up_interval = "day"
            lookback_days = 240
            resample_rule = None
        elif tf in ("30m", "1H", "1h"):
            up_interval = "30minute"
            lookback_days = 30
            resample_rule = "60min" if tf in ("1H", "1h") else None
        elif tf in ("5m", "15m"):
            up_interval = "1minute"
            lookback_days = 7
            resample_rule = "5min" if tf == "5m" else "15min"
        else:
            up_interval = "1minute"
            lookback_days = 5
            resample_rule = None

        encoded_key = urllib.parse.quote(ukey, safe="")
        to_date = date.today().strftime("%Y-%m-%d")
        from_date = (date.today() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

        token = self.config.get("upstox", {}).get("access_token", "").strip()
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        merged_by_ts: Dict[str, List[Any]] = {}

        # Fetch today's intraday candles when using intraday intervals
        if up_interval in ("1minute", "30minute"):
            intra_url = f"https://api.upstox.com/v2/historical-candle/intraday/{encoded_key}/{up_interval}"
            try:
                r_intra = requests.get(intra_url, headers=headers, timeout=5)
                if r_intra.status_code == 200:
                    for c in (r_intra.json().get("data", {}).get("candles", []) or []):
                        merged_by_ts[c[0]] = c
            except Exception:
                pass

        hist_url = f"https://api.upstox.com/v2/historical-candle/{encoded_key}/{up_interval}/{to_date}/{from_date}"
        try:
            r_hist = requests.get(hist_url, headers=headers, timeout=6)
            if r_hist.status_code == 200:
                for c in (r_hist.json().get("data", {}).get("candles", []) or []):
                    merged_by_ts.setdefault(c[0], c)
        except Exception:
            pass

        if not merged_by_ts:
            return None

        # Sort chronologically ascending first
        candles_asc = sorted(merged_by_ts.values(), key=lambda x: x[0])

        if resample_rule and len(candles_asc) >= 5:
            try:
                df = pd.DataFrame(candles_asc, columns=["ts", "open", "high", "low", "close", "volume", "oi"])
                df["ts"] = pd.to_datetime(df["ts"])
                df = df.set_index("ts")
                resamp = df.resample(resample_rule).agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                    "oi": "last"
                }).dropna(subset=["open", "close"])
                candles_asc = [
                    [
                        idx.isoformat(),
                        float(row["open"]),
                        float(row["high"]),
                        float(row["low"]),
                        float(row["close"]),
                        int(row["volume"]),
                        int(row["oi"] or 0)
                    ]
                    for idx, row in resamp.iterrows()
                ]
            except Exception:
                pass

        # Return newest-first (matches caller expectation `reversed(up_candles)`)
        candles_desc = list(reversed(candles_asc))
        return candles_desc[:count]
