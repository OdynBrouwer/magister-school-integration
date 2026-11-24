"""Tests for tools/magister_api_diff.py."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent

spec = importlib.util.spec_from_file_location(
    "magister_api_diff", ROOT / "tools" / "magister_api_diff.py"
)
assert spec is not None and spec.loader is not None

api_diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_diff)


def _write(tmp_path, name, payload):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_normalise_endpoint_drops_query_and_collapses_ids():
    assert (
        api_diff.normalise_endpoint(
            "personen/123/afspraken?van=2026-01-01&tot=2026-02-01"
        )
        == "personen/{id}/afspraken"
    )
    assert (
        api_diff.normalise_endpoint(
            "leerlingen/123/studiewijzers/456/onderdelen/789?gebruikMappenStructuur=true"
        )
        == "leerlingen/{id}/studiewijzers/{id}/onderdelen/{id}"
    )
    assert api_diff.normalise_endpoint("account") == "account"


def test_different_days_do_not_look_like_a_new_endpoint(tmp_path):
    """The query string changes per run; it must not create a diff."""
    baseline = _write(
        tmp_path, "a.json",
        {"personen/1/afspraken?van=2026-01-01&tot=2026-01-14": {"Items": [{"Id": 1}]}},
    )
    current = _write(
        tmp_path, "b.json",
        {"personen/1/afspraken?van=2026-02-01&tot=2026-02-14": {"Items": [{"Id": 2}]}},
    )

    report = api_diff.diff_snapshots(
        api_diff.load_dump(baseline), api_diff.load_dump(current)
    )

    assert report == {}


def test_flatten_marks_collections_and_types():
    flat = api_diff.flatten({"Items": [{"Vak": "wi", "Waarde": 7.5, "Tel": 1}]})

    assert flat == {
        "Items": "array",
        "Items[].Vak": "string",
        "Items[].Waarde": "number",
        "Items[].Tel": "number",
    }


def test_new_column_is_reported_as_added(tmp_path, capsys):
    baseline = {"personen/1/cijfers/laatste": {"items": [{"waarde": "7"}]}}
    current = {
        "personen/1/cijfers/laatste": {"items": [{"waarde": "7", "nieuweKolom": "x"}]}
    }

    report = api_diff.diff_snapshots(
        api_diff.load_dump(_write(tmp_path, "a.json", baseline)),
        api_diff.load_dump(_write(tmp_path, "b.json", current)),
    )

    endpoint = report["personen/{id}/cijfers/laatste"]
    assert endpoint["added"] == {"items[].nieuweKolom": "string"}
    assert endpoint["removed"] == {}
    assert endpoint["changed"] == {}

    api_diff.render_text(report)
    assert "+ items[].nieuweKolom" in capsys.readouterr().out


def test_removed_field_and_type_change_are_reported(tmp_path):
    baseline = {"account": {"Persoon": {"Id": 1, "Naam": "x"}}}
    current = {"account": {"Persoon": {"Id": "1"}}}

    report = api_diff.diff_snapshots(
        api_diff.load_dump(_write(tmp_path, "a.json", baseline)),
        api_diff.load_dump(_write(tmp_path, "b.json", current)),
    )

    change = report["account"]
    assert change["removed"] == {"Persoon.Naam": "string"}
    assert change["changed"] == {"Persoon.Id": ("number", "string")}
    assert change["added"] == {}


def test_missing_and_new_endpoints_are_reported(tmp_path):
    baseline = {"account": {}, "personen/1/afspraken": {"Items": []}}
    current = {"account": {}, "personen/1/absenties": {"Items": []}}

    report = api_diff.diff_snapshots(
        api_diff.load_dump(_write(tmp_path, "a.json", baseline)),
        api_diff.load_dump(_write(tmp_path, "b.json", current)),
    )

    assert report["personen/{id}/afspraken"] == {"removed_endpoint": True}
    assert report["personen/{id}/absenties"] == {"added_endpoint": True}
    assert "account" not in report


def test_cli_exit_codes(tmp_path, capsys):
    same = {"account": {"Persoon": {"Id": 1}}}
    baseline = _write(tmp_path, "a.json", same)
    identical = _write(tmp_path, "b.json", same)
    changed = _write(tmp_path, "c.json", {"account": {"Persoon": {"Id": 1, "Extra": True}}})

    assert api_diff.main([str(baseline), str(identical)]) == 0
    assert "Geen verschillen" in capsys.readouterr().out

    assert api_diff.main([str(baseline), str(changed)]) == 1
    assert "+ Persoon.Extra" in capsys.readouterr().out

    assert api_diff.main([str(baseline), str(tmp_path / "missing.json")]) == 2
    assert "Kon de dump niet lezen" in capsys.readouterr().err


def test_json_output_is_machine_readable(tmp_path, capsys):
    baseline = _write(tmp_path, "a.json", {"account": {"x": 1}})
    current = _write(tmp_path, "b.json", {"account": {"x": "1"}})

    assert api_diff.main([str(baseline), str(current), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["account"]["changed"] == {"x": ["number", "string"]}


def test_invalid_dump_shape_is_rejected(tmp_path, capsys):
    baseline = _write(tmp_path, "a.json", {"account": {}})
    invalid = tmp_path / "b.json"
    invalid.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    assert api_diff.main([str(baseline), str(invalid)]) == 2
    assert "verwacht een JSON-object" in capsys.readouterr().err
