import datetime
import json
import os
import tempfile
import unittest
from unittest import mock

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
        self.service_account = {
            "type": "service_account",
            "project_id": "market-scanner-test",
            "private_key": (
                "-----BEGIN PRIVATE KEY-----\nTEST\n"
                "-----END PRIVATE KEY-----\n"
            ),
            "client_email": (
                "firebase-adminsdk@market-scanner-test.iam."
                "gserviceaccount.com"
            ),
        }
        self.registration_token = (
            "fcm-registration-token:"
            "abcdefghijklmnopqrstuvwxyz0123456789_-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

    @staticmethod
    def access_token(_service_account):
        return "oauth-access-token"

    def delivery_options(self, **overrides):
        options = {
            "service_account_json": self.service_account,
            "registration_tokens": self.registration_token,
            "access_token_factory": self.access_token,
            "now": self.now,
        }
        options.update(overrides)
        return options

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

    def test_sends_one_exact_firebase_message_per_new_symbol(self):
        calls = []

        def post(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse(
                {"name": f"projects/test/messages/{len(calls)}"}
            )

        state, diagnostic = buy_now_push.send_new_buy_now_notifications(
            {},
            {
                "buy_recommendations": [
                    recommendation("NVDA", "Candidat valid"),
                    recommendation("PBR", "Candidat valid"),
                ]
            },
            [candidate("NVDA"), candidate("PBR")],
            post=post,
            **self.delivery_options(),
        )

        self.assertEqual(diagnostic["status"], "sent")
        self.assertEqual(diagnostic["provider"], "firebase")
        self.assertEqual(diagnostic["delivered_symbols"], ["NVDA", "PBR"])
        self.assertEqual(
            state["notified_active_symbols"], ["NVDA", "PBR"]
        )
        self.assertEqual(state["provider"], "firebase")
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            calls[0][1]["json"]["message"]["notification"]["body"],
            "Ordin de cumpărare acum: NVDA.",
        )
        self.assertEqual(
            calls[0][1]["json"]["message"]["token"],
            self.registration_token,
        )
        self.assertEqual(
            calls[0][1]["headers"]["Authorization"],
            "Bearer oauth-access-token",
        )
        self.assertIn(
            "/v1/projects/market-scanner-test/messages:send",
            calls[0][0],
        )
        self.assertNotIn(
            self.service_account["private_key"],
            str(calls[0][1]["json"]),
        )

    def test_active_order_is_not_sent_twice(self):
        calls = []
        result = {
            "buy_recommendations": [
                recommendation("NVDA", "Candidat valid"),
            ]
        }
        candidates = [candidate("NVDA")]
        options = self.delivery_options(
            post=lambda *args, **kwargs: (
                calls.append(kwargs)
                or FakeResponse({"name": "projects/test/messages/first"})
            )
        )
        first_state, _ = buy_now_push.send_new_buy_now_notifications(
            {}, result, candidates, **options
        )
        second_state, diagnostic = (
            buy_now_push.send_new_buy_now_notifications(
                first_state, result, candidates, **options
            )
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(diagnostic["status"], "no_new_orders")
        self.assertEqual(second_state, first_state)

    def test_symbol_can_notify_again_after_leaving_buy_now(self):
        active_state = {
            "version": 2,
            "provider": "firebase",
            "current_symbols": ["NVDA"],
            "notified_active_symbols": ["NVDA"],
        }
        cleared_state, _ = buy_now_push.send_new_buy_now_notifications(
            active_state,
            {"buy_recommendations": []},
            [candidate("NVDA")],
            **self.delivery_options(),
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
            post=lambda *args, **kwargs: (
                calls.append(kwargs)
                or FakeResponse({"name": "projects/test/messages/second"})
            ),
            **self.delivery_options(),
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(diagnostic["delivered_symbols"], ["NVDA"])

    def test_provider_migration_realerts_current_buy_once(self):
        calls = []
        previous_onesignal_state = {
            "version": 1,
            "current_symbols": ["NVDA"],
            "notified_active_symbols": ["NVDA"],
        }
        next_state, diagnostic = (
            buy_now_push.send_new_buy_now_notifications(
                previous_onesignal_state,
                {
                    "buy_recommendations": [
                        recommendation("NVDA", "Candidat valid"),
                    ]
                },
                [candidate("NVDA")],
                post=lambda *args, **kwargs: (
                    calls.append(kwargs)
                    or FakeResponse({"name": "projects/test/messages/nvda"})
                ),
                **self.delivery_options(),
            )
        )

        self.assertEqual(diagnostic["delivered_symbols"], ["NVDA"])
        self.assertEqual(next_state["provider"], "firebase")
        self.assertEqual(len(calls), 1)

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
                service_account_json="",
                registration_tokens="",
                now=self.now,
            )
        )
        failed_state, failed = buy_now_push.send_new_buy_now_notifications(
            {},
            result,
            candidates,
            post=lambda *args, **kwargs: FakeResponse(
                error=RuntimeError("network down")
            ),
            **self.delivery_options(),
        )

        self.assertEqual(missing["status"], "configuration_missing")
        self.assertEqual(missing_state["notified_active_symbols"], [])
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed_state["notified_active_symbols"], [])

    def test_invalid_service_account_is_not_used(self):
        diagnostic = buy_now_push.send_test_notification(
            "test",
            registration_token=self.registration_token,
            service_account_json='{"project_id": "missing-key"}',
            now=self.now,
        )

        self.assertEqual(diagnostic["status"], "configuration_missing")
        self.assertEqual(diagnostic["provider"], "firebase")

    def test_cached_retry_delivers_pending_symbols_and_persists_state(self):
        cached_state = {
            "last_portfolio_ai_analysis": {
                "generated_at": "2026-07-30T17:00:00+03:00",
                "result": {
                    "buy_recommendations": [
                        recommendation("WST", "Candidat valid"),
                    ],
                },
                "buy_candidates": [candidate("WST")],
            },
            "buy_now_push_state": {
                "version": 2,
                "provider": "firebase",
                "current_symbols": ["WST"],
                "notified_active_symbols": [],
            },
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_path = os.path.join(
                temporary_directory,
                "dashboard_state.json",
            )
            with open(state_path, "w", encoding="utf-8") as handle:
                json.dump(cached_state, handle)
            diagnostic = buy_now_push.retry_cached_buy_now_notifications(
                state_path,
                post=lambda *args, **kwargs: FakeResponse(
                    {"name": "projects/test/messages/wst"}
                ),
                **self.delivery_options(),
            )
            with open(state_path, "r", encoding="utf-8") as handle:
                persisted = json.load(handle)

        self.assertEqual(diagnostic["status"], "sent")
        self.assertEqual(diagnostic["delivered_symbols"], ["WST"])
        self.assertEqual(
            persisted["buy_now_push_state"]["notified_active_symbols"],
            ["WST"],
        )

    def test_manual_push_test_targets_fcm_registration_token(self):
        calls = []
        diagnostic = buy_now_push.send_test_notification(
            "test",
            registration_token=self.registration_token,
            service_account_json=self.service_account,
            site_url="https://example.test/",
            post=lambda *args, **kwargs: (
                calls.append(kwargs)
                or FakeResponse({"name": "projects/test/messages/manual"})
            ),
            access_token_factory=self.access_token,
            now=self.now,
        )

        self.assertEqual(diagnostic["status"], "sent")
        self.assertEqual(
            diagnostic["message_ids"],
            ["projects/test/messages/manual"],
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0]["json"]["message"]["notification"]["body"],
            "Ordin de cumpărare acum: TEST.",
        )
        self.assertEqual(
            calls[0]["json"]["message"]["webpush"]["fcm_options"]["link"],
            "https://example.test/",
        )

    def test_multiple_firebase_tokens_receive_same_alert(self):
        calls = []
        second_token = self.registration_token + "-second"
        diagnostic = buy_now_push.send_test_notification(
            "test",
            registration_token=[
                self.registration_token,
                second_token,
            ],
            service_account_json=self.service_account,
            post=lambda *args, **kwargs: (
                calls.append(kwargs["json"]["message"]["token"])
                or FakeResponse(
                    {"name": f"projects/test/messages/{len(calls)}"}
                )
            ),
            access_token_factory=self.access_token,
            now=self.now,
        )

        self.assertEqual(diagnostic["status"], "sent")
        self.assertEqual(diagnostic["target_count"], 2)
        self.assertEqual(
            calls,
            [self.registration_token, second_token],
        )

    def test_real_buy_alert_uses_configured_firebase_token(self):
        calls = []
        with mock.patch.dict(
            os.environ,
            {"FIREBASE_REGISTRATION_TOKENS": self.registration_token},
        ):
            _, diagnostic = buy_now_push.send_new_buy_now_notifications(
                {},
                {
                    "buy_recommendations": [
                        recommendation("NVDA", "Candidat valid"),
                    ],
                },
                [candidate("NVDA")],
                service_account_json=self.service_account,
                access_token_factory=self.access_token,
                post=lambda *args, **kwargs: (
                    calls.append(kwargs)
                    or FakeResponse({"name": "projects/test/messages/nvda"})
                ),
                now=self.now,
            )

        self.assertEqual(diagnostic["status"], "sent")
        self.assertEqual(
            calls[0]["json"]["message"]["token"],
            self.registration_token,
        )

    def test_market_push_selects_only_buy_and_cumpara_verdicts(self):
        signals = buy_now_push.actionable_market_signals([
            {
                "key": "international",
                "label": "Piața internațională",
                "verdict": "BUY (HIGH CONFIDENCE)",
            },
            {
                "key": "romania_bvb",
                "label": "Piața românească BVB",
                "verdict": "CUMPĂRĂ",
            },
            {
                "key": "wait_market",
                "label": "Piața în așteptare",
                "verdict": "WAIT",
            },
        ])
        self.assertEqual(
            set(signals), {"international", "romania_bvb"}
        )

    def test_market_push_does_not_repeat_during_cooldown(self):
        calls = []

        def post(_url, **kwargs):
            calls.append(kwargs["json"]["message"])
            return FakeResponse({
                "name": f"projects/test/messages/{len(calls)}"
            })

        signals = [
            {
                "key": "international",
                "label": "Piața internațională",
                "verdict": "BUY",
            },
            {
                "key": "romania_bvb",
                "label": "Piața românească BVB",
                "verdict": "CUMPĂRĂ",
            },
        ]
        first_state, first = (
            buy_now_push.send_new_market_buy_notifications(
                {}, signals, post=post, **self.delivery_options()
            )
        )
        second_state, second = (
            buy_now_push.send_new_market_buy_notifications(
                first_state, signals, post=post, **self.delivery_options()
            )
        )

        self.assertEqual(first["status"], "sent")
        self.assertEqual(
            first["delivered_markets"],
            ["international", "romania_bvb"],
        )
        self.assertEqual(second["status"], "no_new_market_signals")
        self.assertEqual(second["delivered_markets"], [])
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            calls[0]["notification"]["body"],
            "Piața internațională: BUY.",
        )
        self.assertEqual(calls[0]["data"]["kind"], "market_buy")
        self.assertEqual(
            calls[1]["notification"]["body"],
            "Piața românească BVB: CUMPĂRĂ.",
        )

    def test_market_can_notify_again_after_leaving_buy(self):
        active_state = {
            "version": 1,
            "provider": "firebase",
            "current_markets": ["international"],
            "current_verdicts": {"international": "BUY"},
            "notified_active_markets": ["international"],
        }
        close_calls = []
        cleared_state, closed = (
            buy_now_push.send_new_market_buy_notifications(
                active_state,
                [{
                    "key": "international",
                    "label": "Piața internațională",
                    "verdict": "WAIT",
                }],
                post=lambda *args, **kwargs: (
                    close_calls.append(kwargs["json"]["message"])
                    or FakeResponse({"name": "projects/test/messages/closed"})
                ),
                **self.delivery_options(),
            )
        )
        self.assertEqual(
            closed["delivered_closed_markets"], ["international"]
        )
        self.assertEqual(len(close_calls), 1)
        self.assertEqual(
            close_calls[0]["data"]["kind"], "market_buy_closed"
        )
        self.assertEqual(
            close_calls[0]["notification"]["body"],
            "Fereastra de cumpărare s-a închis — Piața internațională. "
            "Verdict curent: WAIT.",
        )

        repeated_close_calls = []
        stable_state, stable = (
            buy_now_push.send_new_market_buy_notifications(
                cleared_state,
                [{
                    "key": "international",
                    "label": "Piața internațională",
                    "verdict": "WAIT",
                }],
                post=lambda *args, **kwargs: (
                    repeated_close_calls.append(kwargs)
                    or FakeResponse({"name": "unexpected"})
                ),
                **self.delivery_options(),
            )
        )
        self.assertEqual(stable["status"], "no_new_market_signals")
        self.assertEqual(repeated_close_calls, [])

        calls = []
        _, diagnostic = buy_now_push.send_new_market_buy_notifications(
            stable_state,
            [{
                "key": "international",
                "label": "Piața internațională",
                "verdict": "BUY",
            }],
            post=lambda *args, **kwargs: (
                calls.append(kwargs)
                or FakeResponse({"name": "projects/test/messages/again"})
            ),
            **self.delivery_options(),
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            diagnostic["delivered_markets"], ["international"]
        )

    def test_failed_market_close_is_retried(self):
        active_state = {
            "version": 2,
            "provider": "firebase",
            "current_markets": ["romania_bvb"],
            "current_verdicts": {"romania_bvb": "CUMPĂRĂ"},
            "notified_active_markets": ["romania_bvb"],
        }
        wait_signal = [{
            "key": "romania_bvb",
            "label": "Piața românească BVB",
            "verdict": "PRUDENȚĂ",
        }]
        failed_state, failed = (
            buy_now_push.send_new_market_buy_notifications(
                active_state,
                wait_signal,
                service_account_json="",
                registration_tokens="",
                now=self.now,
            )
        )
        self.assertEqual(failed["status"], "configuration_missing")
        self.assertEqual(
            failed_state["pending_close_markets"], ["romania_bvb"]
        )

        calls = []
        next_state, retried = (
            buy_now_push.send_new_market_buy_notifications(
                failed_state,
                wait_signal,
                post=lambda *args, **kwargs: (
                    calls.append(kwargs)
                    or FakeResponse({"name": "projects/test/messages/close"})
                ),
                **self.delivery_options(),
            )
        )
        self.assertEqual(
            retried["delivered_closed_markets"], ["romania_bvb"]
        )
        self.assertEqual(next_state["pending_close_markets"], [])
        self.assertEqual(len(calls), 1)

    def test_market_buy_reminders_repeat_after_four_hours(self):
        calls = []
        post = lambda *args, **kwargs: (
            calls.append(kwargs["json"]["message"]["data"]["market"])
            or FakeResponse({
                "name": f"projects/test/messages/{len(calls)}"
            })
        )
        signals = [
            {
                "key": "international",
                "label": "Piața internațională",
                "verdict": "BUY",
            },
            {
                "key": "romania_bvb",
                "label": "Piața românească BVB",
                "verdict": "CUMPĂRĂ",
            },
        ]
        first_state, _ = buy_now_push.send_new_market_buy_notifications(
            {}, signals, post=post, **self.delivery_options()
        )
        same_time = self.now
        second_state, second = (
            buy_now_push.send_new_market_buy_notifications(
                first_state,
                signals,
                post=post,
                **self.delivery_options(now=same_time),
            )
        )
        before_cooldown = self.now + datetime.timedelta(
            hours=3, minutes=59
        )
        third_state, third = buy_now_push.send_new_market_buy_notifications(
            second_state,
            signals,
            post=post,
            **self.delivery_options(now=before_cooldown),
        )
        at_cooldown = self.now + datetime.timedelta(hours=4)
        _, fourth = buy_now_push.send_new_market_buy_notifications(
            third_state,
            signals,
            post=post,
            **self.delivery_options(now=at_cooldown),
        )

        self.assertEqual(second["delivered_markets"], [])
        self.assertEqual(third["delivered_markets"], [])
        self.assertEqual(
            fourth["delivered_markets"],
            ["international", "romania_bvb"],
        )
        self.assertEqual(
            calls,
            [
                "international", "romania_bvb",
                "international", "romania_bvb",
            ],
        )


if __name__ == "__main__":
    unittest.main()
