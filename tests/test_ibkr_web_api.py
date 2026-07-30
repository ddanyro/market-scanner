import json
import os
import tempfile
import unittest

import ibkr_web_api


class FakeIBKRClient:
    def __init__(self, authenticated=True):
        self.authenticated = authenticated

    def validate_session(self):
        return self.authenticated

    def get_accounts(self):
        return [{'accountId': 'U123', 'currency': 'EUR'}]

    def get_summary(self, account_id):
        self.last_summary_account = account_id
        return {
            'netliquidation': {'amount': 89043.59, 'currency': 'EUR'},
            'availablefunds': {'amount': 85000, 'currency': 'EUR'},
            'maintmarginreq': {'amount': 100, 'currency': 'EUR'},
        }

    def get_ledger(self, account_id):
        self.last_ledger_account = account_id
        return {
            'BASE': {
                'cashbalance': 85949.15,
                'settledcash': 85000,
                'stockmarketvalue': 3094.44,
            },
            'EUR': {'cashbalance': 78887.73},
            'USD': {'cashbalance': 8026.08},
        }

    def get_positions(self, account_id):
        return [{'contractDesc': 'JPM', 'position': 4}]

    def get_all_periods(self, account_ids):
        self.performance_accounts = account_ids
        return {
            'U123': {
                'baseCurrency': 'EUR',
                '1Y': {
                    'dates': ['20260728', '20260729'],
                    'nav': [88000, 89043.59],
                },
            },
        }


class TestIBKRWebAPI(unittest.TestCase):
    def test_snapshot_maps_summary_ledger_positions_and_nav(self):
        client = FakeIBKRClient()
        payload = ibkr_web_api.build_account_snapshot(client)

        self.assertEqual(payload['source'], 'IBKR Client Portal Web API')
        self.assertEqual(len(payload['accounts']), 1)
        account = payload['accounts'][0]
        self.assertEqual(account['base_currency'], 'EUR')
        self.assertEqual(account['summary']['NetLiquidation'], 89043.59)
        self.assertEqual(account['summary']['TotalCashValue'], 85949.15)
        self.assertEqual(account['summary']['GrossPositionValue'], 3094.44)
        self.assertEqual(account['cash_by_currency']['USD'], 8026.08)
        self.assertEqual(payload['positions'][0]['account_id'], 'U123')
        self.assertEqual(len(payload['nav_history']), 2)
        self.assertEqual(payload['nav_history'][-1]['nav'], 89043.59)
        self.assertEqual(payload['nav_history'][-1]['currency'], 'EUR')

    def test_unauthenticated_gateway_is_explicit(self):
        with self.assertRaisesRegex(
            ibkr_web_api.IBKRWebAPIError, 'nu este autentificată'
        ):
            ibkr_web_api.build_account_snapshot(
                FakeIBKRClient(authenticated=False)
            )

    def test_tls_can_only_be_disabled_for_loopback(self):
        with self.assertRaises(ValueError):
            ibkr_web_api.IBKRWebAPIClient(
                base_url='https://example.com/v1/api',
                verify_ssl=False,
            )

    def test_sync_persists_schema_compatible_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            exact_path = os.path.join(temp_dir, 'tws_account.json')
            encrypted_path = os.path.join(temp_dir, 'tws_account.enc.json')
            risk_path = os.path.join(temp_dir, 'tws_account_risk.json')
            payload = ibkr_web_api.sync_account_snapshot(
                client=FakeIBKRClient(),
                output_file=exact_path,
                encrypted_output=encrypted_path,
                risk_output=risk_path,
                password='test-password',
            )
            with open(exact_path, 'r', encoding='utf-8') as handle:
                exact = json.load(handle)
            with open(encrypted_path, 'r', encoding='utf-8') as handle:
                encrypted = json.load(handle)
            with open(risk_path, 'r', encoding='utf-8') as handle:
                risk = json.load(handle)

        self.assertEqual(exact, payload)
        self.assertNotIn('NetLiquidation', json.dumps(encrypted))
        self.assertEqual(risk['privacy_mode'], 'bands_only')
        self.assertNotIn('summary', risk['sanitized_accounts'][0])


if __name__ == '__main__':
    unittest.main()
