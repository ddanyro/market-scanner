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
            self.assertIn('load_order_cache_password', script, filename)
            self.assertIn('git_sync_finish', script, filename)

    def test_shared_sync_stages_every_scanner_output_and_retries_push(self):
        sync = (self.root / 'update_git_sync.sh').read_text(encoding='utf-8')
        for generated in (
            'tradeville_account.enc.json', 'shadow_predictions.jsonl',
            'technical_events_predictions.jsonl.gz',
            'analysis/shadow_forward_validation/collection_coverage.json',
            'analysis/technical_events_validation/technical_events_validation_report.md',
            'analysis/technical_events_validation/event_observations.csv.gz',
            'market_history.json', 'market_indicators.json',
            'watchlist_compact.json', 'portfolio.json', 'index.html',
        ):
            self.assertIn(f'"{generated}"', sync)
        self.assertIn('for attempt in 1 2 3', sync)
        self.assertIn('merge_shadow_ledgers.py', sync)
        self.assertIn('technical_events_shadow.rotate_ledger()', sync)
        self.assertIn('load_shadow_r2_config', sync)
        self.assertIn('shadow_r2_is_primary', sync)
        self.assertIn('market-scanner-cloudflare-account-id', sync)
        self.assertIn('market-scanner-shadow-r2-access-key-id', sync)
        self.assertIn('market-scanner-shadow-r2-secret-access-key', sync)
        self.assertIn(
            'technical_events_predictions.archive-*.jsonl.gz', sync
        )
        self.assertIn('git rebase --autostash -X theirs', sync)
        self.assertIn('load_order_cache_password()', sync)
        self.assertIn('market-scanner-portfolio-password', sync)
        self.assertIn('market-scanner-order-cache-password', sync)
        self.assertIn('security find-generic-password', sync)
        self.assertIn('security add-generic-password', sync)
        self.assertNotIn('.portfolio_order_cache_password', sync)
        self.assertNotIn(
            '"analysis/technical_events_validation/event_observations.csv"',
            sync,
        )

    def test_all_updates_use_cadenced_shadow_maintenance_before_commit(self):
        for filename in (
            'update_portfolio.sh', 'update_international.sh', 'update_all.sh',
        ):
            script = (self.root / filename).read_text(encoding='utf-8')
            self.assertIn('run_shadow_maintenance.py', script)
            self.assertNotIn('evaluate_shadow_forward.py', script)
            self.assertNotIn('evaluate_technical_events_forward.py', script)
        runner = (self.root / 'run_shadow_maintenance.py').read_text(
            encoding='utf-8'
        )
        self.assertIn('evaluate_shadow_forward.py', runner)
        self.assertIn('evaluate_technical_events_forward.py', runner)

    def test_ro_update_loads_shared_r2_configuration(self):
        script = (self.root / 'update_ro.sh').read_text(encoding='utf-8')
        self.assertIn('source "./update_git_sync.sh"', script)
        self.assertIn('load_shadow_r2_config', script)
        self.assertIn('load_order_cache_password', script)

    def test_runtime_never_reads_a_local_password_file(self):
        for filename in (
            'market_scanner.py', 'ibkr_web_api.py', 'ib_tws_sync.py',
            'update_git_sync.sh',
        ):
            content = (self.root / filename).read_text(encoding='utf-8')
            self.assertNotIn('password.txt', content, filename)
            self.assertNotIn('.portfolio_order_cache_password', content, filename)
        scanner = (self.root / 'market_scanner.py').read_text(encoding='utf-8')
        self.assertNotIn('password = "1234"', scanner)
        self.assertIn("Lipsește PORTFOLIO_PASSWORD", scanner)


if __name__ == '__main__':
    unittest.main()
