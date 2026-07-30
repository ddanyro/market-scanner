import xml.etree.ElementTree as ET
import unittest

import ibkr_flex_history


FLEX_WITH_HISTORY = """
<FlexQueryResponse queryName="Dashboard" type="AF">
  <FlexStatements count="1">
    <FlexStatement accountId="U123" fromDate="2026-07-28"
                   toDate="2026-07-30" period="Last365CalendarDays">
      <AccountInformation accountId="U123" currency="EUR" />
      <NetAssetValues>
        <NetAssetValue reportDate="20260728" cash="800" total="1000" />
        <NetAssetValue reportDate="20260729" cash="810" total="1025" />
      </NetAssetValues>
      <ChangeInNAV startingValue="1000" endingValue="1050" />
      <CashReport>
        <CashReportCurrency currency="BASE_SUMMARY"
                            endingCash="825"
                            endingSettledCash="820" />
        <CashReportCurrency currency="EUR" endingCash="700" />
        <CashReportCurrency currency="USD" endingCash="125" />
      </CashReport>
    </FlexStatement>
  </FlexStatements>
</FlexQueryResponse>
"""


class TestIBKRFlexHistory(unittest.TestCase):
    def test_flex_nav_and_cash_are_extracted_without_estimates(self):
        snapshot = ibkr_flex_history.build_flex_account_snapshot(
            ET.fromstring(FLEX_WITH_HISTORY),
            observed_at='2026-07-31T00:00:00+00:00',
        )

        self.assertEqual(snapshot['source'], 'IBKR Flex Web Service')
        self.assertEqual(snapshot['fetched_at'], '2026-07-31T00:00:00+00:00')
        self.assertEqual(len(snapshot['accounts']), 1)
        account = snapshot['accounts'][0]
        self.assertEqual(account['base_currency'], 'EUR')
        self.assertEqual(account['summary']['NetLiquidation'], 1050)
        self.assertEqual(account['summary']['TotalCashValue'], 825)
        self.assertEqual(account['cash_by_currency']['USD'], 125)
        self.assertEqual(
            [point['date'] for point in snapshot['nav_history']],
            ['2026-07-28', '2026-07-29', '2026-07-30'],
        )
        self.assertEqual(snapshot['nav_history'][-1]['nav'], 1050)
        self.assertEqual(snapshot['cash_history'][-1]['cash'], 825)

    def test_existing_history_and_account_fields_are_preserved(self):
        existing = {
            'accounts': [{
                'account_id': 'U123',
                'label': 'IBKR',
                'base_currency': 'EUR',
                'summary': {'AvailableFunds': 500},
                'cash_by_currency': {'RON': 10},
            }],
            'positions': [{'symbol': 'JPM', 'position': 4}],
            'nav_history': [{
                'date': '2026-07-27',
                'nav': 990,
                'currency': 'EUR',
            }],
            'cash_history': [{
                'date': '2026-07-27',
                'cash': 790,
                'currency': 'EUR',
            }],
        }
        snapshot = ibkr_flex_history.build_flex_account_snapshot(
            ET.fromstring(FLEX_WITH_HISTORY),
            existing=existing,
        )

        account = snapshot['accounts'][0]
        self.assertEqual(account['summary']['AvailableFunds'], 500)
        self.assertEqual(account['cash_by_currency']['RON'], 10)
        self.assertEqual(snapshot['positions'][0]['symbol'], 'JPM')
        self.assertEqual(snapshot['nav_history'][0]['date'], '2026-07-27')
        self.assertEqual(snapshot['cash_history'][0]['date'], '2026-07-27')

    def test_query_without_nav_or_cash_does_not_create_snapshot(self):
        root = ET.fromstring("""
        <FlexQueryResponse>
          <FlexStatements count="1">
            <FlexStatement accountId="U123" toDate="2026-07-30">
              <OpenPositions>
                <OpenPosition symbol="JPM" positionValueInBase="100" />
              </OpenPositions>
              <Trades>
                <Trade symbol="JPM" netCashInBase="-50" />
              </Trades>
            </FlexStatement>
          </FlexStatements>
        </FlexQueryResponse>
        """)

        self.assertIsNone(
            ibkr_flex_history.build_flex_account_snapshot(root)
        )

    def test_currency_is_not_guessed_when_report_and_cache_omit_it(self):
        root = ET.fromstring("""
        <FlexQueryResponse>
          <FlexStatements count="1">
            <FlexStatement accountId="U123" toDate="2026-07-30">
              <ChangeInNAV endingValue="1000" />
            </FlexStatement>
          </FlexStatements>
        </FlexQueryResponse>
        """)

        self.assertIsNone(
            ibkr_flex_history.build_flex_account_snapshot(root)
        )

    def test_duplicate_dates_are_replaced_by_latest_flex_value(self):
        existing = {
            'accounts': [{
                'account_id': 'U123',
                'base_currency': 'EUR',
                'summary': {},
            }],
            'nav_history': [{
                'date': '2026-07-29',
                'nav': 999,
                'currency': 'EUR',
            }],
        }
        snapshot = ibkr_flex_history.build_flex_account_snapshot(
            ET.fromstring(FLEX_WITH_HISTORY),
            existing=existing,
        )
        points = {
            point['date']: point['nav']
            for point in snapshot['nav_history']
        }

        self.assertEqual(points['2026-07-29'], 1025)


if __name__ == '__main__':
    unittest.main()
