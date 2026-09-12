# Shadow validation storage

Enhanced Scoring and Technical Events remain immutable shadow systems. Their
historical snapshots can be stored as date-partitioned Parquet objects in a
private Cloudflare R2 bucket. Git continues to contain only the dashboard and
compact aggregate reports after the one-time migration is verified.

## R2 configuration

Create an R2 bucket and an R2 API token restricted to object read/write for
that bucket. The scanner reuses the existing `CLOUDFLARE_ACCOUNT_ID` and the
canonical bucket `market-scanner-shadow`. Configure only the R2 S3 credentials
locally in `.shadow_r2_env`:

```bash
export SHADOW_R2_ACCESS_KEY_ID="..."
export SHADOW_R2_SECRET_ACCESS_KEY="..."
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
