#!/usr/bin/env python3
"""Vergelijk twee ``magister.py --dump-raw`` snapshots.

Magister publiceert geen API-changelog. Maak daarom af en toe een ruwe dump en
vergelijk die met een eerdere: zo zie je welke velden er bijgekomen, verdwenen of
van type veranderd zijn.

Een dump maken (met je eigen gegevens, buiten Home Assistant):

    python3 custom_components/magister_school/script/magister.py --json \\
        --dump-raw baseline.json --schoolserver <school>.magister.net ...
    python3 tools/magister_api_diff.py baseline.json current.json

Uitvoer:

    + pad   nieuw veld
    - pad   verdwenen veld
    ~ pad   type gewijzigd

Exitcodes: 0 = geen verschillen, 1 = verschillen gevonden, 2 = invoerfout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_ID_SEGMENT = re.compile(r"^(?:\d+|[0-9a-fA-F]{8,})$")

LEGEND = "Legenda: + nieuw, - verdwenen, ~ type gewijzigd"


def normalise_endpoint(raw_key: str) -> str:
    """Strip the query string and collapse id-like path segments to ``{id}``.

    Magister-dumps zijn gesleuteld op het volledige pad inclusief querystring,
    bijvoorbeeld ``personen/123/afspraken?van=2026-01-01&tot=2026-02-01``.
    Zonder normalisatie zou elke andere dag een "nieuw endpoint" lijken.
    """
    path = raw_key.split("?", 1)[0]
    parts = [part for part in path.split("/") if part]
    return "/".join(
        "{id}" if _ID_SEGMENT.match(part) else part for part in parts
    )


def type_name(value: Any) -> str:
    """Return a stable type label; ``bool`` first because it subclasses int."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return type(value).__name__


def flatten(
    value: Any, prefix: str = "", out: dict[str, str] | None = None
) -> dict[str, str]:
    """Flatten a JSON value into ``{path: type}`` pairs.

    Lists are flattened with ``[]`` and only for object items, because Magister
    returns collections such as ``Items`` as arrays of records.
    """
    if out is None:
        out = {}

    if isinstance(value, dict):
        if prefix:
            out.setdefault(prefix, "object")
        for key, child in value.items():
            flatten(child, f"{prefix}.{key}" if prefix else str(key), out)
        return out

    if isinstance(value, list):
        if prefix:
            out.setdefault(prefix, "array")
        for item in value:
            if isinstance(item, dict):
                for key, child in item.items():
                    flatten(child, f"{prefix}[].{key}", out)
        return out

    if prefix:
        out[prefix] = type_name(value)
    return out


def load_dump(path: str | Path) -> dict[str, dict[str, str]]:
    """Load a raw dump and return ``{normalised endpoint: flattened paths}``."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: verwacht een JSON-object met endpoints als sleutels")

    snapshots: dict[str, dict[str, str]] = {}
    for raw_key, value in data.items():
        target = snapshots.setdefault(normalise_endpoint(raw_key), {})
        flatten(value, "", target)
    return snapshots


def diff_snapshots(
    baseline: dict[str, dict[str, str]],
    current: dict[str, dict[str, str]],
) -> dict[str, dict[str, Any]]:
    """Return the differences per endpoint. An empty dict means identical."""
    report: dict[str, dict[str, Any]] = {}

    for endpoint in sorted(set(baseline) | set(current)):
        if endpoint not in current:
            report[endpoint] = {"removed_endpoint": True}
            continue
        if endpoint not in baseline:
            report[endpoint] = {"added_endpoint": True}
            continue

        old = baseline[endpoint]
        new = current[endpoint]
        added = {path: new[path] for path in new.keys() - old.keys()}
        removed = {path: old[path] for path in old.keys() - new.keys()}
        changed = {
            path: (old[path], new[path])
            for path in old.keys() & new.keys()
            if old[path] != new[path]
        }
        if added or removed or changed:
            report[endpoint] = {"added": added, "removed": removed, "changed": changed}

    return report


def render_text(report: dict[str, dict[str, Any]], stream: Any = None) -> None:
    """Print a human readable report."""
    stream = stream or sys.stdout

    if not report:
        print("Geen verschillen: de API-responses zijn identiek.", file=stream)
        return

    for endpoint, change in report.items():
        print(f"\n=== {endpoint} ===", file=stream)
        if change.get("added_endpoint"):
            print("  + endpoint komt alleen in de nieuwe dump voor", file=stream)
            continue
        if change.get("removed_endpoint"):
            print("  - endpoint ontbreekt in de nieuwe dump", file=stream)
            continue
        for path, kind in sorted(change.get("added", {}).items()):
            print(f"  + {path}  ({kind})", file=stream)
        for path, kind in sorted(change.get("removed", {}).items()):
            print(f"  - {path}  ({kind})", file=stream)
        for path, (old_kind, new_kind) in sorted(change.get("changed", {}).items()):
            print(f"  ~ {path}  {old_kind} -> {new_kind}", file=stream)

    print(f"\n{LEGEND}", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vergelijk twee magister.py --dump-raw snapshots.",
    )
    parser.add_argument("baseline", help="eerdere dump (JSON)")
    parser.add_argument("current", help="nieuwe dump (JSON)")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="print het rapport als JSON in plaats van tekst",
    )
    args = parser.parse_args(argv)

    try:
        report = diff_snapshots(load_dump(args.baseline), load_dump(args.current))
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"Kon de dump niet lezen: {err}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        render_text(report)

    return 1 if report else 0


if __name__ == "__main__":
    sys.exit(main())
