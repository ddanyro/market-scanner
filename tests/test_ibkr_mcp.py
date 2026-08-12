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

    def test_contract_selection_requires_exact_symbol_and_expected_country(self):
        selected = ibkr_mcp._select_contract("LQQ.PA", {
            "results": [
                {
                    "symbol": "LQQ", "country_code": "US",
                    "exchange": "SMART", "underlying_contract_id": 1,
                    "sections": [{"security_type": "STK"}],
                },
                {
                    "symbol": "LQQ", "country_code": "FR",
                    "exchange": "SBF", "underlying_contract_id": 2,
                    "sections": [{"security_type": "STK"}],
                },
                {
                    "symbol": "LQQU", "country_code": "FR",
                    "exchange": "SBF", "underlying_contract_id": 3,
                    "sections": [{"security_type": "STK"}],
                },
            ]
        })
        self.assertEqual(selected["underlying_contract_id"], 2)

    def test_price_history_normalises_epoch_and_missing_volume(self):
        bars = ibkr_mcp._normalise_price_history({
            "time": [1785801600000, 1785888000000],
            "open": [10, 11], "high": [11, 12], "low": [9, 10],
            "close": [10.5, 11.5], "volume": [100],
        })
        self.assertEqual(len(bars), 2)
        self.assertTrue(bars[0]["date"].startswith("2026-"))
        self.assertEqual(bars[1]["volume"], 0)


class TestIBKRMCPMarketData(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_market_instrument_combines_history_and_snapshot(self):
        class FakeSession:
            async def call(self, name, arguments=None):
                if name == "search_contracts":
                    return {"results": [{
                        "symbol": "AAPL", "country_code": "US",
                        "exchange": "NASDAQ", "description": "Apple Inc.",
                        "underlying_contract_id": 265598,
                        "sections": [{"security_type": "STK"}],
                    }]}
                if name == "get_price_history":
                    return {
                        "time": ["2026-08-07T00:00:00Z"],
                        "open": [220], "high": [225], "low": [219],
                        "close": [224], "volume": [1_000_000],
                        "delayed": 0,
                    }
                if name == "get_price_snapshot":
                    return {"last": {"price": 224.5}, "volume": 1_100_000}
                raise AssertionError(name)

        cache = {"contracts": {}, "instruments": {}}
        symbol, instrument, status = await ibkr_mcp._fetch_market_instrument(
            FakeSession(), "AAPL", cache
        )
        self.assertEqual(symbol, "AAPL")
        self.assertEqual(status, "updated")
        self.assertEqual(instrument["market_data"]["market_price"], 224.5)
        self.assertEqual(instrument["bars"][0]["close"], 224)
        self.assertEqual(instrument["data_provider"], "IBKR MCP")

    async def test_fresh_instrument_uses_cache_without_network(self):
        now = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()
        instrument = {"fetched_at": now, "bars": [{"close": 10}]}
        cache = {
            "contracts": {},
            "instruments": {"AAPL": instrument},
        }
        session = mock.AsyncMock()
        _symbol, result, status = await ibkr_mcp._fetch_market_instrument(
            session, "AAPL", cache
        )
        self.assertIs(result, instrument)
        self.assertEqual(status, "cached")
        session.call.assert_not_awaited()

    async def test_prefetch_limits_large_universe_to_rotating_batch(self):
        cache = {
            "contracts": {}, "instruments": {}, "failures": {},
            "rotation_cursor": 0,
        }

        class FakeSession:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

        async def fake_fetch(_session, symbol, target_cache):
            instrument = {"fetched_at": "2026-08-10T10:00:00+00:00"}
            target_cache["instruments"][symbol] = instrument
            return symbol, instrument, "updated"

        with (
            mock.patch.object(ibkr_mcp, "_read_market_cache", return_value=cache),
            mock.patch.object(ibkr_mcp, "_write_market_cache"),
            mock.patch.object(ibkr_mcp, "ReadOnlyMCPSession", FakeSession),
            mock.patch.object(
                ibkr_mcp, "_fetch_market_instrument", side_effect=fake_fetch
            ),
        ):
            stats = await ibkr_mcp._prefetch_market_data_async(
                ["C", "A", "B"], concurrency=2, batch_size=2
            )

        self.assertEqual(stats["requested"], 3)
        self.assertEqual(stats["scheduled"], 2)
        self.assertEqual(stats["deferred"], 1)
        self.assertEqual(stats["updated"], 2)
        self.assertEqual(set(cache["instruments"]), {"A", "B"})
        self.assertEqual(cache["rotation_cursor"], 2)


class TestIBKRMCPBuildSnapshot(unittest.IsolatedAsyncioTestCase):
    async def test_authorisation_required_is_not_hidden_by_retry(self):
        error = ibkr_mcp.IBKRMCPAuthorizationRequired("login required")
        with mock.patch.object(
            ibkr_mcp,
            "call_tool",
            new=mock.AsyncMock(side_effect=error),
        ) as call_tool:
            with self.assertRaises(ibkr_mcp.IBKRMCPAuthorizationRequired):
                await ibkr_mcp._call_with_retry(
                    "get_account_summary", attempts=2
                )

        call_tool.assert_awaited_once_with(
            "get_account_summary", interactive=False
        )

    async def test_retry_forwards_interactive_reauthorisation(self):
        with mock.patch.object(
            ibkr_mcp,
            "call_tool",
            new=mock.AsyncMock(return_value={"ok": True}),
        ) as call_tool:
            result = await ibkr_mcp._call_with_retry(
                "get_account_summary", interactive=True
            )

        self.assertEqual(result, {"ok": True})
        call_tool.assert_awaited_once_with(
            "get_account_summary", interactive=True
        )

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
