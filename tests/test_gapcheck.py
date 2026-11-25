# -*- coding: utf-8 -*-
from data.research_gaps import RESEARCH_GAPS, BROAD_QUERY
from gapcheck import clean_query, parse_year_groups, parse_closest, verdict, format_check


def test_clean_query_blocks_filter_injection():
    q = clean_query("a, b:c|d  e")
    assert "," not in q and ":" not in q and "|" not in q and "  " not in q


def test_parsers_tolerate_garbage():
    assert parse_year_groups(None) == {}
    assert parse_year_groups({"group_by": [{"key": "2024", "count": 5}, {"key": "x"}]}) == {2024: 5}
    assert parse_closest({"results": [{"title": ""}, {"title": "T", "publication_year": 2025}]})[0]["title"] == "T"


def test_verdict_thresholds():
    assert verdict(0).startswith("⚪") and verdict(5).startswith("🟢")
    assert verdict(30).startswith("🟡") and verdict(500).startswith("🔴")


def test_catalog_is_complete_and_honest():
    assert len({g["id"] for g in RESEARCH_GAPS}) == len(RESEARCH_GAPS)
    for g in RESEARCH_GAPS:
        assert 1 <= g["difficulty"] <= 5 and g["data"] in ("none", "public", "lab", "partner")
        assert g["crowd"] in ("low", "medium", "high") and g["id"] in BROAD_QUERY
        assert g["query"] and "OR " not in g["query"]


def test_format_check_failure():
    assert "تعذّر" in format_check({"ok": False})
