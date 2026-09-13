"""Versioned Cloudflare R2 storage for scanner runtime artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import tempfile
from pathlib import Path

from shadow_parquet_store import R2Client, R2Config


PREFIX = os.environ.get("RUNTIME_R2_PREFIX", "market-scanner-runtime/v1").strip("/")
MANIFEST_KEY = f"{PREFIX}/manifest.json"
WORKER_BASE_URL = os.environ.get(
    "MARKET_SCANNER_DATA_URL",
    "https://market-scanner-portfolio-chat.daniel-dragomir.workers.dev",
).rstrip("/")
LOADER_MARKER = "market-scanner-r2-loader-v1"
PREVIOUS_VERSIONS_TO_KEEP = 2

ARTIFACTS = {
    "dashboard-state": {
        "path": Path("dashboard_state.json"),
        "content_type": "application/json; charset=utf-8",
        "private": True,
        "pull": True,
    },
    "ibkr-market-cache": {
        "path": Path(".ibkr_mcp_market_cache.json"),
        "content_type": "application/json; charset=utf-8",
        "private": True,
        "pull": True,
        "optional": True,
    },
    "bvb-yahoo-history-cache": {
        "path": Path(".bvb_yahoo_history_cache.json.gz"),
        "content_type": "application/gzip",
        "private": True,
        "pull": True,
        "optional": True,
    },
    "shadow-maintenance-state": {
        "path": Path(".shadow_maintenance_state.json"),
        "content_type": "application/json; charset=utf-8",
        "private": True,
        "pull": True,
        "optional": True,
    },
    "enhanced-validation-dataset": {
        "path": Path(
            "analysis/enhanced_scoring_validation/recommendations_with_outcomes.csv"
        ),
        "content_type": "text/csv; charset=utf-8",
        "private": True,
        "pull": False,
        "optional": True,
    },
    "watchlist-compact": {
        "path": Path("watchlist_compact.json"),
        "content_type": "application/json; charset=utf-8",
        "private": False,
        "pull": False,
    },
    "watchlist-details": {
        "path": Path("watchlist_details.json"),
        "content_type": "application/json; charset=utf-8",
        "private": False,
        "pull": False,
    },
    "dashboard-html": {
        "path": Path("index.html"),
        "content_type": "text/html; charset=utf-8",
        "private": False,
        "pull": False,
    },
}


def _config():
    config = R2Config.from_env()
    if config is None:
        raise RuntimeError("R2 runtime nu este configurat")
    return config


def _sha256(content):
    return hashlib.sha256(content).hexdigest()


def _read_manifest(client):
    try:
        payload = json.loads(client.get(MANIFEST_KEY).decode("utf-8"))
    except RuntimeError as exc:
        if "HTTP 404" in str(exc):
            return {"schema": "market-scanner.runtime-r2.v1", "artifacts": {}}
        raise
    if payload.get("schema") != "market-scanner.runtime-r2.v1":
        raise ValueError("Manifest R2 runtime necunoscut")
    return payload


def _atomic_write(path, content, *, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _artifact_bytes(path, spec):
    mode = 0o600 if spec.get("private") else 0o644
    # mkstemp intentionally defaults to 0600. Public runtime artifacts must
    # remain readable by the separate GitHub Pages artifact uploader.
    path.chmod(mode)
    raw = path.read_bytes()
    if str(spec.get("content_type", "")).startswith("application/json"):
        canonical = json.dumps(
            json.loads(raw), ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        if canonical != raw:
            _atomic_write(path, canonical, mode=mode)
        return canonical
    return raw


def _previous_version_keys(previous_descriptor, current_key):
    candidates = [
        previous_descriptor.get("key"),
        *(previous_descriptor.get("previous_keys") or []),
    ]
    retained = []
    for key in candidates:
        if not key or key == current_key or key in retained:
            continue
        retained.append(key)
        if len(retained) >= PREVIOUS_VERSIONS_TO_KEEP:
            break
    return retained


def _prune_runtime_versions(client, artifacts):
    """Delete unreferenced runtime versions, never shadow snapshot datasets."""
    pruned = []
    for name, descriptor in artifacts.items():
        prefix = f"{PREFIX}/{name}/versions/"
        retained = {
            descriptor.get("key"),
            *(descriptor.get("previous_keys") or []),
        }
        for key in client.list_keys(prefix):
            if key not in retained:
                client.delete(key)
                pruned.append(key)
    return pruned


def push_runtime(*, publish_loader=False, config=None, client=None):
    config = config or _config()
    client = client or R2Client(config)
    previous = _read_manifest(client)
    artifacts = dict(previous.get("artifacts") or {})
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    uploaded = []
    unchanged = []

    for name, spec in ARTIFACTS.items():
        path = spec["path"]
        if not path.exists():
            if spec.get("optional"):
                continue
            raise FileNotFoundError(f"Lipsește artefactul runtime obligatoriu: {path}")
        raw = _artifact_bytes(path, spec)
        if name == "dashboard-html" and LOADER_MARKER.encode() in raw:
            # Never replace the full dashboard in R2 with its tiny Pages loader.
            continue
        digest = _sha256(raw)
        previous_descriptor = artifacts.get(name) or {}
        if previous_descriptor.get("sha256") == digest:
            unchanged.append(name)
            continue
        compressed = gzip.compress(raw, compresslevel=9, mtime=0)
        key = f"{PREFIX}/{name}/versions/{digest}.gz"
        if not client.exists(key):
            client.put(key, compressed, content_type="application/gzip")
        artifacts[name] = {
            "key": key,
            "sha256": digest,
            "raw_bytes": len(raw),
            "stored_bytes": len(compressed),
            "content_type": spec["content_type"],
            "content_encoding": "gzip",
            "private": bool(spec["private"]),
            "updated_at": generated_at,
            "previous_keys": _previous_version_keys(previous_descriptor, key),
        }
        uploaded.append(name)

    manifest = {
        "schema": "market-scanner.runtime-r2.v1",
        "generated_at": generated_at,
        "artifacts": artifacts,
    }
    client.put(
        MANIFEST_KEY,
        json.dumps(manifest, separators=(",", ":"), sort_keys=True).encode("utf-8"),
        content_type="application/json",
    )
    retention_warning = None
    try:
        pruned = _prune_runtime_versions(client, artifacts)
    except Exception as exc:
        # The new manifest is already valid. A retention failure must not make
        # the freshly published runtime unavailable; retry on the next push.
        pruned = []
        retention_warning = str(exc)
    if publish_loader:
        _atomic_write(
            Path("index.html"), loader_html().encode("utf-8"), mode=0o644
        )
    print(json.dumps({
        "pushed": sorted(uploaded),
        "unchanged": sorted(unchanged),
        "manifest": MANIFEST_KEY,
        "loader_published": publish_loader,
        "pruned_versions": len(pruned),
        "retention_warning": retention_warning,
    }, ensure_ascii=False))
    return manifest


def pull_runtime(*, config=None, client=None):
    config = config or _config()
    client = client or R2Client(config)
    manifest = _read_manifest(client)
    restored = []
    unchanged = []
    for name, spec in ARTIFACTS.items():
        if not spec.get("pull"):
            continue
        descriptor = (manifest.get("artifacts") or {}).get(name)
        if not descriptor:
            if spec.get("optional"):
                continue
            raise RuntimeError(f"Manifestul R2 nu conține {name}")
        path = spec["path"]
        if path.exists():
            try:
                local_digest = _sha256(path.read_bytes())
            except OSError:
                local_digest = None
            if local_digest == descriptor.get("sha256"):
                unchanged.append(name)
                print(f"[R2 runtime] {name}: neschimbat (cache local).", flush=True)
                continue
        print(
            f"[R2 runtime] {name}: descarc "
            f"{descriptor.get('stored_bytes', 0) / 1048576:.2f} MB...",
            flush=True,
        )
        compressed = client.get(descriptor["key"])
        raw = gzip.decompress(compressed)
        if _sha256(raw) != descriptor.get("sha256"):
            raise RuntimeError(f"Checksum R2 invalid pentru {name}")
        _atomic_write(
            path, raw, mode=0o600 if spec.get("private") else 0o644
        )
        restored.append(name)
    print(json.dumps({
        "pulled": restored,
        "unchanged": unchanged,
        "manifest": MANIFEST_KEY,
    }))
    return manifest


def verify_runtime(*, config=None, client=None):
    config = config or _config()
    client = client or R2Client(config)
    manifest = _read_manifest(client)
    verified = []
    for name, descriptor in sorted((manifest.get("artifacts") or {}).items()):
        content = gzip.decompress(client.get(descriptor["key"]))
        if _sha256(content) != descriptor.get("sha256"):
            raise RuntimeError(f"Checksum R2 invalid pentru {name}")
        verified.append(name)
    print(json.dumps({"verified": verified, "count": len(verified)}))
    return manifest


def loader_html():
    endpoint = f"{WORKER_BASE_URL}/runtime/index.html"
    return f"""<!doctype html>
<html lang=\"ro\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<meta name=\"theme-color\" content=\"#7760f9\"><title>Market Scanner</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#f5f7fb;color:#111827;font-family:system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif}}
.gate{{width:min(440px,calc(100vw - 32px));padding:36px;border:1px solid #e5e7eb;border-radius:24px;background:#fff;box-shadow:0 24px 70px rgba(15,23,42,.15);text-align:center}}
.mark{{width:62px;height:62px;margin:0 auto 18px;display:grid;place-items:center;border-radius:18px;background:linear-gradient(135deg,#7760f9,#4f46e5);color:#fff;font-size:30px;font-weight:800}}
h1{{margin:0 0 10px;font-size:28px}}p{{margin:0 0 24px;color:#64748b;line-height:1.5}}form{{display:flex;gap:10px}}input{{min-width:0;flex:1;padding:14px 16px;border:1px solid #cbd5e1;border-radius:12px;font:inherit;text-align:center;letter-spacing:5px}}input:focus{{outline:3px solid rgba(119,96,249,.18);border-color:#7760f9}}button{{padding:14px 18px;border:0;border-radius:12px;background:#6654ed;color:#fff;font:inherit;font-weight:750;cursor:pointer}}button:disabled{{opacity:.6;cursor:wait}}#status{{min-height:22px;margin:16px 0 0;color:#b91c1c;font-size:14px}}#loading{{display:none;color:#475569}}
@media(max-width:480px){{.gate{{padding:28px 20px}}form{{flex-direction:column}}}}
</style></head><body>
<!-- {LOADER_MARKER} -->
<main class=\"gate\" aria-labelledby=\"gate-title\">
  <div class=\"mark\" aria-hidden=\"true\">M</div>
  <h1 id=\"gate-title\">Market Scanner</h1>
  <p>Introdu parola pentru a accesa întregul dashboard.</p>
  <form id=\"access-form\">
    <input id=\"access-password\" type=\"password\" autocomplete=\"current-password\" placeholder=\"Parolă\" aria-label=\"Parolă\" required>
    <button id=\"access-submit\" type=\"submit\">Accesează</button>
  </form>
  <p id=\"status\" role=\"alert\"></p>
  <p id=\"loading\">Se încarcă dashboardul…</p>
</main>
<script>
var endpoint = {json.dumps(endpoint)};
var tokenMessage = 'market-scanner-portfolio-chat-v1';
var tokenStorageKey = 'market-scanner-dashboard-access-v1';
var tokenTtlMs = 30 * 24 * 60 * 60 * 1000;
function bytesToHex(buffer) {{
  return Array.from(new Uint8Array(buffer)).map(function(value) {{
    return value.toString(16).padStart(2, '0');
  }}).join('');
}}
async function accessToken(password) {{
  var encoder = new TextEncoder();
  var key = await crypto.subtle.importKey('raw',encoder.encode(password),{{name:'HMAC',hash:'SHA-256'}},false,['sign']);
  return bytesToHex(await crypto.subtle.sign('HMAC',key,encoder.encode(tokenMessage)));
}}
function savedToken() {{
  try {{
    var record = JSON.parse(localStorage.getItem(tokenStorageKey) || 'null');
    if (!record || !record.token || record.expiresAt <= Date.now()) {{
      localStorage.removeItem(tokenStorageKey); return '';
    }}
    return record.token;
  }} catch (_error) {{ localStorage.removeItem(tokenStorageKey); return ''; }}
}}
async function loadDashboard(token,rememberAccess) {{
  var status=document.getElementById('status');
  var loading=document.getElementById('loading');
  var submit=document.getElementById('access-submit');
  status.textContent=''; loading.style.display='block'; submit.disabled=true;
  try {{
    var response=await fetch(endpoint,{{cache:'no-store',headers:{{Authorization:'Bearer '+token}}}});
    if(response.status===401)throw new Error('Parolă incorectă.');
    if(!response.ok)throw new Error('Dashboard indisponibil (HTTP '+response.status+').');
    var html=await response.text();
    sessionStorage.setItem(tokenStorageKey,token);
    if(rememberAccess){{
      localStorage.setItem(tokenStorageKey,JSON.stringify({{token:token,expiresAt:Date.now()+tokenTtlMs}}));
    }}
    document.open();document.write(html);document.close();
  }}catch(error){{
    localStorage.removeItem(tokenStorageKey);sessionStorage.removeItem(tokenStorageKey);
    status.textContent=error&&error.message?error.message:String(error);
    loading.style.display='none';submit.disabled=false;
    document.getElementById('access-password').focus();
  }}
}}
document.getElementById('access-form').addEventListener('submit',async function(event){{
  event.preventDefault();var password=document.getElementById('access-password').value;
  if(!password)return;await loadDashboard(await accessToken(password),true);
}});
var existingToken=savedToken();
if(existingToken){{loadDashboard(existingToken,false);}}else{{document.getElementById('access-password').focus();}}
</script></body></html>"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("push", "pull", "verify", "loader"))
    parser.add_argument("--publish-loader", action="store_true")
    args = parser.parse_args()
    if args.command == "push":
        push_runtime(publish_loader=args.publish_loader)
    elif args.command == "pull":
        pull_runtime()
    elif args.command == "verify":
        verify_runtime()
    else:
        _atomic_write(
            Path("index.html"), loader_html().encode("utf-8"), mode=0o644
        )


if __name__ == "__main__":
    main()
