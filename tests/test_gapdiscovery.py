# -*- coding: utf-8 -*-
from gapdiscovery import rebuild_abstract, extract_gap_sentence, parse_discoveries


def test_rebuild_abstract_and_extract():
    inv = {"Hydrogen": [0], "storage": [1], "is": [2], "important.": [3],
           "However,": [4], "the": [5], "wettability": [6], "of": [7], "hydrogen": [8], "in": [9],
           "shale": [10], "remains": [11], "largely": [12], "unexplored": [13], "under": [14], "reservoir": [15],
           "conditions": [16], "today.": [17]}
    text = rebuild_abstract(inv)
    assert text.startswith("Hydrogen storage is important.")
    s = extract_gap_sentence(text)
    assert s and "unexplored" in s and s.startswith("However,")


def test_no_gap_sentence_returns_none():
    assert extract_gap_sentence("We simulate flow in a core. Results agree with experiments well enough.") is None


def test_parse_discoveries_skips_incomplete():
    inv = {w: [i] for i, w in enumerate("Little is known about the long term cyclic behaviour of hydrogen in depleted gas fields today.".split())}
    data = {"results": [{"id": "https://openalex.org/W1", "doi": "https://doi.org/10.1/x", "title": "T",
                         "publication_year": 2026, "publication_date": "2026-10-01",
                         "abstract_inverted_index": inv, "primary_location": {"source": {"display_name": "J"}}},
                        {"id": "W2", "title": "no abstract"}]}
    out = parse_discoveries(data, "topic")
    assert len(out) == 1 and out[0]["venue"] == "J" and out[0]["key"].startswith("https://doi.org")


def test_method_sentences_and_generic_data_are_not_gaps():
    assert extract_gap_sentence("This study develops a framework under conditions of limited data availability for screening.") is None
    assert extract_gap_sentence("The cyclic behaviour of hydrogen in depleted reservoirs remains poorly understood today.")


def test_parse_crossref_filters_by_keyword_and_strips_jats():
    from gapdiscovery import parse_crossref
    data = {"message": {"items": [
        {"DOI": "10.1/a", "title": ["Hydrogen cycling"], "issued": {"date-parts": [[2026, 10, 9]]}, "container-title": ["J"],
         "abstract": "<jats:p>Hydrogen cycling in aquifers remains largely unexplored in the field literature.</jats:p>"},
        {"DOI": "10.1/b", "title": ["Other"], "abstract": "<jats:p>Cancer treatment remains poorly understood in many contexts today.</jats:p>"}]}}
    out = parse_crossref(data, "t", ["hydrogen"])
    assert len(out) == 1 and out[0]["key"].endswith("10.1/a") and out[0]["date"] == "2026-10-09"


def test_noise_filter_drops_medical_eor():
    from gapdiscovery import is_relevant
    assert not is_relevant("Estradiol ratio", "EOR in IVF patients remains unclear", ["oil recovery"])
    assert is_relevant("Polymer flooding", "enhanced oil recovery in sandstone", ["oil recovery"])
    assert not is_relevant("Reservoir computing", "reservoir computing hardware", ["reservoir"])


def test_list_filters_and_get(tmp_path, monkeypatch):
    import database as d
    monkeypatch.setattr(d, "DB_PATH", str(tmp_path / "t.db"), raising=False)
    d.init_gap_tables()
    items = [{"key": f"k{i}", "topic": "A" if i % 2 else "B", "sentence": "s" * 60, "title": f"T{i}", "year": 2026,
              "date": f"2026-10-{i + 1:02d}", "venue": "J", "url": f"u{i}", "cites": 0} for i in range(10)]
    d.add_discovered_gaps(items)
    assert d.count_discovered_gaps() == 10
    assert d.count_discovered_gaps(topic="A") == 5
    assert d.count_discovered_gaps(since="2026-10-08") == 3
    rows = d.list_discovered_gaps(4, 4)
    assert len(rows) == 4 and "id" in rows[0]
    assert d.get_discovered_gap(rows[0]["id"])["key"] == rows[0]["key"]
    assert d.get_discovered_gap(99999) is None
