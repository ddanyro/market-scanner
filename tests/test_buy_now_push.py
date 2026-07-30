import datetime
import unittest

import buy_now_push


class FakeResponse:
    def __init__(self, payload=None, error=None):
        self.payload = payload or {}
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


def candidate(symbol, strict=True, requires_filters=True):
    return {
        "symbol": symbol,
        "strict_eligible": strict,
        "requires_watchlist_filters": requires_filters,
    }


def recommendation(symbol, verdict):
    return {"symbol": symbol, "verdict": verdict}


class BuyNowPushTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.datetime(
            2026, 7, 29, 12, 30, tzinfo=datetime.timezone.utc
        )

    def test_only_dashboard_buy_now_orders_are_selected(self):
        result = {
            "buy_recommendations": [
                recommendation("nvda", "Candidat valid"),
                recommendation("pbr", "Candidat valid"),
                recommendation("aapl", "Pregătit la trigger"),
            ]
        }
        candidates = [
            candidate("NVDA"),
            candidate("PBR", strict=False),
            candidate("AAPL"),
        ]

        self.assertEqual(
            buy_now_push.immediate_buy_symbols(result, candidates),
            ["NVDA"],
        )

    def test_external_candidate_does_not_require_watchlist_filters(self):
        result = {
            "buy_recommendations": [
                recommendation("PBR", "Candidat valid"),
            ]
        }
        candidates = [
            candidate("PBR", strict=False, requires_filters=False),
        ]

        self.assertEqual(
            buy_now_push.immediate_buy_symbols(result, candidates),
            ["PBR"],
        )

    def test_sends_one_exact_message_per_new_symbol(self):
        calls = []

        def post(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse({"id": f"notification-{len(calls)}"})

        state, diagnostic = buy_now_push.send_new_buy_now_notifications(
            {},
            {
                "buy_recommendations": [
                    recommendation("NVDA", "Candidat valid"),
                    recommendation("PBR", "Candidat valid"),
                ]
            },
            [candidate("NVDA"), candidate("PBR")],
            event_token="2026-07-29T12:00:00",
            app_id="app-id",
            api_key="api-key",
            site_url="https://example.test/",
            post=post,
            now=self.now,
        )

        self.assertEqual(diagnostic["status"], "sent")
        self.assertEqual(diagnostic["delivered_symbols"], ["NVDA", "PBR"])
        self.assertEqual(
            state["notified_active_symbols"], ["NVDA", "PBR"]
        )
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            calls[0][1]["json"]["contents"]["ro"],
            "Ordin de cumpărare acum: NVDA.",
        )
        self.assertEqual(
            calls[1][1]["json"]["contents"]["ro"],
            "Ordin de cumpărare acum: PBR.",
        )
        self.assertEqual(
            calls[0][1]["headers"]["Authorization"],
            "Key api-key",
        )
        self.assertNotIn("api-key", str(calls[0][1]["json"]))

    def test_active_order_is_not_sent_twice(self):
        calls = []
        result = {
            "buy_recommendations": [
                recommendation("NVDA", "Candidat valid"),
            ]
        }
        candidates = [candidate("NVDA")]
        first_state, _ = buy_now_push.send_new_buy_now_notifications(
            {},
            result,
            candidates,
            event_token="event-1",
            app_id="app-id",
            api_key="api-key",
            post=lambda *args, **kwargs: (
                calls.append(kwargs) or FakeResponse({"id": "first"})
            ),
            now=self.now,
        )
        second_state, diagnostic = buy_now_push.send_new_buy_now_notifications(
            first_state,
            result,
            candidates,
            event_token="event-1",
            app_id="app-id",
            api_key="api-key",
            post=lambda *args, **kwargs: (
                calls.append(kwargs) or FakeResponse({"id": "duplicate"})
            ),
            now=self.now,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(diagnostic["status"], "no_new_orders")
        self.assertEqual(second_state, first_state)

    def test_symbol_can_notify_again_after_leaving_buy_now(self):
        active_state = {
            "version": 1,
            "current_symbols": ["NVDA"],
            "notified_active_symbols": ["NVDA"],
        }
        cleared_state, _ = buy_now_push.send_new_buy_now_notifications(
            active_state,
            {"buy_recommendations": []},
            [candidate("NVDA")],
            app_id="app-id",
            api_key="api-key",
            now=self.now,
        )
        calls = []
        _, diagnostic = buy_now_push.send_new_buy_now_notifications(
            cleared_state,
            {
                "buy_recommendations": [
                    recommendation("NVDA", "Candidat valid"),
                ]
            },
            [candidate("NVDA")],
            event_token="event-2",
            app_id="app-id",
            api_key="api-key",
            post=lambda *args, **kwargs: (
                calls.append(kwargs) or FakeResponse({"id": "second"})
            ),
            now=self.now,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(diagnostic["delivered_symbols"], ["NVDA"])

    def test_failed_or_unconfigured_delivery_stays_pending(self):
        result = {
            "buy_recommendations": [
                recommendation("NVDA", "Candidat valid"),
            ]
        }
        candidates = [candidate("NVDA")]
        missing_state, missing = (
            buy_now_push.send_new_buy_now_notifications(
                {},
                result,
                candidates,
                app_id="",
                api_key="",
                now=self.now,
            )
        )
        failed_state, failed = buy_now_push.send_new_buy_now_notifications(
            {},
            result,
            candidates,
            app_id="app-id",
            api_key="api-key",
            post=lambda *args, **kwargs: FakeResponse(
                error=RuntimeError("network down")
            ),
            now=self.now,
        )

        self.assertEqual(missing["status"], "configuration_missing")
        self.assertEqual(missing_state["notified_active_symbols"], [])
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed_state["notified_active_symbols"], [])

    def test_empty_onesignal_audience_reports_provider_details(self):
        _, diagnostic = buy_now_push.send_new_buy_now_notifications(
            {},
            {
                "buy_recommendations": [
                    recommendation("WST", "Candidat valid"),
                ]
            },
            [candidate("WST")],
            app_id="app-id",
            api_key="api-key",
            post=lambda *args, **kwargs: FakeResponse({
                "errors": ["All included players are not subscribed"],
            }),
            now=self.now,
        )

        self.assertEqual(diagnostic["status"], "failed")
        self.assertIn(
            "All included players are not subscribed",
            diagnostic["errors"]["WST"],
        )


if __name__ == "__main__":
    unittest.main()
