from unittest.mock import patch

import pytest

import tradeville_bridge as bridge
from tests.test_tradeville_bridge import sample_snapshot


def enriched_snapshot():
    snapshot = sample_snapshot()
    snapshot['enrichment_version'] = 1
    for index, account in enumerate(snapshot['accounts']):
        account['portfolio'] = [{'simbol':'TVBETETF', 'sold':100, 'valuta':'RON', 'ppiata':57}]
        account['orders'] = [{'idord':'C1', 'simbol':'TVBETETF', 'csauv':'V',
                              'tipord':'P', 'cant':-100, 'cantr':-100, 'pret':0, 'stare':'I', 'valuta':'RON'}]
        account['order_details'] = [{'idord':'C1', 'simbol':'TVBETETF', 'obs':f'P<{54 + index}; protectie',
                                     'data':'2026-10-07T18:40:00Z'}]
        account['transactions_request'] = {'complete':True, 'starts_at':'2025-09-16'}
        account['transactions'] = [{'simbol':'TVBETETF','op':'cump','cant':100,
                                    'data':f'2026-09-0{index + 1}T10:00:00Z'}]
    return snapshot


def positions(snapshot):
    with patch.object(bridge, '_existing_overlays', return_value={}):
        return bridge._position_records(snapshot)


def test_conditional_stops_and_entry_dates_are_separate_per_account():
    snapshot = enriched_snapshot()
    orders = bridge._order_records(snapshot)
    assert [o['Stop_Price'] for o in orders] == [54,55]
    assert [o['Total_Qty'] for o in orders] == [100,100]
    assert [o['OrderType'] for o in orders] == ['STP','STP']
    rows = positions(snapshot)
    assert [r['Trail_Stop'] for r in rows] == [54,55]
    assert [r['Trail_Pct'] for r in rows] == [0,0]  # A fixed stop is not trailing.
    assert [r['Entry_Date'] for r in rows] == ['2026-09-01','2026-09-02']


@pytest.mark.parametrize('condition', ['P>60','D2026-10-12','E12345','P<bad','P<0','P<54 OR P>60',''])
def test_non_protective_or_unknown_conditions_do_not_become_stop_loss(condition):
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['order_details'][0]['obs'] = condition
    assert bridge._order_records(snapshot)[0]['Stop_Price'] == 0
    assert positions(snapshot)[0]['Trail_Stop'] == 0


def test_unknown_detail_does_not_join_by_symbol_or_leak_to_other_account():
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['order_details'][0]['idord'] = 'C_OTHER'
    assert positions(snapshot)[0]['Trail_Stop'] == 0
    assert positions(snapshot)[1]['Trail_Stop'] == 55


def test_partial_stop_does_not_claim_protection_for_entire_position():
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['orders'][0]['cantr'] = -30
    assert bridge._order_records(snapshot)[0]['Total_Qty'] == 30
    assert positions(snapshot)[0]['Trail_Stop'] == 0


def test_buy_history_reconstructs_current_cycle_not_an_old_closed_position():
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['transactions'] = [
        {'simbol':'TVBETETF','op':'cump','cant':10,'data':'2025-10-01'},
        {'simbol':'TVBETETF','op':'vanz','cant':-10,'data':'2025-10-02'},
        {'simbol':'TVBETETF','op':'cump','cant':70,'data':'2026-09-03'},
        {'simbol':'TVBETETF','op':'vanz','cant':-20,'data':'2026-09-04'},
        {'simbol':'TVBETETF','op':'cump','cant':50,'data':'2026-09-05'},
    ]
    assert positions(snapshot)[0]['Entry_Date'] == '2026-09-03'


@pytest.mark.parametrize('problem', ['incomplete','missing_buys','transfer','future','invalid_date'])
def test_inconsistent_history_leaves_entry_date_unknown(problem):
    snapshot = enriched_snapshot()
    account = snapshot['accounts'][0]
    if problem == 'incomplete':
        account['transactions_request']['complete'] = False
    elif problem == 'missing_buys':
        account['transactions'][0]['cant'] = 20
    elif problem == 'transfer':
        account['transactions'][0]['op'] = 'transfer'
    elif problem == 'future':
        account['transactions'][0]['data'] = '2099-01-01'
    else:
        account['transactions'][0]['data'] = '2026-02-31'
    assert positions(snapshot)[0]['Entry_Date'] == ''


def test_cancelled_details_and_different_symbol_never_supply_a_stop():
    for update in [{'stare':status} for status in ['A','S','G','P','F','T','E']] + [{'simbol':'SNP'}, {'laex':0}]:
        snapshot = enriched_snapshot()
        snapshot['accounts'][0]['order_details'][0].update(update)
        assert positions(snapshot)[0]['Trail_Stop'] == 0


def test_detail_remaining_quantity_takes_precedence_over_older_active_list():
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['order_details'][0]['cantr'] = 25
    assert bridge._order_records(snapshot)[0]['Total_Qty'] == 25
    assert positions(snapshot)[0]['Trail_Stop'] == 0


@pytest.mark.parametrize('entry_date', ['2026-10-05', ''])
def test_broker_dates_and_stops_survive_portfolio_merge_and_render(tmp_path, monkeypatch, entry_date):
    import pandas as pd
    import ib_sync
    from tests.test_portfolio_accounts import position, render_sections
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GITHUB_ACTIONS', 'false')
    snapshot = enriched_snapshot()
    rows = positions(snapshot)
    rows[0]['Entry_Date'] = entry_date
    pd.DataFrame(rows).to_csv('tradeville_portfolio.csv', index=False)
    old = [dict(row, Entry_Date='2020-01-01') for row in rows]
    pd.DataFrame(old).to_csv('portfolio.csv', index=False)
    assert ib_sync.sync_ibkr(allow_flex=False)
    saved = pd.read_csv('portfolio.csv', keep_default_na=False)
    first = saved[saved.Account == 'Personal'].iloc[0]
    assert first.Entry_Date == entry_date
    assert first.Trail_Stop == 54
    # Exercise actual portfolio table rendering using the scanner's EUR unit convention.
    rendered = position('Personal', 100, 10)
    rendered.update(Entry_Date=first.Entry_Date or '-', Trail_Stop=first.Trail_Stop * 0.2)
    html = render_sections([rendered])['portfolio_rows_html']
    assert '€10.80' in html
    if entry_date:
        assert entry_date in html


def test_live_enrichment_cannot_reuse_stale_overlay_stops_or_dates():
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['orders'] = []
    snapshot['accounts'][0]['transactions'] = []
    overlays = {('Personal','TVBETETF'):{'Trail_Stop':56,'Trail_Pct':8,'Entry_Date':'2020-01-01'}}
    with patch.object(bridge, '_existing_overlays', return_value=overlays):
        row = bridge._position_records(snapshot)[0]
    assert row['Trail_Stop'] == 0
    assert row['Entry_Date'] == ''
    assert row['Trail_Pct'] == 0


def test_sync_reports_old_extension_and_optional_data_failures(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    snapshot = sample_snapshot()
    status = bridge.persist_snapshot(snapshot)
    assert status['enrichment_warning_count'] > 0
    snapshot = enriched_snapshot()
    snapshot['accounts'][0]['enrichment_errors'] = ['activit_timeout']
    status = bridge.persist_snapshot(snapshot)
    assert status['enrichment_warning_count'] == 1
    assert status['entry_date_count'] == 2
    assert status['protected_position_count'] == 2
