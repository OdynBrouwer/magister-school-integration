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
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_component_module(name, filename):
    """Load a component module as part of a synthetic package.

    api.py uses relative imports (``from .const import ...``), which need a
    parent package to resolve.
    """
    pkg_name = "magister_component"
    if pkg_name not in sys.modules:
        package = ModuleType(pkg_name)
        package.__path__ = [str(ROOT)]
        sys.modules[pkg_name] = package
        load_module(f"{pkg_name}.const", ROOT / "const.py")
    return load_module(f"{pkg_name}.{name}", ROOT / filename)


api = load_component_module("api", "api.py")
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


def test_http429_is_returned_as_bounded_timeout(monkeypatch):
    args = SimpleNamespace(
        xsrftoken=None,
        accesstoken="token",
        magisterserver="example.invalid",
        schoolserver="example.invalid",
        debug=False,
        json=True,
    )
    client = script.Magister(args)
    response = script.urllib.error.HTTPError(
        "https://example.invalid/api/leerlingen/1/studiewijzers",
        429,
        "Too Many Requests",
        {"content-type": "application/json"},
        io.BytesIO(b'{"message":"Rate limit reached","secondsLeft":17}'),
    )
    client.opener.open = Mock(side_effect=response)

    with pytest.raises(TimeoutError, match="retry in 17s"):
        client.httpreq("https://example.invalid/api/leerlingen/1/studiewijzers")


@pytest.fixture
def retry_clock(monkeypatch):
    clock = SimpleNamespace(now=0.0)

    def advance(seconds):
        clock.now += seconds

    clock.sleep = Mock(side_effect=advance)
    monkeypatch.setattr(script, "time_mod", SimpleNamespace(
        monotonic=lambda: clock.now,
        sleep=clock.sleep,
    ))
    return clock


@pytest.fixture
def school_client(retry_clock):
    return script.Magister(SimpleNamespace(
        xsrftoken=None,
        accesstoken="token",
        magisterserver="example.invalid",
        schoolserver="example.invalid",
        debug=False,
    ))


@pytest.mark.parametrize(("status", "headers", "body", "delay"), [
    (200, {"content-type": "application/json"},
     b'{"message":"Rate limit reached. Reset in 3 seconds.","secondsLeft":3}', 4),
    (429, {"Retry-After": "5"}, b"", 6),
])
def test_school_fetch_retries_only_the_limited_request(school_client, retry_clock,
                                                      status, headers, body, delay):
    success_headers = {"content-type": "application/json"}
    school_client._read_response = Mock(side_effect=[
        (SimpleNamespace(status=200, headers=success_headers), b'{"Items":[1]}'),
        (SimpleNamespace(status=status, headers=headers), body),
        (SimpleNamespace(status=200, headers=success_headers), b'{"Items":[2]}'),
    ])

    assert school_client.req("afspraken") == {"Items": [1]}
    assert school_client.req("studiewijzers", 2) == {"Items": [2]}
    assert [
        call.args[0].full_url for call in school_client._read_response.call_args_list
    ] == [
        "https://example.invalid/api/afspraken",
        "https://example.invalid/api/studiewijzers/2",
        "https://example.invalid/api/studiewijzers/2",
    ]
    retry_clock.sleep.assert_called_once_with(delay)


@pytest.mark.parametrize(("elapsed", "reset"), [(0, "90"), (60, "6")])
def test_school_fetch_keeps_cooldown_within_subprocess_budget(school_client, retry_clock, elapsed, reset):
    retry_clock.now = elapsed
    school_client._read_response = Mock(return_value=(
        SimpleNamespace(status=429, headers={"Retry-After": reset}), b"",
    ))

    with pytest.raises(TimeoutError, match="Magister rate limit reached"):
        school_client.req("studiewijzers")

    assert school_client._read_response.call_count == 1
    retry_clock.sleep.assert_not_called()


def test_school_fetch_bounds_attempts_per_request(school_client, retry_clock):
    school_client._read_response = Mock(return_value=(
        SimpleNamespace(status=429, headers={"Retry-After": "1"}), b"",
    ))

    with pytest.raises(TimeoutError, match="Magister rate limit reached"):
        school_client.req("studiewijzers")

    assert school_client._read_response.call_count == 3
    assert retry_clock.sleep.call_count == 2


def test_study_guide_workers_share_the_school_cooldown(school_client, retry_clock, monkeypatch):
    school_client._rate_limit.defer(3)

    def read_response(self, request, **kwargs):
        assert retry_clock.now >= 4
        return SimpleNamespace(status=200, headers={"content-type": "application/json"}), b'{"Titel":"Week 1"}'

    monkeypatch.setattr(script.Magister, "_read_response", read_response)

    assert script.studiewijzer_onderdelen(school_client, 1, 2, [{"Id": 3}]) == [
        {"Id": 3, "Titel": "Week 1"},
    ]
    retry_clock.sleep.assert_called_once_with(4)


def test_rate_limit_wait_honors_reset_seconds(monkeypatch):
    failure = subprocess.CalledProcessError(
        75,
        "python3",
        stderr="Magister rate limit reached; retry in 17s\n",
    )
    result = SimpleNamespace(stdout=json.dumps({"kinderen": {"student": {}}}))
    run = Mock(side_effect=[failure, result])
    sleep = Mock()
    monkeypatch.setattr(api.subprocess, "run", run)
    monkeypatch.setattr(api.time, "sleep", sleep)
    client = api.MagisterAPI("school", "user", "password")

    assert client.get_data() == {"kinderen": {"student": {}}}
    assert run.call_count == 2
    sleep.assert_called_once_with(17)


@pytest.mark.parametrize("status", ["502", "503", "504"])
def test_temporary_server_status_maps_to_magister_unavailable(monkeypatch, status):
    failure = subprocess.CalledProcessError(
        75,
        "python3",
        stderr=f"Magister server returned HTTP {status}\n",
    )
    run = Mock(side_effect=[failure, failure])
    sleep = Mock()
    monkeypatch.setattr(api.subprocess, "run", run)
    monkeypatch.setattr(api.time, "sleep", sleep)
    client = api.MagisterAPI("school", "user", "password")

    with pytest.raises(api.MagisterUnavailable, match=f"HTTP {status}") as caught:
        client.get_data()

    assert "niet bij de Home Assistant-integratie" in str(caught.value)
    assert run.call_count == 2
    sleep.assert_called_once_with(2)


def test_request_timeout_maps_to_magister_unavailable(monkeypatch):
    stderr = "Magister request to example.magister.net timed out after 15.1s\n"
    failure = subprocess.CalledProcessError(75, "python3", stderr=stderr)
    run = Mock(side_effect=[failure, failure])
    sleep = Mock()
    monkeypatch.setattr(api.subprocess, "run", run)
    monkeypatch.setattr(api.time, "sleep", sleep)
    client = api.MagisterAPI("school", "user", "password")

    with pytest.raises(api.MagisterUnavailable, match="time-out") as caught:
        client.get_data()

    assert "niet bij de Home Assistant-integratie" in str(caught.value)
    assert run.call_count == 2
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
    setattr(sys.modules["homeassistant.helpers"], "issue_registry", registry)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.update_coordinator", SimpleNamespace(
        DataUpdateCoordinator=DataUpdateCoordinator, UpdateFailed=UpdateFailed,
    ))
    setattr(
        sys.modules["homeassistant.exceptions"],
        "ConfigEntryAuthFailed",
        type("ConfigEntryAuthFailed", (Exception,), {}),
    )
    package = ModuleType("magister_test")
    package.__path__ = [str(ROOT)]
    monkeypatch.setitem(sys.modules, "magister_test", package)
    monkeypatch.setitem(sys.modules, "magister_test.api", api)
    monkeypatch.setitem(sys.modules, "magister_test.const", SimpleNamespace(
        DOMAIN="magister_school", DEFAULT_POLL_INTERVAL=900,
    ))
    return load_module("magister_test.coordinator", ROOT / "coordinator.py")


@pytest.mark.parametrize("failure", [TimeoutError("timed out"), {"kinderen": {}}, {}])
def test_issue_is_created_on_failure_and_cleared_on_recovery(coordinator_module, failure):
    module = coordinator_module
    entry = SimpleNamespace(entry_id="account-1", title="Magister", async_on_unload=Mock())
    data = {"kinderen": {"student": {}}}
    hass = SimpleNamespace(async_add_executor_job=AsyncMock(side_effect=[failure, data]))
    coordinator = module.MagisterDataUpdateCoordinator(hass, entry, "school", "user", "password")
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


def test_temporary_magister_outage_has_dedicated_warning_and_clears(coordinator_module):
    module = coordinator_module
    entry = SimpleNamespace(entry_id="account-1", title="Magister", async_on_unload=Mock())
    outage = module.MagisterUnavailable(
        "Magister is tijdelijk niet beschikbaar (HTTP 503). "
        "Dit is een storing bij Magister/Trevianum."
    )
    data = {"kinderen": {"student": {}}}
    hass = SimpleNamespace(async_add_executor_job=AsyncMock(side_effect=[outage, data]))
    coordinator = module.MagisterDataUpdateCoordinator(
        hass, entry, "school", "user", "password"
    )

    with pytest.raises(module.UpdateFailed, match="tijdelijk niet beschikbaar"):
        asyncio.run(coordinator._async_update_data())

    call = module.ir.async_create_issue.call_args
    assert call.args == (hass, "magister_school", "fetch_failed_account-1")
    assert call.kwargs["severity"] == module.ir.IssueSeverity.WARNING
    assert call.kwargs["translation_key"] == "magister_unavailable"
    module.ir.async_delete_issue.assert_not_called()

    assert asyncio.run(coordinator._async_update_data()) == data
    module.ir.async_delete_issue.assert_called_once_with(
        hass, "magister_school", "fetch_failed_account-1"
    )


def test_issue_translations_are_complete():
    for path in (ROOT / "strings.json", *sorted((ROOT / "translations").glob("*.json"))):
        issues = json.loads(path.read_text())["issues"]
        fetch_issue = issues["fetch_failed"]
        assert "{name}" in fetch_issue["title"]
        assert "{error}" in fetch_issue["description"]
        outage_issue = issues["magister_unavailable"]
        assert "{name}" in outage_issue["title"]


def test_recovery_does_not_clear_another_accounts_issue(coordinator_module):
    module = coordinator_module
    hass = SimpleNamespace(async_add_executor_job=AsyncMock(side_effect=[TimeoutError("timed out"),
                                                                        {"kinderen": {"student": {}}}]))
    clients = [module.MagisterDataUpdateCoordinator(
        hass, SimpleNamespace(
            entry_id=entry_id, title="Magister", async_on_unload=Mock(),
        ), "school", "user", "password",
    ) for entry_id in ("first", "second")]
    with pytest.raises(module.UpdateFailed):
        asyncio.run(clients[0]._async_update_data())
    asyncio.run(clients[1]._async_update_data())
    assert module.ir.async_create_issue.call_args.args[2] == "fetch_failed_first"
    module.ir.async_delete_issue.assert_called_once_with(hass, "magister_school", "fetch_failed_second")
