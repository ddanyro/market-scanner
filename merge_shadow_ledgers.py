"""Merge concurrent append-only shadow ledgers without changing observations."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import shadow_validation


def _read(path: Path):
    if not path.exists():
        return []
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}:{line_number}") from exc
    return rows


def merge_ledgers(paths):
    by_id = {}
    for path in paths:
        for snapshot in _read(Path(path)):
            snapshot_id = snapshot.get("snapshot_id")
            if not snapshot_id:
                raise ValueError(f"Snapshot without id in {path}")
            existing = by_id.get(snapshot_id)
            if existing is not None and existing != snapshot:
                raise ValueError(f"Conflicting payloads for snapshot {snapshot_id}")
            by_id[snapshot_id] = snapshot
    return sorted(
        by_id.values(),
        key=lambda item: (str(item.get("recorded_at") or ""), item["snapshot_id"]),
    )


def write_merged(output, snapshots):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for snapshot in snapshots:
                handle.write(json.dumps(
                    snapshot, ensure_ascii=False, separators=(",", ":")
                ) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        loaded = shadow_validation.load_ledger(temporary)
        errors = shadow_validation.validate_ledger(loaded)
        if errors:
            raise ValueError("Merged ledger failed integrity: " + "; ".join(errors))
        Path(temporary).replace(output)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    snapshots = merge_ledgers(args.inputs)
    write_merged(args.output, snapshots)
    print(f"Merged shadow ledger: {len(snapshots)} snapshots")


if __name__ == "__main__":
    main()
