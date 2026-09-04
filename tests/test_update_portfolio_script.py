import pathlib
import unittest


class TestUpdatePortfolioScript(unittest.TestCase):
    def test_generated_tradeville_snapshot_is_committed_before_rebase(self):
        script = (
            pathlib.Path(__file__).resolve().parents[1] / 'update_portfolio.sh'
        ).read_text(encoding='utf-8')

        self.assertIn('"tradeville_account.enc.json"', script)
        self.assertEqual(script.count('git pull --rebase --autostash'), 2)


if __name__ == '__main__':
    unittest.main()
