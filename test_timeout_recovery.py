"""Regression tests for timeout recovery and unavailable-data reporting."""
import asyncio
import configparser
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

ROOT = Path(__file__).parent / "custom_components" / "magister_school"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


api = load_module("magister_api", ROOT / "api.py")
script = load_module("magister_script", ROOT / "script" / "magister.py")


@pytest.mark.parametrize("failure", [
    subprocess.TimeoutExpired("python3", 90),
    subprocess.CalledProcessError(75, "python3", stderr="Magister request timed out\n"),
])
@pytest.mark.parametrize("recovers", [True, False])
def test_fetch_retries_timeout_once(monkeypatch, failure, recovers):
    data = {"kinderen": {"student": {}}}
    result = SimpleNamespace(stdout=json.dumps(data))
    run = Mock(side_effect=[failure, result if recovers else failure])
    sleep = Mock()
    monkeypatch.setattr(api.subprocess, "run", run)
    monkeypatch.setattr(api.time, "sleep", sleep)
    client = api.MagisterAPI("school", "user", "password")
    if recovers:
        assert client.get_data() == data
    else:
        with pytest.raises(TimeoutError, match="timed out"):
            client.get_data()
    assert run.call_count == 2
    assert all(call.kwargs["timeout"] == 90 for call in run.call_args_list)
    sleep.assert_called_once_with(2)


@pytest.mark.parametrize("result", [
    subprocess.CalledProcessError(1, "python3"),
    subprocess.CalledProcessError(2, "python3"),  # argparse failure, not a timeout
    SimpleNamespace(stdout="invalid JSON"),
])
def test_fetch_does_not_retry_other_errors(monkeypatch, result):
    run = Mock(side_effect=[result])
    sleep = Mock()
    monkeypatch.setattr(api.subprocess, "run", run)
    monkeypatch.setattr(api.time, "sleep", sleep)
    with pytest.raises((subprocess.CalledProcessError, json.JSONDecodeError)):
        api.MagisterAPI("school", "user", "password").get_data()
    run.assert_called_once()
    sleep.assert_not_called()


@pytest.mark.parametrize("method", ["httpreq", "httpredirurl"])
@pytest.mark.parametrize("stage", ["connect", "wrapped_connect", "read"])
def test_http_timeout_includes_safe_context(method, stage):
    args = SimpleNamespace(xsrftoken=None, accesstoken=None, magisterserver="example.invalid",
                           schoolserver="example.invalid", debug=False)
    client = script.Magister(args)
    response = MagicMock()
    response.__enter__.return_value = response
    if stage == "read":
        response.read.side_effect = TimeoutError("sensitive detail")
        client.opener.open = Mock(return_value=response)
    else:
        error = TimeoutError("sensitive detail")
        if stage == "wrapped_connect":
            error = script.urllib.error.URLError(error)
        client.opener.open = Mock(side_effect=error)
    with pytest.raises(TimeoutError, match="example.invalid timed out after") as caught:
        getattr(client, method)("https://example.invalid/private-id?token=secret")
    assert "private-id" not in str(caught.value)
    assert "secret" not in str(caught.value)
    assert "sensitive" not in str(caught.value)
    assert client.opener.open.call_args.kwargs["timeout"] == 15
    if stage == "read":
        response.__exit__.assert_called_once()


def test_script_reports_timeout_exit_code(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(sys, "argv", [str(ROOT / "script" / "magister.py"), "--json"])
    opener = Mock()
    opener.open.side_effect = TimeoutError("private error")
    monkeypatch.setattr(script.urllib.request, "build_opener", lambda *args: opener)
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(str(ROOT / "script" / "magister.py"), run_name="__main__")
    assert caught.value.code == 75
    output = capsys.readouterr()
    assert output.out == ""
    assert "accounts.magister.net timed out after" in output.err
    assert "private error" not in output.err


def test_http_response_handling_is_preserved():
    args = SimpleNamespace(xsrftoken=None, accesstoken=None, magisterserver="example.invalid",
                           schoolserver="example.invalid", debug=False)
    client = script.Magister(args)
    url = "https://example.invalid/api/account"
    response = script.urllib.error.HTTPError(url, 403, "Forbidden",
                                            {"content-type": "application/json"}, io.BytesIO(b'{"denied":true}'))
    client.opener.open = Mock(side_effect=response)
    assert client.httpreq(url) == {"denied": True}
    client.opener.open = Mock(side_effect=script.urllib.error.URLError("DNS failure"))
    with pytest.raises(script.urllib.error.URLError):
        client.httpreq(url)
    client.opener.open = Mock(side_effect=response)
    with pytest.raises(script.urllib.error.HTTPError):
        client.httpredirurl(url)


@pytest.mark.parametrize("minutes, accepted", [(-1, False), (0, False), (4, False), (5, False), (6, True)])
def test_cached_token_expires_with_safety_margin(monkeypatch, minutes, accepted):
    now = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(script, "datetime", SimpleNamespace(now=lambda: now))
    cfg = configparser.ConfigParser()
    cfg["root"] = {"expires": (now + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "accesstoken": "cached-token"}
    args = SimpleNamespace(accesstoken=None)
    # Keep date parsing independent from the fixed clock.
    monkeypatch.setattr(script, "utctime", lambda value: datetime.fromisoformat(value))
    script.apply_auth_config(cfg, args)
    assert args.accesstoken == ("cached-token" if accepted else None)


@pytest.fixture
def coordinator_module(monkeypatch):
    """Load the coordinator with only its Home Assistant boundary mocked."""
    class UpdateFailed(Exception):
        pass

    class DataUpdateCoordinator:
        def __init__(self, hass, *args, **kwargs):
            self.hass = hass

    for name in ("homeassistant", "homeassistant.helpers", "homeassistant.core",
                 "homeassistant.config_entries", "homeassistant.exceptions", "homeassistant.components"):
        monkeypatch.setitem(sys.modules, name, MagicMock())
    registry = MagicMock()
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.issue_registry", registry)
    sys.modules["homeassistant.helpers"].issue_registry = registry
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.update_coordinator", SimpleNamespace(
        DataUpdateCoordinator=DataUpdateCoordinator, UpdateFailed=UpdateFailed,
    ))
    sys.modules["homeassistant.exceptions"].ConfigEntryAuthFailed = type("ConfigEntryAuthFailed", (Exception,), {})
    package = ModuleType("magister_test")
    package.__path__ = [str(ROOT)]
    monkeypatch.setitem(sys.modules, "magister_test", package)
    monkeypatch.setitem(sys.modules, "magister_test.api", api)
    monkeypatch.setitem(sys.modules, "magister_test.const", SimpleNamespace(DOMAIN="magister_school"))
    return load_module("magister_test.coordinator", ROOT / "coordinator.py")


@pytest.mark.parametrize("failure", [TimeoutError("timed out"), {"kinderen": {}}, {}])
def test_issue_is_created_on_failure_and_cleared_on_recovery(coordinator_module, failure):
    module = coordinator_module
    entry = SimpleNamespace(entry_id="account-1", title="Magister", async_on_unload=Mock())
    data = {"kinderen": {"student": {}}}
    hass = SimpleNamespace(async_add_executor_job=AsyncMock(side_effect=[failure, data]))
    coordinator = module.MagisterDataUpdateCoordinator(hass, "school", "user", "password", entry=entry)
    with pytest.raises(module.UpdateFailed):
        asyncio.run(coordinator._async_update_data())
    module.ir.async_create_issue.assert_called_once()
    call = module.ir.async_create_issue.call_args
    assert call.args == (hass, "magister_school", "fetch_failed_account-1")
    assert call.kwargs["translation_key"] == "fetch_failed"
    module.ir.async_delete_issue.assert_not_called()
    assert asyncio.run(coordinator._async_update_data()) == data
    module.ir.async_delete_issue.assert_called_once_with(hass, "magister_school", "fetch_failed_account-1")
    module.ir.async_delete_issue.reset_mock()
    entry.async_on_unload.call_args.args[0]()
    module.ir.async_delete_issue.assert_called_once_with(hass, "magister_school", "fetch_failed_account-1")


def test_issue_translations_are_complete():
    for path in (ROOT / "strings.json", *sorted((ROOT / "translations").glob("*.json"))):
        issue = json.loads(path.read_text())["issues"]["fetch_failed"]
        assert "{name}" in issue["title"]
        assert "{error}" in issue["description"]


def test_recovery_does_not_clear_another_accounts_issue(coordinator_module):
    module = coordinator_module
    hass = SimpleNamespace(async_add_executor_job=AsyncMock(side_effect=[TimeoutError("timed out"),
                                                                        {"kinderen": {"student": {}}}]))
    clients = [module.MagisterDataUpdateCoordinator(
        hass, "school", "user", "password", entry=SimpleNamespace(
            entry_id=entry_id, title="Magister", async_on_unload=Mock(),
        ),
    ) for entry_id in ("first", "second")]
    with pytest.raises(module.UpdateFailed):
        asyncio.run(clients[0]._async_update_data())
    asyncio.run(clients[1]._async_update_data())
    assert module.ir.async_create_issue.call_args.args[2] == "fetch_failed_first"
    module.ir.async_delete_issue.assert_called_once_with(hass, "magister_school", "fetch_failed_second")
