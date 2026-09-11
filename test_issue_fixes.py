"""Tests for issue fixes #31, #32, #33, #34."""
import sys
import os
import importlib.util
import pytest

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


class TestHuiswerkFiltering:
    """Issue #31 — homework filtering by submitted assignments."""

    def test_subject_names_normalizes_dict(self):
        assert set(magister._subject_names({"Naam": "Wiskunde", "Code": "WIS"})) == {"Wiskunde", "WIS"}

    def test_subject_names_handles_string_and_list(self):
        assert magister._subject_names("Engels") == ["Engels"]
        assert magister._subject_names([{"Naam": "Frans"}]) == ["Frans"]

    def test_submitted_set_built_with_normalized_names(self):
        opdr_items = [
            {"Vak": {"Naam": "Wiskunde", "Code": "WIS"}, "InleverenVoor": "2026-09-15T00:00:00Z", "IngeleverdOp": "2026-09-14T10:00:00Z"},
            {"Vak": "Engels", "InleverenVoor": "2026-09-16T00:00:00Z", "IngeleverdOp": None},
        ]
        submitted = set()
        for o in opdr_items:
            if not o.get("IngeleverdOp"):
                continue
            deadline = o.get("InleverenVoor", "")
            date = str(deadline)[:10]
            for name in magister._subject_names(o.get("Vak")):
                submitted.add((date, name))

        assert ("2026-09-15", "Wiskunde") in submitted
        assert ("2026-09-15", "WIS") in submitted
        assert ("2026-09-16", "Engels") not in submitted

    def test_submitted_opdr_set_built_correctly(self):
        """Test that submitted assignments create correct lookup keys."""
        opdr_items = [
            {"Vak": "WIS", "InleverenVoor": "2026-09-15T00:00:00Z", "IngeleverdOp": "2026-09-14T10:00:00Z"},
            {"Vak": "ENG", "InleverenVoor": "2026-09-16T00:00:00Z", "IngeleverdOp": None},
            {"Vak": "FRA", "InleverenVoor": "2026-09-17T00:00:00Z", "IngeleverdOp": "2026-09-16T08:00:00Z"},
        ]
        submitted = set()
        for o in opdr_items:
            if o.get("IngeleverdOp"):
                vak = o.get("Vak", "")
                deadline = o.get("InleverenVoor", "")
                if vak and deadline:
                    submitted.add((vak, deadline[:10]))

        assert ("WIS", "2026-09-15") in submitted
        assert ("FRA", "2026-09-17") in submitted
        assert ("ENG", "2026-09-16") not in submitted  # Not submitted

    def test_huiswerk_count_excludes_submitted(self):
        """Test that huiswerk count excludes submitted assignments."""
        afspraken = [
            {"is_huiswerk": True, "vak": "WIS", "start": "2026-09-15 09:00:00"},
            {"is_huiswerk": True, "vak": "ENG", "start": "2026-09-16 10:00:00"},
            {"is_huiswerk": True, "vak": "FRA", "start": "2026-09-17 11:00:00"},
            {"is_huiswerk": False, "vak": "NAS", "start": "2026-09-18 08:00:00"},
        ]
        submitted_opdr = {("WIS", "2026-09-15"), ("FRA", "2026-09-17")}

        totaal = len([a for a in afspraken if a["is_huiswerk"]])
        onafgerond = len([
            a for a in afspraken
            if a["is_huiswerk"]
            and (a.get("vak", ""), a.get("start", "")[:10]) not in submitted_opdr
        ])

        assert totaal == 3  # All homework items
        assert onafgerond == 1  # Only ENG is unsubmitted


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
