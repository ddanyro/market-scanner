import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import market_security
import tradeville_bridge


def sample_snapshot():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema": tradeville_bridge.SCHEMA,
        "fetched_at": now,
        "source": "Tradeville WebSocket pf4",
        "exchange_rates": [],
        "accounts": [
            {
                "person": {"name": "Personal", "id": "P/1"},
                "portfolio": [
                    {"simbol": "EUR", "tsim": "bani", "sold": 1000, "evaleuro": 1000},
                    {
                        "simbol": "SNP", "market": "BVB", "sold": 100,
                        "costm": 0.7, "ppiata": 0.8, "valuta": "RON",
                        "eval": 80, "evaleuro": 16,
                    },
                ],
                "orders": [
                    {
                        "idord": "10", "simbol": "SNP", "market": "BVB",
                        "csauv": "C", "tipord": "LMT", "cant": 50,
                        "pret": 0.75, "valuta": "RON", "stare": "A",
                    }
                ],
                "account_info": [],
                "settlement": [],
            },
            {
                "person": {"name": "ZENSHOP COM SRL", "id": "Z/1"},
                "portfolio": [
                    {"simbol": "RON", "tsim": "bani", "sold": 71539.17, "evaleuro": 13591.04}
                ],
                "orders": [],
                "account_info": [],
                "settlement": [],
            },
        ],
    }


class TestTradevilleBridge(unittest.TestCase):
    def test_requires_two_distinct_contemporary_accounts(self):
        snapshot = sample_snapshot()
        self.assertIs(tradeville_bridge.validate_snapshot(snapshot), snapshot)
        snapshot["accounts"] = snapshot["accounts"][:1]
        with self.assertRaises(tradeville_bridge.SnapshotError):
            tradeville_bridge.validate_snapshot(snapshot)

    def test_normalises_positions_orders_and_cash_without_mixing_accounts(self):
        snapshot = sample_snapshot()
        positions = tradeville_bridge._position_records(snapshot)
        orders = tradeville_bridge._order_records(snapshot)
        account = tradeville_bridge._account_snapshot(snapshot)

        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["Symbol"], "SNP.RO")
        self.assertEqual(positions[0]["Account"], "Personal")
        self.assertEqual(orders[0]["Action"], "BUY")
        self.assertEqual(orders[0]["Order_ID"], "10")
        self.assertEqual(len(account["accounts"]), 2)
        self.assertEqual(
            account["accounts"][1]["cash_by_currency"]["RON"], 71539.17
        )

    def test_persist_is_atomic_and_encrypts_portable_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "PORTFOLIO_PATH": root / "tradeville_portfolio.csv",
                "ORDERS_PATH": root / "tradeville_orders.csv",
                "ACCOUNT_ENCRYPTED_PATH": root / "tradeville_account.enc.json",
                "RAW_ENCRYPTED_PATH": root / "tradeville_ws_snapshot.enc.json",
                "STATUS_PATH": root / "tradeville_sync_status.json",
            }
            with patch.multiple(tradeville_bridge, **paths):
                status = tradeville_bridge.persist_snapshot(
                    sample_snapshot(), password="secret"
                )
                portfolio = pd.read_csv(paths["PORTFOLIO_PATH"])
                orders = pd.read_csv(paths["ORDERS_PATH"])
                encrypted = json.loads(paths["RAW_ENCRYPTED_PATH"].read_text())
                decoded = json.loads(market_security.decrypt_from_js(encrypted, "secret"))

            self.assertTrue(status["ok"])
            self.assertEqual(portfolio.Symbol.tolist(), ["SNP.RO"])
            self.assertEqual(orders.Order_ID.astype(str).tolist(), ["10"])
            self.assertEqual(decoded["schema"], tradeville_bridge.SCHEMA)

    def test_failure_status_preserves_last_good_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status_path = root / "status.json"
            portfolio_path = root / "portfolio.csv"
            portfolio_path.write_text("sentinel", encoding="utf-8")
            with patch.object(tradeville_bridge, "STATUS_PATH", status_path):
                tradeville_bridge.record_failure(TimeoutError("browser missing"))
            self.assertEqual(portfolio_path.read_text(), "sentinel")
            self.assertTrue(json.loads(status_path.read_text())["stale"])

    def test_bridge_binds_only_to_loopback(self):
        with self.assertRaises(tradeville_bridge.SnapshotError):
            tradeville_bridge.run_sync(host="0.0.0.0", timeout=0.01)


if __name__ == "__main__":
    unittest.main()
