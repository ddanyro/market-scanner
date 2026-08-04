import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

import ib_sync


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
