"""
FoxTrader-Pro Live Price & Signal Database Manager with Automated GitHub Upload
Persists signals in SQLite and JSON, and automatically pushes updates to GitHub via REST API.
"""

import os
import json
import sqlite3
import base64
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "signals.db")
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "signals_database.json")
PRICES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "live_stock_prices.json")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "github_config.json")

class SignalDatabaseManager:
    """Manages persistent SQLite storage, JSON exports, and GitHub repository synchronization."""

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.init_db()
        self.load_config()

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                name TEXT,
                signal_type TEXT,
                bias TEXT,
                price REAL,
                change_pct REAL,
                volume INTEGER,
                stop_loss REAL,
                target1 REAL,
                target2 REAL,
                smc_details TEXT,
                source TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def load_config(self) -> Dict[str, Any]:
        default_config = {
            "github_token": os.environ.get("GITHUB_TOKEN", ""),
            "repo_owner": "Apurba-Pal",
            "repo_name": "FoxTrader-Signals",
            "branch": "main",
            "auto_upload": True,
            "upload_interval_seconds": 60
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
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

    def record_signal(self, sig: Dict[str, Any]) -> int:
        """Stores a newly triggered signal into SQLite and JSON database."""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO signals (timestamp, symbol, name, signal_type, bias, price, change_pct, volume, stop_loss, target1, target2, smc_details, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sig.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            sig.get("symbol", ""),
            sig.get("name", sig.get("symbol", "")),
            sig.get("signal_type", "Algorithmic Trigger"),
            sig.get("bias", "BUY"),
            float(sig.get("price", 0.0)),
            float(sig.get("change_pct", 0.0)),
            int(sig.get("volume", 0)),
            float(sig.get("stop_loss", 0.0)),
            float(sig.get("target1", 0.0)),
            float(sig.get("target2", 0.0)),
            json.dumps(sig.get("smc_details", {})),
            sig.get("source", "FoxTrader Core Engine")
        ))
        sig_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Update JSON exports
        self.export_to_json()
        return sig_id

    def get_recent_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM signals ORDER BY id DESC LIMIT ?', (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        for r in rows:
            try:
                r["smc_details"] = json.loads(r["smc_details"])
            except Exception:
                r["smc_details"] = {}
        return rows

    def export_to_json(self):
        signals = self.get_recent_signals(limit=200)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total_signals": len(signals),
                "signals": signals
            }, f, indent=2)

    def save_live_prices(self, price_dict: Dict[str, Any]):
        with open(PRICES_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "stocks": price_dict
            }, f, indent=2)

    def ensure_repo_exists(self) -> bool:
        """Checks if the target GitHub repo exists; if not, automatically creates it."""
        token = self.config.get("github_token", "").strip()
        owner = self.config.get("repo_owner", "").strip()
        repo = self.config.get("repo_name", "").strip()
        if not token or not repo:
            return False

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "FoxTrader-Pro",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check if repo exists
        check_url = f"https://api.github.com/repos/{owner}/{repo}"
        req = urllib.request.Request(check_url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.code == 200:
                    return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Create the repository automatically
                create_url = "https://api.github.com/user/repos"
                payload = json.dumps({
                    "name": repo,
                    "description": "FoxTrader-Pro Algorithmic Signals & Real-Time Market Intelligence Database",
                    "private": False,
                    "auto_init": True
                }).encode("utf-8")
                create_req = urllib.request.Request(create_url, data=payload, headers=headers, method="POST")
                try:
                    with urllib.request.urlopen(create_req) as c_resp:
                        return c_resp.code in [200, 201]
                except Exception:
                    return False
        except Exception:
            pass
        return False

    def upload_file_to_github(self, file_path_in_repo: str, content_str: str, commit_message: str) -> Dict[str, Any]:
        """Pushes or updates a file directly in the specified GitHub repository."""
        token = self.config.get("github_token", "").strip()
        owner = self.config.get("repo_owner", "").strip()
        repo = self.config.get("repo_name", "").strip()
        branch = self.config.get("branch", "main")

        if not token or not owner or not repo:
            return {"success": False, "error": "GitHub credentials or repo not configured"}

        self.ensure_repo_exists()

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path_in_repo}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "FoxTrader-Pro",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check existing file SHA
        sha = None
        req = urllib.request.Request(f"{url}?ref={branch}", headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                sha = data.get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                return {"success": False, "error": f"Failed checking file: {e.code} {e.reason}"}

        # Build payload
        b64_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        payload = {
            "message": commit_message,
            "content": b64_content,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        put_req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
        try:
            with urllib.request.urlopen(put_req) as resp:
                resp_data = json.loads(resp.read().decode())
                return {
                    "success": True,
                    "commit": resp_data.get("commit", {}).get("sha", "")[:7],
                    "html_url": resp_data.get("content", {}).get("html_url", ""),
                    "file": file_path_in_repo
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            return {"success": False, "error": f"HTTP {e.code}: {err_body}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sync_to_github(self) -> Dict[str, Any]:
        """Pushes signals database, live prices, and a markdown signals report to GitHub."""
        signals = self.get_recent_signals(limit=100)
        
        # 1. signals.json
        signals_json = json.dumps({
            "generated_at": datetime.now().isoformat(),
            "total_signals": len(signals),
            "signals": signals
        }, indent=2)
        res1 = self.upload_file_to_github("data/signals.json", signals_json, "FoxTrader Auto-Sync: Update signals database")

        # 2. Markdown Report
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        md_content = f"# FoxTrader-Pro Live Institutional Signals\n\n"
        md_content += f"> **Last Updated**: `{now_str}` | **Total Active Signals**: `{len(signals)}`\n\n"
        md_content += "| Symbol | Bias | Signal Type | Trigger Price | % Chg | Target 1 | Stop Loss | Timestamp |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for s in signals[:25]:
            bias_emoji = "🟢 **BUY**" if s['bias'] == 'BUY' else "🔴 **SELL**"
            md_content += f"| **{s['symbol']}** | {bias_emoji} | {s['signal_type']} | ₹{s['price']:.2f} | {s['change_pct']:+.2f}% | ₹{s['target1']:.2f} | ₹{s['stop_loss']:.2f} | {s['timestamp']} |\n"
        md_content += "\n\n*Generated automatically by FoxTrader-Pro Algorithmic Trading Platform*\n"

        res2 = self.upload_file_to_github("LATEST_SIGNALS.md", md_content, "FoxTrader Auto-Sync: Update Markdown Signal Board")

        return {
            "success": res1.get("success", False) or res2.get("success", False),
            "signals_result": res1,
            "markdown_result": res2,
            "synced_at": now_str,
            "signals_count": len(signals)
        }
