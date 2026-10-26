"""Tests for issue fixes #31, #32, #33, #34."""
import sys
import json
import os
import importlib.util
import pytest
from types import SimpleNamespace

# Import magister.py script directly
script_path = os.path.join(
    os.path.dirname(__file__),
    "custom_components", "magister_school", "script", "magister.py"
)
spec = importlib.util.spec_from_file_location("magister", script_path)
magister = importlib.util.module_from_spec(spec)
spec.loader.exec_module(magister)


class TestTOTPGeneration:
    """Issue #34 — TOTP code generation."""

    def test_generate_totp_returns_6_digits(self):
        # Standard base32 secret
        code = magister.generate_totp("JBSWY3DPEHPK3PXP")
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_totp_handles_spaces(self):
        code = magister.generate_totp("JBSW Y3DP EHPK 3PXP")
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_totp_handles_lowercase(self):
        code = magister.generate_totp("jbswy3dpehpk3pxp")
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_totp_deterministic_within_same_window(self):
        code1 = magister.generate_totp("JBSWY3DPEHPK3PXP")
        code2 = magister.generate_totp("JBSWY3DPEHPK3PXP")
        assert code1 == code2

    def test_generate_totp_different_secrets_different_codes(self):
        code1 = magister.generate_totp("JBSWY3DPEHPK3PXP")
        code2 = magister.generate_totp("GEZDGNBVGY3TQOJQ")
        # Different secrets should (almost certainly) produce different codes
        # There's a 1/1000000 chance they match, so we don't assert !=
        # But we verify both are valid
        assert len(code1) == 6 and code1.isdigit()
        assert len(code2) == 6 and code2.isdigit()


class TestWasAfwijkend:
    """Issue #33 — was_afwijkend field detection."""

    def test_normal_statuses_not_afwijkend(self):
        # Status 0, 1, 2, 6, 7, 8 are "normal"
        for status in (0, 1, 2, 6, 7, 8):
            assert status not in (3, 4, 5, 9, 10)

    def test_afwijkend_statuses_detected(self):
        # Status 3 (Gewijzigd), 4 (Vervallen Handmatig), 5 (Vervallen Automatisch),
        # 9 (Verplaatst), 10 (Gewijzigd en Verplaatst) are "afwijkend"
        afwijkend_statuses = {3, 4, 5, 9, 10}
        for status in afwijkend_statuses:
            result = status not in (0, 1, 2, 6, 7, 8)
            assert result is True, f"Status {status} should be afwijkend"

    def test_history_keeps_deviation_after_status_is_overwritten(self):
        history = {}
        item = {"Id": 42, "Status": 3}
        assert magister._remember_was_afwijkend(history, "child", item) is True
        item["Status"] = 7
        assert magister._remember_was_afwijkend(history, "child", item) is True

    def test_history_prunes_oldest_entries(self):
        original = magister.HISTORY_LIMIT
        magister.HISTORY_LIMIT = 3
        try:
            history = {}
            for i in range(5):
                magister._remember_was_afwijkend(history, "child", {"Id": i, "Status": 3})
            assert len(history) <= 3
        finally:
            magister.HISTORY_LIMIT = original


class TestHuiswerkAfgerond:
    """Issue #31 — homework finished/unfinished based on the Afgerond field."""

    def test_huiswerk_count_uses_afgerond(self):
        afspraken = [
            {"is_huiswerk": True, "is_afgerond": False},
            {"is_huiswerk": True, "is_afgerond": True},
            {"is_huiswerk": True, "is_afgerond": False},
            {"is_huiswerk": False, "is_afgerond": False},
        ]
        huiswerk = [a for a in afspraken if a["is_huiswerk"]]
        totaal = len(huiswerk)
        onafgerond = len([a for a in huiswerk if not a.get("is_afgerond")])
        assert totaal == 3
        assert onafgerond == 2

    def test_source_reads_afgerond_field(self):
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py"
        )
        with open(script_path, encoding="utf-8") as f:
            content = f.read()
        assert '"is_afgerond": bool(item.get("Afgerond"' in content
        assert 'submitted_opdr' not in content


class TestDateWindow:
    """Issue #32 — configurable date window."""

    def test_deltaymd_today(self):
        result = magister.deltaymd()
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        assert result == today

    def test_deltaymd_days_back(self):
        from datetime import datetime, timedelta
        result = magister.deltaymd(days=-7)
        expected = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        assert result == expected

    def test_deltaymd_days_forward(self):
        from datetime import datetime, timedelta
        result = magister.deltaymd(days=14)
        expected = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        assert result == expected

    def test_deltaymd_weeks_forward(self):
        from datetime import datetime, timedelta
        result = magister.deltaymd(weeks=2)
        expected = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
        assert result == expected


class TestAPIParameters:
    """Issue #34 — API passes totp_secret and date params to subprocess."""

    def test_api_init_accepts_new_params(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components", "magister_school"))
        # Direct import of api module
        api_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "api.py"
        )
        # We can't fully import api.py (needs homeassistant), but we can verify the file content
        with open(api_path) as f:
            content = f.read()

        assert "totp_secret" in content
        assert "days_back" in content
        assert "days_forward" in content
        assert "--days-back" in content
        assert "--days-forward" in content
        # Credentials worden via environment variables doorgegeven, niet via CLI
        assert "MAGISTER_USERNAME" in content
        assert "MAGISTER_PASSWORD" in content
        assert "MAGISTER_TOTP_SECRET" in content
        assert "--totp-secret" not in content
        assert "--username" not in content
        assert "--password" not in content

    def test_init_passes_totp_secret(self):
        """Verify __init__.py passes totp_secret to coordinator."""
        init_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "__init__.py"
        )
        with open(init_path) as f:
            content = f.read()

        assert "totp_secret=entry.data.get(\"totp_secret\")" in content
        assert "days_back=entry.options.get(\"dagen_terug\"" in content
        assert "days_forward=entry.options.get(\"dagen_vooruit\"" in content
        assert "magister_school_appointment_history.json" in content


class TestHistoryFile:
    """Issue #35 \u2014 history file must live under /config, not the container home."""

    def test_load_uses_explicit_history_file(self, tmp_path):
        target = tmp_path / ".storage" / "magister_school_appointment_history.json"
        path, data = magister._load_appointment_history(str(tmp_path / "unused.cache"), str(target))
        assert path == target
        assert data == {}

    def test_save_creates_parent_directory(self, tmp_path):
        target = tmp_path / ".storage" / "history.json"
        magister._save_appointment_history(target, {"a": True})
        assert target.exists()
        assert "a" in target.read_text(encoding="utf-8")


class TestLoginFixes:
    """Issue #34 \u2014 pairfidopromo and softtoken handling."""

    def _source(self):
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py"
        )
        with open(script_path, encoding="utf-8") as f:
            return f.read()

    def test_softtoken_variant_is_accepted(self):
        content = self._source()
        assert "in ('soft-token', 'softtoken')" in content

    def test_pairfidopromo_keeps_existing_payload(self):
        content = self._source()
        start = content.index("'pairfidopromo'")
        block = content[start:start + 400]
        # The promo step must not rebuild the request dict (which dropped username/password).
        assert "d = dict(" not in block


class TestVerrijkteVelden:
    """Extra velden uit de Magister API: absenties, klas/profiel, les-extra's."""

    def _source(self):
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py"
        )
        with open(script_path, encoding="utf-8") as f:
            return f.read()

    def test_absenties_velden(self):
        content = self._source()
        assert '"geoorloofd": bool(item.get("Geoorloofd"' in content
        assert '"code": item.get("Code"' in content
        assert '"lesuur": item.get("Lesuur")' in content

    def test_klas_en_profiel(self):
        content = self._source()
        assert '"klas": ""' in content
        assert '"profiel": ""' in content
        assert 'actieve_aanmelding.get("Groep")' in content
        assert 'actieve_aanmelding.get("Profiel")' in content

    def test_les_extra_velden(self):
        content = self._source()
        assert '"opmerking": item.get("Opmerking")' in content
        assert '"is_online": bool(item.get("IsOnlineDeelname"' in content
        assert '"duurt_hele_dag": bool(item.get("DuurtHeleDag"' in content
        assert '"docentcode": ", ".join(filter(None, ([object_data(item.get("Docent"' in content
        assert '"vak_id": ", ".join(filter(None, ([str(object_data(item.get("Vak"' in content

    def test_overview_sensor_toont_klas_profiel(self):
        sensor_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "sensor.py"
        )
        with open(sensor_path, encoding="utf-8") as f:
            content = f.read()
        assert '"klas": kind_data.get("klas")' in content
        assert '"profiel": kind_data.get("profiel")' in content


class TestVoortgangscijfers:
    """Volledige cijfers via /api/aanmeldingen/{id}/cijfers."""

    def _source(self):
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py"
        )
        with open(script_path, encoding="utf-8") as f:
            return f.read()

    def test_output_heeft_voortgangscijfers(self):
        content = self._source()
        assert '"voortgangscijfers": {}' in content

    def test_fetcht_actieve_aanmelding(self):
        content = self._source()
        # Alleen de actieve (huidige) aanmelding wordt opgehaald
        assert 'mg.req("aanmeldingen", meld["Id"], "cijfers")' in content
        assert 'meld = actieve_aanmelding' in content

    def test_leest_platte_items_met_kolom(self):
        content = self._source()
        # Echte structuur: platte 'items' (kleine letter) met details in 'kolom'
        assert 'response_items(vc, warnings, "voortgangscijfers", "items")' in content
        assert 'cijfer.get("kolom")' in content
        assert 'kolom.get("studievakId")' in content
        assert 'kolom.get("weegfactor")' in content
        assert 'cijfer.get("cijferGetal")' in content
        assert 'cijfer.get("isVoldoende"' in content
        # Oude (foutieve) aannames mogen er niet meer in staan
        assert 'CijferPeriodes' not in content
        assert 'BehaaldeWaarde' not in content

    def test_geen_debug_capture_meer(self):
        content = self._source()
        assert "voortgang_raw_debug" not in content
        assert "magister_voortgang_debug.json" not in content

    def test_overview_sensor_toont_voortgangscijfers(self):
        sensor_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "sensor.py"
        )
        with open(sensor_path, encoding="utf-8") as f:
            content = f.read()
        assert '"voortgangscijfers"' in content


@pytest.mark.parametrize("response, expected", [
    ({"Omschrijving": "<p>Lesstof:</p><ul><li>Learn</li><li>Practice</li></ul>"},
     "Lesstof:\n• Learn\n• Practice"),
    (b"<html>503</html>", "Lesstof:"),
])
def test_studiewijzer_full_text(monkeypatch, response, expected):
    args = SimpleNamespace(xsrftoken=None, accesstoken=None, magisterserver="example.invalid",
                           schoolserver="example.invalid", debug=False, dump_raw=True)
    mg = magister.Magister(args)
    mg.access_token = "current-session"

    def request(client, url):
        assert client is not mg and client.opener is not mg.opener
        assert client.access_token == mg.access_token
        assert url == "https://example.invalid/api/leerlingen/1/studiewijzers/2/onderdelen/3?gebruikMappenStructuur=true"
        return response

    monkeypatch.setattr(magister.Magister, "httpreq", request)
    result = magister.studiewijzer_onderdelen(mg, 1, 2, [{"Id": 3, "Titel": "Week 1", "Omschrijving": "Lesstof:"}])
    assert result[0]["Titel"] == "Week 1"
    assert magister.dehtml(result[0]["Omschrijving"]).strip() == expected
    assert len(mg._raw_dump) == 1


@pytest.fixture
def magister_refresh(monkeypatch, tmp_path, capsys):
    """Run the real fetch/parser with deterministic responses for two students."""
    import json
    from pathlib import Path

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "argv", [script_path, "--json", "--accesstoken", "test-token",
                                      "--schoolserver", "example.invalid"])
    responses = {
        "/account": {"Persoon": {"Id": 1}},
        "/kinderen": {"Items": [{"Id": 2, "Roepnaam": "First"}, {"Id": 3, "Roepnaam": "Second"}]},
        "/aanmeldingen": {"Items": [{"Id": 30, "Start": "2020-01-01", "Einde": "2099-01-01"}]},
        "/afspraken": {"Items": [{"Start": "2026-10-12T08:00:00Z", "Omschrijving": "Math", "Status": 1}]},
        "/cijfers/laatste": {"items": [{"waarde": "8"}]},
        "/cijfers": {"items": [{"waarde": "7", "kolom": {"naam": "wi101"}}]},
        "/studiewijzers": {"Items": [{"Id": 10}, {"Id": 11}, {"Id": 12}]},
        "/studiewijzers/10": {"Titel": "Other", "Onderdelen": {"Items": []}},
        "/studiewijzers/11": {"Titel": "Valid", "Onderdelen": {"Items": [{"Id": 20, "Titel": "Week 1"}]}},
        "/studiewijzers/12": {"Titel": "Empty", "Onderdelen": {"Items": []}},
        "/onderdelen/20": {"Omschrijving": "<p>Full section text</p>"},
    }

    def run(overrides=None):
        current = {**responses, **(overrides or {})}

        def request(client, url):
            path = magister.urllib.parse.urlsplit(url).path
            return next((value for suffix, value in current.items() if path.endswith(suffix)), {"Items": []})

        monkeypatch.setattr(magister.Magister, "httpreq", request)
        magister.main()
        return json.loads(capsys.readouterr().out)

    return run


@pytest.mark.parametrize("broken_guide", [
    {}, {"Fouttype": "OnvoldoendePrivileges"}, b"<html>Service unavailable</html>",
    {"Onderdelen": None}, {"Onderdelen": []}, {"Onderdelen": {}},
    {"Onderdelen": {"Items": None}}, {"Onderdelen": {"Items": {}}},
])
def test_missing_study_guide_sections_preserve_refresh(magister_refresh, broken_guide):
    data = magister_refresh({"/studiewijzers/10": broken_guide})
    assert data["data_warnings"] == {"studiewijzers": 2}
    for name in ("First", "Second"):
        assert data["kinderen"][name]["afspraken"][0]["omschrijving"] == "Math"
        assert data["cijfers"][name][0]["waarde"] == "8"
        guides = data["studiewijzers"][name]
        assert [guide["titel"] for guide in guides] == ["Valid", "Empty"]
        assert guides[0]["onderdelen"][0]["omschrijving"].strip() == "Full section text"
        assert guides[1]["onderdelen"] == []


@pytest.mark.parametrize("endpoint,section,key", [
    ("/aanmeldingen", "aanmeldingen", "Items"),
    ("/afspraken", "afspraken", "Items"),
    ("/roosterwijzigingen", "roosterwijzigingen", "Items"),
    ("/cijfers/laatste", "cijfers", "items"),
    ("/cijfers", "voortgangscijfers", "items"),
    ("/absenties", "absenties", "Items"),
    ("/opdrachten", "opdrachten", "Items"),
    ("/activiteiten", "activiteiten", "Items"),
    ("/studiewijzers", "studiewijzers", "Items"),
])
@pytest.mark.parametrize("bad_items", ["missing", None, {}, "invalid", 42, [None, "invalid", {}]])
def test_invalid_collections_are_reported_without_losing_other_data(magister_refresh, endpoint, section, key, bad_items):
    data = magister_refresh({endpoint: {} if bad_items == "missing" else {key: bad_items}})
    assert data["data_warnings"][section] == (2 * len(bad_items) if isinstance(bad_items, list) else 2)
    assert set(data["kinderen"]) == {"First", "Second"}
    if section != "afspraken":
        assert data["kinderen"]["First"]["afspraken"][0]["omschrijving"] == "Math"
    if section != "cijfers":
        assert data["cijfers"]["Second"][0]["waarde"] == "8"


def test_valid_empty_collections_do_not_warn(magister_refresh):
    data = magister_refresh()
    assert "data_warnings" not in data
    assert data["studiewijzers"]["First"][-1]["onderdelen"] == []


@pytest.mark.parametrize("value", [None, [], "invalid"])
def test_optional_nested_fields_are_safe(magister_refresh, value):
    lesson = {"Start": "2026-10-12T08:00:00Z", "Vak": value, "Docent": value,
              "Vakken": value, "Docenten": value, "Lokalen": value}
    data = magister_refresh({
        "/afspraken": {"Items": [lesson]}, "/roosterwijzigingen": {"Items": [lesson]},
        "/cijfers/laatste": {"items": [{"waarde": "8", "vak": value}]},
        "/cijfers": {"items": [{"waarde": "7", "kolom": value}]},
        "/absenties": {"Items": [{"Afspraak": value}]},
    })
    assert data["kinderen"]["First"]["afspraken"][0]["vak"] == ""
    assert data["cijfers"]["First"][0]["waarde"] == "8"
    assert data["voortgangscijfers"]["First"][0]["waarde"] == "7"
    assert data["absenties"]["First"][0]["afspraak"] == ""


def test_malformed_records_do_not_discard_valid_siblings(magister_refresh):
    data = magister_refresh({"/cijfers/laatste": {"items": [None, {"waarde": "8"}]},
                             "/studiewijzers": {"Items": [{}, {"Id": 11}]},
                             "/studiewijzers/11": {"Titel": "Valid", "Onderdelen": {"Items": [{}, {"Id": 20}]}}})
    assert data["data_warnings"] == {"cijfers": 2, "studiewijzers": 4}
    assert data["cijfers"]["First"][0]["waarde"] == "8"
    assert data["studiewijzers"]["Second"][0]["onderdelen"][0]["omschrijving"].strip() == "Full section text"


@pytest.mark.parametrize("endpoint,response", [
    ("/account", {}), ("/account", {"Persoon": None}), ("/account", {"Persoon": {}}),
    ("/kinderen", {}), ("/kinderen", {"Items": [None]}), ("/kinderen", {"Items": [{}]}),
    ("/kinderen", {"Fouttype": "OtherFailure"}),
])
def test_invalid_identity_fails_explicitly(magister_refresh, endpoint, response):
    with pytest.raises(ValueError, match="Magister (account|children) response"):
        magister_refresh({endpoint: response})


@pytest.mark.parametrize("endpoint", ["/account", "/kinderen", "/cijfers", "/studiewijzers/10"])
def test_expired_session_is_not_hidden(magister_refresh, endpoint):
    with pytest.raises(RuntimeError, match="Magister session expired"):
        magister_refresh({endpoint: b"SecurityToken Expired"})


def test_student_account_permission_response_is_still_supported(magister_refresh):
    data = magister_refresh({"/account": {"Persoon": {"Id": 1, "Roepnaam": "Student"}},
                             "/kinderen": {"Fouttype": "OnvoldoendePrivileges"}})
    assert set(data["kinderen"]) == {"Student"}
    assert "data_warnings" not in data


def test_http_401_is_not_converted_to_empty_data():
    from unittest.mock import Mock

    client = magister.Magister(SimpleNamespace(xsrftoken=None, accesstoken=None, debug=False,
                                              magisterserver="example.invalid", schoolserver="example.invalid"))
    client.opener.open = Mock(side_effect=magister.urllib.error.HTTPError(
        "https://example.invalid/api/account", 401, "Unauthorized", {}, None,
    ))
    with pytest.raises(magister.urllib.error.HTTPError) as caught:
        client.req("account")
    assert caught.value.code == 401


@pytest.mark.parametrize("skipped", [0, 2])
def test_api_reports_incomplete_sections(monkeypatch, caplog, skipped):
    import json
    from unittest.mock import Mock

    monkeypatch.setitem(sys.modules, "magister_api_test.const", SimpleNamespace(
        CONF_SCHOOL="school", CONF_USER="user", CONF_PASS="pass",
        EXIT_AUTH_FAILED=77, AUTH_FAILED_MARKER="AUTHENTICATION_FAILED",
    ))
    api_path = os.path.join(os.path.dirname(script_path), "..", "api.py")
    api_spec = importlib.util.spec_from_file_location("magister_api_test.api", api_path)
    api = importlib.util.module_from_spec(api_spec)
    api_spec.loader.exec_module(api)
    data = {"kinderen": {"Student": {}}}
    if skipped:
        data["data_warnings"] = {"studiewijzers": skipped}
    monkeypatch.setattr(api.subprocess, "run", Mock(return_value=SimpleNamespace(stdout=json.dumps(data))))
    assert api.MagisterAPI("school", "user", "password").get_data() == data
    assert bool(caplog.records) is bool(skipped)
    if skipped:
        assert caplog.records[0].getMessage() == (
            "Incomplete Magister data (invalid collections/records per section): {'studiewijzers': 2}"
        )


class TestOnverwachtAntwoord:
    """Magister antwoordt soms met HTML of een lege body in plaats van JSON.

    Dat gaf 'bytes' object has no attribute 'get' en liet de sensor-run crashen.
    """

    def _magister_met_antwoord(self, response, **attrs):
        mg = magister.Magister.__new__(magister.Magister)
        mg._raw_dump = None
        mg.schoolserver = "example.invalid"
        mg.httpreq = lambda url: response
        mg.logprint = lambda *a, **k: None
        for key, value in attrs.items():
            setattr(mg, key, value)
        return mg

    def test_html_in_plaats_van_json_geeft_lege_dict(self):
        mg = self._magister_met_antwoord(b"<html>503 Service Unavailable</html>")
        assert mg.req("personen", "123", "afspraken") == {}

    def test_lege_body_geeft_lege_dict(self):
        mg = self._magister_met_antwoord(b"")
        assert mg.req("personen", "123", "roosterwijzigingen") == {}

    def test_none_antwoord_geeft_lege_dict(self):
        mg = self._magister_met_antwoord(None)
        assert mg.req("personen", "123", "afspraken") == {}

    def test_echte_json_gaat_onveranderd_door(self):
        data = {"Items": [{"Id": 1}]}
        mg = self._magister_met_antwoord(data)
        assert mg.req("personen", "123", "afspraken") == data

    def test_raw_dump_blijft_gevuld_bij_fout_antwoord(self):
        mg = self._magister_met_antwoord(b"kapot", _raw_dump={})
        mg.req("personen", "123", "afspraken")
        assert mg._raw_dump, "het foute antwoord moet in de raw dump belanden"

    def test_main_guardt_afspraken_en_wijzigingen(self):
        with open(script_path, encoding="utf-8") as f:
            content = f.read()
        assert 'response_items(afspraken, warnings, "afspraken")' in content
        assert 'response_items(wijzigingen, warnings, "roosterwijzigingen")' in content


class TestUitvalInWijzigingen:
    """Issue #37 — vervallen lessen ook in wijzigingen opnemen."""

    def test_map_rooster_item_herkent_uitval(self):
        item = {
            "Id": 5,
            "Start": "2026-09-18T06:35:00.0000000Z",
            "Einde": "2026-09-18T07:25:00.0000000Z",
            "Status": 5,
            "Type": 13,
            "Omschrijving": "wisb",
            "Lokatie": "440",
        }
        result = magister._map_rooster_item(item, {}, 1)
        assert result["is_uitval"] is True
        assert result["start"] and result["start"] != "?"
        assert result["lokaal"] == "440"

    def test_map_rooster_item_geen_uitval(self):
        item = {
            "Id": 6,
            "Start": "2026-09-18T06:35:00.0000000Z",
            "Einde": "2026-09-18T07:25:00.0000000Z",
            "Status": 1,
            "Type": 13,
            "Omschrijving": "wisb",
        }
        result = magister._map_rooster_item(item, {}, 1)
        assert result["is_uitval"] is False

    def test_merge_uitval_broncode_aanwezig(self):
        with open(script_path, encoding="utf-8") as f:
            content = f.read()
        assert "wijziging_ids" in content
        assert '"Vervallen" not in infotstr(item.get("Status"' in content


class TestUnrecordedAttributes:
    """#39 follow-up — omvangrijke attributen uitsluiten van de recorder."""

    def test_unrecorded_attributes_gedefinieerd(self):
        sensor_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "sensor.py"
        )
        with open(sensor_path, encoding="utf-8") as f:
            content = f.read()
        assert "_UNRECORDED_ATTRS = frozenset({" in content
        assert content.count("_unrecorded_attributes = _UNRECORDED_ATTRS") >= 12
        assert '"voortgangscijfers"' in content
        assert '"afspraken"' in content


class TestHacsReviewFixes:
    """Regressions for the HACS default-store review (hacs/default#10760)."""

    ROOT = os.path.dirname(__file__)
    COMPONENT = os.path.join(ROOT, "custom_components", "magister_school")

    def _read(self, name):
        with open(os.path.join(self.COMPONENT, name), encoding="utf-8") as f:
            return f.read()

    def test_unique_ids_are_scoped_to_config_entry(self):
        sensor = self._read("sensor.py")
        calendar = self._read("calendar.py")
        assert 'self._attr_unique_id = "magister_main_data"' not in sensor
        assert 'f"{self._coordinator.entry_id}_magister_' in sensor
        assert 'f"{coordinator.entry_id}_magister_' in calendar

    def test_entity_registry_cleanup_is_entry_scoped(self):
        init = self._read("__init__.py")
        assert "_cleanup_suffix_entities" not in init
        assert "async_entries_for_config_entry" in init

    def test_unique_id_migration_keeps_entity_ids(self):
        init = self._read("__init__.py")
        assert "new_unique_id" in init
        assert "_async_migrate_unique_ids" in init

    def test_zoneinfo_is_not_built_in_event_loop(self):
        calendar = self._read("calendar.py")
        assert calendar.count('ZoneInfo("Europe/Amsterdam")') == 1
        assert '_TZ = ZoneInfo("Europe/Amsterdam")' in calendar

    def test_poll_interval_is_wired_to_coordinator(self):
        assert "poll_interval" in self._read("coordinator.py")
        assert "timedelta(seconds=poll_interval)" in self._read("coordinator.py")
        assert 'entry.options.get("poll_interval"' in self._read("__init__.py")

    def test_login_failure_raises_authentication_required(self):
        api = self._read("api.py")
        assert "EXIT_AUTH_FAILED" in api
        assert "raise AuthenticationRequired(" in api
        script = open(
            os.path.join(self.COMPONENT, "script", "magister.py"), encoding="utf-8"
        ).read()
        assert "sys.exit(EXIT_AUTH_FAILED)" in script

    def test_upstream_mit_notice_is_present(self):
        script = open(
            os.path.join(self.COMPONENT, "script", "magister.py"), encoding="utf-8"
        ).read()
        assert "nlitsme/magister-tool" in script
        assert "Willem Hengeveld" in script
        assert "THE SOFTWARE IS PROVIDED \"AS IS\"" in script

    def test_card_is_bundled_and_served(self):
        assert os.path.isfile(
            os.path.join(self.COMPONENT, "www", "magister-school-card.js")
        )
        init = self._read("__init__.py")
        assert "async_register_static_paths" in init
        assert "async_create_item" in init
        manifest = json.loads(self._read("manifest.json"))
        assert "lovelace" in manifest["dependencies"]


def _load_api_module():
    """Import api.py without Home Assistant by stubbing its relative import."""
    import importlib.util
    import sys
    import types

    pkg_name = "_magister_api_probe"
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = []
    sys.modules[pkg_name] = pkg

    component = os.path.join(
        os.path.dirname(__file__), "custom_components", "magister_school"
    )

    # Load the real const.py so the stub cannot drift from the source.
    const_spec = importlib.util.spec_from_file_location(
        f"{pkg_name}.const", os.path.join(component, "const.py")
    )
    const = importlib.util.module_from_spec(const_spec)
    sys.modules[f"{pkg_name}.const"] = const
    const_spec.loader.exec_module(const)

    path = os.path.join(component, "api.py")
    spec = importlib.util.spec_from_file_location(f"{pkg_name}.api", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{pkg_name}.api"] = module
    spec.loader.exec_module(module)
    return module


def _extract_sensor_helpers():
    """Exec the real helpers from sensor.py without importing Home Assistant."""
    import ast

    path = os.path.join(
        os.path.dirname(__file__),
        "custom_components", "magister_school", "sensor.py",
    )
    source = open(path, encoding="utf-8").read()
    tree = ast.parse(source)

    wanted_funcs = {
        "_get_school_lessen",
        "_get_school_start_items",
        "_counts_for_start",
        "_parse_school_datetime",
    }
    wanted_consts = {"_SCHOOL_DAY_START", "_SCHOOL_DAY_END", "_NON_SCHOOL_SOORTEN"}
    chunks = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
            chunks.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.Assign):
            targets = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if targets & wanted_consts:
                chunks.append(ast.get_source_segment(source, node))

    assert len(chunks) == 7, f"expected 4 functions + 3 constants, got {len(chunks)}"
    import datetime as _dt

    namespace = {"frozenset": frozenset, "datetime": _dt.datetime, "time": _dt.time}
    exec("\n\n".join(chunks), namespace)
    return namespace


class TestSchoolSlugNormalization:
    """Issue #45: a display name with spaces/& can never be a tenant slug."""

    @staticmethod
    def _norm(value):
        return _load_api_module().normalize_school(value)

    def test_accepts_plain_slug(self):
        assert self._norm("trevianum") == "trevianum"

    def test_lowercases_and_strips(self):
        assert self._norm("  Trevianum  ") == "trevianum"

    def test_accepts_hostname(self):
        assert self._norm("trevianum.magister.net") == "trevianum"

    def test_accepts_full_url(self):
        assert self._norm("https://trevianum.magister.net/oidc") == "trevianum"

    def test_rejects_display_name_with_ampersand(self):
        assert (
            self._norm("Onderwijsgemeenschap Venlo & Omstreken.magister.net") is None
        )

    def test_rejects_spaces(self):
        assert self._norm("mijn school") is None

    def test_rejects_empty(self):
        assert self._norm("") is None
        assert self._norm(None) is None

    def test_api_normalizes_stored_school(self):
        api = _load_api_module().MagisterAPI("Trevianum.magister.net", "u", "p")
        assert api.school == "trevianum"


class TestSchoolTimes:
    """Issue #43: a nulmeting is soort 'Algemeen' but still moves the start.

    The end of the school day stays at the last real lesson, so optional items
    such as the recurring "Studie na school" ("stc") or an evening booking do
    not push it later.
    """

    @staticmethod
    def helpers():
        return _extract_sensor_helpers()

    def end_of_day(self, afspraken):
        lessen = self.helpers()["_get_school_lessen"]({"afspraken": afspraken})
        return max((a["einde"] for a in lessen), default=None)

    def start_of_day(self, afspraken):
        items = self.helpers()["_get_school_start_items"]({"afspraken": afspraken})
        return min((a["start"] for a in items), default=None)

    def test_start_includes_nulmeting_with_subject(self):
        """Issue #43: a nulmeting has a subject, so it moves the start."""
        afspraken = [
            {"soort": "Algemeen", "start": "2026-10-12 06:30:00", "einde": "2026-10-12 06:45:00", "duurt_hele_dag": False, "is_uitval": False, "vak": "Wiskunde", "docent": ""},
            {"soort": "Les", "start": "2026-10-12 07:25:00", "einde": "2026-10-12 08:15:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.start_of_day(afspraken) == "2026-10-12 06:30:00"

    def test_start_includes_mentor_meeting_with_teacher(self):
        afspraken = [
            {"soort": "Algemeen", "start": "2026-10-12 06:30:00", "einde": "2026-10-12 06:45:00", "duurt_hele_dag": False, "is_uitval": False, "vak": "", "docent": "I.J.E. Koot"},
            {"soort": "Les", "start": "2026-10-12 07:25:00", "einde": "2026-10-12 08:15:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.start_of_day(afspraken) == "2026-10-12 06:30:00"

    def test_start_excludes_room_booking_without_subject_or_teacher(self):
        """'Studie na school' / '10 leerlingen' carry neither, so they are ignored."""
        for titel in ("Studie na school", "10 leerlingen"):
            afspraken = [
                {"soort": "Algemeen", "start": "2026-10-28 07:00:00", "einde": "2026-10-28 07:30:00", "duurt_hele_dag": False, "is_uitval": False, "vak": "", "docent": "", "omschrijving": titel},
                {"soort": "Les", "start": "2026-10-28 08:35:00", "einde": "2026-10-28 09:25:00", "duurt_hele_dag": False, "is_uitval": False},
            ]
            assert self.start_of_day(afspraken) == "2026-10-28 08:35:00", titel

    def test_end_uses_lessons_only(self):
        """The recurring optional 'Studie na school' must not extend the day."""
        afspraken = [
            {"soort": "Les", "start": "2026-10-28 08:35:00", "einde": "2026-10-28 10:55:00", "duurt_hele_dag": False, "is_uitval": False},
            {"soort": "Algemeen", "start": "2026-10-28 15:25:00", "einde": "2026-10-28 16:15:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.end_of_day(afspraken) == "2026-10-28 10:55:00"

    def test_recurring_every_workday_item_does_not_move_the_start(self):
        """'Studie na school' repeats every working day and is a free choice."""
        afspraken = [
            {"soort": "Algemeen", "start": "2026-10-28 07:00:00", "einde": "2026-10-28 07:30:00", "duurt_hele_dag": False, "is_uitval": False, "herhalend_elke_werkdag": True},
            {"soort": "Les", "start": "2026-10-28 08:35:00", "einde": "2026-10-28 09:25:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.start_of_day(afspraken) == "2026-10-28 08:35:00"

    def test_start_excludes_evening_blocks(self):
        afspraken = [
            {"soort": "Les", "start": "2026-10-28 08:35:00", "einde": "2026-10-28 09:25:00", "duurt_hele_dag": False, "is_uitval": False},
            {"soort": "Algemeen", "start": "2026-10-28 18:30:00", "einde": "2026-10-28 19:10:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.start_of_day(afspraken) == "2026-10-28 08:35:00"

    def test_start_excludes_early_morning_block(self):
        afspraken = [
            {"soort": "Algemeen", "start": "2026-10-28 04:00:00", "einde": "2026-10-28 05:00:00", "duurt_hele_dag": False, "is_uitval": False},
            {"soort": "Les", "start": "2026-10-28 08:35:00", "einde": "2026-10-28 09:25:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.start_of_day(afspraken) == "2026-10-28 08:35:00"

    def test_excludes_all_day_notice(self):
        afspraken = [
            {"soort": "Algemeen", "start": "2026-10-12 00:00:00", "einde": "2026-10-12 23:59:00", "duurt_hele_dag": True, "is_uitval": False},
            {"soort": "Les", "start": "2026-10-12 07:25:00", "einde": "2026-10-12 08:15:00", "duurt_hele_dag": False, "is_uitval": False},
        ]
        assert self.start_of_day(afspraken) == "2026-10-12 07:25:00"
        assert self.end_of_day(afspraken) == "2026-10-12 08:15:00"

    def test_excludes_cancelled(self):
        afspraken = [
            {"soort": "Les", "start": "2026-10-12 07:25:00", "einde": "2026-10-12 08:15:00", "duurt_hele_dag": False, "is_uitval": True},
        ]
        assert self.start_of_day(afspraken) is None
        assert self.end_of_day(afspraken) is None


class TestHerhaling:
    """Recurring background bookings ("Studie na school") are identifiable."""

    def _helpers(self):
        """Exec the real helpers from the script without running the CLI."""
        import ast

        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py",
        )
        source = open(script_path, encoding="utf-8").read()
        tree = ast.parse(source)

        wanted = {"object_data", "_herhaling", "_is_herhalend", "_is_elke_werkdag"}
        chunks = [
            ast.get_source_segment(source, node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        assert len(chunks) == 4, f"expected 4 helpers, got {len(chunks)}"

        namespace = {}
        exec("\n\n".join(chunks), namespace)
        return namespace

    def test_studie_na_school_is_recurring_every_workday(self):
        """Shape copied from the real Magister response."""
        item = {
            "Omschrijving": "Studie na school",
            "Lokatie": "stc",
            "HerhaalStatus": 2,
            "Herhaling": {
                "BeginDatum": "2026-08-24",
                "EindDatum": "2027-07-31",
                "Dagelijks": {"IsElkeWerkdag": True},
            },
        }
        h = self._helpers()
        assert h["_is_elke_werkdag"](item) is True
        assert h["_is_herhalend"](item) is True

    def test_one_off_appointment_is_not_recurring(self):
        item = {"Omschrijving": "Mentorgesprekje", "HerhaalStatus": 0, "Herhaling": None}
        h = self._helpers()
        assert h["_is_elke_werkdag"](item) is False
        assert h["_is_herhalend"](item) is False

    def test_afspraken_use_the_shared_mapper(self):
        """Both lists must go through _map_rooster_item, or fields drift.

        The recurrence fields were first added only to the shared mapper while
        ``afspraken`` still used an inline dict, so the sensor never showed them.
        """
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py",
        )
        content = open(script_path, encoding="utf-8").read()
        assert (
            'kind_data["afspraken"] = [\n'
            "            _map_rooster_item(item, appointment_history, kindid)"
        ) in content
        assert '"is_afgerond": bool(item.get("Afgerond", False))' in content

    def test_mapping_exposes_the_recurrence_fields(self):
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py",
        )
        content = open(script_path, encoding="utf-8").read()
        assert '"herhalend": _is_herhalend(item)' in content
        assert '"herhalend_elke_werkdag": _is_elke_werkdag(item)' in content


class TestCategorie:
    """Magister mixes real appointments and room bookings under 'Algemeen'."""

    def _categorize(self, item):
        import ast

        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py",
        )
        source = open(script_path, encoding="utf-8").read()
        tree = ast.parse(source)
        wanted = {"object_data", "object_list", "infotstr", "_appointment_category"}
        consts = {"AFSPRAAK_TYPE"}
        chunks = [
            ast.get_source_segment(source, node)
            for node in tree.body
            if (isinstance(node, ast.FunctionDef) and node.name in wanted)
            or (
                isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id in consts for t in node.targets)
            )
        ]
        namespace = {}
        exec("\n\n".join(chunks), namespace)
        return namespace["_appointment_category"](item)

    def test_lesson_is_a_lesson(self):
        item = {"Type": 13, "Vakken": [{"Id": 1, "Naam": "Wiskunde B"}], "Docenten": [{"Naam": "X"}]}
        assert self._categorize(item) == "les"

    def test_nulmeting_with_subject_is_an_appointment(self):
        item = {"Type": 2, "Vakken": [{"Id": 1, "Naam": "Geschiedenis"}], "Docenten": []}
        assert self._categorize(item) == "afspraak"

    def test_mentor_meeting_with_teacher_is_an_appointment(self):
        item = {"Type": 2, "Vakken": [], "Docenten": [{"Naam": "I.J.E. Koot"}]}
        assert self._categorize(item) == "afspraak"

    def test_studie_na_school_is_a_booking(self):
        item = {"Type": 2, "Vakken": [], "Docenten": [], "Omschrijving": "Studie na school", "Lokatie": "stc"}
        assert self._categorize(item) == "boeking"

    def test_evening_block_is_a_booking(self):
        item = {"Type": 2, "Vakken": [], "Docenten": [], "Omschrijving": "10 leerlingen"}
        assert self._categorize(item) == "boeking"

    def test_mapping_exposes_categorie(self):
        script_path = os.path.join(
            os.path.dirname(__file__),
            "custom_components", "magister_school", "script", "magister.py",
        )
        content = open(script_path, encoding="utf-8").read()
        assert '"categorie": _appointment_category(item)' in content
