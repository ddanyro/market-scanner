import instrument_metadata


def test_search_contract_metadata_is_authoritative():
    result = instrument_metadata.apply_metadata(
        {
            'Ticker': 'TEST', 'Market': 'România / BVB',
            'Currency': 'RON', 'Contract_ID': 1,
        },
        {
            'contract_id': 42, 'country_code': 'US', 'exchange': 'NASDAQ',
            'currency': 'USD', 'security_type': 'STK',
            'sections': ['STK', 'OPT'],
        },
    )
    assert result['Market'] == 'SUA'
    assert result['Country'] == 'US'
    assert result['Exchange'] == 'NASDAQ'
    assert result['Currency'] == 'USD'
    assert result['Contract_ID'] == 42
    assert result['Options_Supported'] is True
    assert result['Market_Metadata_Source'] == 'IBKR_MCP_SEARCH_CONTRACTS'


def test_listing_convention_classifies_without_ticker_allow_list():
    bvb = instrument_metadata.apply_metadata({'Ticker': 'ABC.RO'})
    europe = instrument_metadata.apply_metadata({'Ticker': 'ABC.PA'})
    usa = instrument_metadata.apply_metadata({'Ticker': 'ABC'})
    assert (bvb['Market'], bvb['Country'], bvb['Exchange']) == (
        'România / BVB', 'RO', 'BVB',
    )
    assert (europe['Market'], europe['Country']) == (
        'Europa / Nasdaq-100', 'FR',
    )
    assert (usa['Market'], usa['Country']) == ('SUA', 'US')


def test_field_aliases_produce_identical_classification():
    contract = {
        'contract_id': 7, 'country_code': 'US', 'exchange': 'NYSE',
        'security_type': 'STK', 'sections': ['STK', 'OPT'],
    }
    rows = [
        {'Ticker': 'CLS'}, {'Symbol': 'CLS'}, {'symbol': 'CLS'},
    ]
    metadata = [instrument_metadata.canonical_metadata(row, contract) for row in rows]
    assert metadata[0] == metadata[1] == metadata[2]
