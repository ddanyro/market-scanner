import gzip
import json
from pathlib import Path

import pytest

import runtime_r2_store as store
from shadow_parquet_store import R2Config


class MemoryR2:
    def __init__(self):
        self.objects = {}
        self.get_calls = []
        self.put_calls = []
        self.delete_calls = []

    def exists(self, key):
        return key in self.objects

    def get(self, key):
        self.get_calls.append(key)
        if key not in self.objects:
            raise RuntimeError("R2 GET a eșuat: HTTP 404")
        return self.objects[key][0]

    def put(self, key, content, *, content_type="application/octet-stream"):
        self.put_calls.append(key)
        self.objects[key] = (bytes(content), content_type)

    def delete(self, key):
        self.delete_calls.append(key)
        self.objects.pop(key, None)

    def list_keys(self, prefix):
        return sorted(key for key in self.objects if key.startswith(prefix))


@pytest.fixture
def r2_config():
    return R2Config(
        account_id="account",
        access_key_id="access",
        secret_access_key="secret",
        bucket="bucket",
        endpoint="https://example.invalid",
    )


def write_runtime_files(root):
    payloads = {
        "dashboard_state.json": b'{"state":"current"}',
        ".ibkr_mcp_market_cache.json": b'{"NVDA":{"price":123}}',
        ".bvb_yahoo_history_cache.json.gz": b"compressed-bvb-cache",
        ".shadow_maintenance_state.json": (
            b'{"schema":"market-scanner.shadow-maintenance.v1","tasks":{}}'
        ),
        "analysis/enhanced_scoring_validation/recommendations_with_outcomes.csv": (
            b"ticker,return_1d\nNVDA,0.01\n"
        ),
        "watchlist_compact.json": b'[{"Ticker":"NVDA"}]',
        "watchlist_details.json": b'{"NVDA":{"ticker":"NVDA"}}',
        "index.html": b"<!doctype html><title>Market Scanner</title><p>full dashboard</p>",
    }
    for name, content in payloads.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return payloads


def test_push_uses_versioned_gzip_objects_and_atomic_manifest(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    payloads = write_runtime_files(tmp_path)
    client = MemoryR2()

    manifest = store.push_runtime(config=r2_config, client=client)

    assert set(manifest["artifacts"]) == set(store.ARTIFACTS)
    saved_manifest = json.loads(client.get(store.MANIFEST_KEY))
    assert saved_manifest == manifest
    for name, descriptor in manifest["artifacts"].items():
        assert "/versions/" in descriptor["key"]
        assert descriptor["key"].endswith(".gz")
        assert descriptor["sha256"] in descriptor["key"]
        assert descriptor["private"] is store.ARTIFACTS[name]["private"]
        assert gzip.decompress(client.get(descriptor["key"])) == payloads[
            str(store.ARTIFACTS[name]["path"])
        ]


def test_pull_restores_only_private_runtime_state_and_checks_integrity(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    payloads = write_runtime_files(tmp_path)
    client = MemoryR2()
    manifest = store.push_runtime(config=r2_config, client=client)
    Path("dashboard_state.json").unlink()
    Path(".ibkr_mcp_market_cache.json").unlink()
    Path(".bvb_yahoo_history_cache.json.gz").unlink()
    Path(".shadow_maintenance_state.json").unlink()
    Path("watchlist_compact.json").write_text("local-public-copy", encoding="utf-8")

    store.pull_runtime(config=r2_config, client=client)

    assert Path("dashboard_state.json").read_bytes() == payloads["dashboard_state.json"]
    assert Path(".ibkr_mcp_market_cache.json").read_bytes() == payloads[
        ".ibkr_mcp_market_cache.json"
    ]
    assert Path(".bvb_yahoo_history_cache.json.gz").read_bytes() == payloads[
        ".bvb_yahoo_history_cache.json.gz"
    ]
    assert Path(".shadow_maintenance_state.json").read_bytes() == payloads[
        ".shadow_maintenance_state.json"
    ]
    assert Path("watchlist_compact.json").read_text() == "local-public-copy"

    dashboard = manifest["artifacts"]["dashboard-state"]
    client.objects[dashboard["key"]] = (gzip.compress(b"tampered"), "application/gzip")
    Path("dashboard_state.json").unlink()
    with pytest.raises(RuntimeError, match="Checksum R2 invalid"):
        store.pull_runtime(config=r2_config, client=client)


def test_loader_does_not_replace_full_dashboard_in_r2(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    payloads = write_runtime_files(tmp_path)
    client = MemoryR2()

    first = store.push_runtime(
        publish_loader=True, config=r2_config, client=client
    )
    assert store.LOADER_MARKER in Path("index.html").read_text(encoding="utf-8")
    assert "cache: 'no-store'" in Path("index.html").read_text(encoding="utf-8")
    assert "window.location.protocol === 'file:'" in Path("index.html").read_text(
        encoding="utf-8"
    )
    assert "window.location.replace(endpoint)" in Path("index.html").read_text(
        encoding="utf-8"
    )

    second = store.push_runtime(config=r2_config, client=client)
    assert second["artifacts"]["dashboard-html"] == first["artifacts"]["dashboard-html"]
    key = second["artifacts"]["dashboard-html"]["key"]
    assert gzip.decompress(client.get(key)) == payloads["index.html"]
    store.verify_runtime(config=r2_config, client=client)


def test_pull_skips_r2_objects_when_local_checksums_are_unchanged(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    write_runtime_files(tmp_path)
    client = MemoryR2()
    manifest = store.push_runtime(config=r2_config, client=client)
    client.get_calls.clear()

    store.pull_runtime(config=r2_config, client=client)

    requested_objects = [
        key for key in client.get_calls if key != store.MANIFEST_KEY
    ]
    assert requested_objects == []
    assert set(manifest["artifacts"]) == set(store.ARTIFACTS)


def test_second_push_reuses_unchanged_r2_versions(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    write_runtime_files(tmp_path)
    client = MemoryR2()
    first = store.push_runtime(config=r2_config, client=client)
    version_puts_before = [
        key for key in client.put_calls if "/versions/" in key
    ]

    second = store.push_runtime(config=r2_config, client=client)

    version_puts_after = [
        key for key in client.put_calls if "/versions/" in key
    ]
    assert version_puts_after == version_puts_before
    assert second["artifacts"] == first["artifacts"]


def test_runtime_retention_keeps_current_and_two_previous_versions_only(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    write_runtime_files(tmp_path)
    client = MemoryR2()
    shadow_key = "market-scanner-shadow/v1/enhanced-scoring/snapshot.parquet"
    client.objects[shadow_key] = (b"PAR1", "application/vnd.apache.parquet")

    manifest = None
    for version in range(5):
        Path("dashboard_state.json").write_text(
            json.dumps({"state": version}), encoding="utf-8"
        )
        manifest = store.push_runtime(config=r2_config, client=client)

    descriptor = manifest["artifacts"]["dashboard-state"]
    version_prefix = f"{store.PREFIX}/dashboard-state/versions/"
    retained_versions = client.list_keys(version_prefix)

    assert len(retained_versions) == 3
    assert descriptor["key"] in retained_versions
    assert set(descriptor["previous_keys"]) == set(retained_versions) - {
        descriptor["key"]
    }
    assert len(client.delete_calls) == 2
    assert shadow_key in client.objects


def test_push_canonicalizes_json_before_hashing_and_upload(
    tmp_path, monkeypatch, r2_config
):
    monkeypatch.chdir(tmp_path)
    write_runtime_files(tmp_path)
    Path("dashboard_state.json").write_text(
        '{\n  "z": 2,\n  "a": 1\n}\n', encoding="utf-8"
    )
    client = MemoryR2()

    manifest = store.push_runtime(config=r2_config, client=client)

    expected = b'{"a":1,"z":2}'
    descriptor = manifest["artifacts"]["dashboard-state"]
    assert Path("dashboard_state.json").read_bytes() == expected
    assert gzip.decompress(client.get(descriptor["key"])) == expected
