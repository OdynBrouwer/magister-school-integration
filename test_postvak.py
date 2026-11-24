"""Tests voor de berichten- en mededelingen-samenvatting in magister.py."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).parent

spec = importlib.util.spec_from_file_location(
    "magister_postvak", ROOT / "custom_components" / "magister_school" / "script" / "magister.py"
)
assert spec is not None and spec.loader is not None

magister = importlib.util.module_from_spec(spec)
spec.loader.exec_module(magister)


class FakeMagister:
    """Geeft canned responses terug op basis van het opgebouwde pad."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def req(self, *args):
        self.calls.append(args)
        path = "/".join(str(arg) for arg in args if not isinstance(arg, dict))
        return self.responses.get(path, {})


def _hub():
    return {"links": {"mappen": {"href": "/api/berichten/mappen"}}}


def _berichten_responses():
    return {
        "berichten": _hub(),
        "berichten/mappen/alle": {
            "items": [
                {"id": 1, "naam": "Postvak in", "aantalOngelezen": 2},
                {"id": 2, "naam": "Archief", "aantalOngelezen": 0},
            ],
            "totalCount": 2,
        },
        "berichten/mappen/1/berichten": {
            "items": [
                {
                    "onderwerp": "Ouderavond",
                    "afzender": {"naam": "Dhr. Jansen"},
                    "verzondenOp": "2026-11-20T10:00:00.0000000Z",
                    "isGelezen": False,
                    "heeftBijlagen": True,
                },
                {
                    "onderwerp": "Nieuw rooster",
                    "afzender": {"naam": "School"},
                    "verzondenOp": "2026-11-21T10:00:00.0000000Z",
                    "isGelezen": True,
                    "heeftBijlagen": False,
                },
            ]
        },
        "berichten/mappen/2/berichten": {
            "items": [
                {
                    "onderwerp": "Oud bericht",
                    "afzender": "Systeem",
                    "verzondenOp": "2026-09-01T10:00:00.0000000Z",
                }
            ]
        },
    }


def test_berichten_samenvatting_telt_ongelezen_en_sorteert_nieuwste_eerst():
    warnings = {}
    samenvatting = magister._berichten_samenvatting(FakeMagister(_berichten_responses()), warnings)

    assert samenvatting["ongelezen"] == 2
    assert samenvatting["mappen"] == [
        {"naam": "Postvak in", "ongelezen": 2},
        {"naam": "Archief", "ongelezen": 0},
    ]
    assert [bericht["onderwerp"] for bericht in samenvatting["laatste"]] == [
        "Nieuw rooster",
        "Ouderavond",
        "Oud bericht",
    ]
    assert warnings == {}


def test_berichten_samenvatting_leest_afzender_als_object_en_als_tekst():
    samenvatting = magister._berichten_samenvatting(
        FakeMagister(_berichten_responses()), {}
    )

    per_onderwerp = {b["onderwerp"]: b for b in samenvatting["laatste"]}
    assert per_onderwerp["Ouderavond"]["afzender"] == "Dhr. Jansen"
    assert per_onderwerp["Oud bericht"]["afzender"] == "Systeem"
    assert per_onderwerp["Ouderavond"]["is_gelezen"] is False
    assert per_onderwerp["Ouderavond"]["heeft_bijlagen"] is True
    assert per_onderwerp["Oud bericht"]["is_gelezen"] is False  # ontbrekend veld

    # afzender zonder naam-object mag geen crash of "None" opleveren
    leeg = magister._bericht_samenvatting({"onderwerp": "x", "afzender": None})
    assert leeg["afzender"] == ""


def test_berichten_samenvatting_beperkt_zich_tot_vijf_berichten():
    responses = {"berichten": _hub(), "berichten/mappen/alle": {"items": []}}
    for map_id in (1, 2, 3):
        responses["berichten/mappen/alle"]["items"].append(
            {"id": map_id, "naam": f"Map {map_id}", "aantalOngelezen": 1}
        )
        responses[f"berichten/mappen/{map_id}/berichten"] = {
            "items": [
                {
                    "onderwerp": f"Bericht {map_id}-{index}",
                    "afzender": {"naam": "School"},
                    "verzondenOp": f"2026-11-0{index + 1}T10:00:00Z",
                }
                for index in range(2)
            ]
        }

    samenvatting = magister._berichten_samenvatting(FakeMagister(responses), {})

    assert samenvatting["ongelezen"] == 3
    assert len(samenvatting["laatste"]) == 5


def test_berichten_samenvatting_zonder_links_geeft_none():
    assert magister._berichten_samenvatting(FakeMagister({"berichten": {}}), {}) is None


def test_berichten_samenvatting_meldt_ontbrekende_mapitems():
    responses = {
        "berichten": _hub(),
        "berichten/mappen/alle": {"items": [{"id": 1, "naam": "Postvak in"}]},
        "berichten/mappen/1/berichten": {"items": None},
    }
    warnings = {}

    samenvatting = magister._berichten_samenvatting(FakeMagister(responses), warnings)

    assert samenvatting["mappen"] == [{"naam": "Postvak in", "ongelezen": 0}]
    assert samenvatting["laatste"] == []
    assert warnings["berichten"] == 1


def test_mededelingen_samenvatting_gebruikt_totalcount():
    responses = {
        "mededelingen": {
            "items": [
                {
                    "onderwerp": "Kerstgala",
                    "afzender": {"naam": "School"},
                    "verzondenOp": "2026-11-22T12:00:00Z",
                }
            ],
            "totalCount": 7,
        }
    }

    samenvatting = magister._mededelingen_samenvatting(FakeMagister(responses), {})

    assert samenvatting["aantal"] == 7
    assert samenvatting["laatste"] == [
        {"onderwerp": "Kerstgala", "afzender": "School", "verzonden_op": "2026-11-22T12:00:00"}
    ]


def test_mededelingen_samenvatting_bij_lege_lijst():
    samenvatting = magister._mededelingen_samenvatting(
        FakeMagister({"mededelingen": {"items": [], "totalCount": 0}}), {}
    )

    assert samenvatting == {"aantal": 0, "laatste": []}


def test_mededelingen_samenvatting_bij_ontbrekende_lijst():
    warnings = {}

    samenvatting = magister._mededelingen_samenvatting(
        FakeMagister({"mededelingen": {"items": None}}), warnings
    )

    assert samenvatting == {"aantal": 0, "laatste": []}
    assert warnings["mededelingen"] == 1
