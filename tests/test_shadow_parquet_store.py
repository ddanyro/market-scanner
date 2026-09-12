import pytest
import requests

import shadow_parquet_store as store


def snapshot(snapshot_id="abc123", recorded_at="2026-09-12T05:30:00+00:00"):
    return {
        "schema": "market-scanner.shadow-prediction.v3",
        "snapshot_id": snapshot_id,
        "recorded_at": recorded_at,
        "run_mode": "portfolio",
        "content_hash": "f" * 64,
        "candidate_count": 1,
        "predictions": [{"symbol": "NVDA", "raw_score": 78.2}],
    }


def config(tmp_path=None):
    return store.R2Config(
        account_id="account",
        access_key_id="access",
        secret_access_key="secret",
        bucket="shadow",
        endpoint="https://account.r2.cloudflarestorage.com",
        prefix="scanner/v1",
        required=True,
    )


class FakeClient:
    def __init__(self):
        self.objects = {}
        self.put_count = 0

    def exists(self, key):
        return key in self.objects

    def put(self, key, content):
        self.put_count += 1
        self.objects[key] = content

    def get(self, key):
        return self.objects[key]

    def list_keys(self, prefix):
        return sorted(key for key in self.objects if key.startswith(prefix))


class FakeResponse:
    status_code = 200
    text = ""
    content = b""


class RecordingSession:
    def __init__(self):
        self.request_data = None

    def request(self, method, url, data, headers, timeout):
        self.request_data = (method, url, data, headers, timeout)
        return FakeResponse()


class StoredThenDisconnectedSession:
    def __init__(self):
        self.methods = []

    def request(self, method, url, data, headers, timeout):
        self.methods.append(method)
        if method == "PUT":
            raise requests.ConnectionError("response lost")
        return FakeResponse()


def test_r2_config_is_disabled_when_no_values(monkeypatch):
    for name in (
        "SHADOW_R2_ACCOUNT_ID", "SHADOW_R2_ACCESS_KEY_ID",
        "SHADOW_R2_SECRET_ACCESS_KEY", "SHADOW_R2_BUCKET",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    assert store.R2Config.from_env() is None


def test_r2_config_reuses_cloudflare_account_and_default_bucket(monkeypatch):
    monkeypatch.delenv("SHADOW_R2_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("SHADOW_R2_BUCKET", raising=False)
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "existing-account")
    monkeypatch.setenv("SHADOW_R2_ACCESS_KEY_ID", "access")
    monkeypatch.setenv("SHADOW_R2_SECRET_ACCESS_KEY", "secret")

    config = store.R2Config.from_env()

    assert config.account_id == "existing-account"
    assert config.bucket == "market-scanner-shadow"


def test_r2_config_rejects_partial_credentials(monkeypatch):
    monkeypatch.setenv("SHADOW_R2_ACCOUNT_ID", "account")
    monkeypatch.setenv("SHADOW_R2_ACCESS_KEY_ID", "access")
    monkeypatch.delenv("SHADOW_R2_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("SHADOW_R2_BUCKET", raising=False)
    with pytest.raises(ValueError, match="incompletă"):
        store.R2Config.from_env()


def test_object_key_is_date_partitioned_and_content_addressed():
    key = store.object_key(
        store.TECHNICAL_DATASET, snapshot(), prefix="scanner/v1"
    )
    assert key == (
        "scanner/v1/technical-events/year=2026/month=09/day=12/"
        "20260912T053000Z-abc123.parquet"
    )


def test_r2_request_uses_sigv4_without_exposing_secret():
    session = RecordingSession()
    client = store.R2Client(config(), session=session)
    client.put("scanner/v1/test.parquet", b"PAR1")
    method, url, body, headers, timeout = session.request_data
    assert method == "PUT"
    assert url.endswith("/shadow/scanner/v1/test.parquet")
    assert body == b"PAR1"
    assert timeout == 90
    assert headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=access/")
    assert "secret" not in headers["Authorization"]


def test_r2_large_put_uses_bulk_upload_timeout():
    session = RecordingSession()
    client = store.R2Client(config(), session=session)

    client.put("runtime/dashboard.json.gz", b"x" * (5 * 1024 * 1024))

    assert session.request_data[-1] == 600


def test_r2_put_accepts_head_confirmation_after_lost_response():
    session = StoredThenDisconnectedSession()
    client = store.R2Client(config(), session=session)

    client.put("runtime/dashboard.json.gz", b"payload")

    assert session.methods == ["PUT", "HEAD"]


def test_r2_large_put_uses_multipart_client(monkeypatch):
    client = store.R2Client(config())
    observed = {}

    def fake_multipart(key, content, content_type):
        observed.update(key=key, size=len(content), content_type=content_type)
        return "uploaded"

    monkeypatch.setattr(client, "_multipart_put", fake_multipart)

    result = client.put("runtime/dashboard.json.gz", b"x" * (4 * 1024 * 1024))

    assert result == "uploaded"
    assert observed == {
        "key": "runtime/dashboard.json.gz",
        "size": 4 * 1024 * 1024,
        "content_type": "application/vnd.apache.parquet",
    }


def test_parquet_round_trip_preserves_full_snapshot(tmp_path):
    source = snapshot()
    path = store.write_snapshot_parquet(
        source, store.ENHANCED_DATASET, tmp_path / "snapshot.parquet"
    )
    assert path.read_bytes()[:4] == b"PAR1"
    assert store.read_snapshot_parquet(path) == source


def test_persist_is_idempotent_and_loads_from_partition(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "SPOOL_DIR", tmp_path / "spool")
    client = FakeClient()
    first = snapshot("first", "2026-09-12T05:30:00Z")
    second = snapshot("second", "2026-09-12T06:30:00Z")

    store.persist_snapshot(first, store.ENHANCED_DATASET, config=config(), client=client)
    store.persist_snapshot(first, store.ENHANCED_DATASET, config=config(), client=client)
    store.persist_snapshot(second, store.ENHANCED_DATASET, config=config(), client=client)

    assert client.put_count == 2
    assert store.load_snapshots(
        store.ENHANCED_DATASET, config=config(), client=client
    ) == [first, second]
    assert store.latest_snapshot(
        store.ENHANCED_DATASET, config=config(), client=client
    ) == second


def test_failed_upload_stays_in_spool(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "SPOOL_DIR", tmp_path / "spool")

    class FailingClient(FakeClient):
        def put(self, key, content):
            raise RuntimeError("upstream unavailable")

    with pytest.raises(RuntimeError, match="upstream unavailable"):
        store.persist_snapshot(
            snapshot(), store.TECHNICAL_DATASET,
            config=config(), client=FailingClient(),
        )
    assert list((tmp_path / "spool").rglob("*.parquet"))


def test_flush_spool_retries_pending_partition(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "SPOOL_DIR", tmp_path / "spool")
    monkeypatch.setattr(store.R2Config, "from_env", classmethod(lambda cls: config()))
    pending = store._spool_path(store.TECHNICAL_DATASET, snapshot())
    store.write_snapshot_parquet(snapshot(), store.TECHNICAL_DATASET, pending)
    uploaded = []

    def fake_persist(payload, dataset, **_kwargs):
        uploaded.append((payload["snapshot_id"], dataset))
        pending.unlink()

    monkeypatch.setattr(store, "persist_snapshot", fake_persist)
    assert store.flush_spool() == 1
    assert uploaded == [("abc123", store.TECHNICAL_DATASET)]
