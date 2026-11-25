"""Tests voor de Lovelace-resource-helper in __init__.py.

De helper leest de Lovelace-data van Home Assistant, die per release van vorm
verschilt: een ``LovelaceData``-dataclass of een gewone dict. Deze tests draaien
alleen als Home Assistant beschikbaar is.
"""

import asyncio
import importlib
from types import SimpleNamespace

import pytest

pytest.importorskip("homeassistant")

integration = importlib.import_module("custom_components.magister_school")


class FakeResources:
    def __init__(self):
        self.items = []

    def async_create_item(self, data):
        self.items.append(data)


def test_reads_resources_attribute_from_dataclass_layout():
    resources = FakeResources()

    class LovelaceData:
        def __init__(self, collection):
            self.resources = collection

    assert integration._lovelace_resources(LovelaceData(resources)) is resources


def test_reads_resources_key_from_older_dict_layout():
    resources = FakeResources()

    assert integration._lovelace_resources({"resources": resources}) is resources


def test_returns_none_without_a_collection():
    assert integration._lovelace_resources(None) is None
    assert integration._lovelace_resources({}) is None
    assert integration._lovelace_resources(object()) is None


def _run(coro):
    return asyncio.run(coro)


def test_card_version_comes_from_the_integration_loader(monkeypatch):
    async def fake_get_integration(hass, domain):
        assert domain == integration.DOMAIN
        return SimpleNamespace(version="1.2.3")

    monkeypatch.setattr(integration, "async_get_integration", fake_get_integration)

    assert _run(integration._card_version(object())) == "1.2.3"


def test_card_version_falls_back_when_the_version_is_missing(monkeypatch):
    async def fake_get_integration(hass, domain):
        return SimpleNamespace(version=None)

    monkeypatch.setattr(integration, "async_get_integration", fake_get_integration)

    assert _run(integration._card_version(object())) == "0"


def test_card_version_falls_back_when_the_integration_is_unknown(monkeypatch):
    async def fake_get_integration(hass, domain):
        raise integration.IntegrationNotFound("magister_school")

    monkeypatch.setattr(integration, "async_get_integration", fake_get_integration)

    assert _run(integration._card_version(object())) == "0"
