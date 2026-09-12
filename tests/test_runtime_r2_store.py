import gzip
import json
from pathlib import Path

import pytest

import runtime_r2_store as store
from shadow_parquet_store import R2Config


class MemoryR2:
    def __init__(self):
        self.objects = {}

    def exists(self, key):
        return key in self.objects

    def get(self, key):
        if key not in self.objects:
            raise RuntimeError("R2 GET a eșuat: HTTP 404")
        return self.objects[key][0]

    def put(self, key, content, *, content_type="application/octet-stream"):
        self.objects[key] = (bytes(content), content_type)


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
        "analysis/enhanced_scoring_validation/recommendations_with_outcomes.csv": (
            b"ticker,return_1d\nNVDA,0.01\n"
        ),
        "watchlist_compact.json": b'[{"Ticker":"NVDA"}]',
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
    Path("watchlist_compact.json").write_text("local-public-copy", encoding="utf-8")

    store.pull_runtime(config=r2_config, client=client)

    assert Path("dashboard_state.json").read_bytes() == payloads["dashboard_state.json"]
    assert Path(".ibkr_mcp_market_cache.json").read_bytes() == payloads[
        ".ibkr_mcp_market_cache.json"
    ]
    assert Path("watchlist_compact.json").read_text() == "local-public-copy"

    dashboard = manifest["artifacts"]["dashboard-state"]
    client.objects[dashboard["key"]] = (gzip.compress(b"tampered"), "application/gzip")
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

    second = store.push_runtime(config=r2_config, client=client)
    assert second["artifacts"]["dashboard-html"] == first["artifacts"]["dashboard-html"]
    key = second["artifacts"]["dashboard-html"]["key"]
    assert gzip.decompress(client.get(key)) == payloads["index.html"]
    store.verify_runtime(config=r2_config, client=client)
