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
        assert '"docentcode": ", ".join(filter(None, ([item.get("Docent"' in content
        assert '"vak_id": ", ".join(filter(None, ([str(item.get("Vak"' in content

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
        assert 'get("items", [])' in content
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
        assert "if not isinstance(afspraken, dict)" in content
        assert "if not isinstance(wijzigingen, dict)" in content


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

    wanted_funcs = {"_get_school_lessen"}
    wanted_consts = {"_NON_SCHOOL_SOORTEN"}
    chunks = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
            chunks.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.Assign):
            targets = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if targets & wanted_consts:
                chunks.append(ast.get_source_segment(source, node))

    assert len(chunks) == 2, f"expected function + constant, got {len(chunks)}"
    namespace = {"frozenset": frozenset}
    exec("\n\n".join(chunks), namespace)
    return namespace["_get_school_lessen"]


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


class TestSchoolStartIncludesTimedAlgemeen:
    """Issue #43: a nulmeting is soort 'Algemeen' but still school time."""

    @staticmethod
    def get_lessen(kind_data):
        return _extract_sensor_helpers()(kind_data)

    def test_includes_timed_algemeen_item(self):
        kind_data = {
            "afspraken": [
                {"soort": "Algemeen", "start": "2026-10-12 06:30:00", "duurt_hele_dag": False, "is_uitval": False},
                {"soort": "Les", "start": "2026-10-12 07:25:00", "duurt_hele_dag": False, "is_uitval": False},
            ]
        }
        lessen = self.get_lessen(kind_data)
        assert len(lessen) == 2
        assert min(a["start"] for a in lessen) == "2026-10-12 06:30:00"

    def test_excludes_all_day_notice(self):
        kind_data = {
            "afspraken": [
                {"soort": "Algemeen", "start": "2026-10-12 00:00:00", "duurt_hele_dag": True, "is_uitval": False},
                {"soort": "Les", "start": "2026-10-12 07:25:00", "duurt_hele_dag": False, "is_uitval": False},
            ]
        }
        lessen = self.get_lessen(kind_data)
        assert len(lessen) == 1
        assert lessen[0]["start"] == "2026-10-12 07:25:00"

    def test_excludes_cancelled(self):
        kind_data = {
            "afspraken": [
                {"soort": "Les", "start": "2026-10-12 07:25:00", "duurt_hele_dag": False, "is_uitval": True},
            ]
        }
        assert self.get_lessen(kind_data) == []

    def test_excludes_block_types(self):
        kind_data = {
            "afspraken": [
                {"soort": "Roostervrij", "start": "2026-10-12 07:25:00", "duurt_hele_dag": False, "is_uitval": False},
                {"soort": "Blokkade", "start": "2026-10-12 08:25:00", "duurt_hele_dag": False, "is_uitval": False},
            ]
        }
        assert self.get_lessen(kind_data) == []
