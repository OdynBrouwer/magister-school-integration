"""Tests voor de Lovelace-resource-helper in __init__.py.

De helper leest de Lovelace-data van Home Assistant, die per release van vorm
verschilt: een ``LovelaceData``-dataclass of een gewone dict. Deze tests draaien
alleen als Home Assistant beschikbaar is.
"""

import importlib

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
