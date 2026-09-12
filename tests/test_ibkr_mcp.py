import unittest
import os
from unittest import mock

import ibkr_mcp


class TestIBKRMCPNormalisation(unittest.TestCase):
    def test_github_actions_requires_explicit_opt_in_and_credentials(self):
        with mock.patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true",
            "IBKR_MCP_RESEARCH_ENABLED": "1",
            "IBKR_MCP_GITHUB_ACTIONS_ENABLED": "0",
            "IBKR_MCP_CREDENTIALS_JSON": "",
        }, clear=False):
            self.assertFalse(ibkr_mcp.runtime_enabled())
        with mock.patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true",
            "IBKR_MCP_RESEARCH_ENABLED": "1",
            "IBKR_MCP_GITHUB_ACTIONS_ENABLED": "1",
            "IBKR_MCP_CREDENTIALS_JSON": '{"access_token":"x","scope":"mcp.read"}',
        }, clear=False):
            self.assertTrue(ibkr_mcp.runtime_enabled())

    def test_contract_cache_map_preserves_requested_alias(self):
        with mock.patch.object(ibkr_mcp, "_read_market_cache", return_value={
            "contracts": {"LQQ.PA": {"contract_id": 42}}
        }):
            result = ibkr_mcp.get_cached_contract_metadata_map(["LQQ.FR"])
        self.assertEqual(result["LQQ.FR"]["contract_id"], 42)
        self.assertEqual(result["LQQ.PA"]["contract_id"], 42)

    def test_snapshot_scalar_understands_ibkr_named_metrics(self):
        self.assertEqual(ibkr_mcp._snapshot_scalar({"volume": 123}), 123)
        self.assertEqual(ibkr_mcp._snapshot_scalar({"annual_pct": 0.31}), 0.31)
        self.assertEqual(ibkr_mcp._snapshot_scalar({"yield_pct": 2.4}), 2.4)

    def test_quote_only_options_are_not_classified_as_full_analytics(self):
        context = ibkr_mcp._annotate_options_quality({
            "contracts": [{
                "bid": 1, "ask": 1.2, "volume": None,
                "open_interest": None, "iv": None,
            }]
        })
        self.assertEqual(context["data_quality"], "quote_only")
        self.assertFalse(context["analytics_available"])

    def test_chain_without_snapshots_is_partial_contract_evidence(self):
        context = ibkr_mcp._annotate_options_quality({
            "contracts": [], "chain_contracts_count": 5,
            "snapshot_error_count": 10,
        })
        self.assertEqual(context["data_quality"], "contracts_only")
        self.assertFalse(context["analytics_available"])

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

    def test_bvb_listing_accepts_ibkr_eu_country_classification(self):
        selected = ibkr_mcp._select_contract("TVBETETF.RO", {
            "results": [{
                "symbol": "TVBETETF", "country_code": "EU",
                "exchange": "BVB", "underlying_contract_id": 813325574,
                "sections": [{"security_type": "STK"}],
            }]
        })
        self.assertEqual(selected["underlying_contract_id"], 813325574)

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
    async def test_completed_session_history_is_not_requested_again(self):
        dt = __import__("datetime")
        now = dt.datetime.now(dt.timezone.utc)
        session_key = ibkr_mcp._latest_completed_session_date("HCA", now)
        calls = []

        class FakeSession:
            async def call(self, name, arguments=None):
                calls.append((name, arguments))
                if name == "get_price_snapshot":
                    return {"last": 400, "volume": 12345}
                raise AssertionError(f"unexpected history request: {name}")

        cache = {
            "contracts": {"HCA": {
                "status": "ok", "resolved_at": now.isoformat(),
                "contract_id": 123, "symbol": "HCA", "exchange": "NYSE",
                "country_code": "US", "security_type": "STK",
            }},
            "instruments": {"HCA": {
                "symbol": "HCA",
                "fetched_at": (now - dt.timedelta(hours=2)).isoformat(),
                "history_fetched_at": (now - dt.timedelta(hours=6)).isoformat(),
                "full_history_fetched_at": (now - dt.timedelta(days=2)).isoformat(),
                "history_checked_session": session_key,
                "market_data": {"market_price": 399, "quote": {}},
                "bars": [{
                    "date": session_key, "open": 395, "high": 401,
                    "low": 394, "close": 399, "volume": 10000,
                }],
            }},
            "failures": {},
        }

        _symbol, instrument, status = await ibkr_mcp._fetch_market_instrument(
            FakeSession(), "HCA", cache
        )

        self.assertEqual(status, "updated")
        self.assertEqual([name for name, _args in calls], ["get_price_snapshot"])
        self.assertEqual(instrument["history_refresh_mode"], "cache")
        self.assertEqual(instrument["bars"][0]["date"], session_key)

    async def test_missing_session_uses_incremental_history_and_merges_cache(self):
        dt = __import__("datetime")
        now = dt.datetime.now(dt.timezone.utc)
        expected = ibkr_mcp._latest_completed_session_date("HCA", now)
        old_date = (dt.date.fromisoformat(expected) - dt.timedelta(days=4)).isoformat()
        history_arguments = []

        class FakeSession:
            async def call(self, name, arguments=None):
                if name == "get_price_history":
                    history_arguments.append(arguments)
                    return {
                        "time": [expected], "open": [400], "high": [405],
                        "low": [399], "close": [404], "volume": [20000],
                    }
                if name == "get_price_snapshot":
                    return {"last": 404}
                raise AssertionError(name)

        cache = {
            "contracts": {"HCA": {
                "status": "ok", "resolved_at": now.isoformat(),
                "contract_id": 123, "symbol": "HCA", "exchange": "NYSE",
                "country_code": "US", "security_type": "STK",
            }},
            "instruments": {"HCA": {
                "fetched_at": (now - dt.timedelta(hours=2)).isoformat(),
                "full_history_fetched_at": (now - dt.timedelta(days=2)).isoformat(),
                "history_checked_session": old_date,
                "market_data": {},
                "bars": [{
                    "date": old_date, "open": 390, "high": 395,
                    "low": 389, "close": 394, "volume": 10000,
                }],
            }},
            "failures": {},
        }

        _symbol, instrument, status = await ibkr_mcp._fetch_market_instrument(
            FakeSession(), "HCA", cache
        )

        self.assertEqual(status, "updated")
        self.assertEqual(history_arguments[0]["period"], "ONE_MONTH")
        self.assertEqual([bar["date"] for bar in instrument["bars"]], [
            old_date, expected,
        ])
        self.assertEqual(instrument["history_refresh_mode"], "incremental")
        self.assertEqual(instrument["history_checked_session"], expected)

    async def test_old_bvb_negative_cache_is_re_resolved_with_canonical_country(self):
        class FakeSession:
            async def call(self, name, arguments=None):
                self.name = name
                self.arguments = arguments
                return {"results": [{
                    "symbol": "TVBETETF", "country_code": "EU",
                    "exchange": "BVB", "underlying_contract_id": 813325574,
                    "sections": [{"security_type": "STK"}],
                }]}

        cache = {"contracts": {"TVBETETF.RO": {
            "status": "not_found",
            "resolved_at": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        }}}
        session = FakeSession()
        contract = await ibkr_mcp._resolve_market_contract(
            session, "TVBETETF.RO", cache
        )
        self.assertEqual(session.arguments, {"query": "TVBETETF"})
        self.assertEqual(contract["contract_id"], 813325574)
        self.assertEqual(contract["country_code"], "RO")

    async def test_non_us_history_and_snapshot_use_contract_id_without_exchange(self):
        requested = []

        class FakeSession:
            async def call(self, name, arguments=None):
                requested.append((name, dict(arguments or {})))
                if name == "get_price_history":
                    return {
                        "time": ["2026-09-11T00:00:00Z"],
                        "open": [100], "high": [102], "low": [99],
                        "close": [101], "volume": [1000],
                    }
                if name == "get_price_snapshot":
                    return {"last": 101}
                raise AssertionError(name)

        cache = {
            "contracts": {"LQQ.PA": {
                "status": "ok", "resolved_at": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat(),
                "contract_id": 41975920, "symbol": "LQQ",
                "exchange": "SBF", "country_code": "FR",
                "security_type": "STK",
            }},
            "instruments": {}, "failures": {},
        }
        _symbol, instrument, status = await ibkr_mcp._fetch_market_instrument(
            FakeSession(), "LQQ.PA", cache
        )
        self.assertEqual(status, "updated")
        self.assertIsNotNone(instrument)
        market_calls = [args for name, args in requested if name.startswith("get_price_")]
        self.assertEqual(len(market_calls), 2)
        self.assertTrue(all(args["contract_id"] == 41975920 for args in market_calls))
        self.assertTrue(all("exchange" not in args for args in market_calls))

    async def test_fetch_market_instrument_combines_history_and_snapshot(self):
        requested_snapshot_fields = []

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
                    requested_snapshot_fields.extend(arguments["market_data_names"])
                    return {
                        "last": {"price": 224.5},
                        "volume": 1_100_000,
                        "bid-ask": {"bid": 224.4, "ask": 224.6},
                        "top-status": "REALTIME",
                        "historical-vol": 0.24,
                        "implied-vol-underlying": {"annual_iv": 0.31},
                        "implied-volatility-percentile": {"52-week": 0.82},
                        "avg-90d-usd-volume": 2_000_000_000,
                    }
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
        self.assertIn("bid_ask", requested_snapshot_fields)
        self.assertIn("implied_volatility_percentile", requested_snapshot_fields)
        quote = instrument["market_data"]["quote"]
        self.assertEqual(quote["top_status"], "REALTIME")
        self.assertAlmostEqual(quote["spread_pct"], 0.08908686, places=5)
        metrics = instrument["market_data"]["snapshot_metrics"]
        self.assertEqual(metrics["derived"]["iv_percentile_52w"], 0.82)
        self.assertEqual(metrics["derived"]["historical_vol"], 0.24)

    async def test_nested_volume_and_historical_vol_are_propagated(self):
        metrics = ibkr_mcp._normalise_snapshot_metrics({
            "avg-90d-usd-volume": {"volume": 329_000_000},
            "historical-vol": {"annual_pct": 0.312},
        })
        self.assertEqual(metrics["scalars"]["avg_90d_usd_volume"], 329_000_000)
        self.assertEqual(metrics["derived"]["historical_vol"], 0.312)

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
    async def test_persistent_session_retries_only_transient_tool_errors(self):
        successful = __import__("types").SimpleNamespace(
            isError=False, structuredContent={"ok": True}, content=[]
        )
        inner = mock.AsyncMock()
        inner.call_tool.side_effect = [
            ibkr_mcp.IBKRMCPError(
                "code -32400: An error occurred. Please try again later."
            ),
            successful,
        ]
        session = ibkr_mcp.ReadOnlyMCPSession()
        session.session = inner
        with mock.patch.object(ibkr_mcp.asyncio, "sleep", mock.AsyncMock()):
            result = await session.call("get_account_summary")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(inner.call_tool.await_count, 2)

    def test_transient_market_failure_has_short_cache_ttl(self):
        transient = {
            "error": "code -32400: Please try again later",
            "transient": True,
        }
        permanent = {
            "error": "No market data permissions",
            "transient": False,
        }
        self.assertEqual(
            ibkr_mcp._failure_ttl_seconds(transient),
            ibkr_mcp.TRANSIENT_FAILURE_TTL_SECONDS,
        )
        self.assertEqual(
            ibkr_mcp._failure_ttl_seconds(permanent),
            ibkr_mcp.MARKET_DATA_TTL_HOURS * 3600,
        )

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
            "get_account_summary", arguments=None, interactive=False
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
            "get_account_summary", arguments=None, interactive=True
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
            "get_pa_allocation": {
                "realtime": True,
                "allocations": {"SECTOR": {"long_positions": {"items": []}}},
            },
            "get_account_trades": {
                "trades": [{
                    "trade_id": "T1", "symbol": "AAPL", "side": "BUY",
                    "size": 2, "price": 200, "commission": 1,
                    "realized_pnl": 0, "trade_time": "2026-08-01T10:00:00Z",
                }]
            },
        }

        class FakeSession:
            def __init__(self, *, interactive=False):
                self.interactive = interactive

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def call(self, name, _arguments=None):
                return responses[name]

        with mock.patch.object(ibkr_mcp, "ReadOnlyMCPSession", FakeSession):
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
        self.assertTrue(payload["portfolio_allocation"]["realtime"])
        self.assertEqual(payload["trade_journal"][0]["symbol"], "AAPL")
        self.assertIsNone(payload["trade_journal"][0]["initial_score"])


if __name__ == "__main__":
    unittest.main()
