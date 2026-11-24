#!/usr/bin/env python3
"""Detecteer nieuwe Magister-functies door de JS-bundels te vergelijken.

Magister publiceert geen changelog, maar de webapp is gewone JavaScript die
zonder inloggen te downloaden is. Alles wat de app kan, staat in die bundels:
API-paden, OIDC-scopes en de stappen van de loginflow. Scan ze nu, vergelijk
later.

    python3 tools/magister_bundle_diff.py --schoolserver <school>.magister.net

De eerste run schrijft de baseline, elke volgende run toont de verschillen.
Er is geen account of wachtwoord nodig: alleen openbare bestanden worden
opgehaald.

Exitcodes: 0 = geen verschillen (of baseline geschreven), 1 = verschillen
gevonden, 2 = invoer- of netwerkfout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

USER_AGENT = "magister-school-integration-bundle-diff/1.0"
MAX_BYTES = 8_000_000

DEFAULT_ENTRIES = ("/magister/", "/op/")
BUCKETS = ("routes", "actions", "scopes", "config")
LEGEND = "Legenda: + nieuw, - verdwenen"

_STRING = re.compile(r"""["'`]([^"'`\\\r\n]{2,160})["'`]""")
_ASSET = re.compile(r"\.(js|css|png|jpe?g|gif|svg|woff2?|ttf|eot|ico|map)$", re.I)
_ROUTE_CHARS = re.compile(r"^[A-Za-z0-9/{}\-_.$~]+$")
_ACTION = re.compile(r"""\baction\s*:\s*["']([a-z0-9\-]{2,40})["']""")
_CONFIG_LINE = re.compile(r"^\s*(\w+)\s*:\s*(.+?),?\s*$", re.M)
_SCRIPT_SRC = re.compile(r"""<script[^>]+src=["']([^"']+)["']""", re.I)
_LOGIN_BUNDLE = re.compile(r"js/account-\w+\.js")
_HASH_IN_NAME = re.compile(r"[.\-_][0-9a-f]{8,}(?=\.[a-z]+$|$)", re.I)
_NUMBER_SEGMENT = re.compile(r"^(\d+|[0-9a-fA-F]{8,})$")
_PLACEHOLDER = re.compile(r"\{[^}]*\}")


def normalise_source(url: str) -> str:
    """Strip scheme, query and content hash so a new build is not a new source."""
    parsed = urllib.parse.urlsplit(url)
    path = _HASH_IN_NAME.sub("", parsed.path)
    return f"{parsed.netloc}{path}"


def normalise_route(route: str) -> str:
    """Collapse ids and placeholders so a different leerling does not differ."""
    path = route.split("?", 1)[0]
    return "/".join(
        "{id}" if _NUMBER_SEGMENT.match(part) else _PLACEHOLDER.sub("{id}", part)
        for part in path.split("/")
    )


def _looks_like_route(value: str) -> bool:
    path = value.split("?", 1)[0]
    if " " in path or "//" in path:
        return False
    if not (path.startswith("/") or "api/" in path):
        return False
    if not _ROUTE_CHARS.match(path):
        return False
    return not _ASSET.search(path)


def extract_routes(text: str) -> list[str]:
    """Return the API/path strings the JavaScript talks about."""
    found = {
        normalise_route(match.group(1))
        for match in _STRING.finditer(text)
        if _looks_like_route(match.group(1))
    }
    return sorted(found)


def extract_actions(text: str) -> list[str]:
    """Return the ``action: "..."`` values, e.g. Magister's login steps."""
    return sorted({match.group(1) for match in _ACTION.finditer(text)})


def extract_scopes(text: str) -> list[str]:
    """Return the OIDC scopes from oidc_config.js; this is Magister's feature list."""
    match = re.search(r"scope\s*:\s*['\"]([^'\"]+)['\"]", text)
    if not match:
        return []
    return sorted(set(match.group(1).split()))


def extract_config(text: str, host: str) -> list[str]:
    """Return ``key=value`` pairs from oidc_config.js, resolved for this school."""
    pairs: list[str] = []
    for match in _CONFIG_LINE.finditer(text):
        key = match.group(1)
        if key == "scope":
            continue
        value = match.group(2).replace("window.location.hostname", f"'{host}'")
        value = re.sub(r"'\s*\+\s*'", "", value).strip()
        value = value.strip("'").strip('"').rstrip(",").strip()
        pairs.append(f"{key}={value}")
    return sorted(set(pairs))


def scan_text(text: str) -> dict[str, list[str]]:
    """Scan one JavaScript/HTML file into its buckets."""
    return {"routes": extract_routes(text), "actions": extract_actions(text)}


def _fetch(url: str, timeout: float) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_BYTES + 1)
        final_url = response.geturl()
    if len(body) > MAX_BYTES:
        raise ValueError(f"{url}: groter dan {MAX_BYTES} bytes")
    return final_url, body.decode("utf-8", "ignore")


def _script_urls(html: str, page_url: str) -> list[str]:
    return [
        urllib.parse.urljoin(page_url, src)
        for src in _SCRIPT_SRC.findall(html)
    ]


def _config_value(config: list[str], key: str, default: str = "") -> str:
    prefix = f"{key}="
    for pair in config:
        if pair.startswith(prefix):
            return pair[len(prefix):]
    return default


def discover_login_bundle(host: str, config: list[str], timeout: float) -> str:
    """Resolve the current ``js/account-<hash>.js`` without logging in."""
    authority = _config_value(config, "authority", "https://accounts.magister.net")
    params = {
        "client_id": _config_value(config, "client_id", f"M6-{host}"),
        "redirect_uri": _config_value(
            config, "redirect_uri", f"https://{host}/oidc/redirect_callback.html"
        ),
        "response_type": _config_value(config, "response_type", "id_token token"),
        "scope": "openid profile",
        "state": "11111111111111111111111111111111",
        "nonce": "11111111111111111111111111111111",
        "acr_values": _config_value(config, "acr_values", f"tenant:{host}"),
    }
    _, well_known = _fetch(f"{authority}/.well-known/openid-configuration", timeout)
    endpoint = json.loads(well_known).get("authorization_endpoint")
    if not endpoint:
        raise ValueError("geen authorization_endpoint in de openid-configuration")

    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    final_url, html = _fetch(url, timeout)
    match = _LOGIN_BUNDLE.search(html)
    if not match:
        raise ValueError(f"geen loginbundle gevonden op {final_url}")
    return urllib.parse.urljoin(authority, match.group(0))


def collect_sources(
    schoolserver: str,
    entries: Iterable[str] = DEFAULT_ENTRIES,
    include_login: bool = True,
    timeout: float = 30.0,
) -> dict[str, dict[str, list[str]]]:
    """Download the public bundles of one school and scan them."""
    host = schoolserver.removeprefix("https://").removeprefix("http://").strip("/")
    base = f"https://{host}"
    scans: dict[str, dict[str, list[str]]] = {}
    seen: set[str] = set()

    def scan(url: str, text: str, extra: dict[str, list[str]] | None = None) -> None:
        key = normalise_source(url)
        if key in seen:
            return
        seen.add(key)
        result = scan_text(text)
        if extra:
            result.update(extra)
        scans[key] = result

    _, shell = _fetch(f"{base}/", timeout)
    scan(f"{base}/", shell)

    _, oidc_js = _fetch(f"{base}/oidc_config.js", timeout)
    oidc_scan: dict[str, list[str]] = {
        "scopes": extract_scopes(oidc_js),
        "config": extract_config(oidc_js, host),
    }
    scan(f"{base}/oidc_config.js", oidc_js, oidc_scan)

    for entry in entries:
        entry_url = f"{base}{entry}"
        final_url, html = _fetch(entry_url, timeout)
        scan(entry_url, html)
        for script_url in _script_urls(html, final_url):
            if not script_url.startswith(base):
                continue
            _, script = _fetch(script_url, timeout)
            scan(script_url, script)

    if include_login:
        bundle_url = discover_login_bundle(host, scans[normalise_source(f"{base}/oidc_config.js")]["config"], timeout)
        _, bundle = _fetch(bundle_url, timeout)
        scan(bundle_url, bundle)

    return scans


def diff_scans(
    baseline: dict[str, dict[str, list[str]]],
    current: dict[str, dict[str, list[str]]],
) -> dict[str, dict[str, Any]]:
    """Return the differences per source. An empty dict means identical."""
    report: dict[str, dict[str, Any]] = {}

    for source in sorted(set(baseline) | set(current)):
        if source not in current:
            report[source] = {"removed_source": True}
            continue
        if source not in baseline:
            report[source] = {"added_source": True}
            continue

        old = baseline[source]
        new = current[source]
        added = {b: sorted(set(new.get(b, [])) - set(old.get(b, []))) for b in BUCKETS}
        removed = {b: sorted(set(old.get(b, [])) - set(new.get(b, []))) for b in BUCKETS}
        added = {b: v for b, v in added.items() if v}
        removed = {b: v for b, v in removed.items() if v}
        if added or removed:
            report[source] = {"added": added, "removed": removed}

    return report


def render_text(report: dict[str, dict[str, Any]], stream: Any = None) -> None:
    """Print a human readable report."""
    stream = stream or sys.stdout

    if not report:
        print("Geen verschillen: de bundels zijn identiek.", file=stream)
        return

    for source, change in report.items():
        print(f"\n=== {source} ===", file=stream)
        if change.get("added_source"):
            print("  + bron is nieuw", file=stream)
            continue
        if change.get("removed_source"):
            print("  - bron bestaat niet meer", file=stream)
            continue
        for bucket, values in sorted(change.get("added", {}).items()):
            for value in values:
                print(f"  + [{bucket}] {value}", file=stream)
        for bucket, values in sorted(change.get("removed", {}).items()):
            for value in values:
                print(f"  - [{bucket}] {value}", file=stream)

    print(f"\n{LEGEND}", file=stream)


def load_baseline(path: str | Path) -> dict[str, dict[str, list[str]]]:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: verwacht een JSON-object")
    return data


def save_baseline(path: str | Path, scans: dict[str, dict[str, list[str]]]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(scans, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vergelijk de openbare Magister JS-bundels met een baseline.",
    )
    parser.add_argument("--schoolserver", required=True, help="bijv. <school>.magister.net")
    parser.add_argument(
        "--baseline",
        default="magister_bundle_baseline.json",
        help="pad van de baseline (wordt aangemaakt als hij ontbreekt)",
    )
    parser.add_argument(
        "--update", action="store_true", help="overschrijf de baseline met de huidige scan"
    )
    parser.add_argument(
        "--entry",
        action="append",
        dest="entries",
        help="extra ingangspagina op de schoolserver (mag meerdere keren)",
    )
    parser.add_argument("--no-login", action="store_true", help="sla de loginbundle over")
    parser.add_argument("--timeout", type=float, default=30.0, help="timeout per request")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="print het rapport als JSON"
    )
    args = parser.parse_args(argv)

    baseline_path = Path(args.baseline)
    entries = tuple(args.entries) if args.entries else DEFAULT_ENTRIES

    try:
        current = collect_sources(
            schoolserver=args.schoolserver,
            entries=entries,
            include_login=not args.no_login,
            timeout=args.timeout,
        )
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"Kon de bundels niet ophalen: {err}", file=sys.stderr)
        return 2

    if args.update or not baseline_path.exists():
        try:
            save_baseline(baseline_path, current)
        except OSError as err:
            print(f"Kon de baseline niet schrijven: {err}", file=sys.stderr)
            return 2
        print(
            f"Baseline geschreven naar {baseline_path} ({len(current)} bronnen).",
            file=sys.stderr,
        )
        return 0

    try:
        baseline = load_baseline(baseline_path)
    except (OSError, ValueError, json.JSONDecodeError) as err:
        print(f"Kon de baseline niet lezen: {err}", file=sys.stderr)
        return 2

    report = diff_scans(baseline, current)

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        render_text(report)

    return 1 if report else 0


if __name__ == "__main__":
    sys.exit(main())
