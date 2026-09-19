import json
import os
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import market_security
import tradeville_bridge


def sample_snapshot():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema": tradeville_bridge.SCHEMA,
        "bridge_version": 2,
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
                "portfolio_graph": [],
                "portfolio_graph_request": {"starts_at": "2025-09-16"},
            },
            {
                "person": {"name": "ZENSHOP COM SRL", "id": "Z/1"},
                "portfolio": [
                    {"simbol": "RON", "tsim": "bani", "sold": 71539.17, "evaleuro": 13591.04}
                ],
                "orders": [],
                "account_info": [],
                "settlement": [],
                "portfolio_graph": [],
                "portfolio_graph_request": {"starts_at": "2025-09-16"},
            },
        ],
    }


class TestTradevilleBridge(unittest.TestCase):
    def test_content_bridge_can_be_reinjected_without_global_const_collision(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "tradeville_bridge" / "content_bridge.js").read_text(
            encoding="utf-8"
        )
        manifest = json.loads(
            (root / "tradeville_bridge" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertTrue(content.startswith('"use strict";\n\n(() => {'))
        self.assertTrue(content.rstrip().endswith("})();"))
        self.assertIn(
            "if (window.__marketScannerTradevilleContentBridgeVersion === CONTENT_BRIDGE_VERSION)",
            content,
        )
        self.assertIn("return;", content)
        self.assertEqual(manifest["version"], "1.3.2")

    def test_reconstructs_nav_cash_and_transfer_adjusted_profit(self):
        epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
        minute = lambda value: int(
            (datetime.fromisoformat(value).replace(tzinfo=timezone.utc) - epoch)
            .total_seconds() / 60
        )
        snapshot = sample_snapshot()
        snapshot["exchange_rates"] = [{"valuta": "EUR", "curs": 5.0}]
        account = snapshot["accounts"][0]
        account["portfolio_graph"] = [
            [],
            [{
                "mnt": minute("2025-09-17"), "cont": "RON",
                "suma": 500, "aport": 500,
            }],
            [{
                "mnt": minute("2025-09-16"), "cont": "RON",
                "curs": 1, "valuta": "RON",
            }],
            [{"cont": "RON", "sold": 1000}],
        ]

        history = tradeville_bridge._account_history(
            account, snapshot, start=date(2025, 9, 16)
        )

        self.assertEqual(
            [point["nav"] for point in history["nav_history"]],
            [200.0, 300.0],
        )
        self.assertEqual(
            [point["cash"] for point in history["cash_history"]],
            [200.0, 300.0],
        )
        self.assertEqual(
            [point["nav"] for point in history["adjusted_nav_history"]],
            [300.0, 300.0],
        )
        self.assertEqual(
            [point["profit"] for point in history["profit_history"]],
            [0.0, 0.0],
        )
        self.assertTrue(history["history_metadata"]["raw_reconstructed"])

    def test_history_start_uses_first_ibkr_nav_date(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tws_account.json"
            path.write_text(json.dumps({
                "nav_history": [
                    {"date": "20250918", "nav": 2},
                    {"date": "20250916", "nav": 1},
                ]
            }), encoding="utf-8")
            self.assertEqual(
                tradeville_bridge._history_start(path), date(2025, 9, 16)
            )

    def test_requires_two_distinct_contemporary_accounts(self):
        snapshot = sample_snapshot()
        self.assertIs(tradeville_bridge.validate_snapshot(snapshot), snapshot)
        snapshot["accounts"] = snapshot["accounts"][:1]
        with self.assertRaises(tradeville_bridge.SnapshotError):
            tradeville_bridge.validate_snapshot(snapshot)

    def test_rejects_old_extension_without_history_protocol(self):
        snapshot = sample_snapshot()
        snapshot["schema"] = "market-scanner.tradeville.websocket.v1"
        snapshot.pop("bridge_version")
        with self.assertRaisesRegex(
            tradeville_bridge.SnapshotError, "chrome://extensions"
        ):
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

    def test_account_summary_uses_latest_graph_when_portfolio_is_empty(self):
        epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
        minute = lambda value: int(
            (datetime.fromisoformat(value).replace(tzinfo=timezone.utc) - epoch)
            .total_seconds() / 60
        )
        snapshot = sample_snapshot()
        snapshot["exchange_rates"] = [{"valuta": "EUR", "curs": 5.0}]
        account = snapshot["accounts"][0]
        account["portfolio"] = []
        account["portfolio_graph"] = [
            [], [],
            [{"mnt": minute("2026-09-16"), "cont": "RON",
              "curs": 1, "valuta": "RON"}],
            [{"cont": "RON", "sold": 1000}],
        ]

        result = tradeville_bridge._account_snapshot(snapshot)

        summary = result["accounts"][0]["summary"]
        self.assertEqual(summary["NetLiquidation"], 200)
        self.assertEqual(summary["TotalCashValue"], 200)

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

    def test_missing_graph_reuses_only_last_encrypted_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "PORTFOLIO_PATH": root / "tradeville_portfolio.csv",
                "ORDERS_PATH": root / "tradeville_orders.csv",
                "ACCOUNT_ENCRYPTED_PATH": root / "tradeville_account.enc.json",
                "RAW_ENCRYPTED_PATH": root / "tradeville_ws_snapshot.enc.json",
                "STATUS_PATH": root / "tradeville_sync_status.json",
            }
            previous = sample_snapshot()
            previous["accounts"][0]["portfolio_graph"] = [
                {"data": "2026-09-18", "eval": 1000}
            ]
            paths["RAW_ENCRYPTED_PATH"].write_text(json.dumps(
                json.loads(market_security.encrypt_for_js(
                    json.dumps(previous), "secret"
                ))
            ), encoding="utf-8")
            current = sample_snapshot()
            current["accounts"][0]["portfolio_graph"] = []
            current["accounts"][0]["portfolio_graph_request"]["error"] = (
                "graf_pers_brut_timeout"
            )

            with patch.multiple(tradeville_bridge, **paths):
                status = tradeville_bridge.persist_snapshot(
                    current, password="secret"
                )
                encrypted = json.loads(paths["RAW_ENCRYPTED_PATH"].read_text())
                decoded = json.loads(
                    market_security.decrypt_from_js(encrypted, "secret")
                )

            account = decoded["accounts"][0]
            self.assertEqual(account["portfolio_graph"], previous["accounts"][0]["portfolio_graph"])
            self.assertTrue(
                account["portfolio_graph_request"]["fallback_last_good"]
            )
            self.assertEqual(status["stale_history_account_count"], 1)

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
