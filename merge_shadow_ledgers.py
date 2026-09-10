"""Merge concurrent append-only shadow ledgers without changing observations."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import tempfile
from pathlib import Path

import shadow_validation


def _read(path: Path):
    if not path.exists():
        return []
    rows = []
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    else:
        lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
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


def write_merged(output, snapshots, validator=shadow_validation):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp.gz" if output.suffix == ".gz" else ".tmp",
        dir=output.parent,
    )
    try:
        raw_handle = os.fdopen(descriptor, "wb")
        handle = (
            gzip.open(raw_handle, "wt", encoding="utf-8")
            if output.suffix == ".gz"
            else open(raw_handle.fileno(), "w", encoding="utf-8", closefd=False)
        )
        with raw_handle, handle:
            for snapshot in snapshots:
                handle.write(json.dumps(
                    snapshot, ensure_ascii=False, separators=(",", ":")
                ) + "\n")
            handle.flush()
            if output.suffix != ".gz":
                os.fsync(raw_handle.fileno())
        loaded = validator.load_ledger(temporary)
        errors = validator.validate_ledger(loaded)
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
    parser.add_argument("--kind", choices=("enhanced", "technical"), default="enhanced")
    args = parser.parse_args()
    snapshots = merge_ledgers(args.inputs)
    validator = shadow_validation
    if args.kind == "technical":
        import technical_events_shadow
        validator = technical_events_shadow
    write_merged(args.output, snapshots, validator=validator)
    print(f"Merged shadow ledger: {len(snapshots)} snapshots")


if __name__ == "__main__":
    main()
