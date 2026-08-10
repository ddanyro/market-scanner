import unittest
from unittest import mock

import ibkr_mcp


class TestIBKRMCPNormalisation(unittest.TestCase):
    def test_write_scope_is_always_rejected(self):
        with self.assertRaisesRegex(ibkr_mcp.IBKRMCPError, "mcp.write"):
            ibkr_mcp._assert_read_only_token({
                "access_token": "secret",
                "scope": "mcp.read mcp.write",
            })
        ibkr_mcp._assert_read_only_token({
            "access_token": "secret",
            "scope": "mcp.read",
        })

    def test_mutating_tool_is_never_callable(self):
        with self.assertRaisesRegex(ibkr_mcp.IBKRMCPError, "read-only"):
            __import__("asyncio").run(
                ibkr_mcp.call_tool("create_order_instruction")
            )

    def test_positions_use_native_symbol_price_and_currency(self):
        rows = ibkr_mcp._normalise_positions({
            "positions": [{
                "contract_description": "BRK B",
                "position": 2,
                "average_price": 500,
                "market_price": 510,
                "currency": "USD",
            }]
        })
        self.assertEqual(rows[0]["Symbol"], "BRK.B")
        self.assertEqual(rows[0]["Shares"], 2)
        self.assertEqual(rows[0]["Buy_Price"], 500)
        self.assertEqual(rows[0]["Current_Price"], 510)
        self.assertEqual(rows[0]["Currency"], "USD")

    def test_orders_extract_limit_and_trailing_stop(self):
        rows = ibkr_mcp._normalise_orders({
            "orders": [
                {
                    "order_type": "LIMIT",
                    "side": "BUY",
                    "limit_price": "16.35",
                    "total_shares_qty": "260",
                    "primary_description": "Buy 260 SPYL",
                    "secondary_description": "Limit 16.3500, GTC",
                },
                {
                    "order_type": "TRAILING_STOP",
                    "side": "SELL",
                    "total_shares_qty": "5",
                    "primary_description": "Sell 5 RTX",
                    "secondary_description": "TRAIL 7.32 STP 209.10, GTC",
                },
            ]
        })
        self.assertEqual(rows[0]["OrderType"], "LMT")
        self.assertEqual(rows[0]["Limit_Price"], 16.35)
        self.assertEqual(rows[1]["OrderType"], "TRAIL")
        self.assertEqual(rows[1]["Trail_Pct"], 7.32)
        self.assertEqual(rows[1]["Calculated_Stop"], 209.10)

    def test_nav_history_uses_longest_available_period(self):
        account_id, points = ibkr_mcp._normalise_nav_history({
            "accounts": {
                "U123": {
                    "base_currency": "EUR",
                    "periods": {
                        "1Y": {
                            "dates": ["20260801", "20260802"],
                            "nav": [100, 102],
                        }
                    },
                }
            }
        }, "USD")
        self.assertEqual(account_id, "U123")
        self.assertEqual(len(points), 2)
        self.assertEqual(points[-1]["nav"], 102)
        self.assertEqual(points[-1]["currency"], "EUR")

    def test_nav_history_removes_quotes_from_ibkr_dates(self):
        _account_id, points = ibkr_mcp._normalise_nav_history({
            "accounts": {
                "U123": {
                    "base_currency": "EUR",
                    "periods": {
                        "1Y": {
                            "dates": ["'20250811'", '"20250812"', 20250813.0],
                            "nav": [100, 101, 102],
                        }
                    },
                }
            }
        }, "EUR")
        self.assertEqual(
            [point["date"] for point in points],
            ["20250811", "20250812", "20250813"],
        )


class TestIBKRMCPBuildSnapshot(unittest.IsolatedAsyncioTestCase):
    async def test_build_snapshot_maps_read_only_tools(self):
        responses = {
            "get_account_summary": {
                "currency": "EUR",
                "net_liquidation": 1000,
                "total_cash_value": 700,
                "available_funds": 650,
                "buying_power": 650,
                "excess_liquidity": 680,
                "gross_position_value": 300,
            },
            "get_account_positions": {"positions": []},
            "get_account_orders": {"orders": []},
            "get_account_balances": {
                "balances": [{"currency": "USD", "cash_balance": 100}]
            },
            "get_pa_performance_all_periods": {
                "accounts": {
                    "U123": {
                        "base_currency": "EUR",
                        "periods": {
                            "1Y": {"dates": ["20260801"], "nav": [1000]}
                        },
                    }
                }
            },
        }

        async def fake_call(name, **_kwargs):
            return responses[name]

        with mock.patch.object(ibkr_mcp, "call_tool", side_effect=fake_call):
            payload = await ibkr_mcp.build_account_snapshot()

        self.assertEqual(payload["source"], "IBKR MCP (read-only)")
        self.assertEqual(payload["accounts"][0]["account_id"], "U123")
        self.assertEqual(
            payload["accounts"][0]["summary"]["NetLiquidation"], 1000
        )
        self.assertEqual(
            payload["accounts"][0]["cash_by_currency"]["USD"], 100
        )
        self.assertEqual(payload["nav_history"][0]["nav"], 1000)


if __name__ == "__main__":
    unittest.main()
