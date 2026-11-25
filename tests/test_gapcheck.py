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
        assert g["query"] and g["query"].count('"') % 2 == 0 and g["query"].count("(") == g["query"].count(")")
        assert g["broad"].count('"') % 2 == 0 and 0 <= g["fit"] <= 2


def test_format_check_failure():
    assert "تعذّر" in format_check({"ok": False})


def test_priority_scoring_and_ranking_static():
    from gapcheck import priority, rank_gaps, live_crowd_points
    by_id = {g["id"]: g for g in RESEARCH_GAPS}
    assert priority(by_id[8]) < priority(by_id[25])        # مختبري صعب < برمجي سهل
    assert priority(by_id[1], 500) < priority(by_id[1], 3)  # الازدحام الحي يخفض الدرجة
    assert live_crowd_points(None) is None and live_crowd_points(0) == 0.5
    ranked = rank_gaps(RESEARCH_GAPS, live=False)
    assert len(ranked) == len(RESEARCH_GAPS) and ranked[0]["score"] >= ranked[-1]["score"]


def test_matrix_formatting_handles_missing():
    from gapcheck import format_matrix
    m = [("A", "x")]; a = [("B", "y"), ("C", "z")]
    out = format_matrix(m, a, {("A", "B"): 2, ("A", "C"): None})
    assert "?" in out and "A × B (2)" in out
