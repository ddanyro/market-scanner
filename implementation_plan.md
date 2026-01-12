# Refactoring Plan: Modularize `market_scanner.py`

## Goal

Break down the monolithic `market_scanner.py` (4300+ lines) into manageable, focused modules to improve maintainability, testing, and readability.

## Modules Structure

### 1. `market_utils.py` (Infrastructure)

* **Responsibility**: Helper functions, State Management, Logging configuration (if any), Path constants.
* **Functions to Move**:
  * `load_state()`
  * `save_state()`
  * `get_random_user_agent()` (if extracted)
  * Any caching primitives (though logic might belong in Data).

### 2. `market_security.py` (Security)

* **Responsibility**: Encryption/Decryption logic for frontend JS compatibility.
* **Functions to Move**:
  * `encrypt_for_js(data, password)`
  * Imports: `Crypto` libraries (`AES`, `PBKDF2`, `pad`, etc.)

### 3. `market_data.py` (Data Acquisition)

* **Responsibility**: Fetching data from external sources (Yahoo Finance, Finviz).
* **Functions to Move**:
  * `get_finviz_data(ticker)`
  * `check_market_status()` (Fetching ^GSPC data)
  * `get_cached_watchlist_ticker` (and related cache logic)
  * `is_fresh`

### 4. `market_scanner.py` (Orchestrator)

* **Responsibility**: Main entry point, Argument parsing, High-level loop, Watchlist processing logic.
* **Retained Logic**:
  * `process_watchlist_ticker()` (High-level business logic)
  * `update_watchlist_data()`
  * `main()`

*Note:* `market_scanner_analysis.py` already exists and handles the heavy lifting of Analysis and HTML generation for the specialized "Swing Trading" section. We will continue to leverage it.

## Execution Steps

1. **Create `market_utils.py`**:
    * Extract state functions.
    * Extract constants (STATE_FILE, etc.).

2. **Create `market_security.py`**:
    * Extract `encrypt_for_js`.

3. **Create `market_data.py`**:
    * Extract `get_finviz_data`.
    * Extract cache dictionary (`_finviz_cache`) and related logic.

4. **Update `market_scanner.py`**:
    * Import new modules.
    * Update function calls to use `module.function()`.

5. **Verification**:
    * Run `market_scanner.py` (simulated or real) to check for ImportErrors or logical breaks.
    * Ensure generated HTML is identical.

## User Review Required

* None. This is a refactor without functional changes.
