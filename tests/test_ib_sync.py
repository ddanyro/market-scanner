import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import ib_sync
import pytest


@pytest.mark.parametrize('entry_date', ['', '2026-10-01'])
def test_tradeville_accounts_remain_separate_and_keep_own_preferences(tmp_path, monkeypatch, entry_date):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GITHUB_ACTIONS', 'false')
    rows = [
        {'Symbol': 'TVBETETF', 'Shares': 130, 'Buy_Price': 57.48,
         'Current_Price': 60, 'Currency': 'RON', 'Account': 'First', 'Account_ID': '01',
         'Entry_Date': entry_date},
        {'Symbol': 'TVBETETF', 'Shares': 654, 'Buy_Price': 56.45,
         'Current_Price': 60, 'Currency': 'RON', 'Account': 'Second', 'Account_ID': '02'},
    ]
    pd.DataFrame(rows).to_csv('tradeville_portfolio.csv', index=False)
    pd.DataFrame([
        dict(rows[0], Broker='Tradeville', Target=71),
        dict(rows[1], Broker='Tradeville', Target=82),
    ]).to_csv('portfolio.csv', index=False)
    assert ib_sync.sync_ibkr(allow_flex=False)
    saved = pd.read_csv('portfolio.csv', dtype={'Account_ID': str})
    assert len(saved) == 2
    accounts = saved.set_index('Account_ID')
    assert accounts.loc['01', 'Shares'] == 130
    assert accounts.loc['02', 'Shares'] == 654
    assert accounts.loc['01', 'Buy_Price'] == pytest.approx(57.48)
    assert accounts.loc['02', 'Buy_Price'] == pytest.approx(56.45)
    assert accounts.loc['01', 'Target'] == 71
    assert accounts.loc['02', 'Target'] == 82
    assert saved['Shares'].sum() == 784
    assert saved['Investment'].sum() == pytest.approx(44390.7)
    assert saved['Position_ID'].nunique() == 2


def test_same_symbol_at_ibkr_does_not_hide_tradeville(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GITHUB_ACTIONS', 'false')
    pd.DataFrame([{'Symbol': 'SAME', 'Shares': 3, 'Buy_Price': 10,
                   'Currency': 'USD'}]).to_csv('tws_positions.csv', index=False)
    pd.DataFrame([{'Symbol': 'SAME', 'Shares': 5, 'Buy_Price': 20,
                   'Currency': 'USD', 'Account_ID': 'A'}]).to_csv('tradeville_portfolio.csv', index=False)
    assert ib_sync.sync_ibkr(allow_flex=False)
    saved = pd.read_csv('portfolio.csv')
    assert len(saved) == 2
    assert set(saved['Shares']) == {3, 5}
    assert set(saved['Broker']) == {'IBKR', 'Tradeville'}


class TestIBSyncPortfolioPersistence(unittest.TestCase):
    def test_github_flex_snapshot_cannot_remove_tracked_position(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'portfolio.csv')
            pd.DataFrame(
                [
                    {'Symbol': 'AMZN', 'Shares': 4},
                    {'Symbol': 'TVBETETF.RO', 'Shares': 2061},
                ]
            ).to_csv(path, index=False)

            incomplete_flex = pd.DataFrame(
                [{'Symbol': 'TVBETETF.RO', 'Shares': 2061}]
            )
            with patch.dict(
                os.environ,
                {'GITHUB_ACTIONS': 'true'},
                clear=False,
            ):
                os.environ.pop('IBKR_ALLOW_REMOTE_POSITION_WRITES', None)
                written = ib_sync._persist_portfolio_positions(
                    incomplete_flex, path
                )

            self.assertFalse(written)
            saved = pd.read_csv(path)
            self.assertEqual(
                set(saved['Symbol']), {'AMZN', 'TVBETETF.RO'}
            )

    def test_local_tws_snapshot_remains_authoritative(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'portfolio.csv')
            pd.DataFrame(
                [{'Symbol': 'OLD', 'Shares': 1}]
            ).to_csv(path, index=False)
            tws_snapshot = pd.DataFrame(
                [{'Symbol': 'AMZN', 'Shares': 4}]
            )

            with patch.dict(os.environ, {'GITHUB_ACTIONS': 'false'}):
                written = ib_sync._persist_portfolio_positions(
                    tws_snapshot, path
                )

            self.assertTrue(written)
            saved = pd.read_csv(path)
            self.assertEqual(saved['Symbol'].tolist(), ['AMZN'])

    def test_remote_write_requires_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'portfolio.csv')
            pd.DataFrame(
                [{'Symbol': 'AMZN', 'Shares': 4}]
            ).to_csv(path, index=False)
            flex_snapshot = pd.DataFrame(
                [{'Symbol': 'TVBETETF.RO', 'Shares': 2061}]
            )

            with patch.dict(
                os.environ,
                {
                    'GITHUB_ACTIONS': 'true',
                    'IBKR_ALLOW_REMOTE_POSITION_WRITES': 'true',
                },
            ):
                written = ib_sync._persist_portfolio_positions(
                    flex_snapshot, path
                )

            self.assertTrue(written)
            saved = pd.read_csv(path)
            self.assertEqual(saved['Symbol'].tolist(), ['TVBETETF.RO'])


if __name__ == '__main__':
    unittest.main()
