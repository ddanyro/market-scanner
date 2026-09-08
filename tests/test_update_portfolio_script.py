import pathlib
import unittest


class TestUpdatePortfolioScript(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(__file__).resolve().parents[1]

    def test_all_local_update_scripts_use_shared_start_and_finish_sync(self):
        for filename in (
            'update_portfolio.sh', 'update_international.sh', 'update_all.sh',
        ):
            script = (self.root / filename).read_text(encoding='utf-8')
            self.assertIn('source "./update_git_sync.sh"', script, filename)
            self.assertIn('git_sync_start', script, filename)
            self.assertIn('git_sync_finish', script, filename)

    def test_shared_sync_stages_every_scanner_output_and_retries_push(self):
        sync = (self.root / 'update_git_sync.sh').read_text(encoding='utf-8')
        for generated in (
            'tradeville_account.enc.json', 'shadow_predictions.jsonl',
            'analysis/shadow_forward_validation/collection_coverage.json',
            'market_history.json', 'market_indicators.json',
            'watchlist_compact.json', 'portfolio.json', 'index.html',
        ):
            self.assertIn(f'"{generated}"', sync)
        self.assertIn('for attempt in 1 2 3', sync)
        self.assertIn('merge_shadow_ledgers.py', sync)
        self.assertIn('git rebase --autostash -X theirs', sync)

    def test_international_and_all_refresh_forward_reports_before_commit(self):
        for filename in ('update_international.sh', 'update_all.sh'):
            script = (self.root / filename).read_text(encoding='utf-8')
            self.assertIn('evaluate_shadow_forward.py', script)


if __name__ == '__main__':
    unittest.main()
