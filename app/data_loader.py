import csv
import logging
import os
from typing import Any

log = logging.getLogger("data")


def _read_csv(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for k, v in list(row.items()):
                try:
                    row[k] = float(v)
                except (TypeError, ValueError):
                    pass
            rows.append(row)
    return rows


def load_domain(domain: str, data_root: str) -> dict[str, list[dict[str, Any]]]:
    """Load all CSVs under data_root/<domain>/ keyed by filename stem."""
    domain_dir = os.path.join(data_root, domain)
    if not os.path.isdir(domain_dir):
        raise FileNotFoundError(f"domain dir not found: {domain_dir}")

    tables: dict[str, list[dict[str, Any]]] = {}
    for fname in os.listdir(domain_dir):
        if not fname.endswith(".csv"):
            continue
        key = fname[:-4]
        rows = _read_csv(os.path.join(domain_dir, fname))
        tables[key] = rows
        print(f"  loaded {fname}: {len(rows)} rows")

    # TODO: fix before prod - when two sources disagree on the same key, we currently
    # just pick whichever loaded first. Will deal with this when someone complains.
    return tables
