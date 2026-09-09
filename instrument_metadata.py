"""Canonical instrument metadata shared by scanner data paths.

Contract metadata resolved by IBKR ``search_contracts`` is authoritative.
Local fields and listing suffixes are used only when that metadata is absent.
No symbol allow-list is maintained here.
"""

from __future__ import annotations

from typing import Any


US_EXCHANGES = {
    "AMEX", "ARCA", "BATS", "IEX", "NASDAQ", "NYSE", "SMART",
}
EUROPEAN_SUFFIX_COUNTRIES = {
    ".RO": "RO", ".PA": "FR", ".DE": "DE", ".AS": "NL",
    ".L": "GB", ".MI": "IT", ".MC": "ES", ".BR": "BE",
    ".SW": "CH",
}
COUNTRY_CURRENCIES = {
    "US": "USD", "RO": "RON", "FR": "EUR", "DE": "EUR",
    "NL": "EUR", "IT": "EUR", "ES": "EUR", "BE": "EUR",
    "GB": "GBP", "CH": "CHF",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _symbol(item: dict[str, Any]) -> str:
    return _text(
        item.get("Ticker") or item.get("Symbol") or item.get("symbol")
    ).upper()


def _suffix_country(symbol: str) -> str | None:
    for suffix, country in EUROPEAN_SUFFIX_COUNTRIES.items():
        if symbol.endswith(suffix):
            return country
    # The scanner's canonical symbol convention uses an explicit suffix for
    # non-US listings. An unqualified listed equity is therefore US-listed.
    return "US" if symbol and "." not in symbol else None


def _security_type(item: dict[str, Any], contract: dict[str, Any]) -> str:
    value = _text(
        contract.get("security_type")
        or item.get("Security_Type")
        or item.get("security_type")
        or item.get("Asset_Class")
        or item.get("instrument_type")
    ).upper()
    if value in {"ETF", "FUND"}:
        return "FUND"
    return value or "STK"


def _market(country: str, exchange: str) -> str | None:
    if country == "US" or exchange in US_EXCHANGES:
        return "SUA"
    if country == "RO" or exchange in {"BVB", "BUCHAREST"}:
        return "România / BVB"
    if country:
        return "Europa / Nasdaq-100"
    return None


def canonical_metadata(
    item: dict[str, Any], contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return canonical metadata fields for one instrument observation."""
    contract = contract if isinstance(contract, dict) else {}
    symbol = _symbol(item)
    embedded = item.get("Instrument_Metadata")
    embedded = embedded if isinstance(embedded, dict) else {}
    country = _text(
        contract.get("country_code")
        or embedded.get("country")
        or item.get("Country")
        or item.get("country")
    ).upper() or _suffix_country(symbol)
    exchange = _text(
        contract.get("exchange")
        or embedded.get("exchange")
        or item.get("Exchange")
        or item.get("exchange")
    ).upper()
    if not exchange and country == "RO":
        exchange = "BVB"
    security_type = _security_type(item, contract)
    currency = _text(
        contract.get("currency")
        or embedded.get("currency")
        or item.get("Currency")
        or item.get("currency")
        or COUNTRY_CURRENCIES.get(country or "")
    ).upper()
    contract_id = (
        contract.get("contract_id")
        or embedded.get("contract_id")
        or item.get("Contract_ID")
        or item.get("contract_id")
    )
    sections = contract.get("sections") or embedded.get("sections") or []
    sections = sorted({_text(value).upper() for value in sections if _text(value)})
    source = (
        "IBKR_MCP_SEARCH_CONTRACTS"
        if contract.get("contract_id") else
        _text(embedded.get("source") or item.get("Market_Metadata_Source"))
        or "LOCAL_CANONICAL_SYMBOL"
    )
    result = {
        "market": _market(country or "", exchange),
        "country": country,
        "exchange": exchange or None,
        "security_type": security_type,
        "currency": currency or None,
        "contract_id": contract_id,
        "sections": sections,
        "options_supported": "OPT" in sections if sections else None,
        "source": source,
    }
    return result


def apply_metadata(
    item: dict[str, Any], contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply canonical names while preserving the original observation."""
    result = dict(item)
    metadata = canonical_metadata(result, contract)
    result.update({
        "Market": metadata["market"],
        "Country": metadata["country"],
        "Exchange": metadata["exchange"],
        "Security_Type": metadata["security_type"],
        "Currency": metadata["currency"],
        "Contract_ID": metadata["contract_id"],
        "Market_Metadata_Source": metadata["source"],
        "Options_Supported": metadata["options_supported"],
        "Instrument_Metadata": metadata,
    })
    return result
