"""Immutable Parquet storage for shadow-validation snapshots on Cloudflare R2.

The scanner keeps its local ledgers as a crash-safe write-ahead fallback.  When
R2 credentials are configured, every snapshot is also written as one immutable
Parquet object.  Objects are partitioned by dataset and UTC calendar date, so
new runs never rewrite historical data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import io
import json
import os
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import requests


ENHANCED_DATASET = "enhanced-scoring"
TECHNICAL_DATASET = "technical-events"
KNOWN_DATASETS = {ENHANCED_DATASET, TECHNICAL_DATASET}
SPOOL_DIR = Path(".shadow_parquet_spool")
DEFAULT_PREFIX = "market-scanner-shadow/v1"
DEFAULT_BUCKET = "market-scanner-shadow"


@dataclass(frozen=True)
class R2Config:
    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket: str
    endpoint: str
    prefix: str = DEFAULT_PREFIX
    required: bool = False

    @classmethod
    def from_env(cls):
        values = {
            "account_id": (
                os.environ.get("SHADOW_R2_ACCOUNT_ID", "").strip()
                or os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
            ),
            "access_key_id": os.environ.get("SHADOW_R2_ACCESS_KEY_ID", "").strip(),
            "secret_access_key": os.environ.get(
                "SHADOW_R2_SECRET_ACCESS_KEY", ""
            ).strip(),
            "bucket": (
                os.environ.get("SHADOW_R2_BUCKET", "").strip()
                or DEFAULT_BUCKET
            ),
        }
        # R2 is opt-in through its dedicated S3 credentials. The Cloudflare
        # account id may already exist for Workers, without enabling R2.
        if not values["access_key_id"] and not values["secret_access_key"]:
            return None
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ValueError(
                "Configurație R2 incompletă; lipsesc: " + ", ".join(missing)
            )
        endpoint = os.environ.get("SHADOW_R2_ENDPOINT", "").strip()
        endpoint = endpoint or (
            f"https://{values['account_id']}.r2.cloudflarestorage.com"
        )
        return cls(
            **values,
            endpoint=endpoint.rstrip("/"),
            prefix=(
                os.environ.get("SHADOW_R2_PREFIX", DEFAULT_PREFIX).strip("/")
                or DEFAULT_PREFIX
            ),
            required=os.environ.get("SHADOW_R2_REQUIRED", "").casefold()
            in {"1", "true", "yes", "on"},
        )


def is_configured():
    return R2Config.from_env() is not None


def _utc_timestamp(value):
    parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def object_key(dataset, snapshot, *, prefix=DEFAULT_PREFIX):
    if dataset not in KNOWN_DATASETS:
        raise ValueError(f"Dataset shadow necunoscut: {dataset}")
    timestamp = _utc_timestamp(snapshot["recorded_at"])
    snapshot_id = str(snapshot.get("snapshot_id") or "").strip()
    if not snapshot_id:
        raise ValueError("Snapshotul nu are snapshot_id")
    stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    root = f"{prefix.strip('/')}/" if prefix.strip("/") else ""
    return (
        f"{root}{dataset}/year={timestamp:%Y}/month={timestamp:%m}/"
        f"day={timestamp:%d}/{stamp}-{snapshot_id}.parquet"
    )


def _duckdb():
    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover - exercised in deployment
        raise RuntimeError(
            "Lipsește dependența duckdb; rulează pip install -r requirements.txt"
        ) from exc
    return duckdb


def write_snapshot_parquet(snapshot, dataset, destination):
    """Write one immutable, analytics-ready snapshot as a ZSTD Parquet partition."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata = dict(snapshot)
    predictions = metadata.pop("predictions", []) or []
    metadata_json = json.dumps(
        metadata, separators=(",", ":"), ensure_ascii=False
    )
    rows = []
    for index, prediction in enumerate(predictions or [None]):
        prediction = prediction or {}
        options = prediction.get("options") or {}
        if not isinstance(options, dict):
            options = {}
        rows.append((
            dataset,
            snapshot.get("schema"),
            snapshot.get("snapshot_id"),
            snapshot.get("recorded_at"),
            snapshot.get("run_mode"),
            snapshot.get("content_hash"),
            int(snapshot.get("candidate_count") or 0),
            metadata_json,
            index,
            prediction.get("symbol") or prediction.get("ticker"),
            prediction.get("baseline_score"),
            prediction.get("baseline_decision"),
            prediction.get("raw_score", prediction.get("enhanced_raw_score")),
            prediction.get("portfolio_fit_observed"),
            prediction.get(
                "adjusted_score_formula", prediction.get("enhanced_adjusted_score")
            ),
            prediction.get("enhanced_decision_shadow", prediction.get("enhanced_decision")),
            options.get("cohort"),
            options.get("data_available"),
            options.get("data_partial"),
            options.get("formula_score"),
            prediction.get("technical_events_score"),
            prediction.get("technical_events_direction"),
            prediction.get("technical_events_confidence"),
            json.dumps(prediction, separators=(",", ":"), ensure_ascii=False)
            if prediction else None,
        ))
    duckdb = _duckdb()
    connection = duckdb.connect(database=":memory:")
    try:
        connection.execute(
            """
            CREATE TABLE shadow_snapshot (
                dataset VARCHAR NOT NULL,
                schema_version VARCHAR,
                snapshot_id VARCHAR NOT NULL,
                recorded_at TIMESTAMPTZ NOT NULL,
                run_mode VARCHAR,
                content_hash VARCHAR,
                candidate_count BIGINT,
                snapshot_meta_json VARCHAR NOT NULL,
                prediction_index BIGINT NOT NULL,
                ticker VARCHAR,
                baseline_score DOUBLE,
                baseline_decision VARCHAR,
                enhanced_raw_score DOUBLE,
                portfolio_fit DOUBLE,
                adjusted_score DOUBLE,
                enhanced_decision VARCHAR,
                options_status VARCHAR,
                options_available BOOLEAN,
                options_partial BOOLEAN,
                options_score DOUBLE,
                technical_events_score DOUBLE,
                technical_events_direction VARCHAR,
                technical_events_confidence DOUBLE,
                prediction_json VARCHAR
            )
            """
        )
        connection.executemany(
            "INSERT INTO shadow_snapshot VALUES ("
            + ",".join(["?"] * 24)
            + ")",
            rows,
        )
        escaped = str(destination.resolve()).replace("'", "''")
        connection.execute(
            f"COPY shadow_snapshot TO '{escaped}' "
            "(FORMAT PARQUET, COMPRESSION ZSTD)"
        )
    finally:
        connection.close()
    return destination


def read_snapshot_parquet(source):
    duckdb = _duckdb()
    escaped = str(Path(source).resolve()).replace("'", "''")
    connection = duckdb.connect(database=":memory:")
    try:
        rows = connection.execute(
            f"SELECT snapshot_meta_json, prediction_json "
            f"FROM read_parquet('{escaped}') ORDER BY prediction_index"
        ).fetchall()
    finally:
        connection.close()
    if not rows:
        raise ValueError(f"Partiție Parquet goală: {source}")
    snapshot = json.loads(rows[0][0])
    snapshot["predictions"] = [
        json.loads(prediction_json)
        for _, prediction_json in rows
        if prediction_json is not None
    ]
    return snapshot


class R2Client:
    """Small SigV4 S3 client covering the R2 operations used by the scanner."""

    def __init__(self, config, *, session=None):
        self.config = config
        self.session = session or requests.Session()

    @staticmethod
    def _sign(key, message):
        return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()

    def _request(self, method, key="", *, params=None, body=b"", headers=None):
        params = params or {}
        body = body or b""
        now = dt.datetime.now(dt.timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")
        endpoint = urllib.parse.urlsplit(self.config.endpoint)
        path_parts = [self.config.bucket]
        if key:
            path_parts.append(key.lstrip("/"))
        canonical_uri = "/" + "/".join(
            urllib.parse.quote(part, safe="-_.~/") for part in path_parts
        )
        query_items = []
        for name, value in sorted(params.items()):
            query_items.append(
                f"{urllib.parse.quote(str(name), safe='-_.~')}="
                f"{urllib.parse.quote(str(value), safe='-_.~')}"
            )
        canonical_query = "&".join(query_items)
        payload_hash = hashlib.sha256(body).hexdigest()
        signed = {
            "host": endpoint.netloc,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
        }
        canonical_headers = "".join(
            f"{name}:{value.strip()}\n" for name, value in sorted(signed.items())
        )
        signed_headers = ";".join(sorted(signed))
        canonical_request = "\n".join(
            [method, canonical_uri, canonical_query, canonical_headers,
             signed_headers, payload_hash]
        )
        scope = f"{date_stamp}/auto/s3/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256", amz_date, scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])
        date_key = self._sign(
            ("AWS4" + self.config.secret_access_key).encode("utf-8"), date_stamp
        )
        region_key = self._sign(date_key, "auto")
        service_key = self._sign(region_key, "s3")
        signing_key = self._sign(service_key, "aws4_request")
        signature = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        request_headers = dict(headers or {})
        request_headers.update(signed)
        request_headers["Authorization"] = (
            "AWS4-HMAC-SHA256 "
            f"Credential={self.config.access_key_id}/{scope},"
            f"SignedHeaders={signed_headers},Signature={signature}"
        )
        url = self.config.endpoint + canonical_uri
        if canonical_query:
            url += "?" + canonical_query
        # Large runtime artifacts can take more than 90 seconds to upload on a
        # slow uplink.  Keep the normal timeout for metadata and immutable
        # snapshots, but allow bulk PUTs enough time to finish.
        timeout = 600 if method == "PUT" and len(body) >= 5 * 1024 * 1024 else 90
        response = self.session.request(
            method, url, data=body, headers=request_headers, timeout=timeout
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"R2 {method} {key or self.config.bucket}: "
                f"HTTP {response.status_code} {response.text[:300]}"
            )
        return response

    def exists(self, key):
        try:
            self._request("HEAD", key)
            return True
        except RuntimeError as exc:
            if "HTTP 404" in str(exc):
                return False
            raise

    def _multipart_put(self, key, content, content_type):
        import boto3
        from boto3.s3.transfer import TransferConfig
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=self.config.endpoint,
            aws_access_key_id=self.config.access_key_id,
            aws_secret_access_key=self.config.secret_access_key,
            region_name="auto",
            config=Config(
                connect_timeout=30,
                read_timeout=600,
                retries={"max_attempts": 5, "mode": "adaptive"},
                s3={"addressing_style": "path"},
                tcp_keepalive=True,
            ),
        )
        client.upload_fileobj(
            io.BytesIO(content),
            self.config.bucket,
            key,
            ExtraArgs={"ContentType": content_type},
            Config=TransferConfig(
                multipart_threshold=4 * 1024 * 1024,
                multipart_chunksize=5 * 1024 * 1024,
                max_concurrency=1,
                use_threads=False,
            ),
        )
        return client.head_object(Bucket=self.config.bucket, Key=key)

    def put(self, key, content, *, content_type="application/vnd.apache.parquet"):
        if len(content) >= 4 * 1024 * 1024 and isinstance(
            self.session, requests.Session
        ):
            return self._multipart_put(key, content, content_type)
        last_error = None
        for _attempt in range(3):
            try:
                return self._request(
                    "PUT", key, body=content,
                    headers={"content-type": content_type},
                )
            except requests.RequestException as exc:
                last_error = exc
                # R2 may persist the complete object and close the connection
                # before the client receives the response.  A successful HEAD
                # makes the retry idempotent and avoids another large upload.
                try:
                    return self._request("HEAD", key)
                except (requests.RequestException, RuntimeError):
                    continue
        raise last_error

    def get(self, key):
        return self._request("GET", key).content

    def delete(self, key):
        return self._request("DELETE", key)

    def list_keys(self, prefix):
        keys = []
        token = None
        while True:
            params = {"list-type": "2", "prefix": prefix}
            if token:
                params["continuation-token"] = token
            root = ET.fromstring(self._request("GET", params=params).content)
            keys.extend(
                node.text for node in root.findall(".//{*}Contents/{*}Key")
                if node.text
            )
            truncated = (
                root.findtext(".//{*}IsTruncated", default="false").casefold()
                == "true"
            )
            if not truncated:
                break
            token = root.findtext(".//{*}NextContinuationToken")
            if not token:
                raise RuntimeError("R2 list response trunchiat fără continuation token")
        return sorted(keys)


def _spool_path(dataset, snapshot):
    key = object_key(dataset, snapshot, prefix="")
    return SPOOL_DIR / key


def persist_snapshot(snapshot, dataset, *, config=None, client=None):
    """Persist a snapshot to R2; retries are safe because object keys are stable."""
    config = config if config is not None else R2Config.from_env()
    if config is None:
        return {"status": "DISABLED", "dataset": dataset, "key": None}
    client = client or R2Client(config)
    key = object_key(dataset, snapshot, prefix=config.prefix)
    spool = _spool_path(dataset, snapshot)
    write_snapshot_parquet(snapshot, dataset, spool)
    stored = False
    try:
        stored = client.exists(key)
        if not stored:
            client.put(key, spool.read_bytes())
            stored = True
        return {"status": "STORED", "dataset": dataset, "key": key}
    finally:
        # Keep failed uploads in the spool for an explicit retry.
        if stored:
            spool.unlink(missing_ok=True)


def _download_snapshot(client, key):
    descriptor, temporary = tempfile.mkstemp(suffix=".parquet")
    os.close(descriptor)
    target = Path(temporary)
    try:
        target.write_bytes(client.get(key))
        return read_snapshot_parquet(target)
    finally:
        target.unlink(missing_ok=True)


def load_snapshots(dataset, *, config=None, client=None):
    config = config if config is not None else R2Config.from_env()
    if config is None:
        return []
    client = client or R2Client(config)
    prefix = f"{config.prefix.strip('/')}/{dataset}/"
    rows = [_download_snapshot(client, key) for key in client.list_keys(prefix)]
    unique = {row.get("snapshot_id"): row for row in rows}
    return sorted(
        unique.values(), key=lambda row: (row.get("recorded_at", ""), row.get("snapshot_id", ""))
    )


def latest_snapshot_and_ids(dataset, *, config=None, client=None):
    """Return the latest snapshot and the immutable IDs present in R2."""
    config = config if config is not None else R2Config.from_env()
    if config is None:
        return None, set()
    client = client or R2Client(config)
    prefix = f"{config.prefix.strip('/')}/{dataset}/"
    keys = client.list_keys(prefix)
    snapshot_ids = {
        key.rsplit("/", 1)[-1].removesuffix(".parquet").split("-", 1)[-1]
        for key in keys
        if key.endswith(".parquet") and "-" in key.rsplit("/", 1)[-1]
    }
    latest = _download_snapshot(client, keys[-1]) if keys else None
    return latest, snapshot_ids


def latest_snapshot(dataset, *, config=None, client=None):
    latest, _snapshot_ids = latest_snapshot_and_ids(
        dataset, config=config, client=client
    )
    return latest


def persist_optional(snapshot, dataset):
    """Store when configured; fail closed only when SHADOW_R2_REQUIRED is set."""
    config = R2Config.from_env()
    if config is None:
        return {"status": "DISABLED", "dataset": dataset, "key": None}
    try:
        result = persist_snapshot(snapshot, dataset, config=config)
        print(f"[Shadow R2] {dataset}: {result['key']}")
        return result
    except Exception as exc:
        if config.required:
            raise
        print(f"[Shadow R2] Avertisment {dataset}: {exc}")
        return {"status": "PENDING_RETRY", "dataset": dataset, "error": str(exc)}


def flush_spool():
    config = R2Config.from_env()
    if config is None or not SPOOL_DIR.exists():
        return 0
    completed = 0
    for parquet in sorted(SPOOL_DIR.rglob("*.parquet")):
        relative = parquet.relative_to(SPOOL_DIR)
        dataset = relative.parts[0] if relative.parts else ""
        if dataset not in KNOWN_DATASETS:
            continue
        snapshot = read_snapshot_parquet(parquet)
        persist_snapshot(snapshot, dataset, config=config)
        completed += 1
    if completed:
        print(f"[Shadow R2] Retry finalizat: {completed} partiții")
    return completed


def migrate_existing():
    if not is_configured():
        raise SystemExit("R2 nu este configurat; setează variabilele SHADOW_R2_*")
    import shadow_validation
    import technical_events_shadow

    counts = {}
    datasets = (
        (ENHANCED_DATASET, shadow_validation.load_local_ledger()),
        (TECHNICAL_DATASET, technical_events_shadow.load_local_ledger()),
    )
    for dataset, snapshots in datasets:
        for snapshot in snapshots:
            persist_snapshot(snapshot, dataset)
        counts[dataset] = len(snapshots)
        print(f"Migrat {dataset}: {len(snapshots)} snapshoturi")
    return counts


def verify_migration():
    if not is_configured():
        raise SystemExit("R2 nu este configurat; setează variabilele SHADOW_R2_*")
    import shadow_validation
    import technical_events_shadow

    checks = {}
    datasets = (
        (ENHANCED_DATASET, shadow_validation.load_local_ledger()),
        (TECHNICAL_DATASET, technical_events_shadow.load_local_ledger()),
    )
    for dataset, local_rows in datasets:
        remote_rows = load_snapshots(dataset)
        local_ids = {row.get("snapshot_id") for row in local_rows}
        remote_ids = {row.get("snapshot_id") for row in remote_rows}
        missing = sorted(local_ids - remote_ids)
        checks[dataset] = {
            "local": len(local_ids),
            "remote": len(remote_ids),
            "missing": len(missing),
        }
        print(json.dumps({dataset: checks[dataset]}, ensure_ascii=False))
        if missing:
            raise RuntimeError(
                f"Migrare incompletă pentru {dataset}: {len(missing)} snapshoturi lipsă"
            )
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("status", "probe", "migrate", "verify", "flush"),
        nargs="?", default="status",
    )
    args = parser.parse_args()
    if args.command == "migrate":
        migrate_existing()
        return
    if args.command == "verify":
        verify_migration()
        return
    if args.command == "flush":
        flush_spool()
        return
    if args.command == "probe":
        config = R2Config.from_env()
        if config is None:
            raise SystemExit("R2 nu este configurat; setează variabilele SHADOW_R2_*")
        client = R2Client(config)
        counts = {
            dataset: len(client.list_keys(f"{config.prefix}/{dataset}/"))
            for dataset in sorted(KNOWN_DATASETS)
        }
        print(json.dumps({
            "connected": True,
            "bucket": config.bucket,
            "objects": counts,
        }, indent=2))
        return
    config = R2Config.from_env()
    print(json.dumps({
        "configured": config is not None,
        "bucket": config.bucket if config else None,
        "prefix": config.prefix if config else None,
        "required": config.required if config else False,
    }, indent=2))


if __name__ == "__main__":
    main()
