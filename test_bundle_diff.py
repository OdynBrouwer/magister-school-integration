"""Tests for tools/magister_bundle_diff.py."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent

spec = importlib.util.spec_from_file_location(
    "magister_bundle_diff", ROOT / "tools" / "magister_bundle_diff.py"
)
assert spec is not None and spec.loader is not None

bundle_diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle_diff)


def test_normalise_source_strips_scheme_query_and_hash():
    assert (
        bundle_diff.normalise_source(
            "https://school.magister.net/op/app.d358d3a80ece6a53eb6b.js?v=2"
        )
        == "school.magister.net/op/app.js"
    )
    assert (
        bundle_diff.normalise_source(
            "https://accounts.magister.net/js/account-f60d39e6d650e83d2a65.js"
        )
        == "accounts.magister.net/js/account.js"
    )
    assert (
        bundle_diff.normalise_source("https://school.magister.net/oidc_config.js")
        == "school.magister.net/oidc_config.js"
    )


def test_normalise_route_collapses_ids_but_keeps_literal_parts():
    assert (
        bundle_diff.normalise_route("/api/personen/123/cijfers")
        == "/api/personen/{id}/cijfers"
    )
    assert bundle_diff.normalise_route("/api/m6/applicatietoegang") == "/api/m6/applicatietoegang"
    assert (
        bundle_diff.normalise_route("/api/m6/studiewijzer/onderdeel/{0}/toegangen")
        == "/api/m6/studiewijzer/onderdeel/{id}/toegangen"
    )
    assert bundle_diff.normalise_route("/api/sessies?top=50") == "/api/sessies"


def test_extract_routes_keeps_api_paths_and_drops_noise():
    js = """
    var url = "/api/berichten";
    var other = "api/sessies";
    var asset = "/Content/app/styles/main.css";
    var mime = "application/json";
    var external = "https://example.com/api/x";
    var withQuery = "/api/leerlingen/?top=10";
    var placeholder = "/api/leerlingen/123/cijfers";
    """

    assert bundle_diff.extract_routes(js) == [
        "/api/berichten",
        "/api/leerlingen/",
        "/api/leerlingen/{id}/cijfers",
        "api/sessies",
    ]


def test_extract_actions_from_login_bundle():
    js = """
    return {action: "select-user", users: users};
    return {action: "skip-pair-fido-promo"};
    return {action: "pair-soft-token", code: code};
    return {notAnAction: "ignore-me"};
    """

    assert bundle_diff.extract_actions(js) == [
        "pair-soft-token",
        "select-user",
        "skip-pair-fido-promo",
    ]


def test_extract_scopes_and_config_resolve_the_school_host():
    js = """var getOidcConfig = function () {
  var config = {
    authority: 'https://accounts.magister.net',
    client_id: 'M6-' + window.location.hostname,
    redirect_uri: 'https://' + window.location.hostname + '/oidc/redirect_callback.html',
    response_type: 'id_token token',
    scope: 'openid profile grades.read learningmaterials.user',
    monitorSession: false
  };
  return config;
};
"""

    assert bundle_diff.extract_scopes(js) == [
        "grades.read",
        "learningmaterials.user",
        "openid",
        "profile",
    ]
    config = bundle_diff.extract_config(js, "school.magister.net")
    assert "client_id=M6-school.magister.net" in config
    assert (
        "redirect_uri=https://school.magister.net/oidc/redirect_callback.html" in config
    )
    assert "monitorSession=false" in config
    assert not any(pair.startswith("scope=") for pair in config)


def test_extract_config_from_settings_js_captures_feature_flags():
    js = """window.globalSettings = {
  apiHost: window.location.origin + '/',
  featureFlags: {
    m6LoggingEnabled: true,
    enableOPP: true
  },
  learningMaterialsHostname: 'https://learningmaterials.magister.net',
  kennisnetLogin: true,
};
"""

    config = bundle_diff.extract_config(js, "school.magister.net")

    assert "apiHost=https://school.magister.net/" in config
    assert "enableOPP=true" in config
    assert "m6LoggingEnabled=true" in config
    assert "kennisnetLogin=true" in config
    assert "learningMaterialsHostname=https://learningmaterials.magister.net" in config
    assert not any(pair.endswith("={") or pair.endswith("=}") for pair in config)


def test_collect_sources_adds_config_for_settings_js(monkeypatch):
    pages = {
        "https://school.magister.net/": "<html></html>",
        "https://school.magister.net/oidc_config.js": (
            "var config = { authority: 'https://accounts.magister.net',"
            " scope: 'openid grades.read' };"
        ),
        "https://school.magister.net/op/": (
            '<script src="settings.js"></script>'
            '<script src="app.abc123def4567890.js"></script>'
        ),
        "https://school.magister.net/op/settings.js": (
            "window.globalSettings = { featureFlags: { enableOPP: true } };"
        ),
        "https://school.magister.net/op/app.abc123def4567890.js": 'var u = "/api/berichten";',
    }

    def fake_fetch(url, timeout):
        return url, pages[url]

    monkeypatch.setattr(bundle_diff, "_fetch", fake_fetch)

    scans = bundle_diff.collect_sources(
        "school.magister.net", entries=("/op/",), include_login=False
    )

    assert scans["school.magister.net/op/app.js"]["routes"] == ["/api/berichten"]
    assert "enableOPP=true" in scans["school.magister.net/op/settings.js"]["config"]
    assert scans["school.magister.net/oidc_config.js"]["scopes"] == ["grades.read", "openid"]


def test_diff_scans_reports_new_route_scope_and_source():
    baseline = {
        "school.magister.net/op/app.js": {"routes": ["/api/berichten"], "actions": []},
        "school.magister.net/gone.js": {"routes": ["/api/oud"], "actions": []},
    }
    current = {
        "school.magister.net/op/app.js": {
            "routes": ["/api/berichten", "/api/leermiddelen/amn"],
            "actions": [],
        },
        "school.magister.net/oidc_config.js": {
            "routes": [],
            "actions": [],
            "scopes": ["learningmaterials.user"],
        },
    }

    report = bundle_diff.diff_scans(baseline, current)

    assert report["school.magister.net/op/app.js"] == {
        "added": {"routes": ["/api/leermiddelen/amn"]},
        "removed": {},
    }
    assert report["school.magister.net/gone.js"] == {"removed_source": True}
    assert report["school.magister.net/oidc_config.js"] == {"added_source": True}


def test_diff_scans_is_empty_for_identical_scans():
    scans = {"school.magister.net/op/app.js": {"routes": ["/api/berichten"], "actions": []}}

    assert bundle_diff.diff_scans(scans, scans) == {}


def _scan(routes):
    return {"school.magister.net/op/app.js": {"routes": routes, "actions": []}}


def test_main_writes_baseline_then_reports_changes(tmp_path, monkeypatch, capsys):
    baseline = tmp_path / "baseline.json"
    monkeypatch.setattr(
        bundle_diff, "collect_sources", lambda **kwargs: _scan(["/api/berichten"])
    )

    assert bundle_diff.main(["--schoolserver", "school.magister.net", "--baseline", str(baseline)]) == 0
    assert "Baseline geschreven" in capsys.readouterr().err
    assert json.loads(baseline.read_text(encoding="utf-8")) == _scan(["/api/berichten"])

    monkeypatch.setattr(
        bundle_diff,
        "collect_sources",
        lambda **kwargs: _scan(["/api/berichten", "/api/leermiddelen/amn"]),
    )

    assert bundle_diff.main(["--schoolserver", "school.magister.net", "--baseline", str(baseline)]) == 1
    assert "+ [routes] /api/leermiddelen/amn" in capsys.readouterr().out


def test_main_identical_scan_exits_zero(tmp_path, monkeypatch, capsys):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(_scan(["/api/berichten"])), encoding="utf-8")
    monkeypatch.setattr(
        bundle_diff, "collect_sources", lambda **kwargs: _scan(["/api/berichten"])
    )

    assert bundle_diff.main(["--schoolserver", "school.magister.net", "--baseline", str(baseline)]) == 0
    assert "Geen verschillen" in capsys.readouterr().out


def test_main_json_output(tmp_path, monkeypatch, capsys):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(_scan([])), encoding="utf-8")
    monkeypatch.setattr(
        bundle_diff, "collect_sources", lambda **kwargs: _scan(["/api/berichten"])
    )

    assert (
        bundle_diff.main(
            ["--schoolserver", "school.magister.net", "--baseline", str(baseline), "--json"]
        )
        == 1
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["school.magister.net/op/app.js"]["added"] == {
        "routes": ["/api/berichten"]
    }


def test_main_network_error_exits_two(tmp_path, monkeypatch, capsys):
    def boom(**kwargs):
        raise OSError("kon geen verbinding maken")

    monkeypatch.setattr(bundle_diff, "collect_sources", boom)

    assert (
        bundle_diff.main(
            ["--schoolserver", "school.magister.net", "--baseline", str(tmp_path / "b.json")]
        )
        == 2
    )
    assert "Kon de bundels niet ophalen" in capsys.readouterr().err


def test_main_update_overwrites_baseline(tmp_path, monkeypatch, capsys):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(_scan(["/api/oud"])), encoding="utf-8")
    monkeypatch.setattr(
        bundle_diff, "collect_sources", lambda **kwargs: _scan(["/api/nieuw"])
    )

    assert (
        bundle_diff.main(
            [
                "--schoolserver",
                "school.magister.net",
                "--baseline",
                str(baseline),
                "--update",
            ]
        )
        == 0
    )
    assert json.loads(baseline.read_text(encoding="utf-8")) == _scan(["/api/nieuw"])
