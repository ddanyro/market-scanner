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


if __name__ == "__main__":
    unittest.main()
