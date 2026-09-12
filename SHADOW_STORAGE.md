# Shadow validation storage

Enhanced Scoring and Technical Events remain immutable shadow systems. Their
historical snapshots can be stored as date-partitioned Parquet objects in a
private Cloudflare R2 bucket. Git continues to contain only the dashboard and
compact aggregate reports after the one-time migration is verified.

## R2 configuration

Create an R2 bucket and an R2 API token restricted to object read/write for
that bucket. The scanner uses the canonical bucket `market-scanner-shadow`.
On macOS, configure local access once in Keychain; the prompts do not echo
the values:

```bash
./configure_shadow_r2_keychain.sh
```

All local update scripts load these entries automatically. As a backward-
compatible alternative, configuration may still be supplied in
`.shadow_r2_env`:

```bash
export SHADOW_R2_ACCESS_KEY_ID="..."
export SHADOW_R2_SECRET_ACCESS_KEY="..."
export CLOUDFLARE_ACCOUNT_ID="..."
```

The file is ignored by Git. Add the two R2 credentials as GitHub Actions
Secrets. The workflow reuses the existing `CLOUDFLARE_ACCOUNT_ID` secret;
there is no duplicate account-id or bucket secret for shadow storage.
R2 is required automatically once its two credentials are configured, so an
upload failure stops the collection run instead of silently leaving only the
local crash-safe copy.

## Object layout

Each snapshot is one immutable ZSTD Parquet object:

```text
market-scanner-shadow/v1/<dataset>/year=YYYY/month=MM/day=DD/
  YYYYMMDDTHHMMSSZ-<snapshot_id>.parquet
```

Datasets are `enhanced-scoring` and `technical-events`. Re-running an upload is
idempotent because the content-addressed snapshot ID is part of the key.

## Migration

After exporting the environment variables, migrate all existing local ledgers:

```bash
python shadow_parquet_store.py migrate
python shadow_parquet_store.py verify
```

Run the existing validation reports once and compare their sample counts before
removing legacy ledger files from Git tracking. The application merges R2 and
local snapshots by `snapshot_id` during the transition.

## Runtime artifacts

The same private bucket stores versioned gzip copies of the large runtime
artifacts under `market-scanner-runtime/v1/`. Each update restores the private
state and IBKR cache, generates the dashboard, uploads immutable versions, and
then atomically replaces the manifest that points to the current set:

- `dashboard-state` — private scanner state, restored before a run;
- `ibkr-market-cache` — private reusable IBKR cache, restored before a run;
- `watchlist-compact` — public dashboard payload served through the Worker;
- `dashboard-html` — public generated dashboard served through the Worker.

R2 remains private. The Cloudflare Worker exposes only the last two named
artifacts; it never exposes state or the IBKR cache. After migration, GitHub
Pages contains only a small dashboard loader.

Useful integrity checks after loading the Keychain configuration:

```bash
python runtime_r2_store.py push
python runtime_r2_store.py pull
python runtime_r2_store.py verify
```
