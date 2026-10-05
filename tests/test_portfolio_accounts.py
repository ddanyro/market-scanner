import ast
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest

import market_scanner as scanner
from portfolio_identity import position_key, ownership, same_owner


def position(account, shares, buy):
    return dict(Symbol='TVBETETF', Broker='Tradeville', Account=account,
        Account_ID=account, Shares=shares, Buy_Price=buy, Current_Price=12,
        Price_Native=60, Currency='RON', Investment=shares*buy,
        Current_Value=shares*12, Profit=shares*(12-buy), Profit_Pct=(12/buy-1)*100,
        Target=None, Max_Profit=None, Suggested_Stop=10, Trail_Stop=0, Trail_Pct=0,
        Trend='Bullish', RSI_Status='Neutral', Status='Neutral', RSI=55,
        Sparkline=[10,11,12], Chart_History=[10,11,12], Chart_Dates=['a','b','c'],
        Company_Name='ETF', ATR_Native=1, Date='2026-10-05')


def render_sections(rows):
    """Real renderer sections, without unrelated AI calls/network/state writes."""
    source = Path(scanner.__file__).read_text()
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'generate_html_dashboard')
    def assigns(n, name):
        return isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)
    scope = dict(vars(scanner), portfolio_df=pd.DataFrame(rows), watchlist_df=pd.DataFrame(),
                 orders_df=pd.DataFrame(), dashboard_rates={'RON': 0.2})
    for begin, end in [('portfolio_rows_html', 'ticker_lookup'),
                       ('portfolio_detail_data', 'portfolio_payload')]:
        start = next(i for i,n in enumerate(function.body) if assigns(n, begin))
        # Each section contains setup assignments followed by its actual row loop.
        loop = next(i for i in range(start, len(function.body)) if isinstance(function.body[i], ast.For))
        exec(compile(ast.Module(body=function.body[start:loop+1], type_ignores=[]),
                     '<portfolio-renderer>', 'exec'), scope)
    return scope


def test_renderer_keeps_two_rows_and_their_own_chart_details():
    from bs4 import BeautifulSoup
    first, second = position('First',130,11), position('Second',654,10)
    result = render_sections([first, second])
    soup = BeautifulSoup(result['portfolio_rows_html'], 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == 2
    assert len({r['id'] for r in rows}) == 2
    assert 'Tradeville · First' in rows[0].get_text()
    assert 'Tradeville · Second' in rows[1].get_text()
    assert [r['data-shares'] for r in rows] == ['130','654']
    details = result['portfolio_detail_data']
    assert len(details) == 2
    assert '130 acțiuni' in details[position_key(first)]['explanation']
    assert '654 acțiuni' in details[position_key(second)]['explanation']
    assert details[position_key(first)]['levels'][0]['value'] == 55
    assert details[position_key(second)]['levels'][0]['value'] == 50


def test_identity_survives_csv_lowercase_and_account_rename():
    item = position('First',130,11)
    lower = {k.lower():v for k,v in item.items()}
    assert position_key(item) == position_key(lower)
    assert ownership(lower)['Account_ID'] == 'First'
    assert position_key(item) == position_key(dict(item, Account='Renamed'))
    assert position_key(item) != position_key(dict(item, Account_ID='Second'))


def test_history_and_orders_do_not_cross_accounts():
    first, second = position('First',130,11), position('Second',654,10)
    old = dict(first, Chart_History=[1,2,3,4], Chart_Dates=['a','b','c','d'])
    updated = scanner._preserve_portfolio_chart_history([old], [second])
    assert updated[0]['Chart_History'] == [10,11,12]
    assert not same_owner(first, second)
    assert not same_owner(first, {'Broker':'IBKR'})
    assert same_owner(first, {'Order_Source':'Tradeville WebSocket', 'Account_ID':'First'})
    assert not same_owner(second, {'Order_Source':'Tradeville WebSocket', 'Account_ID':'First'})


def test_manual_stop_is_not_suppressed_by_other_account_order(tmp_path):
    first, second = position('First',130,11), position('Second',654,10)
    path = tmp_path/'tradeville.csv'
    pd.DataFrame([dict(first, Trail_Stop=55), dict(second, Trail_Stop=54)]).to_csv(path,index=False)
    orders = pd.DataFrame([dict(first, Action='SELL')])
    result = scanner._tradeville_stop_orders_from_portfolio(path, orders)
    assert result['Account_ID'].tolist() == ['Second']
    assert result['Total_Qty'].tolist() == [654]


def test_orders_and_buy_levels_are_account_scoped():
    first, second = position('First',130,11), position('Second',654,10)
    orders = pd.DataFrame([dict(first, Action='SELL'), dict(second, Action='SELL')])
    kept = scanner._filter_orders_against_current_positions(orders, pd.DataFrame([second]))
    assert kept['Account_ID'].tolist() == ['Second']
    buys = pd.DataFrame([dict(first, Action='BUY', OrderType='LMT', Limit_Price=55),
                         dict(second, Action='BUY', OrderType='LMT', Limit_Price=50)])
    levels = scanner._build_active_buy_order_chart_levels(buys)
    assert levels[position_key(first)][0]['value'] == 55
    assert levels[position_key(second)][0]['value'] == 50


def test_order_detail_javascript_never_borrows_another_account():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for the dashboard JavaScript regression test')
    source = Path(scanner.__file__).read_text()
    start = source.index('async function detailForActiveBuyOrder(')
    end = source.index('async function openOrderDetail(', start)
    script = """
const assert = require('node:assert/strict');
const portfolioDetailData = {
    FIRST: {account: 'First', levels: [{value: 55}]},
    SECOND: {account: 'Second', levels: [{value: 50}]},
    TVBETETF: {account: 'Legacy IBKR', levels: [{value: 99}]}
};
const buyRecommendationDetailData = {};
const activeBuyOrderLevels = {
    FIRST: [{value: 54}], SECOND: [{value: 49}], NEW: [{value: 48}]
};
async function ensureWatchlistDetailsLoaded() {
    return {TVBETETF: {account: 'Market', levels: []}};
}
""" + source[start:end] + """
(async () => {
    const first = await detailForActiveBuyOrder('TVBETETF', 'FIRST');
    const second = await detailForActiveBuyOrder('TVBETETF', 'SECOND');
    const fresh = await detailForActiveBuyOrder('TVBETETF', 'NEW');
    assert.equal(first.account, 'First');
    assert.deepEqual(first.levels.map(x => x.value), [55, 54]);
    assert.equal(second.account, 'Second');
    assert.deepEqual(second.levels.map(x => x.value), [50, 49]);
    assert.equal(fresh.account, 'Market');
    assert.deepEqual(fresh.levels.map(x => x.value), [48]);
    assert.equal((await detailForActiveBuyOrder('TVBETETF')).account, 'Legacy IBKR');
    assert.equal((await detailForActiveBuyOrder('TVBETETF', 'NO_BUY')).account, 'Market');
    assert.deepEqual(portfolioDetailData.FIRST.levels, [{value: 55}]);
})().catch(error => { console.error(error); process.exit(1); });
"""
    result = subprocess.run([node, '-e', script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
